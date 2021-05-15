import atexit
import logging
import os
import time
import traceback

import MySQLdb
import discord
from discord.ext import commands

INITIAL_EXTENSIONS = [
    "cogs.restart",
    "cogs.oauth",
    "cogs.upload"
]
logging.basicConfig(level=logging.INFO,
                    format="\033[38;5;4m%(asctime)s \033[38;5;10m[%(module)s] [%(name)s]=>L%(lineno)d "
                           "\033[38;5;14m[%(levelname)s] \033[0m%(message)s")


class main(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

        ok = False
        i = 0

        while not ok and i < 10:
            try:
                self.con = MySQLdb.connect(
                    user='root',
                    passwd='docker_sql',
                    host='dockerserver_mysql_1',
                    charset="utf8")
                ok = True
            except MySQLdb._exceptions.OperationalError:
                i += 1
                time.sleep(1)
                print(f"bootstrap:upload.py:WARN: Can't connect to MySQL server {i}/10")
            finally:
                self.con.autocommit(True)
                self.cursor = self.con.cursor()
                self.cursor.execute("CREATE DATABASE IF NOT EXISTS clanbot")
                self.cursor.execute("CREATE TABLE IF NOT EXISTS clanbot.upload_channel (id BIGINT, url TEXT)")
                self.cursor.execute(
                    "CREATE TABLE IF NOT EXISTS clanbot.guild_data "
                    "( `guild_id` BIGINT NOT NULL , "
                    "`mention_id` BIGINT NULL DEFAULT NULL , "
                    "`upload_id` BIGINT NULL DEFAULT NULL , "
                    "`mcid_id` BIGINT NOT NULL , "
                    "`mod_id` BIGINT NOT NULL , "
                    "`notification_id` BIGINT NOT NULL )"
                )

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


def close(bot):
    bot.cursor.close()
    bot.con.close()


if __name__ == '__main__':
    # with open('token', 'r') as f:
    #     TOKEN = f.readline().rstrip()
    intents = discord.Intents.default()
    intents.members = True
    bot = main(command_prefix=',', help_command=None, intents=intents)  # command_prefixはコマンドの最初の文字として使うもの。 e.g. !ping
    atexit.register(close, bot)
    bot.run(os.environ.get("TOKEN"))  # Botのトークン
