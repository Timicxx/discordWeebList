import discord
from discord.ext import commands
from asyncio import sleep
import json
from modules.Weeb import *
from modules.TraceMoe import TraceMoe

#region Definitions
with open('auth.json', 'rb') as f:
    auth = json.load(f)
DISCORD_TOKEN = auth["auth"]["discord_token"]
DEBUG_CHANNEL = "487923259057111040"
#endregion


#region Objects
bot = commands.Bot(command_prefix='%')
tracemoe_bot = TraceMoe(bot)
weeb_client = Manager(AnimeManager(), MangaManager())
#endregion


#region Discord Events
@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name="%help"))
    await weeb_client.list_all(bot, DEBUG_CHANNEL)
    tracemoe_status = tracemoe_bot.initialize()
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
    await tracemoe_bot.getSource(ctx)

@bot.command(pass_context=True)
async def sauce(ctx):
    '''Martin 2.0'''
    pass

@bot.command(pass_context=True)
async def yt2mp3(ctx):
    '''Download mp3 with ID3 Tags from a YouTube link'''
    pass
#endregion

# Start the bot
bot.run(DISCORD_TOKEN)
