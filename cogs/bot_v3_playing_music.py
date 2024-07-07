import asyncio

import discord
import yt_dlp
import ytmusicapi

from discord.ext import commands
from cogs.bot_v3_controls import join_vc
from cogs.bot_v3_queue import Queuing
from cogs.bot_v3_misc import current, set_status, check_video_status
from cogs.picking_song import PicksongEmbed

yt_api_unofficial = ytmusicapi.YTMusic()
FFMPEG_PATH: str = 'C:/ffmpeg/ffmpeg.exe'

song_to_play: str | None = None


class Playing(commands.Cog):
    """Cog that contains all commands used to play music"""

    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot
        self.queuing = Queuing(self.bot)

    @commands.command()
    async def top1000(self, ctx: discord.ext.commands.Context.voice_client) -> None:
        """Wipe queue and replace it with veronica's top 1000"""

        if ctx.voice_client is None:
            await join_vc(ctx)

        await ctx.send('Starting queue process')

        playlist_id: str = 'PLIwZ2BK481_17wMRlFBpj4thz-m7gGdF9'
        ctx.bot.queue: list = self.queuing.add_playlist_to_queue([], playlist_id, False)

        await ctx.send('Added top1000 to qeue')

        if ctx.voice_client.is_playing() is False:
            return await self.play_from_queue(ctx)

    @commands.command()
    async def play(self, ctx: discord.ext.commands.Context.voice_client, *,
                   yt_url: str = commands.parameter(description='- url of youtube video [optional]')) \
            -> discord.Message | None:
        """Play a song using url or a search query"""

        if not hasattr(ctx.author.voice, 'channel'):
            return await ctx.send('Please join a voice channel before using this command')

        if '&list=' in yt_url:
            return await ctx.send('Please provide a search qeury, a video url or use the playlist commands.')

        elif 'https://www.youtube.com/watch?v=' in yt_url:

            yt_url = yt_url.split('&t=')[0]
            if await check_video_status(yt_url) == 'valid':
                if ctx.voice_client:
                    ctx.voice_client.stop()
                await join_vc(ctx)
                await current(ctx, yt_url, 'current')
                await set_status(ctx, yt_url)
                await self.play_song(ctx, yt_url)
            else:
                return await ctx.send('Please provide a valid youtube url.')

        else:
            fetch_message: discord.Message = await ctx.send('Fetching results'
                                                            ', please wait for the embed with options to spawn to '
                                                            'avoid errors.')
            search_query: str = yt_url
            song_embed = PicksongEmbed(ctx, search_query, False)
            await song_embed.send()

            while True:
                if ctx.bot.chosen_song is None:
                    await asyncio.sleep(0.1)
                else:

                    ctx.bot.queue.insert(0, ctx.bot.chosen_song)
                    await fetch_message.delete()
                    await join_vc(ctx)

                    if ctx.voice_client.is_playing():
                        ctx.voice_client.stop()
                    else:
                        await current(ctx, ctx.bot.chosen_song, 'current')
                        await set_status(ctx, ctx.bot.chosen_song)
                        await self.play_song(ctx, ctx.bot.chosen_song)
                    ctx.bot.chosen_song = None
                    return

    @play.error
    async def play_error(self, ctx: discord.ext.commands.Context, error) -> discord.Message | None:
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send('The command you are using is missing an argument, please check the help command'
                                  ' for all required arguments')

    @commands.command()
    async def start_queue(self, ctx: discord.ext.commands) -> None:
        """Start playing queue"""

        if not hasattr(ctx.author.voice, 'channel'):
            return await ctx.send('Please join a voice channel before using this command')
        await join_vc(ctx)

        return await self.play_from_queue(ctx)

    async def play_song(self, ctx: discord.ext.commands.Context.voice_client, song_to_play_link: str) -> None:
        """Function that uses FFMPEG to download and play a song"""

        # setup
        FFMPEG_OPTIONS: dict = {'executable': FFMPEG_PATH,
                                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', # noqa
                                'options': '-vn'}
        YT_DLP_OPTIONS: dict = {'format': 'bestaudio'}
        vc = ctx.voice_client

        # setup yt api and get song link
        with yt_dlp.YoutubeDL(YT_DLP_OPTIONS) as ydlp:
            if song_to_play_link in ctx.bot.queue:
                ctx.bot.queue.remove(song_to_play_link)
            ctx.bot.current_song: str = song_to_play_link

            # download and play song
            song_info = ydlp.extract_info("ytsearch:%s" % song_to_play_link, download=False)['entries'][0]
            url2: str = song_info['url']
            source_to_play = discord.FFmpegOpusAudio(url2, **FFMPEG_OPTIONS)
            vc.play(source_to_play, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_from_queue(ctx),
                                                                                     self.bot.loop))

    async def play_from_queue(self, ctx: discord.ext.commands.Context) -> None:
        """Function that grabs the next song from queue and passses it to the play_song function"""

        if not ctx.bot.queue:
            await ctx.send('Qeue is empty, please provide a new song or playlist')
            return await self.bot.change_presence(activity=discord.Game(name='Waiting for a song to play...'))
        else:
            song_link = ctx.bot.queue[0]
            await self.play_song(ctx, song_link)
            await current(ctx, song_link, 'current')
            return await set_status(ctx, song_link)


async def setup(bot: discord.ext.commands.Bot) -> None:
    """Function used to set up this cog"""

    await bot.add_cog(Playing(bot))
