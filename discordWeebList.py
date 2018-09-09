import discord
import pickle
import datetime
import json
import os
import re
import requests
from discord.ext import commands
from asyncio import sleep
from shutil import copyfile

with open('auth.json') as f:
    auth = json.load(f)

TOKEN = auth["auth"]["token"]

bot = commands.Bot(command_prefix='%')


class Entry():
    def __init__(self, id, title, max, url, thumbnail):
        self.id = id
        self.title = title
        self.status = "Planning"
        self.ep_ch = 0
        self.max = max
        self.score = 0.0
        self.url = url
        self.thumbnail = thumbnail
        self.ctx = None

    def __repr__(self):
        return self.title

    def set_title(self, title):
        self.title = title

    def set_ctx(self, ctx):
        self.ctx = ctx

    def set_status(self, status):
        self.status = status

    def set_ep_ch(self, ep_ch):
        self.ep_ch = ep_ch

    def set_score(self, score):
        self.score = score


def save():
    # Backup the savefile
    bck = "backup\\" + datetime.datetime.now().strftime("backup_%H_%M_%d_%m_%Y.bck")
    copyfile('weeblist.p', bck)

    # Save the list to pickle file
    with open('weeblist.p', 'wb') as weeb:
        pickle.dump(list, weeb, protocol=pickle.HIGHEST_PROTOCOL)


def load():
    # Loads the list from a pickle file
    list = {}
    try:
        with open('weeblist.p', 'rb') as weeb:
            list = pickle.load(weeb)
            # Checks if the list is empty, if yes then proceeds to try to load the backup file
            if list is []:
                print("Save file is corrupted.")
            return list
    except FileNotFoundError:
        print("Could not find pickle file. Creating a new one...")
        with open('weeblist.p', 'wb') as weeb:
            pickle.dump(list, weeb, protocol=pickle.HIGHEST_PROTOCOL)
            return list


def edit_entry(entry):
    '''Creates a embed from the specified values'''

    # Creates a embed with the title, redirect url and a color
    embed = discord.Embed(title=entry.title, url=entry.url, color=0xff80ff)

    # Sets the thumbnail
    embed.set_thumbnail(url=entry.thumbnail)

    # Adds a status field
    embed.add_field(name="Status", value=entry.status, inline=False)

    # Checks if it's an anime or manga
    if entry.url.find('anime') is not -1:
        # Sets the field name as "Episodes"
        name = "Episodes"
    else:
        # Sets the field name as "Chapters"
        name = "Chapters"
    embed.add_field(name=name, value=str(entry.ep_ch) + '/' + str(entry.max), inline=False)

    # Adds a score field
    embed.add_field(name="Score", value=entry.score, inline=False)

    # Save the list
    save()

    # Returns the embed
    return embed


async def migrate_entry(ctx, id: int, title: str, url: str, thumbnail: str, status: str, ep_ch: int, max: int,
                        score: float):
    '''Migrates an old entry'''

    # Adds the entry to the dictionary
    list[id] = Entry(id, title, max, url, thumbnail)
    list[id].set_status(status)
    list[id].set_ep_ch(ep_ch)
    list[id].set_score(score)

    embed = edit_entry(list[id])

    # Sends a entry in form of a embeded message
    msg = await bot.send_message(ctx.message.channel, ' ', embed=embed)
    list[id].set_ctx(msg)


def what_is_this_anime(id):
    query = '''
    query($id: Int) {
        Media(id: $id, type: ANIME) {
            id
            type
            title {
                romaji
            }
            episodes
            coverImage {
                large
            }
            siteUrl
        }
    }
    '''

    variables = {
        'id': id
    }

    url = 'https://graphql.anilist.co'

    response = requests.post(url, json={'query': query, 'variables': variables})
    data = response.json()
    data = data["data"]["Media"]

    return data


def what_is_this_manga(id):
    query = '''
    query($id: Int) {
        Media(id: $id, type: MANGA) {
            id
            type
            title {
                romaji
            }
            chapters
            coverImage {
                large
            }
            siteUrl
        }
    }
    '''

    variables = {
        'id': id
    }

    url = 'https://graphql.anilist.co'

    response = requests.post(url, json={'query': query, 'variables': variables})
    data = response.json()
    data = data["data"]["Media"]

    return data


