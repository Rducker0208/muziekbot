import asyncio
import discord
import yt_dlp


from discord.ext import commands
from cogs.bot_v3_controls import join_vc
from cogs.bot_v3_queue import Queuing
from cogs.bot_v3_misc import current, set_status


FFMPEG_PATH = 'C:/ffmpeg/ffmpeg.exe'


class Playing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queuing = Queuing(self.bot)

    # Command die een speellijst speelt met de Veronica top 1000
    @commands.command()
    async def top1000(self, ctx):
        if ctx.voice_client is None:
            await join_vc(ctx)
        playlist_id = 'PLIwZ2BK481_17wMRlFBpj4thz-m7gGdF9'
        ctx.bot.queue = self.queuing.add_to_queue([], playlist_id, False)

        await ctx.send('Added top1000 to qeue')
        if ctx.voice_client.is_playing() is False:
            await self.play_from_queue(ctx)

    def play_song(self, ctx, song_to_play_link):
        FFMPEG_OPTIONS = {'executable': FFMPEG_PATH,
                          'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        YT_DLP_OPTIONS = {'format': 'bestaudio'}
        vc = ctx.voice_client
        with yt_dlp.YoutubeDL(YT_DLP_OPTIONS) as ydlp:
            if song_to_play_link in ctx.bot.queue:
                ctx.bot.queue.remove(song_to_play_link)

            song_info = ydlp.extract_info("ytsearch:%s" % song_to_play_link, download=False)['entries'][0]
            url2 = song_info['url']
            source_to_play = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
            vc.play(source_to_play, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_from_queue(ctx),
                                                                                     self.bot.loop))

    # speel items uit qeue, herhaalt zich dmv lambda functie
    async def play_from_queue(self, ctx):
        if not ctx.bot.queue:
            await ctx.send('Qeue is empty, please provide a new song or playlist')
            return await self.bot.change_presence(activity=discord.Game(name='Waiting for a song to play...'))
        else:
            song_link = ctx.bot.queue[0]
            self.play_song(ctx, song_link)
            await current(ctx, song_link)
            await set_status(ctx, song_link)


async def setup(bot):
    await bot.add_cog(Playing(bot))



