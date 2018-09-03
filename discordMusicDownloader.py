from __future__ import unicode_literals
from urllib import request
from bs4 import BeautifulSoup as BS
import youtube_dl
import os
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

import discord
from discord.ext import commands
from asyncio import sleep

bot = commands.Bot(command_prefix='^')

TOKEN = "NDU1NDEyNTczMTQwMTU2NDE2.Dm2rAA.FVm9M8pwKYH3GLjBQmnSbXJu-VI"

class Song:
    def __init__(self, title, artist, cover_art=None):
        self.title = title
        self.artist = artist
        if self.title.find('-') is not -1:
            self.title = self.title.split(' - ')[1]
            self.artist = self.title.split(' - ')[0]
        self.album = self.title.split('(')[0]
        self.full_song = "{} - {}".format(self.artist, self.title)
        self.cover = "{} - {}.jpg".format(self.artist, self.title)
        self.mp3 = "{} - {}.mp3".format(self.artist, self.title)

        if cover_art is not None:
            self.cover = cover_art

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

def download_sc(sc, info):
    html = request.urlopen(sc).read()
    soup = BS(html, 'html.parser')
    for link in soup.find_all('div'):
        for img in link.find_all('img'):
            new_link = img.get("src")
            if new_link.find('gif') != -1:
                continue
            request.urlretrieve(new_link, info.cover)

def get_info(sc):
    html = request.urlopen(sc).read()
    soup = BS(html, 'html.parser')

    song_info = soup.title.text.split('|')[0]

    title = song_info.split('by')[0][:-1]
    artist = song_info.split('by')[1][1:-1]

    song = Song(title, artist)
    return song

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

def finish(info):
    os.remove(info.cover)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')	

@bot.command(pass_context=True)
async def download(ctx, yt: str, sc: str):
    await bot.delete_message(ctx.message)
    info = get_info(sc)
    download_sc(sc, info)
    download_yt(yt, info)
    tags(info)
    finish(info)
    await bot.send_file(ctx.message.channel, 'downloads\\' + info.mp3)
	
bot.run(TOKEN)
