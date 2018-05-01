import asyncio
import os
import random
import string
from copy import deepcopy
from io import BytesIO
from time import sleep

import discord
from discord.ext import commands

from PIL import Image
from redbot.core import Config, RedContext, checks
from redbot.core.bot import Red
from redbot.core.i18n import CogI18n
from selenium import webdriver

_ = CogI18n("Screenshot", __file__)

class Screenshot:
    """Screenshot commands.
    Originially made by https://github.com/adam-psycho"""


    def __init__(self, bot: Red):
        self.bot = bot
        self.max_size = 1024 * 8000  # 8MB
        self.max_processes = 4
        self.processes = 0
        self.default_options = {
        '-f': False,
        '-w': 1024,
        '-h': 768,
        }


    async def fullpage(self, driver):

        """
        from here
        http://stackoverflow.com/questions/1145850/
        how-to-get-height-of-entire-document-with-javascript
        """

        js = 'return Math.max( document.body.scrollHeight, document.body.offsetHeight,  document.documentElement.clientHeight,  document.documentElement.scrollHeight,  document.documentElement.offsetHeight);'

        scrollheight = driver.execute_script(js)

        slices = []
        offset = 0
        while offset < scrollheight:

            driver.execute_script("window.scrollTo(0, %s);" % offset)
            img = Image.open(BytesIO(driver.get_screenshot_as_png()))
            offset += img.size[1]
            slices.append(img)

            if len(slices) > 50:
                raise Exception('Image too large')

        screenshot = Image.new('RGB', (slices[0].size[0], scrollheight))
        offset = 0
        for img in slices:
            screenshot.paste(img, (0, offset))
            offset += img.size[1]

        return screenshot


    async def convert_to_jpeg(self, png, jpg):
        im = Image.open(png)
        rgb_im = im.convert('RGB')
        os.remove(png)
        rgb_im.save(jpg)


    async def set_processes(self, value):
        self.processes = value


    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(aliases=["ss"])
    async def screenshot(self, ctx: RedContext, url, options=None):
        """Screenshots a web page.

        Takes optional arguments.
        Example: r.ss -f -w=1920 -h=1024 reddit.com"""
        options = deepcopy(self.default_options)
        driver = self.configure_browser(options)
        

        if 'http' not in url:
            url = 'http://{}'.format(url)

        elif self.processes > self.max_processes:
            await ctx.send('Too many processes running, try again later.')

        tmp = await ctx.send('Screenshotting <{}>...'.format(url))


        rand_str = lambda n: ''.join(
            random.choice(
                string.ascii_uppercase + string.digits) for _ in range(n))

        filename = rand_str(5)
        png = '{}.{}'.format(filename, 'png')
        jpg = '{}.{}'.format(filename, 'jpg')

        try:
            driver.get(url)
            await asyncio.sleep(1)
            driver.save_screenshot(png)

            await self.convert_to_jpeg(png, jpg)

            filesize = os.stat(jpg).st_size
            if filesize > self.max_size:
                await tmp.edit(content='File too large for <{}>'.format(url))
            else:
                await tmp.edit(content='Screenshot for <{}> grabbed!'.format(url))
                try:
                    await ctx.channel.send(file=discord.File(jpg))
                except:
                    await ctx.channel.send(file=discord.File(png))
        except Exception as e:
            await tmp.edit(content='Screenshot failed. Either could not grab screenshot or the site is down.```py\n{}\n```'.format(str(e)))
        driver.close()

    #await self.set_processes(self.processes - 1)

    def configure_browser(self, options):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('no-sandbox')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.set_window_position(0, 0)
        driver.set_window_size(options['-w'], options['-h'])
        return driver
