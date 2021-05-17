import logging
import os
from io import BytesIO

import discord
from discord.ext import commands

from PIL import Image
from main import main


class vote(commands.Cog):
    def __init__(self, bot: main):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.command(aliases=["ss"])
    async def showservers(self,ctx):
        if os.path.isfile("./srt/screenshot.jpg"):
            im = Image.open("./srt/screenshot.jpg")
            im = im.crop((341,217,681,322))
            img_bytes = BytesIO()
            im.save(img_bytes,format="PNG")
            img_bytes.seek(0)
            await ctx.send("今のANNIサーバー一覧",file=discord.File(img_bytes,filename="screenshot.jpg"))
        else:
            await ctx.send("申しわかりません。ただいまANNIサーバー検知システムを起動中(再起動中)です。もうしばらく(最大10分)お待ちください。")


def setup(bot):
    bot.add_cog(vote(bot))
