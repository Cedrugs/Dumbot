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

Logics for cogs/log.py

"""

from lib.database import db
from datetime import datetime
from discord.ext.commands import Context
from discord import Embed
from utils.collections import *
from utils.tools import *
from typing import Union


__all__ = ('process_voice',)

class EventLog:

    def __init__(self, event_type: str, **kwargs):
        self.log_type = EVENT_LOG
        self.type = event_type
        self.member = kwargs.get('member', None)
        self.before = kwargs.get('before', None)
        self.after = kwargs.get('after', None)
        self.message = kwargs.get('message', None)


    async def setup(self, ctx: Context):
        if not self.type in set(EVENT_LOG):
            raise TypeError(f"Expected {', '.join(set(self.log_type))}, given {self.type}")

        data = await db.record('SELECT * FROM logging WHERE GuildID = ?', ctx.guild.id)

        if data and data[1] and data[2] and data[3]:
            listed_type = [] or data[3].split(', ')

            if self.type in listed_type:


    async def determine_type(self):
        if self.type == self.log_type['VOICE_EVENT']:
            if not self.before.channel and self.after.channel:
                return 'JOIN_VC'



    async def embed(self, ctx):
        embed = Embed(color=)


    async def send(self, embed: Embed, url: str):




async def process_voice(member, before, after):
    data = await db.record("SELECT * FROM logging WHERE GuildID = ?", member.guild.id)
    if data and data[1] and data[3]:
        enabled_logger = [] or data[3].split(', ')
        embed = Embed(colour=colors['green'], timestamp=datetime.utcnow())
        embed.set_footer(text=f"ID: {member.id}")
        text = None
        if not before.channel and after.channel and 'JOIN_VC' in enabled_logger:
            text = f"{member} joined {after.channel}"
        if before.channel and not after.channel and 'LEFT_VC' in enabled_logger:
            text = f"{member} left {before.channel}"
        if before.channel and after.channel and 'MOVE_VC' in enabled_logger:
            text = f"{member} moved from {before.channel} to {after.channel}"
        if text:
            embed.set_author(name=text, icon_url=member.avatar_url)
            await send_webhook(data[1], embed=embed)


async def deleted_message(message):
    data = await db.record('SELECT * FROM logging WHERE GuildID = ?', message.guild.id)
    if data and data[1] and data[3]:
        enabled_logger = [] or data[3].split(', ')
        embed = Embed(color=colors['green'], timestamp=datetime.utcnow())
        embed.set_footer(text=f"Message ID: {message.id}")
        text = None
