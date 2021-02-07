from discord import Member
from utils.tools import *
from utils.collections import *
from utils.paginator import Paginator
from datetime import datetime
from dateutil import relativedelta
from lib.database import db


__all__ = [
    'kick_member', 'ban_member', 'unban_member', 'mute_member', 'unmute_member', 'check_warning', 'process_warning',
    'list_warn_member', 'remove_warn_member', 'add_warn_member', 'softban_member'
]


async def kick_member(ctx, user: Member, reason: str):
    moderator = "Automod" if ctx.author != user else ctx.author
    await user.kick(reason=f"Kick | {reason} | {moderator}")
    await send_success(ctx, f'Kicked {user}. Reason: `{reason}`')


async def ban_member(ctx, user: Member, reason: str):
    moderator = "Automod" if ctx.author != user else ctx.author
    await user.ban(reason=f"Ban | {reason} | {moderator}")
    await send_success(ctx, f'Banned {user}. Reason: `{reason}`')


async def unban_member(ctx, user: BannedMember, reason: str):
    await ctx.guild.unban(user=user, reason=f"Unban | {reason} | {ctx.author}")
    await send_success(ctx, f'Unbanned {user}. Reason: `{reason}`')


async def softban_member(ctx, user: Member, reason: str):
    moderator = "Automod" if ctx.author != user else ctx.author
    await user.ban(reason=f"Softban | {reason} | {moderator}")
    await send_success(ctx, f"Softbanned {user}. Reason: `{reason}`")


async def mute_member(bot, ctx, user: Member, duration, reason: str, hardmute: bool = False):
    check = await db.record('SELECT * FROM mutes WHERE GuildID = ? AND UserID = ?', ctx.guild.id, user.id)
    role = await get_mute_role(bot, user.guild.id)
    mute = 'Hardmute' if hardmute else 'Mute'
    moderator = "Automod" if ctx.author != user else ctx.author
    if not role:
        return await send_error(ctx, "Mute role is either deleted or changed, please consider resetting it.")
    if check:
        return await send_error(ctx, f"{user} is already muted for `{check[4]}`!")
    if role in user.roles:
        return await send_error(ctx, f"{user} is already muted!")
    await user.add_roles(role, reason=f"{mute} | {reason} | {moderator}")
    if hardmute:
        await clean_roles(user, f"{mute} | {reason} | {moderator}", [role, ctx.guild.default_role])
    expired = datetime.utcnow() + relativedelta.relativedelta(seconds=duration)
    await db.autoexecute(
        "INSERT INTO mutes(GuildID, UserID, MutedAt, ExpiredAt, Reason) VALUES(?, ?, ?, ?, ?)",
        user.guild.id, user.id, datetime.utcnow().strftime(date_fmt), expired.strftime(date_fmt), reason
    )
    await dm_user(user, f"**{user.guild}:** You're {mute}d for `{cv_sec(duration)}` with reason, `{reason}`.")
    await send_success(ctx, f"{mute}d {user} for `{cv_sec(duration)}`.")


async def unmute_member(bot, ctx, user: Member, reason: str):
    role = await get_mute_role(bot, user.guild.id)
    check = await db.record("SELECT * FROM mutes WHERE GuildID = ? AND UserID = ?", user.guild.id, user.id)
    if not role:
        return await send_error(ctx, "Mute role is either deleted or changed, please consider resetting it.")
    if role not in user.roles or not check:
        return await send_error(ctx, f"How can you unmute {user} while he's not muted?")
    await user.remove_roles(role, reason=f"Unmute | {reason} | {ctx.author}")
    await db.autoexecute("DELETE FROM mutes WHERE GuildID = ? AND UserID = ?", user.guild.id, user.id)
    await dm_user(user, f"**{user.guild}:** You're unmuted from case `{check[4]}`.")
    return await send_success(ctx, f"Unmuted {user} from case `{check[4]}`.")


