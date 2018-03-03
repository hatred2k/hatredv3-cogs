import asyncio
import random
import json

import discord
import requests
from discord.ext import commands

from redbot.core.bot import Red
from redbot.core import checks, Config, RedContext


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
        """Retrieves raw data from fortnite servers.
        Parameters
        ----------
        username : str
            The epic-nickname of the user.
        platform : str
            The platform the user has played on.
        Returns
        -------
        str
            The raw statistical json data.
        """
        headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'TRN-Api-Key': "{}".format(await self.config.fortnite_api_key())
        }
        if platform is None:
            platform = "pc"
        platforms = ["xbox", "psn", "pc"]
        url = "https://api.fortnitetracker.com/v1/profile/{}/{}".format(platform, username)
        data = requests.request("GET", url, headers=headers)
        if "error" in data.json():
            platforms.remove(platform)
            try:
                new_platform = random.choice(platforms)
                url = "https://api.fortnitetracker.com/v1/profile/{}/{}".format(new_platform, username)
                print("new_platform: {}\n1{}".format(new_platform, platforms))
                data = await self.get_raw_player_data(url)
                if "error" in data:
                    platforms.remove(new_platform)
                    only_platform = platforms[0]
                    url = "https://api.fortnitetracker.com/v1/profile/{}/{}".format(only_platform, username)
                    print("only_platform: {}\n2{}".format(only_platform, platforms))
                    data = await self.get_raw_player_data(url)
                return data
            except Exception as e:
                return "Either an error occured or no data could be found:\n```py{}\n```".format(e)
        else:
            data = requests.request("GET", url, headers=headers)
            return data.json()


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
                temp = await ctx.send("Fetching profile...")
                author = ctx.author
                guild = ctx.guild
                stats = await self.get_fortnite_data(username, platform)
                username = stats["epicUserHandle"]
                platform = stats["platformName"]
                wins = stats["lifeTimeStats"][8]["value"]
                score = stats["lifeTimeStats"][6]["value"]
                matches = stats["lifeTimeStats"][7]["value"]
                kills = stats["lifeTimeStats"][10]["value"]
                killratio = stats["lifeTimeStats"][11]["value"]
                time_played = stats["lifeTimeStats"][13]["value"]
                avg_survival_time = stats["lifeTimeStats"][14]["value"]

                data = discord.Embed(colour=ctx.author.colour)
                data.set_thumbnail(url=author.avatar_url)
                data.add_field(name="Username", value=username)
                data.add_field(name="Platform", value=platform)
                data.add_field(name="Wins", value=wins)
                data.add_field(name="Score", value=score)
                data.add_field(name="Matches Played", value=matches)
                data.add_field(name="Kills", value=kills)
                data.add_field(name="K/D Ratio", value=killratio)
                data.add_field(name="Time Played", value=time_played)
                data.add_field(name="Average Survival Time", value=avg_survival_time)
                data.set_footer(text='Retrived from FortniteTracker | {}'.format(datetime.datetime.now().strftime("%A, %B %-d %Y at %-I:%M%p").replace("PM", "pm").replace("AM", "am")), icon_url='https://i.imgur.com/IMjozOI.jpg')
                data.set_author(name=author.name, icon_url=author.avatar_url)
                
                await temp.edit(embed=data)
            except TypeError:
                await temp.edit(content="That profile could not be found.")
