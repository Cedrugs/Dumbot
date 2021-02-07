"""
Paginator tools, Yeah! This one is made by me, no i mean Rapptz.
In order to get this working, you may need to install additional package such as [discord.ext.menus]
Which can be installed by running this command:
[ python -m pip install -U git+https://github.com/Rapptz/discord-ext-menus ]
"""

from discord.ext.menus import ListPageSource, MenuPages
from discord.ext.commands import Context
from typing import Union

import discord

__all__ = ['Paginator']


class Paginator(ListPageSource):

    def __init__(
            self, ctx, data, name, title, per_page, color=0x3498DB, footer="{total}",
            clear_reaction_after=False, delete_message_after=False
    ):
        """
        A function to paginate a list and returning embed.
        :param ctx: Context to do something. [commands.Context]
        :param data: Data to iterate and turn it to paginator [list]
        :param name: Name of the object on the data [str]
        :param title: Title of the embed [str]
        :param per_page: How many data to display every page on embed [int]
        :param color: Color of the embed [int / discord.Colour]
        :param footer: Footer of the embed [str] | default to '{total}' "{total} (1-x of x {name}) "
        :param clear_reaction_after: Clear the reaction after the paginator stopped [bool] | default to False
        :param delete_message_after: Delete the messages after the paginator stopped [bool] | default to False
        """
        self.title: str = title
        self.name: str = name
        self.ctx: Context = ctx
        self.data: list or tuple = data
        self.page: int = per_page
        self.color: Union[discord.Color, int] = color
        self.footer: str = footer
        self.clear_reaction: bool = clear_reaction_after
        self.delete_message: bool = delete_message_after

        super().__init__(data, per_page=self.page)

    # noinspection PyUnusedLocal
    async def write(self, menu, offset, fields=None):
        total_data = len(self.entries)
        total = f"{offset:,} - {min(total_data, offset + self.per_page -1):,} of {total_data:,} {self.name}"

        e = discord.Embed(color=self.color)
        e.set_footer(text=self.footer.format(total=total))

        for name, value in fields:
            e.add_field(name=name, value=value, inline=False)

        return e

    # noinspection PyUnresolvedReferences
    async def format_page(self, menu, entries):
        offset = (menu.current_page * self.per_page) + 1

        fields = []
        table = ("\n".join(entry for num, entry, in enumerate(entries)))

        fields.append((self.title, table))
        return await self.write(menu, offset, fields)

    async def start(self):
        page = Paginator(self.ctx, self.data, self.name, self.title, int(self.per_page), self.color, self.footer)
        menu = MenuPages(
            source=page, clear_reactions_after=self.clear_reaction, delete_message_after=self.delete_message
        )
        await menu.start(self.ctx)
