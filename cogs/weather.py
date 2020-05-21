import os
import pyowm
import json
import datetime
import calendar
import gettext
import locale

from discord.ext import commands
from datetime import timezone
from datetime import timedelta
from datetime import date

gettext.install('climabot', localedir='locales')

class Weather(commands.Cog):

    def __init__(self, bot):
        self.__bot = bot
        self.__owm = pyowm.OWM(os.getenv('OPENWEATHER_KEY'), language=os.getenv('LANG')[:2])
        self.__jsonFilename = "weather_users.json"

        self.__setLang(os.getenv('LANG')[:5])

    def __get_weather_icon(self, detailed_weather_desc):

        w_icon = ""
        if _("nubes") in detailed_weather_desc:
            w_icon = "⛅️"
        elif _("lluvia") in detailed_weather_desc:
            w_icon = "🌧"
        elif _("claro") in detailed_weather_desc:
            w_icon = "🌞"
        elif _("neblina") in detailed_weather_desc:
            w_icon = "🌫"
        elif _("nieve") in detailed_weather_desc:
            w_icon = "🌨"

        return w_icon

    def __add_user_to_json(self, id, city):
        users = self.__get_users_from_json()
        users[str(id)] = ' '.join(city)

        j = json.dumps(users)
        with open(self.__jsonFilename, 'w') as f:
            f.write(j)
            f.close()

    def __get_users_from_json(self):
        users = {}
        try:
            with open(self.__jsonFilename, 'r') as f:
                users = json.load(f)
                f.close()
        except:
            print(f'File {self.__jsonFilename} not found')

        return users

    def __get_city_for_user(self, id):
        _id = str(id)
        users = self.__get_users_from_json()
        city = ''
        if _id in users.keys():
            city = users[_id]
        return city

    def __getSupportedLanguages(self):
        dirs = [ x for x in os.listdir('locales') if os.path.isdir(os.path.join('locales', x)) ]
        return dirs

    def __setLang(self, lang):

        languages = [ x.lower() for x in self.__getSupportedLanguages() ]
        if lang.lower() in languages:
            lang = lang[:2] + '_' + lang[-2:].upper()
            t = gettext.translation('climabot', localedir='locales', languages=[lang])
            t.install()

            self.__owm = pyowm.OWM(os.getenv('OPENWEATHER_KEY'), language=lang[:2])

            locale.setlocale(locale.LC_ALL, (lang, locale.getpreferredencoding()))

            return True
        return False

    @commands.command(name="tiempo")
    async def weather(self, ctx, *args):

        city = ' '.join(args)
        if len(city) == 0:
            city = self.__get_city_for_user(ctx.author.id)

        if city == '':
            await ctx.send(_('No tenés ciudad definida. Por favor, usá el comando ".setup" para empezar'))
            return

        observation = self.__owm.weather_at_place(city)
        w = observation.get_weather()

        detailed = w.get_detailed_status()
        sunrise = datetime.datetime.fromtimestamp(w.get_sunrise_time(), tz=timezone(timedelta(hours=-3)))
        sunset = datetime.datetime.fromtimestamp(w.get_sunset_time(), tz=timezone(timedelta(hours=-3)))
        temp = w.get_temperature('celsius')['temp']
        temp_max = w.get_temperature('celsius')['temp_max']
        temp_min = w.get_temperature('celsius')['temp_min']
        humidity = w.get_humidity()
        wind_speed = w.get_wind()['speed']
        clouds = w.get_clouds()
        pressure = w.get_pressure()['press']

        await ctx.send(detailed[0].upper() + detailed[1:] + " - " + _('Temperatura actual') + " " + str(temp) + "°C, " + _('máxima') + "  " + str(temp_max) + "°C, " + _('mínima') + "  " + str(temp_min) + "°C - " + _('Humedad') + " " + str(humidity) + "% - " + _('Velocidad del viento') + " " + str(wind_speed) + " m/s - " + _('Salida del 🌞') + "  " + str(sunrise.hour) + ":" + str(sunrise.minute) + " " + _('y')  +  " " + _('Puesta del 🌞') + "  " + str(sunset.hour) + ":" + str(sunset.minute) + " - " + _('Presión atmosférica') + "  " + str(pressure) + " hpa - " + _('Nubes') + " " + str(clouds) + "%")


    @commands.command(name="pronostico")
    async def forecast(self, ctx, *args):

        my_limit = 1
        num = {_('un'): 1, _('dos'): 2, _('tres'): 3, _('cuatro'): 4, _('cinco'): 5, _('seis'): 6, '1': 2, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, _('hoy'): 1, _('mañana'): 2, _('pasado'): 3}
        when = [x for x in args if x in list(num.keys())]
        if len(when) > 0:
            if any([True for x in args if x in [_('dia'), _('día'), _('dias'), _('días'), _('pasado'), _('mañana'), _('hoy')]]):
                my_limit = num[when[0]]

        city = self.__get_city_for_user(ctx.author.id)
        if len(city) == 0 and len(args) == 0:
            await ctx.send(_('No tenés ciudad asignada! Podés pasarme la ciudad como parámetro o usar el comando ".setup"'))
            return

        if len(city) == 0 and len(args) != 0:
            city = []
            for x in args:
                city.append(x)
                if x.find(',') != -1:
                    city = ' '.join(city)
                    break

        fc = self.__owm.daily_forecast(city, limit=my_limit)
        w_str = ""
        for weather in fc.get_forecast().get_weathers():
            f_date = datetime.datetime.fromtimestamp(weather.get_reference_time(), tz=timezone(timedelta(hours=-3)))
            detailed = weather.get_detailed_status()
            w_date = calendar.day_abbr[f_date.weekday()] + " " + str(f_date.day)
            if date.today() == datetime.date(f_date.year, f_date.month, f_date.day):
                w_date = _('Hoy')
            w_str += w_date[0].upper() + w_date[1:] + " " + detailed[0].upper() +  detailed[1:] + " " + self.__get_weather_icon(detailed) + " - "

        await ctx.send(w_str[:-2])

    @commands.command()
    async def setup(self, ctx, *args):

        users = self.__get_users_from_json()
        if len(args) == 0:
            if str(ctx.author.id) in users.keys():
                await ctx.send(_('Tu ciudad actual es') + ": " + self.__get_city_for_user(ctx.author.id) + ". " + _('Si querés cambiar de ciudad pasame el nombre también.'))
            else:
                await ctx.send(_('Tenés que pasarme la ciudad en formato "nombre de ciudad,pais". Por ejemplo: sunchales,ar'))
            return

        if str(ctx.author.id) in users.keys():
            await ctx.send(_('Ya tenés configurada la ciudad') + " " + self.__get_city_for_user(ctx.author.id) + ". " + _('Sobrescribir? (si/no)'))

            def check(m):
                return m.content.lower() in ['si', 's', 'yes', 'no', 'n'] and m.author == ctx.author

            msg = await self.__bot.wait_for('message', check=check, timeout=60.0)
            if msg.content.lower() in ['s', 'si', 'yes', 'sí']:
                self.__add_user_to_json(ctx.author.id, args)
                await ctx.send(_('Actualizado'))
            else:
                await ctx.send(_('No toco nada entonces'))
        else:
            self.__add_user_to_json(ctx.author.id, args)
            await ctx.send(_('Actualizado'))

    @commands.command("idioma")
    async def lang(self, ctx, *args):
        if len(args) == 0:
            return

        if self.__setLang(args[0]):
            await ctx.send(_('Actualizado'))
        else:
            await ctx.send(_('Idioma no encontrado'))
