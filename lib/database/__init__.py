from aiosqlite import connect as aioconnect, __version__


db_version = '0.5a'
aiosqlite = __version__


class Database:

    def __init__(self, path='./lib/database/db.db'):

        self.path = path

    async def record(self, commands, *values):
        async with aioconnect(self.path) as cur:
            items = await cur.execute(commands, tuple(values))

            return await items.fetchone()

    async def recordall(self, commands, *values):
        async with aioconnect(self.path) as cur:
            items = await cur.execute(commands, tuple(values))

            return await items.fetchall()

    async def field(self, commands, *values):
        async with aioconnect(self.path) as cur:
            items = await cur.execute(commands, tuple(values))

            if (fetch := await items.fetchone()) is not None:
                return fetch[0]

    async def execute(self, commands, *values):
        async with aioconnect(self.path) as cur:
            await cur.execute(commands, tuple(values))

    async def autoexecute(self, commands, *values):
        async with aioconnect(self.path) as cur:
            await cur.execute(commands, tuple(values))
            await cur.commit()

    async def column(self, commands, *values):
        async with aioconnect(self.path) as cur:
            items = await cur.execute(commands, tuple(values))

            return [item[0] for item in await items.fetchall()]

    async def commit(self):
        async with aioconnect(self.path) as db:
            await db.commit()


db = Database()
