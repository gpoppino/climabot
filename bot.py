#!/usr/bin/python3

import os

from utils.language import botlanguage
from discord.ext import commands
from dotenv import load_dotenv
from cogs import *

load_dotenv()

bot = commands.Bot(command_prefix='.')

bot.add_cog(greetings.Greetings(bot))
bot.add_cog(weather.Weather(bot))
bot.add_cog(language.Language(bot))

botlanguage.install()

bot.run(os.getenv('DISCORD_TOKEN'))
