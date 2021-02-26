efalse = '<:false:746690731376377856>'  # False Emoji.
etrue = '<:true:746690806814998658>'  # True emoji.

punishments = ['ban', 'kick', 'mute', 'hardmute', 'softban']
no_args = ['no', 'nah', '0', 'false']
date_fmt = '%A, %Y/%m/%d %X'
no_reason = "No reason provided"

mc_server = [
    'play.ecc.eco', 'play.cubecraft.net', 'minehut.com', 'hub.mcs.gg', 'pvpwars.net', 'Play.datblock.com',
    'join.manacube.net', 'org.archonhq.net', 'play.mcprison.com', 'play.pocketpixels.net', 'play.EarthMC.net',
    'play.extremecraft.net', 'mccentral.org', 'play.vulengate.com', 'org.mc-gtm.net', 'mc.minebox.es',
    'Play.Performium.net', 'Play.Performium.net', 'play.mineheroes.org', 'us.mineplex.com',
    'play.fadecloud.com', 'mc.vortexpvp.gg', 'blocksmc.com', 'play.ham5teak.net.au', 'org.pvpcloud.org',
    'come.play-ml.ru', 'mc.arkhamnetwork.org', 'mc.gamesmadeinpola.com', 'play.ggmc.me', 'munchymc.com',
    'minesaga.net', 'play.pokefind.co', 'play.oplegends.com', 'SkittleMC.com', 'purpleprison.net',
    'gg.prisonfun.com', 'blocksmc.com', 'mc.herobrine.org', 'mccentral.org', 'casual.universemc.us',
    'play.tritonpvp.net', 'Play.Performium.net'
]

colors = {
    'green': 0x89f989,
    'red': 0xee6565,
    'yellow': 0xE6E71A,
    'blue': 0x3fa3ff
}

VALID_DB = ['welcomer', 'goodbye', 'guilds', 'verify']
YES_ARGS = ['yes', 'ok', 'sure', 'fine', '0', 'true', 'alright', 'aight', 'ya', 'yeah', '1', 'yep']
EVENT_LOG = {
    'VOICE_EVENT': {
        'JOIN_VC': {
            'formal': 'Member Join Voice Channel',
            'color': colors['green'],
            'format': '{0} joined {1}'
        },
        'LEFT_VC': {
            'formal': 'Member Left Voice Channel',
            'color': colors['red'],
            'format': '{0} left {1}'
        },
        'MOVE_VC': {
            'formal': 'Member Move Between Voice Channel',
            'color': colors['green'],
            'format': '{0} moved from {1} to {2}'
        }
    },
    'JOIN_AND_LEAVE': {
        'MEMBER_JOIN': {
            'formal': 'Member Join Server',
            'color': colors['green'],
            'format': '{0} joined this server'
        },
        'MEMBER_LEFT': {
            'formal': 'Member Left Server',
            'color': colors['red'],
            'format': '{0} left this server'
        }
    },
    'MESSAGE_EVENT': {
        'DELETED_MSG': {
            'formal': 'Deleted Message',
            'color': colors['green'],
            'format': '{0} Deleted Message'
        },
        'EDITED_MSG': {
            'formal': 'Edited Message',
            'color': colors['green'],
            'format': '{0} Edited his message'
        },
        'PURGED_MSG': {
            'formal': 'Purged Message using Command',
            'color': colors['green'],
            'format': '{0} Purged {1} messages on {2}'
        }
    },
    'MEMBER_EVENT': {
        'ROLE_UPDATE': {
            'formal': 'Role Update',
            'color': colors['green'],
            'format': '{0} {1} role {2}'
        },
        'NAME_UPDATE': {
            'formal': 'Nickname Changed',
            'color': colors['green'],
            'format': '{0} their nickname from {1} to {2}'
        },
        'AVATAR_CHANGES': {
            'formal': 'Avatar Changed',
            'color': colors['green'],
            'format': '{0} changed their avatar'
        },
        'MEMBER_BAN': {
            'formal': 'Member Banned',
            'color': colors['red'],
            'format': '{0} banned from this server'
        },
        'MEMBER_UNBAN': {
            'formal': 'Member Unbanned',
            'color': colors['green'],
            'format': '{0} unbanned from this server'
        }
    },
    'MOD_LOG': {
        "BANS": {
            'formal': "Full log for banned Member",
            'color': colors['red'],
            'format': '**Violator:** {0}\n**Reason:** {1}\n**Duration:** {2}\n**Moderator:** {3}'
        },
        "MUTES": {
            "formal": "Muted Member",
            'color': colors['red'],
            'format': '**Violator:** {0}\n**Reason:** {1}\n**Moderator:** {2}'
        },
        'WARNINGS': {
            "formal": "Warned Member",
            'color': colors['yellow'],
            'format': '**Violator:** {0}\n**Reason:** {1}\n**Moderator:** {2}'
        },
        'KICKS': {
            'formal': "Kicked Member",
            'color': colors['red'],
            'format': '**Violator:** {0}\n**Reason:** {1}\n**Moderator:** {2}'
        },
        'HARDMUTES': {
            'formal': "Hardmuted Member",
            'color': colors['red'],
            'format': '**Violator:** {0}\n**Reason:** {1}\n**Duration:** {2}\n**Moderator:** {3}'
        },
        'UNMUTES': {
            'formal': "Unmuted Member",
            'colors': colors['green'],
            'format': '**Violator:** {0}\n**Reason:** {1}\n**Moderator:** {2}'
        },
        'UNBANS': {
            'formal': "Unbanned Member",
            'colors': colors['green'],
            'format': '**Violator:** {0}\n**Reason:** {1}\n**Moderator:** {2}'
        }
    }
}


number_ends = {
    1: "st",
    2: "nd",
    3: "rd",
    4: "th",
    5: "th",
    6: "th",
    7: "th",
    8: "th",
    9: "th",
    10: "th"
}

converter = {
    1: "This is their 2nd warnings.",
    2: "This is their 3rd warnings.",
    3: "This is their 4th warnings.",
    4: "This is their last warnings."
}

userinput = {
    1: "This is your 2nd warnings.",
    2: "This is your 3rd warnings.",
    3: "This is your 4th warnings.",
    4: "This is your last warnings."
}


alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z']
special_chars = ['!', '?', '<', '>', ';', ':', '[', ']', '}', '{', '-', '_', '+', '=', '(', ')', '/', '|', '`', '~']
