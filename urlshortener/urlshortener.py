import asyncio
import random

import discord
import requests
from discord.ext import commands

from redbot.core.commands import Context
from redbot.core.bot import Red

BaseCog = getattr(commands, "Cog", object)

class Urlshortener(BaseCog):
    """Urlshortener commands."""  

    def __init__(self, bot: Red):
        self.bot = bot
        self.key = await self.config.api_key()
        self.config = Config.get_conf(self, 5432732823, force_registration=True)
        default_global_settings = {
            "api_key": None
        }
        self.config.register_global(**default_global_settings)


    async def _shortnen_url(self, url):
        req_url = 'https://www.googleapis.com/urlshortener/v1/url?key={}'.format(self.key)
        payload = {'longUrl': url}
        headers = {'content-type': 'application/json'}
        r = requests.post(req_url, json=payload, headers=headers)
        resp = json.loads(r.text)
        return resp['id']


    async def _expand_url(self, url):
        req_url = 'https://www.googleapis.com/urlshortener/v1/url'
        payload = {'key': self.key, 'shortUrl': url}
        r = requests.get(req_url, params=payload)
        resp = json.loads(r.text)
        return resp['longUrl']


    @commands.group(name="url")
    async def url(self, ctx: RedContext):
        """Shorten and expand goo.gl links"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()


    @url.command(name="shorten")
    async def url_shorten(self, ctx: RedContext, url):
        """Shorten a link into a goo.gl link"""
        shortened_url = await self._shortnen_url(url)
        await ctx.send("Shortened link: {}".format(shortened_url))

    
    @url.command(name="expand")
    async def url_expand(self, ctx: RedContext, url):
        """Expand a goo.gl link into it's original link"""
        expanded_url = await self._expand_url(url)
        await ctx.send("Expanded link: {}".format(expanded_url))
