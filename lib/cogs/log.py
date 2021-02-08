from discord.ext.commands import Cog, group, guild_only, bot_has_permissions, BucketType
from discord import Embed, TextChannel, File
from lib.database import db
from utils.collections import *
from utils.checks import *
from utils.tools import *
from datetime import datetime
from typing import Optional


import logging


log = logging.getLogger(__name__)


class Log(Cog, name='Logging'):

    def __init__(self, bot):
        self.bot = bot

    @group(
        name='log',
        description='List of enabled log in this server',
        invoke_without_command=True
    )
    @guild_only()
    async def log_cmd(self, ctx):
        await ctx.send("Enabled logging:")

    @log_cmd.command(
        name='channel',
        description='Set the logging channel'
    )
    @guild_only()
    @admin_or_perms(manage_guild=True)
    @bot_has_permissions(manage_guild=True)
    @cooldown(1, 3, 1, 1, BucketType.user)
    async def log_channel_cmd(self, ctx, channel: Optional[TextChannel]):
        channel = channel or ctx.channel
        webhook = await channel.create_webhook(
            name="Dumbo Webhook",
            reason=f"Create Channel | Logging Channel | {ctx.author}",
            avatar=await self.bot.user.avatar_url.read()
        )
        await db.autoexecute(
            "INSERT INTO logging(GuildID, WebhookURL, ChannelID) VALUES(?, ?, ?)",
            ctx.guild.id, webhook.url, channel.id
        )
        await send_success(ctx, f"Logging channel has been set to {channel.mention}")


def setup(bot):
    bot.add_cog(Log(bot))
