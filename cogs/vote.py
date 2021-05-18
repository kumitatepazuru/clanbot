import logging
import os
from io import BytesIO

import discord
import numpy as np
from PIL import Image
from discord.ext import commands, tasks

from main import main


class vote(commands.Cog):
    def __init__(self, bot: main):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.loop.start()

    @commands.command(aliases=["ss"])
    async def showservers(self, ctx):
        if os.path.isfile("./srt/screenshot.jpg"):
            im = Image.open("./srt/screenshot.jpg")
            im = im.crop((341, 280, 681, 327))
            img_bytes = BytesIO()
            im.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            await ctx.send("今のANNIサーバー一覧\n\n**表示の見方**\n緑: 参加できます\n青: phase 3です。プレミアム会員の方は参加できます\n赤: phase 4以上で参加できません。",
                           file=discord.File(img_bytes, filename="screenshot.jpg"))
        else:
            await ctx.send("申し訳ありません。ただいまANNIサーバー検知システムを起動中(再起動中)です。もうしばらく(最大10分)お待ちください。")

    @commands.command(aliases=["ts"])
    async def textservers(self, ctx):
        if os.path.isfile("./srt/screenshot.jpg"):
            im = np.array(Image.open("./srt/screenshot.jpg"))
            l = []
            for i in range(9):
                p = im[295, 363 + i * 36]
                if np.sum(p) > 100:
                    l.append(str(np.argmax(p) + 1))
                else:
                    l.append("0")
            # await ctx.send(" ".join(l))
            await ctx.send(
                "サーバー数:" + str(len(l) - l.count("0")) +
                "\n**内訳**\n参加可能なサーバー: " + str(l.count("2")) +
                "\nphase 3でプレミアム会員のみ参加可能なサーバー: " + str(l.count("3")) +
                "\nphase 4以上で参加できないサーバー: " + str(l.count("1"))
            )

        else:
            await ctx.send("申し訳ありません。ただいまANNIサーバー検知システムを起動中(再起動中)です。もうしばらく(最大10分)お待ちください。")

    def cog_unload(self):
        self.loop.cancel()

    @tasks.loop(seconds=1)
    async def loop(self):
        self.logger.info("unti")


def setup(bot):
    bot.add_cog(vote(bot))
