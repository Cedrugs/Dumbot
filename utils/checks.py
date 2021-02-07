from discord.ext import commands
from lib.database import db
from utils.error import NotEligible, InvalidDB
from utils.collections import VALID_DB

import discord


__all__ = [
    'eligible', 'admin_or_perms', 'owner_only', 'check_db', 'cooldown', 'CustomCooldown'
]


class CustomCooldown:
    def __init__(self, rate: int, per: float, alter_rate: int, alter_per: float, bucket: commands.BucketType):
        self.cd = per
        self.pcd = alter_rate
        self.default_mapping = commands.CooldownMapping.from_cooldown(rate, per, bucket)
        self.altered_mapping = commands.CooldownMapping.from_cooldown(alter_rate, alter_per, bucket)

    # noinspection PyProtectedMember
    async def __call__(self, ctx: commands.Context):
        bypass = [x[0] for x in await db.recordall("SELECT * FROM guilds WHERE GuildID = ?", ctx.guild.id) if x[2] == 1]
        key = ctx.guild.id
        if key in bypass:
            bucket = self.altered_mapping.get_bucket(ctx.message)
        else:
            bucket = self.default_mapping.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
        return True


def eligible(user1: discord.Member, user2: discord.Member):
    if isinstance(user2, discord.Member):
        if user1.top_role < user2.top_role or user1.top_role == user2.top_role:
            raise NotEligible(user=user2)
        return True
    elif isinstance(user2, discord.Role):
        if user1.top_role < user2 or user1.top_role == user2:
            raise NotEligible(user=user2)
        return True


def admin_or_perms(**perms):
    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError('Invalid permission(s): %s' % (', '.join(invalid)))

    async def predicate(ctx):
        role_data = await db.record('SELECT RoleID FROM Moderators WHERE GuildID = ?', ctx.guild.id)
        if role_data:
            admin_role = ctx.guild.get_role(role_data[0])
            if admin_role:
                if admin_role in ctx.author.roles:
                    return True
        ch = ctx.channel
        permissions = ch.permissions_for(ctx.author)
        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]
        if not missing:
            return True
        raise commands.MissingPermissions(missing)
    return commands.check(predicate)


def owner_only():
    async def predicate(ctx):
        if ctx.author.id == ctx.guild.owner.id:
            return True
        raise commands.MissingPermissions(['guild_owner'])
    return commands.check(predicate)


def check_db(**tables):
    invalid_table = set(tables) - set(VALID_DB)
    if invalid_table:
        raise InvalidDB(f"Invalid table(s) for {', '.join(invalid_table)}")

    async def predicate(ctx):
        guild_id = ctx.guild.id
        for table in set(tables):
            data = await db.record(f"SELECT * FROM {table} WHERE GuildID = ?", guild_id)
            if data:
                return True
            if table == VALID_DB[0]:
                await db.autoexecute('INSERT INTO Welcomer(GuildID) VALUES(?)', guild_id)
            if table == VALID_DB[1]:
                await db.autoexecute('INSERT INTO Goodbye(GuildID) VALUES(?)', guild_id)
            if table == VALID_DB[2]:
                await db.autoexecute('INSERT INTO Guilds(GuildID) VALUES(?)', guild_id)
            if table == VALID_DB[3]:
                await db.autoexecute('INSERT INTO Verify(GuildID) VALUES(?)', guild_id)
        return True
    return commands.check(predicate)


def cooldown(rate: int, per: float, premium_rate: int, premum_per: float, bucket: commands.BucketType):
    return commands.check(CustomCooldown(rate, per, premium_rate, premum_per, bucket))
