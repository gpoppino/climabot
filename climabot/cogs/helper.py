from discord.ext import commands

class Helper(commands.Cog):

    def __init__(self, bot):
        self.__bot = bot

    @commands.command(name="ayuda", help="Muestra la ayuda de los comandos")
    async def showHelp(self, ctx, *args):
        cmdstr = ""
        for cog in self.__bot.cogs:
            commands = self.__bot.get_cog(cog).get_commands()
            for c in commands:
                if len(args) > 0:
                    if c.name == args[0]:
                        await ctx.send(c.name + ": " + c.help)
                        break
                else:
                    cmdstr += c.name + " "

        if len(cmdstr) != 0:
            await ctx.send("Comandos disponibles: " + cmdstr)

