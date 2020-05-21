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

        if any([True for x in [_('hola'), _('buenas'), _('que tal'), _('que onda'), _('volví'), _('volvi')] if x in message.content.lower()]):
            greetings = [
                _('como va?'), _('que haces vieja?'), _('hola! tanto tiempo!'), _('qué haces loco?'), _('hola'), _('todo bien?'), _('qué gusto verte!'), _('buenas'), _('mucho gusto'), _('que tal?'), _('que onda?'), _('que onda'), _('que tal')
            ]

            responses = [
                'cool', _('joya!'), _('bien'), _('de una'), _('buenísimo!'), _('acá andamos...')
            ]

            channel = message.channel
            await channel.send(random.choice(greetings))

            def check(m):
                return m.content.lower() not in greetings and m.channel == channel

            msg = await self.__bot.wait_for('message', check=check, timeout=10.0)
            await channel.send(random.choice(responses) + " {.author.name}".format(msg))

        elif any([True for x in [_('chau'), _('nos vemos'), _('me voy'), _('me retiro')] if x in message.content.lower()]):
            goodbyes = [
                _('hasta siempre!'), _('chau'), _('adiós'), _('saludos'), _('nos vemos vieja'), _('hasta luego!'), _('cuidate'), _('un abrazo grande!'), _('hasta pronto'), _('hasta la vista, baby')
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

