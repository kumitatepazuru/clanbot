import json
import logging
import os
import random
import string
import zipfile

import discord
import requests
from discord.ext import commands

from lib import issetup
from main import main


def randomname(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


class upload(commands.Cog):
    def __init__(self, bot: main):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.command()
    async def dlf(self, ctx: commands.Context, *args):
        if await issetup(ctx.guild, self.bot.cursor, ctx.channel,self.logger):
            if len(args) != 2:
                await ctx.send("自分が使っているファイルなどを共有するコマンド\n\n**使い方**\n,dlf [共有ファイル名] [コメント]")
            else:
                self.logger.info("started dl man")
                self.logger.info("create new channel " + ctx.author.name + "-アップロード")
                guild: discord.Guild = self.bot.get_guild(ctx.guild.id)
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True),
                    guild.get_member(ctx.author.id): discord.PermissionOverwrite(read_messages=True)
                }
                channel: discord.TextChannel = await guild.create_text_channel(name=ctx.author.name + "-アップロード",
                                                                               overwrites=overwrites)
                self.bot.cursor.execute(f"INSERT INTO clanbot.upload_channel VALUES ({channel.id},'[]')")

                msg = await channel.send(
                    ctx.author.mention + " こちらに、modファイルを**まとめずに**送信してください。(自動的にまとめられます）\n送り終わったら🆗を押してください")
                await msg.add_reaction("🆗")

                def check(ren: discord.Reaction, user: discord.User) -> bool:
                    # リアクション先のメッセージや追加された絵文字が適切かどうか判断する。
                    return str(
                        ren.emoji) in "🆗" and ren.message == msg and user == ctx.author

                reaction, _ = await self.bot.wait_for("reaction_add", check=check)
                await msg.clear_reactions()

                fn = randomname(8)
                while os.path.isdir(fn):
                    fn = randomname(8)
                os.makedirs("./httpd/file/" + fn + "/")
                fn = "./httpd/file/" + fn + "/" + args[0] + ".zip"
                with zipfile.ZipFile(fn, "w", zipfile.ZIP_LZMA) as z:
                    self.bot.cursor.execute(f"SELECT url FROM clanbot.upload_channel WHERE id={channel.id}")
                    rows = self.bot.cursor.fetchall()
                    await channel.send("送信されたファイルからzipファイルを生成中...")
                    for i in json.loads(rows[0][0]):
                        inf = zipfile.ZipInfo(os.path.basename(i), (1980, 1, 1, 0, 0, 0))
                        z.writestr(inf, requests.get(i).content)
                self.logger.info("file generated URL:" + fn)
                await channel.delete(reason="ファイルの作成が完了したため")
                self.bot.cursor.execute(f"SELECT mention_id,upload_id FROM clanbot.guild_data WHERE id={ctx.guild.id}")
                rows = self.bot.cursor.fetchall()
                self.logger.warning(str(rows))

    @commands.Cog.listener(name='on_message')
    async def msg(self, message: discord.Message):
        self.bot.cursor.execute(f"SELECT url FROM clanbot.upload_channel WHERE id={message.channel.id}")
        rows = self.bot.cursor.fetchall()
        if len(rows) != 0:
            for i in message.attachments:
                self.logger.info(i.url)
                f = json.loads(rows[0][0])
                f.append(i.url)
                self.bot.cursor.execute(
                    "UPDATE clanbot.upload_channel SET url='" + json.dumps(f) + f"' WHERE id={message.channel.id}")


def setup(bot):
    bot.add_cog(upload(bot))
