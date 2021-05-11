import logging
import subprocess
import sys

import discord
from discord.ext import commands


from lib import process_output


class main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.command()
    async def restart(self, ctx):
        if ctx.author.id == 635377375739248652:
            msg = "You had the required permissions for this command.\nExecute the command.\n***The bot will be " \
                  "temporarily unavailable!***\n------------- LOG -------------\n"
            m: discord.Message = await ctx.send(msg)
            p = subprocess.Popen(["git", "pull"],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            msg, m = await process_output(p, m, msg, ctx)
            msg += "------------- EXITED -------------\n"
            try:
                await m.edit(content=msg)
            except discord.errors.HTTPException:
                msg = msg.splitlines()[-1]
                await ctx.send(msg)
            self.logger.info("exit.")
            with open("ID_DISCORD_CL_CLAN", "w") as f:
                f.write(str(ctx.channel.id))
            sys.exit()
        else:
            await ctx.send(
                "***You do not have the required permissions to execute this command. Please contact admin.***"
            )

    @commands.command()
    async def cmd(self, ctx, *args):
        if ctx.author.id == 635377375739248652:
            msg = "You had the required permissions for this command.\nExecute the command.\n------------- LOG " \
                  "-------------\n "
            m: discord.Message = await ctx.send(msg)
            p = subprocess.Popen(args,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            msg, m = await process_output(p, m, msg, ctx)
            msg += "------------- EXITED -------------"
            await m.edit(content=msg)
        else:
            await ctx.send(
                "***You do not have the required permissions to execute this command. Please contact admin.***"
            )


def setup(bot):
    bot.add_cog(main(bot))
