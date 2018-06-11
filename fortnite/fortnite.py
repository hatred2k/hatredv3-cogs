import asyncio
import random
import json

import discord
import datetime
import requests
from discord.ext import commands

from redbot.core.bot import Red
from redbot.core import checks, Config
from redbot.core.i18n import Translator
from redbot.core.commands import Context

_ = Translator("Fortnite", __file__)

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
        

    async def get_lifetime_data(self, username, platform=None):
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
                        return
                return data
            except:
                return
        else:
            req = await self.get_raw_player_data(url)
            return req

    async def get_solo_data(self, username, platform=None):
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
                        return
                return data["stats"]["p2"]
            except:
                return
        else:
            req = await self.get_raw_player_data(url)
            return req["stats"]["p2"]

    async def get_duo_data(self, username, platform=None):
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
                        return
                return data["stats"]["p10"]
            except:
                return
        else:
            req = await self.get_raw_player_data(url)
            return req["stats"]["p10"]

    async def get_squad_data(self, username, platform=None):
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
                        return
                return data["stats"]["p9"]
            except:
                return
        else:
            req = await self.get_raw_player_data(url)
            return req["stats"]["p9"]


    @checks.is_owner()
    @commands.group(name="fortniteset")
    async def fortnite_set(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @fortnite_set.command(name="key", aliases=["token"])
    async def set_key(self, ctx: Context, api_token):
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
    @commands.group(name="fortnite")
    async def fortnite(self, ctx: Context):
        """Shows fortnite stats

        Defaults to PC stats"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()


    @commands.cooldown(1, 2, commands.BucketType.user)
    @fortnite.command(name="stats")
    async def fortnite_lifetime(self, ctx: Context, username, platform=None):
        """Shows lifetime stats across Solo Duos, and Squads

        Defaults to PC"""
        if await self.config.fortnite_api_key() is None:
            await ctx.send("No API token found.\nYou can enter one by using `{}fortniteset token`".format(ctx.prefix))
            return
        else:
            try:
                author = ctx.author
                guild = ctx.guild
                stats = await self.get_lifetime_data(username, platform)
                data = discord.Embed(title="Lifetime Stats", colour=ctx.author.colour)
                data.set_thumbnail(url=author.avatar_url)
                data.add_field(name="Username", value=stats["epicUserHandle"])
                data.add_field(name="Platform", value=stats["platformNameLong"])
                data.add_field(name="Wins", value=stats["lifeTimeStats"][8]["value"])
                data.add_field(name="Score", value=stats["lifeTimeStats"][6]["value"])
                data.add_field(name="Matches Played", value=stats["lifeTimeStats"][7]["value"])
                data.add_field(name="Kills", value=stats["lifeTimeStats"][10]["value"])
                data.add_field(name="K/D Ratio", value=stats["lifeTimeStats"][11]["value"])
                data.add_field(name="Win %", value=stats["lifeTimeStats"][9]["value"])
                data.set_footer(text="ID: {}".format(stats["accountId"]), icon_url="https://i.imgur.com/IMjozOI.jpg")
                data.set_author(name=author.name, icon_url=author.avatar_url)
                await ctx.send(embed=data)
            except TypeError:
                await ctx.send("That profile could not be found.")
            except ValueError as e:
                await ctx.send("An error occured while attempting to retrieve the platform.\nIf the username has spaces, try enclosing it in quotes.")
                await ctx.send("```py\n{}\n```".format(str(e)))


    @commands.cooldown(1, 2, commands.BucketType.user)
    @fortnite.command(name="solo")
    async def fortnite_solo(self, ctx: Context, username, platform=None):
        """Shows solo stats

        Defaults to PC"""
        if await self.config.fortnite_api_key() is None:
            await ctx.send("No API token found.\nYou can enter one by using `{}fortniteset token`".format(ctx.prefix))
            return
        else:
            try:
                author = ctx.author
                guild = ctx.guild
                lifetime = await self.get_lifetime_data(username, platform)
                stats = await self.get_solo_data(username, platform)
                data = discord.Embed(title="Solo Stats", colour=ctx.author.colour)
                data.set_thumbnail(url=author.avatar_url)
                data.add_field(name="Username", value=lifetime["epicUserHandle"])
                data.add_field(name="Platform", value=lifetime["platformNameLong"])
                data.add_field(name="Wins", value=stats["top1"]["value"])
                data.add_field(name="Score", value=stats["score"]["value"])
                data.add_field(name="Matches Played", value=stats["matches"]["value"])
                data.add_field(name="Kills", value=stats["kills"]["value"])
                data.add_field(name="K/D Ratio", value=stats["kd"]["value"])
                data.add_field(name="Win %", value=stats["winRatio"]["value"])
                data.set_footer(text="ID: {}".format(lifetime["accountId"]), icon_url="https://i.imgur.com/IMjozOI.jpg")
                data.set_author(name=author.name, icon_url=author.avatar_url)
                await ctx.send(embed=data)
            except TypeError:
                await ctx.send("That profile could not be found.")
            except ValueError:
                await ctx.send("An error occured while attempting to retrieve the platform.\nIf the username has spaces, try enclosing it in quotes.")


    @commands.cooldown(1, 2, commands.BucketType.user)
    @fortnite.command(name="duo", aliases=["duos"])
    async def fortnite_duo(self, ctx: Context, username, platform=None):
        """Shows duo stats

        Defaults to PC"""
        if await self.config.fortnite_api_key() is None:
            await ctx.send("No API token found.\nYou can enter one by using `{}fortniteset token`".format(ctx.prefix))
            return
        else:
            try:
                author = ctx.author
                guild = ctx.guild
                lifetime = await self.get_lifetime_data(username, platform)
                stats = await self.get_duo_data(username, platform)
                data = discord.Embed(title="Duo Stats", colour=ctx.author.colour)
                data.set_thumbnail(url=author.avatar_url)
                data.add_field(name="Username", value=lifetime["epicUserHandle"])
                data.add_field(name="Platform", value=lifetime["platformNameLong"])
                data.add_field(name="Wins", value=stats["top1"]["value"])
                data.add_field(name="Score", value=stats["score"]["value"])
                data.add_field(name="Matches Played", value=stats["matches"]["value"])
                data.add_field(name="Kills", value=stats["kills"]["value"])
                data.add_field(name="K/D Ratio", value=stats["kd"]["value"])
                data.add_field(name="Win %", value=stats["winRatio"]["value"])
                data.set_footer(text="ID: {}".format(lifetime["accountId"]), icon_url="https://i.imgur.com/IMjozOI.jpg")
                data.set_author(name=author.name, icon_url=author.avatar_url)
                await ctx.send(embed=data)
            except TypeError:
                await ctx.send("That profile could not be found.")
            except ValueError as e:
                await ctx.send("An error occured while attempting to retrieve the platform.\nIf the username has spaces, try enclosing it in quotes.")
                await ctx.send("```py\n{}\n```".format(str(e)))


    @commands.cooldown(1, 2, commands.BucketType.user)
    @fortnite.command(name="squad", aliases=["squads"])
    async def fortnite_squad(self, ctx: Context, username, platform=None):
        """Shows squad stats

        Defaults to PC"""
        if await self.config.fortnite_api_key() is None:
            await ctx.send("No API token found.\nYou can enter one by using `{}fortniteset token`".format(ctx.prefix))
            return
        else:
            try:
                author = ctx.author
                guild = ctx.guild
                lifetime = await self.get_lifetime_data(username, platform)
                stats = await self.get_squad_data(username, platform)
                data = discord.Embed(title="Sqaud Stats", colour=ctx.author.colour)
                data.set_thumbnail(url=author.avatar_url)
                data.add_field(name="Username", value=lifetime["epicUserHandle"])
                data.add_field(name="Platform", value=lifetime["platformNameLong"])
                data.add_field(name="Wins", value=stats["top1"]["value"])
                data.add_field(name="Score", value=stats["score"]["value"])
                data.add_field(name="Matches Played", value=stats["matches"]["value"])
                data.add_field(name="Kills", value=stats["kills"]["value"])
                data.add_field(name="K/D Ratio", value=stats["kd"]["value"])
                data.add_field(name="Win %", value=stats["winRatio"]["value"])
                data.set_footer(text="ID: {}".format(lifetime["accountId"]), icon_url="https://i.imgur.com/IMjozOI.jpg")
                data.set_author(name=author.name, icon_url=author.avatar_url)
                await ctx.send(embed=data)
            except TypeError:
                await ctx.send("That profile could not be found.")
            except ValueError:
                await ctx.send("An error occured while attempting to retrieve the platform.\nIf the username has spaces, try enclosing it in quotes.")
