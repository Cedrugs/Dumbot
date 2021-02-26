from discord.ext.commands import AutoShardedBot, when_mentioned_or, Context
from discord import __version__, Activity, ActivityType
from glob import glob
from datetime import datetime
from utils.tools import get_db_prefix, linebreaks
from platform import python_version
from discord import Intents
from asyncio import sleep
from lib.database import Database
from utils.jsons import read_json


import logging


log = logging.getLogger(__name__)
intent = Intents().all()
cog_path = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]


async def custom_prefixes(bots, message):
    if not message.guild:
        return when_mentioned_or('.')(bots, message)
    prefix = await get_db_prefix(message.guild.id)
    return when_mentioned_or(prefix)(bots, message)


class Ready(object):
    def __init__(self):
        for cog in cog_path:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)

    def all_ready(self):
        return all([getattr(self, cog) for cog in cog_path if cog])


class Bot(AutoShardedBot):
    def __init__(self):
        self.ready = False
        self.version = ''
        self.cog_ready = Ready
        self.db = Database('./lib/database/db.db')
        self.startuptime = None
        super().__init__(command_prefix=custom_prefixes, case_insensitive=True, intents=intent)

    def setup(self):
        if not cog_path:
            print(f"No cog to load | {datetime.utcnow().strftime('%X')}")
        for cog in cog_path:
            try:
                self.load_extension(f"lib.cogs.{cog}")
                print(f"{cog.title()} cog has been loaded | {datetime.utcnow().strftime('%X')}")
            except Exception as exc:
                log.error('Error while loading cogs', exc)

    def run(self, version):
        self.version = version
        print(f"Running setup | {datetime.utcnow().strftime('%X')}")
        linebreaks()
        self.setup()
        data = read_json("config.json")
        linebreaks()
        print(f"Running bot | {datetime.utcnow().strftime('%X')}")
        super().run(data['bot_token'], reconnect=True)

    async def process(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if not self.ready:
                await ctx.send("The bot is starting, please try again in a few seconds.")
            else:
                log.info(
                    f'Command: {ctx.message.content} | User: {ctx.author}({ctx.author.id}) | Guild ID: {ctx.guild.id}'
                )
                await self.invoke(ctx)

    async def on_connect(self):
        linebreaks()
        print(f"Bot connected to {self.user} Version: {self.version} |  {datetime.utcnow().strftime('%X')}")
        linebreaks()

    @staticmethod
    async def on_disconnect():
        linebreaks()
        print(f"Bot disconnected | {datetime.utcnow().strftime('%X')}")

    @staticmethod
    async def on_resumed():
        linebreaks()
        print(f"Bot reconnected | {datetime.utcnow().strftime('%X')}")

    async def on_ready(self):
        if not self.ready:
            while not self.cog_ready.all_ready:
                await sleep(0.4)
        self.ready = True
        self.startuptime = datetime.utcnow()
        await self.change_presence(activity=Activity(name='.help', type=ActivityType.listening))
        print(f"Bot is connected and ready to use | {datetime.utcnow().strftime('%X')}")
        linebreaks()
        print(f"Running on python {python_version()} | Discord.py {__version__} | {round(self.latency * 1000)}ms")
        linebreaks()
        log.info(f'Bot is turned on and connected to {self.user} | Running on {self.guilds} guilds')

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process(message)


bot = Bot()
