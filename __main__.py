#!/usr/bin/python3
import asyncio
import os
import discord

from climabot.utils.language import botlanguage
from climabot.utils.botlogging import init_logging
from discord.ext import commands
from dotenv import load_dotenv
from climabot.cogs import *


async def main():
    init_logging()
    load_dotenv()

    botlanguage.install()

    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False
    intents.message_content = True

    bot = commands.Bot(command_prefix=".", intents=intents)
    async with bot:
        await bot.add_cog(greetings.Greetings(bot))
        await bot.add_cog(weather.Weather(bot))
        await bot.add_cog(language.Language(bot))
        await bot.add_cog(cryptocoins.CryptoCoins())
        await bot.add_cog(spotify.Spotify(bot))
        await bot.add_cog(openai.OpenAIGPT(bot))

        await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
