import logging

import discord
from discord.ext import commands

from lib import usedname
from main import main


class vote(commands.Cog):
    def __init__(self, bot: main):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.command(alias=["ss"])
    async def showservers(self,ctx):
        with open("./srt/screenshot.jpg","rb") as f:
            ctx.send(file=discord.File(f,filename="screenshot.jpg"))


def setup(bot):
    bot.add_cog(vote(bot))
