import logging

import discord
from discord.ext import commands

from lib import issetup
from main import main


class cmd_setup(commands.Cog):
    def __init__(self, bot: main):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.command(name="setup")
    async def setup_cmd(self, ctx: commands.Context):
        if ctx.author.guild_permissions.administrator:
            if not await issetup(ctx.guild, self.bot.cursor, ctx.channel, self.logger, False):
                guild: discord.Guild = self.bot.get_guild(ctx.guild.id)
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True),
                    guild.get_member(ctx.author.id): discord.PermissionOverwrite(read_messages=True)
                }
                channel: discord.TextChannel = await guild.create_text_channel(name="clanbot-初期設定",
                                                                               overwrites=overwrites)
                await channel.send(ctx.author.mention + "この度は、clanbotを使用していただき、有難うございます。")
                await channel.send("早速、初期設定を始めましょう。")
                await channel.send(
                    "まず、ロールの設定です。\n運営や、クラン(チーム)長等の運営ロールを地位が高い順に上から並び替えてください。(そのようなロールが存在しない場合は問題ありません。)\n"
                    "次に、このbotを入れて生成された `clanbot` というロールを先程並び替えた運営ロールの真下に移動させてください。(運営ロールが存在しない場合は一番上に移動させてください)")
                await channel.send(
                    "できたら、`,set setup [mcidを記入しておくチャンネル] [運営のみが参照できるチャンネル] [botの重要な情報等の通知を行うチャンネル] [クラン(チーム)用ロール]` でサーバーの登録をしましょう。\n\n**各引数の説明**"
                    "mcidを記入しておくチャンネルは、そこにmcidを記入すると自動的に認証が始まるチャンネルをメンションしてください。そのようなチャンネルがない場合は作成してください。\n"
                    "運営のみが参照できるチャンネルは、何かしらの問題（例えば、mcidが存在しない等）が発生した時に送信するチャンネルをメンションしてください。そのようなチャンネルがない場合は作成してください。\n"
                    "botの重要な情報等の通知を行うチャンネルは、botの更新情報や障害情報、認証完了メッセージなどを送信するチャンネルをメンションしてください。そのようなチャンネルがない場合は作成してください。\n"
                    "クラン(チーム)用ロールは、クラン(チーム)の人のみに付与されるロールをメンションしてください。そのようなロールがない場合は作成してください。")
            else:
                await ctx.send("既に初期設定が完了しています。設定を変更するには、 `,help` でヘルプを参照してください。")
        else:
            await ctx.send("管理者権限を持っている人のみがこのコマンドを実行できます")

    @commands.group()
    async def set(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("このコマンドに引数が足りません。\n\n**使い方**\n※[]は適切なメンションや文字に置き換えてください。()で囲まれているものは任意です。\n"
                           "`,set setup [mcidを記入しておくチャンネル] [運営のみが参照できるチャンネル] [botの重要な情報等の通知を行うチャンネル] [クラン(チーム)用ロール]` 初期設定を行う")

    @set.command()
    async def setup(self, ctx):
        self.logger.info(str(ctx.message.channel_mentions))
        self.logger.info(str(ctx.message.role_mentions))
        if len(ctx.message.channel_mentions) == 3 and len(ctx.message.role_mentions) == 1:
            self.bot.cursor.execute("INSERT INTO clanbot.guild_data (`id`, `guild_id`, `mention_id`, `upload_id`, `mcid_id`, `mod_id`, `notification_id`, `clan_id`) VALUES "
                                    f"(NULL, {ctx.guild.id}, NULL, NULL, {ctx.message.channel_mentions[0].id}, {ctx.message.channel_mentions[1].id}, {ctx.message.channel_mentions[2].id}, {ctx.message.role_mentions[0].id})")
            await ctx.send("登録しました。")
        else:
            await ctx.send("このコマンドに引数が足りないか多すぎます。\n\n**使い方**\n※[]は適切なメンションや文字に置き換えてください。()で囲まれているものは任意です。\n"
                           "`,set setup [mcidを記入しておくチャンネル] [運営のみが参照できるチャンネル] [botの重要な情報等の通知を行うチャンネル] [クラン(チーム)用ロール]` 初期設定を行う")


def setup(bot):
    bot.add_cog(cmd_setup(bot))
