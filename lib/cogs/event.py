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
"""

from discord.ext.commands import Cog
from lib.database import db
from utils.collections import *
from utils.tools import *
from discord import Embed
from datetime import datetime


class Event(Cog, name='Event'):

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        data = await db.record("SELECT * FROM logging WHERE GuildID = ?", member.guild.id)
        if not data or not data[1]:
            return
        embed = Embed(colour=colors['green'], timestamp=datetime.utcnow())
        embed.set_footer(text=f"ID: {member.id}")
        text = None
        if not before.channel and after.channel:
            text = f"{member} joined {after.channel}"
        if before.channel and not after.channel:
            text = f"{member} left {before.channel}"
        if before.channel and after.channel:
            text = f"{member} moved from {before.channel} to {after.channel}"
        if text:
            embed.set_author(name=text, icon_url=member.avatar_url)
            await send_webhook(data[1], embed=embed)


def setup(bot):
    bot.add_cog(Event(bot))
