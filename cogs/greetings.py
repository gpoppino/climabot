import random

from discord.ext import commands

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.__bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__bot.user} has connected to Discord!')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.__bot.user:
            return

        if any([True for x in ['hola', 'buenas', 'que tal', 'que onda', 'volví', 'volvi'] if x in message.content.lower()]):
            greetings = [
                'como va?', 'que haces vieja?', 'hola! tanto tiempo!', 'qué haces loco?', 'buongiorno', 'hola', 'hi', 'todo bien?', 'qué gusto verte!', 'Buenas', 'mucho gusto', 'que tal?', 'que onda?', 'que onda', 'que tal', 'soy un botcito...'
            ]

            responses = [
                'cool', 'joya!', 'bien', 'de una', "buenísimo!", "acá andamos...", 'mira vo'
            ]

            channel = message.channel
            await channel.send(random.choice(greetings))

            def check(m):
                return m.content.lower() not in greetings and m.channel == channel

            msg = await self.__bot.wait_for('message', check=check, timeout=10.0)
            await channel.send(random.choice(responses) + " {.author.name}".format(msg))

        elif any([True for x in ['chau', 'nos vemos', 'me voy', 'me retiro'] if x in message.content.lower()]):
            goodbyes = [
                'hasta siempre!', 'chau', 'ciao', 'adiós', 'saludos', 'nos vemos vieja', 'hasta luego!', 'cuidate', 'un abrazo grande!', 'hasta pronto', 'hasta la vista, baby'
            ]

            channel = message.channel
            await channel.send(random.choice(goodbyes))


    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        with open('err.log', 'a') as f:
            if event == 'on_message':
                f.write(f'Unhandled message: {args[0]}\n')
            else:
                raise

