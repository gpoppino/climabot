import os
import pyowm
import json
import datetime

from discord.ext import commands
from datetime import timezone
from datetime import timedelta
from datetime import date


class Weather(commands.Cog):
    def __init__(self, bot):
        self.__bot = bot
        self.__owm = pyowm.OWM(os.getenv('OPENWEATHER_KEY'), language='es')
        self.__jsonFilename = "weather_users.json"

    def __get_weather_icon(self, detailed_weather_desc):

        w_icon = ""
        if "nubes" in detailed_weather_desc:
            w_icon = "⛅️"
        elif "lluvia" in detailed_weather_desc:
            w_icon = "🌧"
        elif "claro" in detailed_weather_desc:
            w_icon = "🌞"
        elif "neblina" in detailed_weather_desc:
            w_icon = "🌫"
        elif "nieve" in detailed_weather_desc:
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

    @commands.command(name='tiempo')
    async def currentWeather(self, ctx, *args):

        city = ' '.join(args)
        print("CITY == " + city)
        if len(city) == 0:
            city = self.__get_city_for_user(ctx.author.id)

        print(city)
        if city == '':
            await ctx.send('No tenés ciudad definida. Por favor, usá el comando ".setup" para empezar')
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

        await ctx.send(detailed[0].upper() + detailed[1:] + " - Temperatura actual " + str(temp) + "°C, máxima " + str(temp_max) + "°C, mínima " + str(temp_min) + "°C -  Humedad " + str(humidity) + "% - Velocidad del viento " + str(wind_speed) + " m/s - Salida del 🌞 " + str(sunrise.hour) + ":" + str(sunrise.minute) + " y Puesta del 🌞 " + str(sunset.hour) + ":" + str(sunset.minute) + " - Presión atmosférica " + str(pressure) + " hpa - Nubes " + str(clouds) + "%")


    @commands.command(name='pronostico')
    async def _forecast(self, ctx, *args):

        my_limit = 1
        num = {'un': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5, 'seis': 6, '1': 2, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, 'mañana': 1, 'pasado': 2}
        when = [x for x in args if x in list(num.keys())]
        if len(when) > 0:
            if any([True for x in args if x in ['dia', 'día', 'dias', 'días', 'pasado', 'mañana']]):
                my_limit = num[when[0]]

        city = self.__get_city_for_user(ctx.author.id)
        if len(city) == 0 and len(args) == 0:
            await ctx.send('No tenés ciudad asignada! Podés pasarme la ciudad como parámetro o usar el comando ".setup"')
            return

        if len(city) == 0 and len(args) != 0:
            city = []
            for x in args:
                city.append(x)
                if x.find(',') != -1:
                    city = ' '.join(city)
                    break

        fc = self.__owm.daily_forecast(city, limit=my_limit)
        weekday = {0: 'Lun', 1: 'Mar', 2:'Mie', 3:'Jue', 4:'Vie', 5:'Sab', 6:'Dom'}

        w_str = ""
        for weather in fc.get_forecast().get_weathers():
            f_date = datetime.datetime.fromtimestamp(weather.get_reference_time(), tz=timezone(timedelta(hours=-3)))
            detailed = weather.get_detailed_status()
            w_date = weekday[f_date.weekday()] + " " + str(f_date.day)
            if date.today() == datetime.date(f_date.year, f_date.month, f_date.day):
                w_date = "Hoy"
            w_str += w_date + " " + detailed[0].upper() +  detailed[1:] + " " + self.__get_weather_icon(detailed) + " - "

        await ctx.send(w_str[:-2])

    @commands.command()
    async def setup(self, ctx, *args):

        users = self.__get_users_from_json()
        print(users)
        if len(args) == 0:
            print(ctx.author.id)
            print(users.keys())
            if str(ctx.author.id) in users.keys():
                await ctx.send("Tu ciudad actual es: '" + self.__get_city_for_user(ctx.author.id) + "'. Si querés cambiar de ciudad pasame el nombre también.")
            else:
                await ctx.send("Tenés que pasarme la ciudad en formato 'nombre de ciudad,pais'. Por ejemplo: sunchales,ar")
            return

        if str(ctx.author.id) in users.keys():
            await ctx.send("Ya tenés configurada la ciudad '" + self.__get_city_for_user(ctx.author.id) + "'. Sobrescribir? (si/no)")

            def check(m):
                return m.content.lower() in ['si', 's', 'yes', 'no', 'n'] and m.author == ctx.author

            msg = await self.__bot.wait_for('message', check=check, timeout=60.0)
            if msg.content.lower() in ['s', 'si', 'yes', 'sí']:
                self.__add_user_to_json(ctx.author.id, args)
                await ctx.send("Actualizado")
            else:
                await ctx.send('No toco nada entonces')
        else:
            self.__add_user_to_json(ctx.author.id, args)
            await ctx.send("Actualizado")


