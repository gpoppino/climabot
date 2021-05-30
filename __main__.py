#!/usr/bin/python3

import os

from climabot.utils.language import botlanguage
from climabot.utils.botlogging import init_logging
from discord.ext import commands
from dotenv import load_dotenv
from climabot.cogs import *

init_logging()
load_dotenv()

bot = commands.Bot(command_prefix='.')

bot.add_cog(greetings.Greetings(bot))
bot.add_cog(weather.Weather(bot))
bot.add_cog(language.Language(bot))
bot.add_cog(cryptocoins.CryptoCoins())
bot.add_cog(spotify.Spotify(bot))
bot.add_cog(helper.Helper(bot))

botlanguage.install()

bot.run(os.getenv('DISCORD_TOKEN'))
