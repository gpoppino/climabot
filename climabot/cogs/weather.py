import os
import pyowm
import json
import datetime
import calendar
import discord
import sys, pathlib

from matplotlib import pyplot as plt
from pyowm.utils.config import get_config_from
from climabot.conf import pyowm_bot_config
from climabot.utils import botlanguage
from discord.ext import commands
from datetime import timezone
from datetime import timedelta
from datetime import date

class Weather(commands.Cog):

    def __init__(self, bot):
        self.__bot = bot
        self.__owm = pyowm.OWM(os.getenv('OPENWEATHER_KEY'), pyowm_bot_config.WEATHER_DEFAULT_CONFIG)
        self.__jsonFilename = "weather_users.json"

        botlanguage.addListener(self)

    def __get_weather_icon(self, detailed_weather_desc):

        w_icon = ""
        if _("nubes rotas") in detailed_weather_desc:
            w_icon = "⛅️"
        elif _("nubes") in detailed_weather_desc:
            w_icon = "☁️"
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

    def __get_pop(self, weather):

        if weather.precipitation_probability == None:
            return 0

        return int(100 * weather.precipitation_probability)

    def __get_forecast_at_place(self, city, type):

        mgr = self.__owm.weather_manager()
        fc = mgr.forecast_at_place(city, type).forecast
        fc.actualize()

        return fc

    def setLanguage(self, lang):
        self.__owm.configuration["language"] = lang[:2]

    @commands.command(name="tiempo", help="Muestra diferentes variables relacionadas al clima actual del día para la ciudad seleccionada")
    async def weather(self, ctx, *args):

        city = ' '.join(args)
        if len(city) == 0:
            city = self.__get_city_for_user(ctx.author.id)

        if city == '':
            await ctx.send(_('No tenés ciudad definida. Por favor, usá el comando ".setup" para empezar'))
            return

        mgr = self.__owm.weather_manager()
        observation = mgr.weather_at_place(city)
        w = observation.weather

        detailed = w.detailed_status
        sunrise = datetime.datetime.fromtimestamp(w.sunrise_time(), tz=timezone(timedelta(hours=-3)))
        sunset = datetime.datetime.fromtimestamp(w.sunset_time(), tz=timezone(timedelta(hours=-3)))
        temp = w.temperature('celsius')['temp']
        temp_max = w.temperature('celsius')['temp_max']
        temp_min = w.temperature('celsius')['temp_min']
        humidity = w.humidity
        wind_speed = w.wind()['speed']
        clouds = w.clouds
        pressure = w.pressure['press']
        sunrise_minute = "0" + str(sunrise.minute) if len(str(sunrise.minute)) == 1 else str(sunrise.minute)
        sunset_minute = "0" + str(sunset.minute) if len(str(sunset.minute)) == 1 else str(sunset.minute)

        await ctx.send(detailed[0].upper() + detailed[1:] + " " + "(" + str(self.__get_pop(w)) + "%)" + " - " + _('Temperatura actual') + " " + str(temp) + "°C, " +
                        _('máxima') + "  " + str(temp_max) + "°C, " + _('mínima') + "  " + str(temp_min) + "°C - " +
                        _('Humedad') + " " + str(humidity) + "% - " + _('Velocidad del viento') + " " + str(wind_speed) +
                        " m/s - " + _('Salida del 🌞') + "  " + str(sunrise.hour) + ":" + sunrise_minute + " " +
                        _('y')  +  " " + _('Puesta del 🌞') + "  " + str(sunset.hour) + ":" + sunset_minute +
                        " - " + _('Presión atmosférica') + "  " + str(pressure) + " hpa - " + _('Nubes') + " " + str(clouds) + "%")


    @commands.command(name="pronostico", help="Muestra el pronostico del tiempo de los próximos 5 días")
    async def forecast(self, ctx, *args):

        city = ' '.join(args)
        if len(city) == 0:
            city = self.__get_city_for_user(ctx.author.id)

        if city == '':
            await ctx.send(_('No tenés ciudad definida. Por favor, usá el comando ".setup" para empezar'))
            return

        fc = self.__get_forecast_at_place(city, 'daily')
        w_str = ""
        for weather in fc:
            f_date = datetime.datetime.fromtimestamp(weather.reference_time(), tz=timezone(timedelta(hours=-3)))
            detailed = weather.detailed_status
            w_date = calendar.day_abbr[f_date.weekday()] + " " + str(f_date.day)
            if date.today() == datetime.date(f_date.year, f_date.month, f_date.day):
                w_date = _('Hoy')

            w_str += w_date[0].upper() + w_date[1:] + " " + detailed[0].upper() +  detailed[1:] + " " + self.__get_weather_icon(detailed) + " " + "(" + str(self.__get_pop(weather)) + "%)" + " - "

        await ctx.send(w_str[:-2])


    @commands.command(name="3h", help="Muestra el pronóstico de la temperatura y probabilidad de lluvia cada 3 horas por las próximas 24 horas")
    async def three_hour_forecast(self, ctx, *args):

        city = ' '.join(args)
        if len(city) == 0:
            city = self.__get_city_for_user(ctx.author.id)

        if city == '':
            await ctx.send(_('No tenés ciudad definida. Por favor, usá el comando ".setup" para empezar'))
            return

        sample = 0
        time_data, temp_data, pop_data = [], [], []
        fc = self.__get_forecast_at_place(city, '3h')
        for weather in fc:
            date_and_time = datetime.datetime.fromtimestamp(weather.reference_time(), tz=timezone(timedelta(hours=-3)))
            time_data.append(date_and_time)
            temp_data.append(weather.temperature('celsius')['temp'])
            pop_data.append(self.__get_pop(weather))

            if sample >= (24 / 3):
                break
            sample += 1

        fig, ax = plt.subplots(2, 1)
        ax[0].plot(time_data, temp_data)
        ax[0].grid(True)
        ax[0].set_ylabel(_("Temperatura (°C)"))
        ax[1].plot(time_data, pop_data)
        ax[1].fill_between(time_data, pop_data)
        ax[1].grid(True)
        ax[1].set_ylabel(_("Probabilidad de lluvia (%)"))
        ax[1].set_xlabel(_("Fecha y Hora"))
        ax[1].set_ylim(0, 100)
        fig.suptitle(_("Pronóstico cada 3 horas en ") + city[0].upper() + city[1:-3])
        fig.autofmt_xdate()
        plt.savefig("temp.png", format="png")

        embed = discord.Embed()
        file = discord.File("temp.png", filename="temp.png")
        embed.set_image(url="attachment://temp.png")
        await ctx.send(file=file, embed=embed)

    @commands.command(help="Permite configurar la ciudad y país para el usuario")
    async def setup(self, ctx, *args):

        users = self.__get_users_from_json()
        if len(args) == 0:
            if str(ctx.author.id) in users.keys():
                await ctx.send(_('Tu ciudad actual es') + ": " + self.__get_city_for_user(ctx.author.id) + ". " +
                                 _('Si querés cambiar de ciudad pasame el nombre también.'))
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
