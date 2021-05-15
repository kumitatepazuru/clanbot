import logging
import os
import traceback

import discord
from discord.ext import commands

INITIAL_EXTENSIONS = [
    "cogs.restart",
    "cogs.oauth"
]
logging.basicConfig(level=logging.INFO,
                    format="\033[38;5;4m%(asctime)s \033[38;5;10m[%(module)s] [%(name)s]=>L%(lineno)d "
                           "\033[38;5;14m[%(levelname)s] \033[0m%(message)s")


class main(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except SystemExit:
                pass
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        # 起動したらターミナルにログイン通知が表示される
        logging.info('Bot logged')
        if os.path.isfile("ID_DISCORD_CL_CLAN"):
            with open("ID_DISCORD_CL_CLAN") as f:
                channel = self.get_channel(int(f.read().splitlines()[0]))
                await channel.send("restarted. command completed.")
            os.remove("ID_DISCORD_CL_CLAN")


if __name__ == '__main__':
    # with open('token', 'r') as f:
    #     TOKEN = f.readline().rstrip()

    intents = discord.Intents.default()
    intents.members = True
    bot = main(command_prefix=',', help_command=None, intents=intents)  # command_prefixはコマンドの最初の文字として使うもの。 e.g. !ping
    bot.run(os.environ.get("TOKEN"))  # Botのトークン