@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name="%help"))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command(pass_context=True)
async def anime(ctx, id: int):
    '''Adds a entry and sends it with the embed'''

    # Deletes the senders message
    await bot.delete_message(ctx.message)

    # Check if entry already exists
    try:
        if list[id]:
            msg = await bot.send_message(ctx.message.channel,
                                         'Entry with the id {} already exists.'.format(list[id].id))
            await sleep(5)
            await bot.delete_message(msg)
            return
    except:
        pass

    # Gets entry through AniList API
    anime = what_is_this_anime(id)
    if anime is None:
        msg = await bot.send_message(ctx.message.channel, "Can not find anime with id {}.".format(list[id]))
        await sleep(5)
        await bot.delete_message(msg)
        return

    # Adds the entry to the dictionary
    list[id] = Entry(anime["id"], anime["title"]["romaji"], anime["episodes"], anime["siteUrl"],
                     anime["coverImage"]["large"])

    embed = edit_entry(list[id])

    # Sends a entry in form of a embeded message
    msg = await bot.send_message(ctx.message.channel, ' ', embed=embed)
    list[id].set_ctx(msg)


@bot.command(pass_context=True)
async def manga(ctx, id: int):
    '''Adds a entry and sends it with the embed'''

    # Deletes the senders message
    await bot.delete_message(ctx.message)

    # Check if entry already exists
    try:
        if list[id]:
            msg = await bot.send_message(ctx.message.channel,
                                         'Entry with the id {} already exists.'.format(list[id].id))
            await sleep(5)
            await bot.delete_message(msg)
            return
    except:
        pass

    # Gets entry through AniList API
    manga = what_is_this_manga(id)
    if manga is None:
        msg = await bot.send_message(ctx.message.channel, "Can not find manga with id {}.".format(list[id]))
        await sleep(5)
        await bot.delete_message(msg)
        return

    # Adds the entry to the dictionary
    list[id] = Entry(manga["id"], manga["title"]["romaji"], manga["chapters"], manga["siteUrl"],
                     manga["coverImage"]["large"])

    embed = edit_entry(list[id])

    # Sends a entry in form of a embeded message
    msg = await bot.send_message(ctx.message.channel, ' ', embed=embed)
    list[id].set_ctx(msg)


@bot.command(pass_context=True)
async def remove(ctx, id: int):
    '''Removes a entry from the list'''

    await bot.delete_message(ctx.message)

    # Checks if the entry exists
    if list[id] is None:
        msg = await bot.send_message(ctx.message.channel, 'Entry does not exist.')
        await sleep(5)
        await bot.delete_message(msg)
        return

    await bot.delete_message(list[id].ctx)
    del list[id]


@bot.command(pass_context=True)
async def score(ctx, entry: int, score):
    '''Updates the score for a entry'''

    # Check if score is a valid value
    try:
        score = float(score)
        pass
    except ValueError:
        msg = await bot.send_message(ctx.message.channel, 'Wrong value.')
        await sleep(5)
        await bot.delete_message(msg)
        return

    # Checks if the entry exists
    if list[entry] is None:
        msg = await bot.send_message(ctx.message.channel, 'Entry does not exist.')
        await sleep(5)
        await bot.delete_message(msg)
        return

    # Gets the entry
    current_entry = list[entry]

    # If desired score is higher than 10, set it to 10
    if score > 10.0:
        score = 10.0

    # Changes the score of that entry
    current_entry.set_score(score)

    # Creates a new embed with the new value
    embed = edit_entry(current_entry)

    # Deletes the senders message
    await bot.delete_message(ctx.message)

    # Edits the message holding the entry
    await bot.edit_message(current_entry.ctx, ' ', embed=embed)


@bot.command(pass_context=True)
async def episode(ctx, entry: int, ep: int):
    '''Updates the episode for a entry'''

    # Checks if the entry exists
    if list[entry] is None:
        msg = await bot.send_message(ctx.message.channel, 'Entry does not exist.')
        await sleep(5)
        await bot.delete_message(msg)
        return

    # Gets the entry
    current_entry = list[entry]

    # If desired episode is higher than max episode count, set it to max episode count
    if current_entry.max > 0:
        if ep > current_entry.max:
            ep = current_entry.max

    # Changes the episode of that entry
    current_entry.set_ep_ch(ep)

    # Creates a new embed with the new value
    embed = edit_entry(current_entry)

    # Deletes the senders message
    await bot.delete_message(ctx.message)

    # Edits the message holding the entry
    await bot.edit_message(current_entry.ctx, ' ', embed=embed)


@bot.command(pass_context=True)
async def chapter(ctx, entry: int, ch: int):
    '''Updates the chapter for a entry'''

    # Checks if the entry exists
    if list[entry] is None:
        msg = await bot.send_message(ctx.message.channel, 'Entry does not exist.')
        await sleep(5)
        await bot.delete_message(msg)
        return

    # Gets the entry
    current_entry = list[entry]

    # If desired chapter is higher than max chapter count, set it to max chapter count
    if current_entry.max > 0:
        if ch > current_entry.max:
            ch = current_entry.max

    # Changes the chapter of that entry
    current_entry.set_ep_ch(ch)

    # Creates a new embed with the new value
    embed = edit_entry(current_entry)

    # Deletes the senders message
    await bot.delete_message(ctx.message)

    # Edits the message holding the entry
    await bot.edit_message(current_entry.ctx, ' ', embed=embed)