async def add_warn_member(bot, ctx, user: Member, reason: str):
    user_data = await db.recordall("SELECT * FROM warns WHERE GuildID = ? AND UserID = ?", ctx.guild.id, user.id)
    guild_data = await db.recordall('SELECT * FROM warns WHERE GuildID = ?', ctx.guild.id)
    u_count, g_count = len(user_data) + 1, len(guild_data) + 1
    reason_db = reason if reason.lower() != "no reason provided" or not reason else \
        f"No reason provided | {ctx.prefix}warn reason {g_count} <reason>"
    await db.autoexecute(
        'INSERT INTO warns(GuildID, UserID, ModID, WarnID, Reason, WarnedAt) VALUES(?, ?, ?, ?, ?, ?)',
        ctx.guild.id, user.id, ctx.author.id, g_count, reason_db, datetime.utcnow().strftime(date_fmt)
    )
    await dm_user(
        user, f"**{ctx.guild}:** You've been warned by **{ctx.author}** for `{reason}`, "
              f"this is your {num_cv(u_count)} warning."
    )
    await send_success(ctx, f"Warned {user} for `{reason}`, this is their {num_cv(u_count)} warning.")
    await check_warning(bot, ctx, user)


async def remove_warn_member(bot, ctx, user: Member, case_id: int = None, everything: bool = False):
    if not everything:
        check = await db.record(
            "SELECT * FROM warns WHERE GuildID = ? AND UserID = ? AND WarnID = ?", ctx.guild.id, user.id, case_id
        )
        if not check:
            return await send_error(ctx, f"There's no case with id `#{case_id}`.")
        await db.autoexecute(
            'DELETE FROM warns WHERE GuildID = ? AND UserID = ? AND WarnID = ?', ctx.guild.id, user.id, case_id
        )
        return await send_success(ctx, f"Removed case `#{case_id}` from {user}.")
    if await send_confirmation(bot, ctx, f"Are you sure that you want to clear **{user}** warnings?"):
        check = await db.recordall('SELECT * FROM warns WHERE GuildID = ? AND UserID = ?', ctx.guild.id, user.id)
        if not check:
            return await send_error(ctx, f"{user} doesn't have any warnings (cases).")
        await db.autoexecute("DELETE FROM warns WHERE GuildID = ? AND UserID = ?", ctx.guild.id, user.id)
        return await send_success(ctx, f"Deleted `{len(check)}` cases from {user}.")


async def list_warn_member(bot, ctx, user: Member):
    warnings = await db.recordall('SELECT * FROM warns WHERE GuildID = ? AND UserID = ?', ctx.guild.id, user.id)
    if not warnings:
        return await send_error(ctx, f"{user} doesn't have any warnings (cases).")
    warnings.sort(key=lambda dt: datetime.strptime(dt[5], date_fmt))
    fmt = [
        f"\n**{num + 1}. Case #{data[3]}**\nReason: `{data[4]}`\nModerator: "
        f"{nickname(bot, data[2], True) if user.id != data[2] else 'Automod'}\nTime: `{data[5]}`"
        for num, data in enumerate(warnings)
    ]
    await Paginator(ctx, fmt, "warnings", f"{user} warnings", per_page=5, clear_reaction_after=True).start()


async def check_warning(bot, ctx, user: Member):
    data = await db.recordall("SELECT * FROM warns WHERE GuildID = ? AND UserID = ?", ctx.guild.id, user.id)
    punishment = await db.recordall("SELECT * FROM warn_punishment WHERE GuildID = ?", ctx.guild.id)
    for punish in punishment:
        if punish[1] < len(data):
            await process_warning(bot, ctx, user, punish[2], len(data))


async def process_warning(bot, ctx, user: Member, punishment: str, warnings: int):
    default_reason = f"Reached {num_cv(warnings)} warnings"
    if punishment == punishments[0]:
        await ban_member(ctx, user, default_reason)
    if punishment == punishments[1]:
        await kick_member(ctx, user, default_reason)
    if punishment == punishments[2]:
        await mute_member(bot, ctx, user, 1800, default_reason)
    if punishment == punishments[3]:
        await mute_member(bot, ctx, user, 1800, default_reason, hardmute=True)
    if punishment == punishments[4]:
        await softban_member(ctx, user, default_reason)
