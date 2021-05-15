import json
import logging
import time

import MySQLdb
import discord
from discord.ext import commands

ok = False
i = 0
while not ok and i < 10:
    try:
        con = MySQLdb.connect(
            user='root',
            passwd='docker_sql',
            host='dockerserver_mysql_1',
            charset="utf8")
        ok = True
    except MySQLdb._exceptions.OperationalError:
        i += 1
        time.sleep(1)
        print(f"bootstrap:upload.py:WARN: Can't connect to MySQL server {i}/10")
    else:
        cursor = con.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS clanbot")
        cursor.execute("CREATE TABLE IF NOT EXISTS clanbot.upload_channel (id BIGINT, url TEXT)")


class upload(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.command()
    async def dlf(self, ctx: commands.Context):
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
        cursor.execute(f"INSERT INTO clanbot.upload_channel VALUES ({channel.id},'[]')")

        msg = await channel.send(ctx.author.mention+" こちらに、modファイルを**まとめずに**送信してください。(自動的にまとめられます）\n送り終わったら🆗を押してください")
        await msg.add_reaction("🆗")

        def check(ren: discord.Reaction, user: discord.User) -> bool:
            # リアクション先のメッセージや追加された絵文字が適切かどうか判断する。
            return str(
                ren.emoji) in "🆗" and ren.message == msg and user == ctx.author

        reaction, _ = await self.bot.wait_for("reaction_add", check=check)
        await msg.clear_reactions()
        cursor.execute(f"SELECT url FROM clanbot.upload_channel WHERE id={channel.id}")
        rows = cursor.fetchall()
        await channel.send("\n".join(json.loads(rows[0][0])))

    @commands.Cog.listener(name='on_message')
    async def msg(self, message: discord.Message):
        cursor.execute(f"SELECT url FROM clanbot.upload_channel WHERE id={message.channel.id}")
        rows = cursor.fetchall()
        if len(rows) != 0:
            for i in message.attachments:
                self.logger.info(i.url)
                f = json.loads(rows[0][0])
                f.append(i.url)
                cursor.execute(
                    "UPDATE clanbot.upload_channel SET url='" + json.dumps(f) + f"' WHERE id={message.channel.id}")

    def __del__(self):
        cursor.close()
        con.close()


def setup(bot):
    bot.add_cog(upload(bot))
