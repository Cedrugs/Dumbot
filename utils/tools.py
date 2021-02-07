from discord.ext import commands
from inspect import Parameter
from discord.utils import find
from lib.database import db
from utils.checks import CustomCooldown
from utils.collections import *
from utils.error import *
from typing import Optional, List, Union
from emoji import UNICODE_EMOJI


import discord
import re
import asyncio


__all__ = (
    'get_db_prefix', 'linebreaks', 'generate_param', 'BannedMember', 'send_error', 'send_success', 'get_mute_role',
    'Duration', 'cv_sec', 'dm_user', 'num_cv', 'send_confirmation', 'nickname', 'clean_roles', 'del_msg', 'is_unicode',
    'finditer', 'fetch_message'
)


def finditer(name, iterable):
    """
    Find the most similar things on the iterable
    :param name: The pattern name
    :param iterable: Iterable either list or tuple.
    :return: The most similar things
    """
    items = []
    most_sim = None
    for item in iterable:
        result = re.search(name.lower(), str(item).lower())
        if result:
            items.append(item)
    if len(items) == 1:
        return items[0]
    if len(items) > 1:
        most_sim = items[0]
        len_most_sim = len(str(items[0]))
        for thing in items:
            if len(str(thing)) < len_most_sim:
                most_sim = thing
    if not most_sim and not items:
        return None
    return most_sim


def linebreaks(amount: int = 55, line: str = '-'):
    print(line * amount)


def generate_param(name: str):
    return Parameter(name=name, kind=Parameter.POSITIONAL_ONLY)


def error_converter(err_type: str): pass


def bool_converter(args):
    if isinstance(args, int):
        if args == 0:
            return False
        return True
    if isinstance(args, str):
        if args.lower() in YES_ARGS:
            return True
        return False
    raise TypeError("Invalid type of bool")


def cv_sec(time: int):
    day = time // (24 * 3600)
    time = time % (24 * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    time %= 60
    seconds = time
    day_ = f'{day} day{"s" if day > 1 else ""} '
    hour_ = f'{hour} hour{"s" if hour > 1 else ""} '
    minute_ = f'{minutes} minute{"s" if minutes > 1 else ""} '
    second_ = f'{seconds} second{"s" if seconds > 1 else ""} '
    return f"{day_ if day > 0 else ''}{hour_ if hour > 0 else ''}" \
           f"{minute_ if minutes > 0 else ''}{second_ if seconds > 0 else ''}".lstrip().rstrip()


def is_unicode(emoji: str):
    return emoji in UNICODE_EMOJI


def get_cmd_info(cmd: commands.Command):
    details = {}
    alias_raw = cmd.aliases
    alias = ''
    syntax = [str(cmd)]
    if alias:
        for aliases in alias_raw:
            if len(str(aliases)) > len(alias):
                alias = aliases
        if alias is not None and alias != '':
            syntax.append(alias)

    cmd_and_alias = "|".join(syntax)
    params = []

    for key, value in cmd.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

    param_raw = " ".join(params)

    for check in cmd.checks:
        if isinstance(check, CustomCooldown):
            details.update({"cooldown": check.cd, "premium_cooldown": check.pcd})
        else:
            try:
                perms = [c for c in check.__closure__[0].cell_contents.keys()]
                perm_1 = check.__qualname__.split(".", 1)[0]
            except TypeError:
                perms = None
                perm_1 = check
            except AttributeError:
                perms = None
                perm_1 = check
            if perms and perm_1:
                details.update({perm_1: perms})
    details.update({
        "desc": cmd.description if cmd.description else "No Description",
        "syntax": f"{cmd_and_alias} {param_raw}",
        "brief": cmd.brief if cmd.brief else None
    })
    print(details)


def num_cv(number: int):
    if number > 3:
        return f"{number}th"
    if number < 0:
        return None
    return f"{number}{number_ends[number]}"


def nickname(ctx_or_bot, user_id: int, mention: bool = False):
    if isinstance(ctx_or_bot, commands.Context):
        user = ctx_or_bot.bot.get_user(user_id)
    else:
        user = ctx_or_bot.get_user(user_id)
    if not user:
        return "Deleted User"
    if mention:
        return user.mention
    return str(user)


async def fetch_message(ctx_or_bot, channel_id: int, message_id: int, guild_id: int = None):
    message = None
    if isinstance(ctx_or_bot, (commands.Bot, commands.AutoShardedBot)):
        guild = ctx_or_bot.get_guild(guild_id)
        if not guild_id or guild:
            raise InvalidMessage(str(guild))
        channel = guild.get_channel(channel_id)
        if channel:
            try:
                message = await channel.fetch_message(message_id)
            except discord.NotFound:
                pass
    if isinstance(ctx_or_bot, commands.Context):
        channel = ctx_or_bot.guild.get_channel(channel_id)
        if channel:
            try:
                message = await channel.fetch_message(message_id)
            except discord.NotFound:
                pass
    return message


async def del_msg(ctx, amount: Optional[int] = 1, user: Optional[bool] = True, bot: commands.AutoShardedBot = None):

    if isinstance(ctx, discord.Message):
        ctx = bot.get_context(ctx, cls=commands.Context)

    print_message = False
    raise_error = False

    global_delete = user

    def user_check(m):
        return m.author.id == ctx.author.id

    deleted = 0
    try:
        if global_delete:
            deleted = await ctx.channel.purge(limit=amount + 1, bulk=True, check=user_check)
        if not global_delete:
            deleted = await ctx.channel.purge(limit=amount + 1, bulk=True)

        if print_message:
            if len(deleted) == 0:
                if raise_error:
                    print("Can't delete message! Error: Forbidden")
                    await ctx.send(f"{efalse} I don't have enough permission to delete tis message!")
            else:
                print(f'Deleted {len(deleted)} Messages')

    except discord.Forbidden:
        await ctx.send(f"{efalse} I don't have enough permission to delete this message!")
    except discord.NotFound:
        await ctx.send(f'{efalse} Message not found!')


async def send_confirmation(bot: commands.AutoShardedBot, ctx: commands.Context, text: str, timeout: int = 30):
    to_react = await ctx.send(text)
    await to_react.add_reaction('👍')
    await to_react.add_reaction('👎')

    # noinspection PyShadowingNames,PyUnusedLocal
    def check(reaction, user):
        return user.id == ctx.author.id

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=timeout, check=check)
        if str(reaction.emoji) == '👍':
            await to_react.delete()
            return True
        elif str(reaction.emoji) == '👎' or str(reaction.emoji) not in ['👎', '👍']:
            await to_react.delete()
            return False
    except asyncio.TimeoutError:
        return False


