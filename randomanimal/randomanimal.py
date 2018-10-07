import asyncio
import random

import discord
import requests
from discord.ext import commands

from redbot.core import commands
from redbot.core import Config, checks
from redbot.core.bot import Red
from redbot.core.config import Group
from redbot.core.commands import Context

BaseCog = getattr(commands, "Cog", object)

class Randomanimal(BaseCog):
    """Randomanimal commands."""  

    def __init__(self, bot: Red):
        self.bot = bot


    @commands.command()
    async def randomcat(self, ctx: Context):
        url = "http://aws.random.cat/meow"
        request_data = requests.get(url)
        data = discord.Embed(colour=random.randint(0x000000, 0xFFFFFF))
        data.set_image(url=request_data.json()['file'])
        await ctx.send(embed=data)

    @commands.command()
    async def randomdog(self, ctx: Context):
        url = "https://random.dog/woof.json"
        request_data = requests.get(url)
        data = discord.Embed(colour=random.randint(0x000000, 0xFFFFFF))
        data.set_image(url=request_data.json()['url'])
        await ctx.send(embed=data)
