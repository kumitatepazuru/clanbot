import logging
import os

import discord
from discord.ext import commands

from lib import usedname
from main import main


class vote(commands.Cog):
    def __init__(self, bot: main):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.command(aliases=["ss"])
    async def showservers(self,ctx):
        if os.path.isfile("./srt/screenshot.jpg"):
            with open("./srt/screenshot.jpg","rb") as f:
                await ctx.send(file=discord.File(f,filename="screenshot.jpg"))
        else:
            await ctx.send("申しわかりません。ただいまANNIサーバー検知システムを起動中(再起動中)です。もうしばらく(最大10分)お待ちください。")


def setup(bot):
    bot.add_cog(vote(bot))
