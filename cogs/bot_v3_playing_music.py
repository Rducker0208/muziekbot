import time

import discord
from discord.ext import commands
from bot_v3 import queue
from cogs.bot_v3_controls import Controls
from cogs.bot_v3_queue import Queuing


class Playing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = queue
        self.queuing = Queuing(self.bot)
        self.controls = Controls(self.bot)

    # Command die een speellijst speelt met de Veronica top 1000
    @commands.command()
    async def top1000(self, ctx):
        if ctx.voice_client is None:
            await self.controls.join(ctx)
        playlist_id = 'PLvubIPSEU2C7zVgsSJT4N-qfqol_boAm6'
        self.queue = []
        self.queuing.add_to_queue(playlist_id, False)

        # await ctx.send('Added top1000 to qeue')
        # if ctx.voice_client.is_playing() is False:
        #     await play_from_queue(ctx)


async def setup(bot):
    await bot.add_cog(Playing(bot))