async def clean_roles(user: discord.Member, reason: str, exception: List[discord.Role]):
    success = 0
    for role in user.roles:
        if role not in exception:
            try:
                await user.remove_roles(role, reason=reason)
            except discord.Forbidden:
                success += 1
    return f"Removed `{success}`/`{len(user.roles)}` roles."


async def get_db_prefix(guild_id: int):
    data = await db.record('SELECT Prefix FROM Guilds WHERE GuildID = ?', guild_id)
    if not data:
        await db.autoexecute('INSERT INTO guilds(GuildID) VALUES(?)', guild_id)
        return '.'
    return data[0]


async def get_mute_role(bot, guild_id: int):
    guild = bot.get_guild(guild_id)
    data = await db.record('SELECT MuteRole FROM guilds WHERE GuildID = ?', guild.id)
    if data:
        role = guild.get_role(data[0])
        return role if role else None


async def send_error(ctx_or_ch: Union[discord.TextChannel, commands.Context], args: str, delete_after: int = None):
    embed = discord.Embed(color=colors['red'], description=f"**{efalse} {args}**")
    if isinstance(ctx_or_ch, (commands.Context, discord.Message)):
        ctx_or_ch = ctx_or_ch.channel
    if delete_after:
        return await ctx_or_ch.send(embed=embed, delete_after=delete_after)
    await ctx_or_ch.send(embed=embed)


async def send_success(ctx_or_ch: Union[discord.TextChannel, commands.Context], args: str, delete_after: int = None):
    embed = discord.Embed(color=colors['green'], description=f"**{etrue} {args}**")
    if isinstance(ctx_or_ch, (commands.Context, discord.Message)):
        ctx_or_ch = ctx_or_ch.channel
    if delete_after:
        return await ctx_or_ch.send(embed=embed, delete_after=delete_after)
    await ctx_or_ch.send(embed=embed)


async def dm_user(user: discord.Member, message: str):
    try:
        await user.send(message)
    except discord.Forbidden:
        pass
    except discord.HTTPException:
        pass


class BannedMember(commands.Converter):
    async def convert(self, ctx, arg):
        if arg.startswith('<@!') and arg.endswith('>'):
            arg = re.sub("@!", "", arg).strip('<>')
        if ctx.guild.me.guild_permissions.ban_members:
            if arg.isdigit():
                uname = ctx.bot.get_user(int(arg))
                if not uname:
                    raise commands.MemberNotFound(arg)
                try:
                    user = (await ctx.guild.fetch_ban(discord.Object(id=int(arg)))).user
                    if user:
                        return user
                except discord.NotFound:
                    raise NotBanned(uname)
            else:
                banned = [e.user for e in await ctx.guild.bans()]
                if banned:
                    if (user := find(lambda u: str(u) == arg, banned)) is not None:
                        return user
                    else:
                        raise commands.MemberNotFound(arg)
        raise commands.MemberNotFound(arg)


class Duration(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(re.compile("(?:(\d{1,5})([hsmd]))+?"), args)
        time_dict = {'h': 3600, 's': 1, 'm': 60, 'd': 86400}
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * int(key)
            except KeyError:
                raise commands.BadArgument("Duration must be a number! [h|m|d|s]")
            except ValueError:
                raise commands.BadArgument("Duration must be a number! [h|m|d|s]")
        if time > 0:
            return round(time)
        raise commands.BadArgument("Duration must be more than 60 seconds!")
