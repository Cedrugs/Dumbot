from discord.ext.commands import Cog, command, guild_only, bot_has_permissions, Greedy, MissingRequiredArgument, \
    BucketType, group, MissingPermissions
from utils.checks import *
from utils.tools import *
from utils.collections import *
from utils.error import *
from utils.paginator import *
from discord import Member, TextChannel, Role, Permissions, PermissionOverwrite, Embed
from typing import Optional
from lib.logics import *
from lib.database import db
from typing import Union
from datetime import datetime


import logging


log = logging.getLogger(__name__)


class Mods(Cog, name='Moderation'):

    def __init__(self, bot):

        self.bot = bot

    @command(
        name='ban',
        description="Ban a user"
    )
    @admin_or_perms(ban_members=True)
    @bot_has_permissions(ban_members=True)
    @guild_only()
    @cooldown(1, 3, 1, 2, BucketType.user)
    async def ban_cmd(self, ctx, users: Greedy[Member], *, reason: Optional[str] = no_reason):
        if not users:
            raise MissingRequiredArgument(generate_param("users"))
        for user in users:
            eligible(ctx.author, user)
            await ban_member(ctx, user, reason)

    @command(
        name='softban',
        aliases=['sban'],
        description='Softban a user (ban and automatically unban them)'
    )
    @guild_only()
    @admin_or_perms(ban_members=True)
    @bot_has_permissions(ban_members=True)
    @guild_only()
    @cooldown(1, 3, 1, 2, BucketType.user)
    async def softban_cmd(self, ctx, users: Greedy[Member], *, reason: Optional[str] = no_reason):
        if not users:
            raise MissingRequiredArgument(generate_param("users"))
        for user in users:
            eligible(ctx.author, user)
            await softban_member(ctx, user, reason)

    @command(
        name='kick',
        description="Kick a user"
    )
    @guild_only()
    @admin_or_perms(kick_members=True)
    @bot_has_permissions(kick_members=True)
    @cooldown(1, 3, 1, 2, BucketType.user)
    async def kick_cmd(self, ctx, users: Greedy[Member], *, reason: Optional[str] = no_reason):
        if not users:
            raise MissingRequiredArgument(generate_param("users"))
        for user in users:
            eligible(ctx.author, user)
            await kick_member(ctx, user, reason)

    @command(
        name='unban',
        description="Unban a user"
    )
    @guild_only()
    @admin_or_perms(ban_members=True)
    @bot_has_permissions(ban_members=True)
    @cooldown(1, 3, 1, 2, BucketType.user)
    async def unban_cmd(self, ctx, user: BannedMember, *, reason: Optional[str] = no_reason):
        await unban_member(ctx, user, reason)

    @command(
        name='purge',
        description="Delete a messages",
        aliases=['clear', 'remove']
    )
    @guild_only()
    @admin_or_perms(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    @cooldown(1, 3, 1, 2, BucketType.user)
    async def purge_cmd(self, ctx, amount: Optional[int] = 50):
        if not 0 < amount <= 500:
            return await send_error(
                ctx, "You can only purge message from 1-500 at once, for advanced clear, use `.nuke`"
            )
        deleted = await ctx.channel.purge(limit=amount + 1)
        await send_success(ctx, f"Purged {len(deleted) - 1} messages.", delete_after=10)

    @command(
        name='nuke',
        description="Nuke a channel (re-create it)",
        aliases=['explode', 'wipe']
    )
    @guild_only()
    @admin_or_perms(manage_channels=True, manage_messages=True)
    @bot_has_permissions(manage_channels=True, manage_messages=True)
    @cooldown(1, 20, 1, 15, BucketType.user)
    async def nuke_cmd(self, ctx, channel: Optional[TextChannel], reason: Optional[str] = no_reason):
        await del_msg(ctx)
        channel = channel or ctx.channel
        if await send_confirmation(self.bot, ctx, f"Are you sure that you want to nuke {channel.mention}?"):
            channelpos = channel.position
            channel_slowmode = channel.slowmode_delay
            new_channel = await ctx.guild.create_text_channel(
                name=channel.name,
                category=channel.category,
                position=channelpos,
                overwrites=channel.overwrites,
                slowmode_delay=channel_slowmode,
                reason=f"Nuke Channel [Instant Clear] | {reason} | {ctx.author}"
            )
            await channel.delete()
            await send_success(new_channel, f"{new_channel.mention} has been nuked.", delete_after=10)

    @command(
        name='mute',
        description="Mute a user",
        usage="<users> [duration (h|m|d|s)] [reason]"
    )
    @guild_only()
    @admin_or_perms(manage_roles=True)
    @bot_has_permissions(manage_roles=True)
    @cooldown(1, 3, 1, 2, BucketType.user)
    async def mute_cmd(
            self, ctx, users: Greedy[Member], duration: Optional[Duration] = 1800, *,
            reason: Optional[str] = no_reason
    ):
        if not users:
            raise MissingRequiredArgument(generate_param("users"))
        for user in users:
            eligible(ctx.author, user)
            await mute_member(self.bot, ctx, user, duration, reason)

    @command(
        name='muterole',
        description='Set a mute role for your server or create it.'
    )
    @guild_only()
    @admin_or_perms(manage_guild=True, manage_roles=True)
    @bot_has_permissions(manage_guild=True, manage_roles=True)
    @cooldown(1, 4, 1, 2, BucketType.user)
    async def muterole_cmd(self, ctx, role: Union[Role, str]):
        if isinstance(role, Role):
            await db.autoexecute("UPDATE guilds SET MuteRole = ? WHERE GuildID = ?", role.id, ctx.guild.id)
            return await send_success(ctx, f"Mute role has been updated to {role.mention}.")
        if isinstance(role, str) and role.lower() == 'create':
            message = await ctx.send("Creating the mute role.")
            mute_role = await ctx.guild.create_role(
                name='Muted',
                permissions=Permissions(
                    read_message_history=True,
                    view_channel=True
                ),
                hoist=True,
                reason=f"Create role | Mute Role | {ctx.author}"
            )
            await message.edit(content="Applying permissions to all channel, this may take a while to complete.")
            perms = PermissionOverwrite(send_messages=False)
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(mute_role, overwrite=perms)
            await message.edit(content="Inserting to database.")
            await db.autoexecute('UPDATE guilds SET MuteRole = ? WHERE GuildID = ?', mute_role.id, ctx.guild.id)
            await message.delete()
            await send_success(ctx, f"Created mute role. ({mute_role.mention})")

    @command(
        name='hardmute',
        aliases=['hmute'],
        description="Hardmute a user (Remove all their roles and mute them)"
    )
    @guild_only()
    @admin_or_perms(manage_roles=True)
    @bot_has_permissions(manage_roles=True)
    @cooldown(1, 3, 1, 2, BucketType.user)
    async def hardmute_cmd(
            self, ctx, users: Greedy[Member], duration: Optional[Duration] = 1800, *,
            reason: Optional[str] = no_reason
    ):
        if not users:
            raise MissingRequiredArgument(generate_param("users"))
        for user in users:
            eligible(ctx.author, user)
            await mute_member(self.bot, ctx, user, duration, reason, hardmute=True)

    @command(
        name='unmute',
        aliases=['umute'],
        description="Unmute a user"
    )
    @guild_only()
    @admin_or_perms(manage_roles=True)
    @bot_has_permissions(manage_roles=True)
    @cooldown(1, 3, 1, 2, BucketType.user)
    async def unmute_cmd(self, ctx, users: Greedy[Member], *, reason: Optional[str] = no_reason):
        if not users:
            raise MissingRequiredArgument(generate_param("users"))
        for user in users:
            eligible(ctx.author, users)
            await unmute_member(self.bot, ctx, user, reason)

    @group(
        name='warn',
        aliases=['strike'],
        description='Warn a user',
        invoke_without_command=True
    )
    @guild_only()
    @admin_or_perms(manage_roles=True, ban_members=True, kick_members=True)
    @bot_has_permissions(manage_roles=True)
    @cooldown(1, 3, 1, 2, BucketType.user)
    async def warn_cmd(self, ctx, users: Greedy[Member], *, reason: Optional[str] = no_reason):
        if not users:
            raise MissingRequiredArgument(generate_param("users"))
        for user in users:
            await add_warn_member(self.bot, ctx, user, reason)

    @command(
        name='removewarn',
        aliases=['deletewarn'],
        description='Remove a warning from user'
    )
    @guild_only()
    @admin_or_perms(manage_roles=True)
    @bot_has_permissions(manage_roles=True)
    @cooldown(1, 3, 1, 2, BucketType.user)
    async def warn_remove_cmd(self, ctx, user: Member, case_ids: Greedy[int], *, reason: Optional[str] = no_reason):
        if not user:
            raise MissingRequiredArgument(generate_param("user"))
        for case in case_ids:
            await remove_warn_member(ctx, user, case)

    @command(
        name='clearwarning',
        aliases=['clearwarn'],
        description='Remove all warning from user',
    )
    @guild_only()
    @admin_or_perms(manage_roles=True)
    @bot_has_permissions(manage_roles=True)
    @cooldown(1, 4, 1, 2, BucketType.user)
    async def clear_warn_cmd(self, ctx, user: Member, *, reason: Optional[str] = no_reason):
        await remove_warn_member(self.bot, ctx, user, everything=True)

    @command(
        name='warnings',
        aliases=['warns'],
        description='List of user warning'
    )
    @guild_only()
    @cooldown(1, 2, 1, 1, BucketType.user)
    async def warnings_cmd(self, ctx, user: Optional[Member]):
        await list_warn_member(self.bot, ctx, user or ctx.author)

    @warn_cmd.group(
        name='punishment',
        description='List of punishment caused by warning',
        invoke_without_command=True
    )
    @guild_only()
    @admin_or_perms(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    @cooldown(1, 2, 1, 1, BucketType.user)
    async def warn_punishment_cmd(self, ctx):
        data = await db.recordall('SELECT * FROM warn_punishment WHERE GuildID = ?', ctx.guild.id)
        if not data:
            return await send_error(ctx, f"This server doesn't have any punishment.")
        data.sort(key=lambda num: num[1])
        fmt = [f"• **{data[1]}** warnings: `{data[2]}`" for data in data]
        await Paginator(ctx, fmt, 'punishment', f'{ctx.guild} Punishment', 10, clear_reaction_after=True).start()

    @warn_punishment_cmd.command(
        name='add',
        description='Add a new punishment for warning',
    )
    @guild_only()
    @admin_or_perms(ban_members=True, kick_members=True, manage_roles=True)
    @bot_has_permissions(ban_members=True, kick_members=True, manage_roles=True)
    @cooldown(1, 5, 1, 3, BucketType.user)
    async def warn_punishment_add_cmd(self, ctx, after: int, punishment: str):
        if punishment.lower() not in punishments:
            raise InvalidChoice(punishments)
        check = await db.record('SELECT * FROM warn_punishment WHERE GuildID = ? AND After = ?', ctx.guild.id, after)
        if not check:
            await db.autoexecute(
                'INSERT INTO warn_punishment(GuildID, After, WType) VALUES(?, ?, ?)', ctx.guild.id, after, punishment
            )
            return await send_success(ctx, f"Punishment for `{after}` warnings has been set to `{punishment}`.")
        if await send_confirmation(
            self.bot, ctx,
            f"Punishment for `{after}` is already filled with `{check[2]}`, would you like to "
            f"override it with `{punishment}`?", 10
        ):
            await db.autoexecute(
                'UPDATE warn_punishment SET WType = ? WHERE GuildID = ? AND After = ?',
                punishment, ctx.guild.id, after
            )
            return await send_success(ctx, f'Updated punishment for `{after}` warnings to `{punishment}`')

    @warn_punishment_cmd.command(
        name='remove',
        aliases=['del', 'delete'],
        description="Remove an existing punishment for warning"
    )
    @guild_only()
    @admin_or_perms(ban_members=True, kick_members=True, manage_roles=True)
    @bot_has_permissions(ban_members=True, kick_members=True, manage_roles=True)
    @cooldown(1, 5, 1, 3, BucketType.user)
    async def warn_punishment_del_cmd(self, ctx, after: Union[str, int]):
        if isinstance(after, str) and after.lower() == 'clear':
            if await send_confirmation(
                    self.bot, ctx, "Are you sure that you want to clear all warning punishment?", 10
            ):
                await db.autoexecute("DELETE FROM warn_punishment WHERE GuildID = ?", ctx.guild.id)
                return await send_success(ctx, f"Removed all warning punishment.")
        if isinstance(after, int):
            check = await db.record(
                'SELECT * FROM warn_punishment WHERE GuildID = ? AND After = ?', ctx.guild.id, after
            )
            if not check:
                return await send_error(ctx, f"There's no punsihment for `{after}` warnings.")
            await db.autoexecute("DELETE FROM warn_punishment WHERE GuildID AND After = ?", ctx.guild.id, after)
            return await send_success(ctx, f"Removed warning punishment for `{after}` warnings.")
        raise InvalidChoice(['"clear"', 'number'])

    @command(
        name='announce',
        description='Announce something to specified channel'
    )
    @guild_only()
    @admin_or_perms(manage_messages=True)
    @bot_has_permissions(manage_messages=True, send_messages=True)
    @cooldown(1, 3, 1, 2, BucketType.user)
    async def announce_cmd(self, ctx, channel: Optional[TextChannel], *, text: str):
        channel = channel or ctx.channel
        em = Embed(title="📣 New Announcement!", description=text, timestamp=datetime.utcnow(), color=colors['yellow'])
        em.set_footer(text=ctx.author)
        await channel.send(embed=em)
        if await send_confirmation(self.bot, ctx, "Would you like to ping `@everyone`?", timeout=10):
            await channel.send("||@everyone||")
        return await send_success(ctx, f"Announcement sent to {channel.mention}", delete_after=10)

    @command(
        name='lock',
        description='Lock a channel',
        aliases=['lockdown']
    )
    @guild_only()
    @admin_or_perms(manage_channels=True, manage_roles=True)
    @bot_has_permissions(manage_channels=True, manage_roles=True, send_messages=True)
    @cooldown(1, 2, 1, 1, BucketType.user)
    async def lockdown_cmd(self, ctx, channel: Optional[TextChannel], role: Optional[Role]):
        channel: TextChannel = channel or ctx.channel
        target = role or ctx.guild.default_role
        overwrite = channel.overwrites
        if target not in channel.overwrites:
            overwrite.update({target: PermissionOverwrite(send_messages=False)})
            await channel.edit(overwrites=overwrite)
            return await send_success(ctx, f"Locked down {channel.mention}.")
        elif overwrite[target].send_messages:
            overwrite[target].send_messages = False
            await channel.set_permissions(target, overwrite=overwrite[target])
            return await send_success(ctx, f"Locked down {channel.mention}")
        return await send_error(ctx, f"{channel.mention} is already locked down.")

    @command(
        name='unlock',
        description='Unlock a channel from lockdown',
        aliases=['ulock']
    )
    @guild_only()
    @admin_or_perms(manage_channels=True, manage_roles=True)
    @bot_has_permissions(manage_channels=True, manage_roles=True, send_messages=True)
    @cooldown(1, 2, 1, 1, BucketType.user)
    async def unlock_cmd(self, ctx, channel: Optional[TextChannel], role: Optional[Role]):
        channel: TextChannel = channel or ctx.channel
        target = role or ctx.guild.default_role
        overwrite = channel.overwrites
        if target not in overwrite:
            overwrite.update({target: PermissionOverwrite(send_messages=True)})
            await channel.edit(overwrites=overwrite)
            return await send_success(ctx, f"Unlocked {channel.mention}.")
        elif not overwrite[target].send_messages or overwrite[target].send_messages is None:
            overwrite[target].send_messages = True
            await channel.set_permissions(target, overwrite=overwrite[target])
            return await send_success(ctx, f"Unlocked {channel.mention}.")
        return await send_error(ctx, f"{channel.mention} is not locked down.")

    @command(
        name='changenick',
        description='Change someone nickname',
        aliases=['cn', 'cnick']
    )
    @guild_only()
    @bot_has_permissions(manage_nicknames=True)
    @cooldown(1, 2, 1, 1, BucketType.user)
    async def changenick_cmd(self, ctx, user: Optional[Member], *, nick: str):
        user = user or ctx.author
        if user == ctx.author:
            if not user.guild_permissions.change_nickname:
                raise MissingPermissions(['change_nickname'])
            await user.edit(nick=nick, reason=f"Change Nick | Request by | {ctx.author}")
            return await send_success(ctx, f"Changed {user} nickname to {user.display_name}")
        if not ctx.author.guild_permissions.manage_nicknames:
            raise MissingPermissions(['manage_nicknames'])
        eligible(ctx.author, user)
        await user.edit(nick=nick, reason=f"Change Nick | Request by | {ctx.author}")
        return await send_success(ctx, f"Changed {user} nickname to {user.display_name}")


def setup(bot):
    bot.add_cog(Mods(bot))