@bot.command(pass_context=True)
async def max(ctx, entry: int, max: int):
    '''Updates the max for a entry'''

    # Checks if the entry exists
    if list[entry] is None:
        msg = await bot.send_message(ctx.message.channel, 'Entry does not exist.')
        await sleep(5)
        await bot.delete_message(msg)
        return

    # Gets the entry
    current_entry = list[entry]

    # Changes the max of that entry
    current_entry.set_max(max)

    # Creates a new embed with the new value
    embed = edit_entry(current_entry)

    # Deletes the senders message
    await bot.delete_message(ctx.message)

    # Edits the message holding the entry
    await bot.edit_message(current_entry.ctx, ' ', embed=embed)


@bot.command(pass_context=True)
async def status(ctx, entry: int, status: str):
    '''Updates the status for a entry'''

    # Checks if the entry exists
    if list[entry] is None:
        msg = await bot.send_message(ctx.message.channel, 'Entry does not exist.')
        await sleep(5)
        await bot.delete_message(msg)
        return

    # Gets the entry
    current_entry = list[entry]

    # Changes the status of that entry
    current_entry.set_status(status)

    # Creates a new embed with the new value
    embed = edit_entry(current_entry)

    # Deletes the senders message
    await bot.delete_message(ctx.message)

    # Edits the message holding the entry
    await bot.edit_message(current_entry.ctx, ' ', embed=embed)


@bot.command(pass_context=True)
async def title(ctx, entry: int, title: str):
    '''Updates the title for a entry'''

    # Checks if the entry exists
    if list[entry] is None:
        msg = await bot.send_message(ctx.message.channel, 'Entry does not exist.')
        await sleep(5)
        await bot.delete_message(msg)
        return

    # Gets the entry
    current_entry = list[entry]

    # Changes the title of that entry
    current_entry.set_title(title)

    # Creates a new embed with the new value
    embed = edit_entry(current_entry)

    # Deletes the senders message
    await bot.delete_message(ctx.message)

    # Edits the message holding the entry
    await bot.edit_message(current_entry.ctx, ' ', embed=embed)


@bot.command(pass_context=True)
async def backup(ctx):
    '''Backups the list'''

    await bot.delete_message(ctx.message)
    msg = await bot.send_message(ctx.message.channel, 'Saving...')
    save()
    await bot.wait_until_ready()
    await bot.edit_message(msg, 'Saved')
    await sleep(5)
    await bot.delete_message(msg)


@bot.command(pass_context=True)
async def migrate(ctx, new_channel_id):
    '''Migrate old entries into a new channel'''

    await sleep(1)
    await bot.delete_message(ctx.message)

    try:
        id = int(new_channel_id)
        pass
    except ValueError:
        msg = await bot.send_message(ctx.message.channel, 'Wrong value.')
        await sleep(5)
        await bot.delete_message(msg)
        return

    new_channel = bot.get_channel(new_channel_id)
    if new_channel is None:
        msg = await bot.send_message(ctx.message.channel, "Channel with id {} doesn't exist.".format(new_channel_id))
        await sleep(5)
        await bot.delete_message(msg)
        return

    async for message in bot.logs_from(new_channel, limit=500):
        embed = message.embeds
        for item in embed:
            title = item["title"]
            url = item["url"]
            thumbnail = item["thumbnail"]["url"]
            status = item["fields"][0]["value"]
            ep_ch = item["fields"][1]["value"].split('/')[0]
            max = item["fields"][1]["value"].split('/')[1]
            score = item["fields"][2]["value"]
            id = None

            if url.find('anime') is not -1:
                id = re.search(r'anime/(\d+)', url).groups()[0]
            else:
                id = re.search(r'manga/(\d+)', url).groups()[0]
            id = int(id)

            await migrate_entry(ctx, id, title, url, thumbnail, status, int(ep_ch), int(max), float(score))

    msg = await bot.send_message(ctx.message.channel, 'Done migrating entries.')
    await sleep(5)
    await bot.delete_message(msg)


@bot.command(pass_context=True)
async def id(ctx, keyword: str):
    '''Returns the id that belongs to the title specified'''

    await sleep(2)
    await bot.delete_message(ctx.message)

    matches = ""

    for key, value in list.items():
        if str(value).lower().find(keyword) is not -1:
            matches += "{}: {}\n".format(key, value)

    msg = await bot.send_message(ctx.message.channel, matches)
    await sleep(10)
    await bot.delete_message(msg)

list = load()
bot.run(TOKEN)
