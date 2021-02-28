import os
import gettext
import locale

from climabot.utils.language import botlanguage
from discord.ext import commands

class Language(commands.Cog):

    def __init__(self, bot):
        self.__bot = bot

    @commands.command("idioma")
    async def lang(self, ctx, *args):
        if len(args) == 0:
            return

        lang = args[0]
        if botlanguage.isSupportedLanguage(lang):
            if botlanguage.setLanguage(lang):
                await ctx.send(_('Actualizado'))
            else:
                await ctx.send(_('Idioma no encontrado'))
