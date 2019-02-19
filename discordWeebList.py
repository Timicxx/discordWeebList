import discord
from discord.ext import commands
from asyncio import sleep
import json
from modules.Weeb import *
from modules.TraceMoe import TraceMoe
from modules.discord_yt2mp3 import yt2mp3

#region Definitions
with open('auth.json', 'rb') as f:
    auth = json.load(f)
DISCORD_TOKEN = auth["auth"]["discord_token"]
CHANNEL_ID = auth["channel"]["channel_id"]
#endregion


#region Objects
bot = commands.Bot(command_prefix='%')
tracemoe_client = TraceMoe(bot)
yt2mp3_client = yt2mp3(bot)
weeb_client = Manager(AnimeManager(), MangaManager())
#endregion


#region Discord Events
@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name="github.timbobimbo.club | %help"))
    await weeb_client.init(bot, CHANNEL_ID)
    tracemoe_status = tracemoe_client.initialize()
    print('------')
    print('DISCORD BOT')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print('TRACE.MOE')
    print('Logged in as')
    print(tracemoe_status["email"])
    print('------')

#endregion


#region Discord Commands
@bot.command(pass_context=True)
async def weeb(ctx):
    '''Manage Rafal's Weeb List'''
    await weeb_client.menu(ctx)

@bot.command()
async def backup():
    '''Backup Weeb List'''
    await weeb_client.dump_to_json()

@bot.command(pass_context=True)
async def trace(ctx):
    '''Find source of an anime screenshot'''
    await tracemoe_client.getSource(ctx)

@bot.command(pass_context=True)
async def sauce(ctx):
    '''Martin 2.0'''
    pass
    
@bot.command(pass_context=True)
async def yt2mp3(ctx, yt: str, artist: str, title: str, album: str, cover_art: str):
    '''Download mp3 with ID3 Tags from a YouTube link'''
    await yt2mp3_client.download_m(ctx, yt, artist, title, album, cover_art)
#endregion

# Start the bot
bot.run(DISCORD_TOKEN)
