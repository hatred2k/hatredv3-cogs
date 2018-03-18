import asyncio
import random

import discord
import requests
from discord.ext import commands

from redbot.core import RedContext
from redbot.core.bot import Red


class Randomanimal:
    """Randomanimal commands."""  

    def __init__(self, bot: Red):
        self.bot = bot


    @commands.command()
    async def randomcat(self, ctx: RedContext):
        url = "http://aws.random.cat/meow"
        request_data = requests.get(url)
        data = discord.Embed(colour=random.randint(0x000000, 0xFFFFFF))
        data.set_image(url=request_data.json()['file'])
        await ctx.send(embed=data)

    @commands.command()
    async def randomdog(self, ctx: RedContext):
        url = "https://random.dog/woof.json"
        request_data = requests.get(url)
        data = discord.Embed(colour=random.randint(0x000000, 0xFFFFFF))
        data.set_image(url=request_data.json()['url'])
        await ctx.send(embed=data)
