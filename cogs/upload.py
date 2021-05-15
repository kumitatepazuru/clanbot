import logging

import discord
from discord.ext import commands
import MySQLdb


class upload(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.command()
    async def dlf(self, ctx):
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

        con = MySQLdb.connect(
            user='root',
            passwd='docker_sql',
            host='dockerserver_mysql_1',
            charset="utf8")
        cursor = con.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS clanbot")
        cursor.execute("CREATE TABLE IF NOT EXISTS clanbot.upload_channel (id int)")
        cursor.execute(f"INSERT INTO clanbot.upload_channel VALUES ({channel.id})")
        cursor.execute("SELECT * FROM clanbot.upload_channel")

        # 実行結果をすべて取得する
        rows = cursor.fetchall()

        # 一行ずつ表示する
        for row in rows:
            self.logger.warning(row)

        cursor.close()
        con.close()

def setup(bot):
    bot.add_cog(upload(bot))
