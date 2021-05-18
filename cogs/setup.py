import logging

import discord
import typing
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
            cursor = self.bot.con.cursor()
            if not await issetup(ctx.guild, cursor, ctx.channel, self.logger, False):
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
            cursor.close()
        else:
            await ctx.send("管理者権限を持っている人のみがこのコマンドを実行できます")

    @commands.group()
    async def set(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("このコマンドに引数が足りません。\n\n**使い方**\n※[]は適切なメンションや文字に置き換えてください。()で囲まれているものは任意です。\n"
                           "`,set setup [mcidを記入しておくチャンネル] [運営のみが参照できるチャンネル] [botの重要な情報等の通知を行うチャンネル] [クラン(チーム)用ロール]` 初期設定を行う\n"
                           "`,set mention [ロール or off]` 通知時に任意のロールにメンションをするロールを指定(offで解除)\n"
                           "`,set upload [チャンネル or off]` ファイル共有時に通知をするチャンネルを設定(offで解除)")

    @set.command()
    async def setup(self, ctx, mcid: typing.Optional[discord.TextChannel] = None,
                    mod: typing.Optional[discord.TextChannel] = None,
                    notification: typing.Optional[discord.TextChannel] = None,
                    clan: typing.Optional[discord.Role] = None):
        if mcid != None and mod is not None and notification is not None and clan is not None:
            cursor = self.bot.con.cursor()
            cursor.execute(
                "INSERT INTO clanbot.guild_data (`id`, `guild_id`, `mention_id`, `upload_id`, `mcid_id`, `mod_id`, `notification_id`, `clan_id`) VALUES "
                f"(NULL, {ctx.guild.id}, NULL, NULL, {mcid.id}, {mod.id}, {notification.id}, {clan.id})")
            cursor.close()
            await ctx.send("登録しました。")

            await ctx.send(
                "\n\nオプション機能として\n通知時に任意のロールにメンションをする設定 `,set mention [ロール or off]`\nファイル共有時に通知をするチャンネルを設定 `,set upload [ロール or off]`\n"
                "があります。ぜひご活用ください。")
        else:
            await ctx.send("このコマンドに引数が足りないか多すぎます。\n\n**使い方**\n※[]は適切なメンションや文字に置き換えてください。()で囲まれているものは任意です。\n"
                           "`,set setup [mcidを記入しておくチャンネル] [運営のみが参照できるチャンネル] [botの重要な情報等の通知を行うチャンネル] [クラン(チーム)用ロール]` 初期設定を行う")

    @set.command()
    async def mention(self, ctx, role: typing.Union[discord.Role, str]):
        cursor = self.bot.con.cursor()
        if issetup(ctx.guild, cursor, ctx.channel, self.logger):
            if len(ctx.message.role_mentions) == 1:
                cursor.execute(
                    f"UPDATE `guild_data` SET `mention_id` ={role.id}  WHERE guild_id={ctx.guild}")
                await ctx.send("設定しました。")
            elif role == "off":
                cursor.execute(
                    f"UPDATE `guild_data` SET `mention_id` =NULL  WHERE guild_id={ctx.guild}")
                await ctx.send("設定しました。")
            else:
                await ctx.send("このコマンドに引数が足りないか多すぎます。\n\n**使い方**\n※[]は適切なメンションや文字に置き換えてください。()で囲まれているものは任意です。\n"
                               "`,set mention [ロール or off]` 通知時に任意のロールにメンションをするロールを指定(offで解除)")
        cursor.close()

    @set.command()
    async def upload(self, ctx, channel: typing.Union[discord.TextChannel, str]):
        cursor = self.bot.con.cursor()
        if issetup(ctx.guild, cursor, ctx.channel, self.logger):
            if len(ctx.message.channel_mentions) == 1:
                cursor.execute(
                    f"UPDATE `guild_data` SET `upload_id` ={channel.id}  WHERE guild_id={ctx.guild}")
                await ctx.send("設定しました。")
            elif channel == "off":
                cursor.execute(
                    f"UPDATE `guild_data` SET `upload_id` =NULL  WHERE guild_id={ctx.guild}")
                await ctx.send("設定しました。")
            else:
                await ctx.send("このコマンドに引数が足りないか多すぎます。\n\n**使い方**\n※[]は適切なメンションや文字に置き換えてください。()で囲まれているものは任意です。\n"
                               "`,set upload [チャンネル or off]` ファイル共有時に通知をするチャンネルを設定(offで解除)")
        cursor.close()


def setup(bot):
    bot.add_cog(cmd_setup(bot))
