from discord.ext.commands import Cog
from discord.ext.tasks import loop
from lib.database import db
from datetime import datetime
from utils.collections import date_fmt
from utils.tools import *


import logging
import discord


log = logging.getLogger(__name__)


class Process(Cog, name='Process'):

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        self.auto_unmute.start()
        print('Auto Unmute Process started')

    @loop(seconds=2)
    async def auto_unmute(self):
        data = await db.recordall("SELECT * FROM mutes")
        if not data:
            return
        for item in data:
            expired = datetime.strptime(item[3], date_fmt)
            if datetime.utcnow() >= expired:
                guild = self.bot.get_guild(item[0])
                if not guild:
                    return await db.autoexecute("DELETE FROM mutes WHERE GuildID = ?", item[0])
                _role = await db.record("SELECT MuteRole FROM guilds WHERE GuildID = ?", item[0])
                if not _role:
                    return
                role = guild.get_role(_role[0])
                if not role:
                    return
                member = guild.get_member(item[1])
                if member:
                    try:
                        await member.remove_roles(role, reason=f"Unmute from case [{item[4]}].")
                    except discord.Forbidden:
                        await dm_user(
                            member, f"**{guild}:** I'm unable to unmute you, please contact your server admin. ERR: 403"
                        )
                    else:
                        await dm_user(member, f"**{guild}:** You're now unmuted from case `{item[4]}`.")
                await db.autoexecute('DELETE FROM mutes WHERE GuildID = ? AND UserID = ?', item[0], item[1])


def setup(bot):
    bot.add_cog(Process(bot))
