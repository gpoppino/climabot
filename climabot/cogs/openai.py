import os
from openai import AsyncOpenAI

from discord.ext import commands


class OpenAIGPT(commands.Cog):

    def __init__(self, bot):
        # Load your API key from an environment variable or secret management service
        self.__client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.__bot = bot

    @commands.command(name="gpt", help="Generates text using OpenAI GPT-3.5 Turbo")
    async def get_openai_gpt_response(self, ctx, *args):
        if len(args) == 0:
            return

        message = ' '.join(args).strip()
        async with ctx.typing():
            response = await self.__client.chat.completions.create(model="gpt-3.5-turbo",
                                                                   messages=[{"role": "system",
                                                                              "content": "You are a helpful assistant"},
                                                                             {"role": "user", "content": message}]
                                                                   )
        await ctx.send(response.choices[0].message.content)
