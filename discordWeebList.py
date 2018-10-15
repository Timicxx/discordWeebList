import discord
from discord.ext import commands
from asyncio import sleep
import json
from modules.Weeb import *
from modules.WhatAnimeGa import WhatAnimeGa

#region Definitions
with open('auth.json', 'rb') as f:
    auth = json.load(f)
DISCORD_TOKEN = auth["auth"]["discord_token"]
WHATANIMEGA_TOKEN = auth["auth"]["whatanimega_token"]
DEBUG_CHANNEL = "487923259057111040"
#endregion


#region Objects
bot = commands.Bot(command_prefix='%')
whatAnimeBot = WhatAnimeGa(WHATANIMEGA_TOKEN, bot)
weeb_client = Manager(AnimeManager(), MangaManager())
#endregion


#region Discord Events
@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name="%help"))
    await weeb_client.list_all(bot, DEBUG_CHANNEL)
    whatAnimeGaStatus = whatAnimeBot.initialize()
    print('------')
    print('DISCORD BOT')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print('WHATANIME.GA')
    print('Logged in as')
    print(whatAnimeGaStatus["email"])
    print(whatAnimeGaStatus["user_id"])
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
async def whatanime(ctx):
    '''Find source of an anime screenshot'''
    await whatAnimeBot.getSource(ctx)

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
