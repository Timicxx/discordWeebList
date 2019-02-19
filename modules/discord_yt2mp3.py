import youtube_dl
import os
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import discord
from discord.ext import commands
from asyncio import sleep

class Song:
    def __init__(self, title, artist, cover_art=None, album=None):
        self.title = title
        self.artist = artist
        if self.title.find('-') is not -1:
            self.title = self.title.split(' - ')[1]
            self.artist = self.title.split(' - ')[0]
        self.album = album
        if album is None:
            self.album = self.title.split('(')[0]
        self.full_song = "{} - {}".format(self.artist, self.title)
        self.cover = "{} - {}.jpg".format(self.artist, self.title)
        self.mp3 = "{} - {}.mp3".format(self.artist, self.title)

        if cover_art is not None:
            self.cover = cover_art

class yt2mp3:
    def __init__(self, bot):
        self.bot = bot
    
    @staticmethod
    def download_yt(yt, info):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads//' + info.full_song + '.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([yt])
    
    @staticmethod
    def tags(info):
        image = open(info.cover, 'rb').read()

        audio = EasyID3('downloads\\' + info.mp3)
        audio['artist'] = info.artist
        audio['title'] = info.title
        audio['album'] = info.album
        audio['albumartist'] = info.artist
        audio.save(v2_version=3)

        audio = ID3('downloads\\' + info.mp3)
        audio.add(APIC(3, 'image/jpeg', 3, 'Front cover', image))
        audio.save(v2_version=3)
    
    @staticmethod
    def finish(info):
        os.remove(info.cover)

    async def download_m(ctx, yt, artist, title, album, cover_art):
        await self.bot.delete_message(ctx.message)
        info = Song(title, artist, cover_art, album)
        self.download_yt(yt, info)
        self.tags(info)
        self.finish(info)
        await self.bot.send_file(ctx.message.channel, 'downloads\\' + info.mp3)
