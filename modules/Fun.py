import discord
from asyncio import sleep

class Fun:
    def __init__(self):
        self.bot = None
    
    def init(self, bot):
        self.bot = bot
    
    async def loop(self, ctx):
        '''Infinite Loop'''
        
        await sleep(0.5)
        await self.bot.delete_message(ctx.message)
        
        stop_loop = False
        while not stop_loop:
            msg = await self.bot.send_message(ctx.message.channel, "ping")
            msg = await self.bot.send_message(ctx.message.channel, "pong")
            response = await self.bot.wait_for_message(timeout=0.5)
            if response is not None:
                if response.content is "%stop":
                    stop_loop = True
