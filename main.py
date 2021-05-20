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
    "cogs.fileman",
    "cogs.setup",
    "cogs.vote"
]
logging.basicConfig(level=logging.INFO,
                    format="\033[38;5;4m%(asctime)s \033[38;5;10m[%(module)s] [%(name)s]=>L%(lineno)d "
                           "\033[38;5;14m[%(levelname)s] \033[0m%(message)s")


class HelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.commands_heading = "コマンド"
        self.no_category = "その他"
        self.command_attrs["help"] = "コマンド一覧と簡単な説明を表示"

    def get_ending_note(self):
        return (f"各コマンドの説明: ,help <コマンド名>\n"
                f"各カテゴリの説明: ,help <カテゴリ名>\n")


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
            else:
                self.con.autocommit(True)
                cursor = self.con.cursor()
                cursor.execute("CREATE DATABASE IF NOT EXISTS clanbot")
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS clanbot.upload_channel ( `id` INT NOT NULL AUTO_INCREMENT , `channel_id` BIGINT NOT NULL , `url` TEXT NOT NULL , PRIMARY KEY (`id`))")
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS clanbot.guild_data "
                    "( `id` INT NOT NULL AUTO_INCREMENT,"
                    "`guild_id` BIGINT NOT NULL , "
                    "`mention_id` BIGINT NULL DEFAULT NULL , "
                    "`upload_id` BIGINT NULL DEFAULT NULL , "
                    "`mcid_id` BIGINT NOT NULL , "
                    "`mod_id` BIGINT NOT NULL , "
                    "`notification_id` BIGINT NOT NULL  , "
                    "`clan_id` BIGINT NULL DEFAULT NULL, "
                    "PRIMARY KEY (`id`))"
                )
                cursor.close()

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

    async def join(self, guild: discord.Guild):
        logging.info("server joined guild id:"+str(guild.id))
        if guild.system_channel is not None:
            channel = guild.system_channel
            await channel.send("こんにちは!\nclanbotです。これは、主にminecraftのマルチプレイサーバーにおけるチーム(クラン)のdiscordサーバーの運営に役立てるbotです。\n"
                               "まずは、初期設定をしましょう。 `,setup` で初期設定を実行できます(専用のチャンネルが作成されます)")


def close(bot):
    bot.cursor.close()
    bot.con.close()


if __name__ == '__main__':
    # with open('token', 'r') as f:
    #     TOKEN = f.readline().rstrip()
    intents = discord.Intents.default()
    intents.members = True
    intents.guilds = True
    bot = main(command_prefix=',', intents=intents, help_command=HelpCommand())  # command_prefixはコマンドの最初の文字として使うもの。 e.g. !ping
    atexit.register(close, bot)
    bot.run(os.environ.get("TOKEN"))  # Botのトークン
