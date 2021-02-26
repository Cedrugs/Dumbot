"""
The MIT License (MIT)

Copyright (c) 2020-present Cedrugs

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

______________________________________________________________________________

Cogs for Logging

"""


from discord.ext.commands import Cog, group, guild_only, bot_has_permissions, BucketType
from discord import TextChannel, Embed
from lib.database import db
from utils.checks import *
from utils.tools import *
from typing import Optional
from utils.collections import *
from datetime import datetime


import logging


log = logging.getLogger(__name__)


class Log(Cog, name='Logging'):

    def __init__(self, bot):
        self.bot = bot

    @group(
        name='log',
        description='List of enabled log in this server',
        invoke_without_command=True,
        aliases=['logging']
    )
    @guild_only()
    async def log_cmd(self, ctx):
        data = await db.record('SELECT * FROM logging WHERE GuildID = ?', ctx.guild.id)
        if not data:
            return await send_success(ctx, "This server doesn't have activated logger")
        enabled = '\n'.join(f'`{item}` ({CONV_EVENT[item]})' for item in data[3].split(', '))
        embed = Embed(
            color=colors['blue'],
            timestamp=datetime.utcnow(),
            description=f"{enabled}",
            title="Enabled Logging"
        )
        await ctx.send(embed=embed)

    @log_cmd.command(
        name='channel',
        description='Set the logging channel'
    )
    @guild_only()
    @admin_or_perms(manage_guild=True)
    @bot_has_permissions(manage_guild=True)
    @cooldown(1, 3, 1, 1, BucketType.user)
    async def log_channel_cmd(self, ctx, channel: Optional[TextChannel]):
        data = await db.record('SELECT * FROM logging')
        channel = channel or ctx.channel
        webhook = await channel.create_webhook(
            name="Dumbo Webhook",
            reason=f"Create Channel | Logging Channel | {ctx.author}",
            avatar=await self.bot.user.avatar_url.read()
        )
        if not data:
            await db.autoexecute(
                "INSERT INTO logging(GuildID, WebhookURL, ChannelID) VALUES(?, ?, ?)",
                ctx.guild.id, webhook.url, channel.id
            )
        else:
            await db.autoexecute(
                "UPDATE logging SET WebhookURL = ?, ChannelID = ? WHERE GuildID = ?",
                webhook.url, channel.id, ctx.guild.id
            )
        await send_success(ctx, f"Logging channel has been set to {channel.mention}")


def setup(bot):
    bot.add_cog(Log(bot))
