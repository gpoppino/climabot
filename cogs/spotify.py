from discord.ext import commands
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import os, re

class Spotify(commands.Cog):

    def __init__(self, bot):
        self.__bot = bot
        self.__sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=os.getenv("SPOTIFY_CLIENT_ID"), client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")))

    def __get_artists_names(self, artists):
        artists_names = ''
        for artist in artists:
            artists_names += artist['name'] + ", "
        artists_names = artists_names.rstrip(", ")

        return artists_names.strip()

    async def __show_track_info(self, track, message):
        minutes = int(track['duration_ms'] / 1000 / 60)
        _seconds = int((track['duration_ms'] / 1000) - (minutes * 60))
        seconds = str(_seconds)
        if _seconds < 10:
            seconds = "0" + str(_seconds)

        artists_names = self.__get_artists_names(track['artists'])
        await message.channel.send("🎵 " + _("Título") + ": " + track['name'] + " - " + _("Artistas") + ": " + artists_names + " - " + _("Album") + ": " +
            track['album']['name'] + " - " + _("Duración") + ": " + str(minutes) + ":" + seconds + " 🎵 " + track['external_urls']['spotify'])

    async def __show_album_info(self, album, message):
        artists_names = self.__get_artists_names(album['artists'])
        await message.channel.send("🎵 " + _("Título") + ": " + album['name'] + " - " + _("Artistas") + ": " + artists_names + " - " + _("Discográfica") + ": " + album['label'] +
            " - " + _("Fecha de lanzamienta") + ": " + album['release_date'] + " 🎵 " + album['external_urls']['spotify'])

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.__bot.user:
            return

        p = re.compile(".*spotify(:.*:.*).*")
        result = p.match(message.content)

        if not result:
            return

        g = result.group(1).split(":")
        type = g[1]
        id = g[2]

        if type == "track":
            track = self.__sp.track(id)
            await self.__show_track_info(track, message)
        elif type == "album":
            album = self.__sp.album(id)
            await self.__show_album_info(album, message)
        else:
            await message.channel.send(_("No encontrado!"))

