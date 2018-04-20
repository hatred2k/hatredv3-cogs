import asyncio
import random
import json

import discord
import datetime
import requests
from discord.ext import commands

from redbot.core.bot import Red
from redbot.core import checks, Config, RedContext
from redbot.core.i18n import CogI18n

_ = CogI18n("Fortnite", __file__)

class Fortnite:
    """Fortnite commands."""


    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, 451736518321, force_registration=True)
        default_global_settings = {
            "fortnite_api_key": None
        }
        self.config.register_global(**default_global_settings)


    async def get_raw_player_data(self, url):
        headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'TRN-Api-Key': "{}".format(await self.config.fortnite_api_key())
        }
        data = requests.request("GET", url, headers=headers)
        return data.json()

    async def get_fortnite_data(self, username, platform=None):
        if platform is None:
            platform = "pc"
        platforms = ["xbox", "psn", "pc"]
        url = "https://api.fortnitetracker.com/v1/profile/{}/{}".format(platform, username)
        req = await self.get_raw_player_data(url)
        if "error" in req:
            platforms.remove(platform)
            try:
                new_platform = random.choice(platforms)
                url = "https://api.fortnitetracker.com/v1/profile/{}/{}".format(new_platform, username)
                data = await self.get_raw_player_data(url)
                if "error" in data:
                    platforms.remove(new_platform)
                    only_platform = platforms[0]
                    url = "https://api.fortnitetracker.com/v1/profile/{}/{}".format(only_platform, username)
                    data = await self.get_raw_player_data(url)
                    if "error" in data:
                        return "Profile could not be found"
                return data
            except:
                return
        else:
            req = await self.get_raw_player_data(url)
            return req


    @checks.is_owner()
    @commands.group(name="fortniteset")
    async def fortnite_set(self, ctx: RedContext):
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @fortnite_set.command(name="key", aliases=["token"])
    async def set_key(self, ctx: RedContext, api_token):
        """Sets the fortnite API token
        You will need to register and generate a token.

        You can get these by visiting https://fortnitetracker.com/site-api
        After registering, on the same page, you will be able to generate an api key.
        Copy that and enter it here."""
        author = ctx.author
        try:
            await self.config.fortnite_api_key.set(api_token)
            await ctx.send("Token set.")
        except Exception as e:
            await ctx.send("```py\n{}\n```".format(str(e)))


    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    @commands.command()
    async def fortnite(self, ctx: RedContext, username, platform=None):
        """Shows fortnite stats

        Defaults to PC"""
        if await self.config.fortnite_api_key() is None:
            await ctx.send("No API token found.\nYou can enter one by using `{}fortniteset token`".format(ctx.prefix))
            return
        else:
            try:
                author = ctx.author
                guild = ctx.guild
                stats = await self.get_fortnite_data(username, platform)
                data = discord.Embed(colour=ctx.author.colour)
                data.set_thumbnail(url=author.avatar_url)
                data.add_field(name="Username", value=stats["epicUserHandle"])
                data.add_field(name="Platform", value=stats["platformNameLong"])
                data.add_field(name="Wins", value=stats["lifeTimeStats"][8]["value"])
                data.add_field(name="Score", value=stats["lifeTimeStats"][6]["value"])
                data.add_field(name="Matches Played", value=stats["lifeTimeStats"][7]["value"])
                data.add_field(name="Kills", value=stats["lifeTimeStats"][10]["value"])
                data.add_field(name="K/D Ratio", value=stats["lifeTimeStats"][11]["value"])
                data.add_field(name="Win %", value=stats["lifeTimeStats"][9]["value"])
                #data.add_field(name="Average Survival Time", value=stats["lifeTimeStats"][14]["value"])
                data.set_footer(text='{}'.format(datetime.datetime.now().strftime("%A, %B %-d %Y at %-I:%M%p").replace("PM", "pm").replace("AM", "am")), icon_url='https://i.imgur.com/IMjozOI.jpg')
                data.set_author(name=author.name, icon_url=author.avatar_url)
                
                await ctx.send(embed=data)
            except TypeError:
                await ctx.send("That profile could not be found.")
            except ValueError:
                await ctx.send("An error occured while attempting to retrieve the platform.\nIf the username has spaces, try encloding it in quotes.")
