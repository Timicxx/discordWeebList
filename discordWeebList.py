import discord
import pickle
from discord.ext import commands
from asyncio import sleep

bot = commands.Bot(command_prefix='^')

TOKEN = "NDU1NDEyNTczMTQwMTU2NDE2.Dm2rAA.FVm9M8pwKYH3GLjBQmnSbXJu-VI"
	
class Entry():
    def __init__(self, title, status, ep_ch, max, score, url, thumbnail, ctx=None):
        self.title = title
        self.status = status
        self.ep_ch = ep_ch
        self.max = max
        self.score = score
        self.url = url
        self.thumbnail = thumbnail
        self.ctx = ctx

def save():
    # Save the list to pickle file
    with open('weeblist.p', 'wb') as weeb:
        pickle.dump(list, weeb, protocol=pickle.HIGHEST_PROTOCOL)

def load():
    # Loads the list from a pickle file
    list = {}
    try:
        with open('weeblist.p', 'rb') as weeb:
            list = pickle.load(weeb)
            return list
    except FileNotFoundError:
        print("Could not find pickle file. Creating a new one...")
        with open('weeblist.p', 'wb') as weeb:
            pickle.dump(list, weeb, protocol=pickle.HIGHEST_PROTOCOL)
            return list

def edit_entry(entry):
    '''Creates a embed from the specified values'''

    # Creates a embed with the title, redirect url and a color
    embed=discord.Embed(title=entry.title, url=entry.url, color=0xff80ff)
	
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

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
	
@bot.command(pass_context=True)
async def add_entry(ctx, title: str, status: str, ep_ch: int, max: int, score: float, url: str, thumbnail: str):
    '''Adds a entry and sends it with the embed'''
    
    if list[title]:
        await bot.send_message(ctx.message.channel, 'Entry with the same title already exists.')
        return
    # Adds the entry to the dictionary
    list[title] = Entry(title, status, ep_ch, max, score, url, thumbnail)
	
    embed = edit_entry(list[title])
	
    # Deletes the senders message
    await bot.delete_message(ctx.message)
	
    # Sends a entry in form of a embeded message
    msg = await bot.send_message(ctx.message.channel, ' ', embed=embed)
    list[title].ctx = msg

@bot.command(pass_context=True)
async def score(ctx, entry: str, score):
    '''Updates the score for a entry'''
	
    # Check if score is a valid value
    try:
        score = float(score)
        pass 
    except ValueError:
        await bot.send_message(ctx.message.channel, 'Wrong value.')
        return
	
    # Checks if the entry exists
    if list[entry] is None:
        await bot.send_message(ctx.message.channel, 'Entry does not exist.')
        return
    
    # Gets the entry
    current_entry = list[entry]
	
    # If desired score is higher than 10, set it to 10
    if score > 10:
        score = 10
	
    # Changes the score of that entry
    current_entry.score = score

    # Creates a new embed with the new value
    embed = edit_entry(current_entry)
	
    # Deletes the senders message
    await bot.delete_message(ctx.message)
	
    # Edits the message holding the entry
    await bot.edit_message(current_entry.ctx, ' ', embed=embed)

@bot.command(pass_context=True)
async def episode(ctx, entry: str, ep: int):
    '''Updates the episode for a entry'''
	
    # Checks if the entry exists
    if list[entry] is None:
        await bot.send_message(ctx.message.channel, 'Entry does not exist.')
        return
    
    # Gets the entry
    current_entry = list[entry]
	
    # If desired episode is higher than max episode count, set it to max episode count
    if current_entry.max is not None:
        if ep > current_entry.max:
            ep = current_entry.max
	
    # Changes the episode of that entry
    current_entry.ep_ch = ep

    # Creates a new embed with the new value
    embed = edit_entry(current_entry)
	
    # Deletes the senders message
    await bot.delete_message(ctx.message)
	
    # Edits the message holding the entry
    await bot.edit_message(current_entry.ctx, ' ', embed=embed)

@bot.command(pass_context=True)
async def chapter(ctx, entry: str, ch: int):
    '''Updates the chapter for a entry'''
	
    # Checks if the entry exists
    if list[entry] is None:
        await bot.send_message(ctx.message.channel, 'Entry does not exist.')
        return
    
    # Gets the entry
    current_entry = list[entry]
	
    # If desired chapter is higher than max chapter count, set it to max chapter count
    if current_entry.max is not None:
        if ch > current_entry.max:
            ch = current_entry.max
	
    # Changes the chapter of that entry
    current_entry.ep_ch = ch

    # Creates a new embed with the new value
    embed = edit_entry(current_entry)
	
    # Deletes the senders message
    await bot.delete_message(ctx.message)
	
    # Edits the message holding the entry
    await bot.edit_message(current_entry.ctx, ' ', embed=embed)
	
@bot.command(pass_context=True)
async def max(ctx, entry: str, max: int):
    '''Updates the max for a entry'''
	
    # Checks if the entry exists
    if list[entry] is None:
        await bot.send_message(ctx.message.channel, 'Entry does not exist.')
        return
    
    # Gets the entry
    current_entry = list[entry]
	
    # Changes the max of that entry
    current_entry.max = max

    # Creates a new embed with the new value
    embed = edit_entry(current_entry)
	
    # Deletes the senders message
    await bot.delete_message(ctx.message)
	
    # Edits the message holding the entry
    await bot.edit_message(current_entry.ctx, ' ', embed=embed)
	
@bot.command(pass_context=True)
async def status(ctx, entry: str, status: str):
    '''Updates the status for a entry'''
	
    # Checks if the entry exists
    if list[entry] is None:
        await bot.send_message(ctx.message.channel, 'Entry does not exist.')
        return
    
    # Gets the entry
    current_entry = list[entry]
	
    # Changes the status of that entry
    current_entry.status = status

    # Creates a new embed with the new value
    embed = edit_entry(current_entry)
	
    # Deletes the senders message
    await bot.delete_message(ctx.message)
	
    # Edits the message holding the entry
    await bot.edit_message(current_entry.ctx, ' ', embed=embed)

@bot.command(pass_context=True)
async def title(ctx, entry: str, title: str):
    '''Updates the title for a entry'''
	
    # Checks if the entry exists
    if list[entry] is None:
        await bot.send_message(ctx.message.channel, 'Entry does not exist.')
        return
    
    # Gets the entry
    current_entry = list[entry]
	
    # Changes the title of that entry
    current_entry.title = title

    # Creates a new embed with the new value
    embed = edit_entry(current_entry)
	
    # Deletes the senders message
    await bot.delete_message(ctx.message)
	
    # Edits the message holding the entry
    await bot.edit_message(current_entry.ctx, ' ', embed=embed)

list = load()
bot.run(TOKEN)
