from discord.ext.commands import Context, Bot
from discord import Message
from datetime import datetime
from utils.tools import *
from utils.collections import *
from utils.checks import *


import asyncio
import discord
import re
import logging


__all__ = (
    'WaitFor',
)
logger = logging.getLogger(__name__)


class WaitFor:

    def __init__(
            self, bot: Bot, ctx: Context, source: list or tuple, colour: int, footer: str, date=datetime.utcnow(),
            timeout: int = 120, name: str = "Task"
    ):
        self.bot = bot
        self.ctx = ctx
        self.data = source
        self.colour = colour
        self.footer = footer
        self.date = date
        self.timeout = timeout
        self.task = name

    async def start(self):
        answer = []
        embed = discord.Embed(colour=self.colour, timestamp=self.date)
        embed.set_footer(text=self.footer)

        for item in self.data:

            def check(m):
                return m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id

            embed.title = item[0]
            embed.description = item[1].format(ans=answer)

            if item[2]:
                embed.set_image(url=item[2])

            await self.ctx.send(embed=embed)

            try:
                msg = await self.bot.wait_for('message', timeout=self.timeout, check=check)

                if msg:
                    if msg.content.lower() in ['abort', 'cancel']:
                        await self.ctx.send(f'{etrue} {self.task} has been cancelled!')
                        return None

                    if isinstance(item[3], list):
                        if item[3][0] == 'fetch':
                            type_check = await self.check_type(
                                self.ctx, item[3][0], msg, item[4],
                                meessage_channel=answer[item[3][1]]
                            )
                        else:
                            type_check = await self.check_type(
                                self.ctx, item[3][0], msg, item[4],
                                choice=item[3][1]
                            )
                    else:
                        type_check = await self.check_type(self.ctx, item[3], msg, item[4])

                    if not type_check[0]:
                        await self.ctx.send(str(type_check[1]))
                        return None

                    answer.append(type_check[1])

                else:
                    await self.ctx.send(f"{efalse} Something went wrong while trying to get answer, code: #w_for/196")
                    return None

            except asyncio.TimeoutError:
                await self.ctx.send(f'{efalse} {self.task} has been cancelled due to timeout!')
                return None

        await self.ctx.send(f'{etrue} {self.task} has been completed!')
        return tuple(answer)

    async def check_type(
            self, ctx: Context, message_type: str, message: Message, optional: bool, choice: list = None,
            meessage_channel: discord.TextChannel = None
    ):

        if message.content.lower() == "none" and optional:
            return True, None

        result = None
        err = "Invalid options!"
        types = ['channel', 'role', 'emoji', 'multi', 'fetch', 'int', 'str']
        if message_type == types[0]:
            err = "Invalid channel name or ID!"
            if message.raw_channel_mentions:
                result = ctx.guild.get_channel(message.raw_channel_mentions[0])
            elif message.content.isdigit():
                result = ctx.guild.get_channel(int(message.content))
            elif message.content.isascii():
                result = finditer(str(message.content), ctx.guild.text_channels)
                print(result.id)
        if message_type == types[1]:
            err = "Invalid role name or ID!"
            if message.raw_role_mentions:
                result = ctx.guild.get_role(int(message.raw_role_mentions[0]))
            elif message.content.isdigit():
                result = ctx.guild.get_role(int(message.content))
            elif message.content.isascii():
                result = finditer(message.content, ctx.guild.roles)
            if result:
                if not eligible(ctx.author, result):
                    result = None
                    err = "You can't use a role that higher than your's"
        if message_type == types[2]:
            err = "Invalid emoji, must be a unicode or a guild emoji!"
            if '<:' in message.content:
                converted = re.sub(':.*?:', '', message.content).strip('<>')
                result = self.bot.get_emoji(int(converted))
            if '<:' not in message.content:
                result = is_unicode(message.content)
        if message_type == types[3]:
            if not choice or not isinstance(choice, list):
                raise TypeError("Option choice must atleast contain a list with 1 items.")
            err = "Invalid choices!"
            if (choices := message.content.lower()) in choice:
                result = choices
        if message_type == types[4]:
            err = "Message ID must be a number!"
            if message.content.isdigit():
                err = "Invalid message ID!"
                result = await fetch_message(ctx, meessage_channel.id, int(message.content))
        if message_type == types[5]:
            err = "You can only input a number!"
            if message.content.isdigit():
                result = int(message.content)
        if result or message_type == types[6]:
            if message_type == types[6]:
                result = message.content
            return True, result
        return False, f"{efalse} {err}"
