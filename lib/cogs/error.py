from discord.ext.commands import Cog
from discord.ext import commands
from utils.collections import *
from utils.error import *

import discord
import logging


log = logging.getLogger(__name__)


class Error(Cog, name='Error'):

    def __init__(self, bot):

        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        try:
            err_msg = None
            if isinstance(error, commands.MissingRequiredArgument):
                missing_args = str(error.param).replace('_', '').split(':')[0]
                err_msg = f"You must fill `{missing_args}` parameter"
            elif isinstance(error, commands.MissingPermissions):
                err_msg = f"You are missing {', '.join(f'`{perms}`' for perms in error.missing_perms)} permission(s)"
            elif isinstance(error, commands.MemberNotFound):
                err_msg = f"There's no member named`{error.argument}`"
            elif isinstance(error, commands.RoleNotFound):
                err_msg = f"There's no role named `{error.argument}`"
            elif isinstance(error, commands.ChannelNotFound):
                err_msg = f"There's no channel named `{error.argument}`"
            elif isinstance(error, commands.CommandOnCooldown):
                err_msg = f"You're on cooldown, retry after {error.retry_after:,.2f} secs"
            elif isinstance(error, commands.DisabledCommand):
                err_msg = f"This command either is disabled, or under development."
            elif isinstance(error, commands.BotMissingPermissions):
                err_msg = f"I'm missing `{', '.join(f'`{perms}`` permission(s)' for perms in error.missing_perms)}`"
            elif isinstance(error, discord.Forbidden):
                err_msg = f"I don't have enough permissions to do this"
            elif isinstance(error, commands.NoPrivateMessage):
                err_msg = "This command can't be used in Private Channel (Direct Message)"
            elif isinstance(error, commands.CheckFailure):
                pass
            elif isinstance(error, commands.BadArgument):
                if str(error).startswith('Converting to "int"'):
                    param = str(error).split('"')
                    err_msg = f'Parameter `{param[3]}` must be a number'
            elif isinstance(error.original, NotBanned):
                err_msg = f"{error.original.uname} is not banned"
            elif isinstance(error, commands.CommandInvokeError):
                if isinstance(error.original, NotEligible):
                    err_msg = f"You can't do that to {error.original.user} due to role hierarchy"
                elif isinstance(error.original, InvalidChoice):
                    valid = '/'.join(f"`{data}`" for data in error.original.correct)
                    err_msg = f"That's a invalid choice, should be {valid}"
                else:
                    log.error("Error under [on_command_error/CommandInvokeError]", error.original)
            else:
                log.error("Error under Error cog", error)
            if err_msg:
                embed = discord.Embed(color=0xee6565, description=f"{efalse} **{err_msg}.**")
                await ctx.send(embed=embed)
        except Exception as exc:
            log.error("Error under [on_command_error]:", exc)


def setup(bot):
    bot.add_cog(Error(bot))
