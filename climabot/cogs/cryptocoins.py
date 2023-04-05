import json
import requests

from discord.ext import commands


API_URL_BASE = 'https://api.blockchain.com/v3/exchange/'

class CryptoCoins(commands.Cog):

    @commands.command(name="precio", help="Muestra el precio de la criptomoneda seleccionada")
    async def get_crypto_price(self, ctx, *args):

        if len(args) != 2:
            return

        param = '-'.join(args).upper()
        api_url = '{0}tickers/{1}'.format(API_URL_BASE, param)
        response = requests.get(api_url)

        if response.status_code == 200:
            price = json.loads(response.content.decode('utf-8'))
            await ctx.send(_("Precio actual") + ": $" + str(price['last_trade_price']) + " | " + _("Precio 24h") + ": $" + str(price['price_24h']))
        else:
            await ctx.send(_("Símbolo no encontrado!"))
