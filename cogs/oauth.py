import logging

import discord
from discord.ext import commands

from lib import usedname
from main import main


class oauth(commands.Cog):
    def __init__(self, bot: main):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.Cog.listener(name='on_message')
    async def msg(self, message: discord.Message):
        self.bot.cursor.execute(f"SELECT mcid_id,clan_id,notification_id,mod_id FROM clanbot.guild_data WHERE guild_id={message.guild.id}")
        rows = self.bot.cursor.fetchall()
        if len(rows) != 0:
            rows = rows[0]
            if message.channel.id == rows[0]:
                self.logger.info("got mcid msg")
                self.logger.info("create new channel "+message.author.name + "-認証")
                guild: discord.Guild = self.bot.get_guild(message.guild.id)
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True),
                    guild.get_member(message.author.id): discord.PermissionOverwrite(read_messages=True)
                }
                channel: discord.TextChannel = await guild.create_text_channel(name=message.author.name + "-認証",
                                                                               overwrites=overwrites)
                if await usedname(message.content, channel):
                    self.logger.info("Already used mcid. Continue authentication.")
                    self.logger.info(f"URL: https://ja.namemc.com/profile/{message.content}.1")
                    msg: discord.Message = await channel.send(
                        message.author.mention + f"https://ja.namemc.com/profile/{message.content}.1\n"
                                                 f"このユーザーでよろしいでしょうか。問題がない場合は\N{HEAVY LARGE CIRCLE}を"
                                                 f"選択してしてください。\nなにか問題等がある場合はこのチャンネルでそのまま問題をお話ください。")

                    await msg.add_reaction("\N{HEAVY LARGE CIRCLE}")

                    def check(ren: discord.Reaction, user: discord.User) -> bool:
                        # リアクション先のメッセージや追加された絵文字が適切かどうか判断する。
                        return str(
                            ren.emoji) in "\N{HEAVY LARGE CIRCLE}" and ren.message == msg and user == message.author

                    reaction, _ = await self.bot.wait_for("reaction_add", check=check)
                    await msg.clear_reactions()
                    self.logger.info("completed authentication.")
                    await channel.delete(reason="ユーザーに問題はなく、それをユーザー自身が同意したため、認証用チャンネルを削除した")
                    if rows[1] is not None:
                        await message.author.add_roles(message.guild.get_role(rows[1]))
                    await self.bot.get_channel(rows[2]).send(message.author.mention + "メンバーへようこそ！")
                else:
                    self.logger.warning("not used this mcid.")
                    self.logger.warning(f"content: {message.content}")
                    await self.bot.get_channel(rows[3]).send(
                        "@everyone " + message.author.name + "が送信した" + message.
                        content + "は存在しませんでした。適切な処理をしてください。チャンネル: " + channel.mention)


def setup(bot):
    bot.add_cog(oauth(bot))
