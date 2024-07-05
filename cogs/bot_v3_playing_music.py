import asyncio

import discord
import yt_dlp
import ytmusicapi

from discord.ext import commands
from cogs.bot_v3_controls import join_vc
from cogs.bot_v3_queue import Queuing
from cogs.bot_v3_misc import current, set_status, check_video_status, get_songinfo

yt_api_unofficial = ytmusicapi.YTMusic()
FFMPEG_PATH: str = 'C:/ffmpeg/ffmpeg.exe'

song_to_play: str | None = None


class PicksongEmbed(discord.ui.View):
    """Embed that contains 5 songs which the user can pick 1 off to start playing/queue"""

    def __init__(self, ctx, search_string, add_to_queue):
        super().__init__()
        self.ctx: discord.ext.commands.Context = ctx
        self.search_string: str = search_string
        self.add_to_queue: bool = add_to_queue

        self.message: discord.Message | None = None
        self.chosen_id: str | None = None
        self.song_option_counter: int = 1
        self.song_counter: int = 0
        self.song_ids: list = []
        self.song_options: list = []

    async def send(self) -> None:
        """Function that sends the message including the embed"""

        embed: discord.Embed = await self.create_embed()
        self.message: discord.Message = await self.ctx.send(embed=embed, view=self)

    async def create_embed(self) -> discord.Embed | discord.Message:
        """Function that gets song names/ids and puts them into an embed"""

        embed = discord.Embed(title='Pick a song:',
                              colour=discord.Colour.dark_embed())

        # verzamel top 5 liedjes aan de hand van search string
        for i in range(5):
            try:
                videoId = yt_api_unofficial.search(self.search_string)[self.song_counter]['videoId']
            except KeyError:
                try:
                    videoId = yt_api_unofficial.search(self.search_string)[self.song_counter + 1]['videoId']
                except KeyError:
                    try:
                        videoId = yt_api_unofficial.search(self.search_string)[self.song_counter + 2]['videoId']
                    except KeyError:
                        return await self.ctx.send('Couldn\'t find that song, please check your spelling and retry.')
            self.song_ids.append(videoId)
            self.song_counter += 1

        # verander eerder verzamelde ids in namen
        for song_id in self.song_ids:
            song_title, song_artist = get_songinfo(song_id)
            self.song_options.append(f'{song_title} by: {song_artist}')

        # voeg tekst toe aan embed
        for song_option in self.song_options:
            embed.add_field(name='',
                            value=f'{self.song_option_counter}.{song_option}',
                            inline=False)
            self.song_option_counter += 1

        return embed

    async def update_message(self) -> None:
        """Function that updates the message and deletes it if needed"""

        global song_to_play
        song_to_play = None
        if self.add_to_queue is True:
            self.ctx.bot.append(f'https://www.youtube.com/watch?v={self.chosen_id}')
            await self.message.delete()
        elif self.add_to_queue == 'front':
            self.ctx.bot.insert(0, f'https://www.youtube.com/watch?v={self.chosen_id}')
            await self.message.delete()
        else:
            await self.message.delete()
            song_to_play = f'https://www.youtube.com/watch?v={self.chosen_id}'

    @discord.ui.button(label='1', style=discord.ButtonStyle.primary)
    async def first_song_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.chosen_id = self.song_ids[0]
        await self.update_message()

    @discord.ui.button(label='2', style=discord.ButtonStyle.primary)
    async def second_song_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.chosen_id = self.song_ids[1]
        await self.update_message()

    @discord.ui.button(label='3', style=discord.ButtonStyle.primary)
    async def third_song_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.chosen_id = self.song_ids[2]
        await self.update_message()

    @discord.ui.button(label='4', style=discord.ButtonStyle.primary)
    async def fourth_song_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.chosen_id = self.song_ids[3]
        await self.update_message()

    @discord.ui.button(label='5', style=discord.ButtonStyle.primary)
    async def fifth_song_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.chosen_id = self.song_ids[4]
        await self.update_message()


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
                self.play_song(ctx, yt_url)
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
                if song_to_play is None:
                    await asyncio.sleep(0.1)
                else:
                    ctx.bot.queue.insert(0, song_to_play)
                    await fetch_message.delete()
                    await join_vc(ctx)

                    if ctx.voice_client.is_playing():
                        ctx.voice_client.stop()
                    else:
                        await current(ctx, song_to_play, 'current')
                        await set_status(ctx, song_to_play)
                        self.play_song(ctx, song_to_play)
                    break

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

    def play_song(self, ctx: discord.ext.commands.Context.voice_client, song_to_play_link: str) -> None:
        """Function that uses FFMPEG to download and play a song"""

        # setup
        FFMPEG_OPTIONS: dict = {'executable': FFMPEG_PATH,
                                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
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
            source_to_play = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
            vc.play(source_to_play, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_from_queue(ctx),
                                                                                     self.bot.loop))

    async def play_from_queue(self, ctx: discord.ext.commands.Context) -> None:
        """Function that grabs the next song from queue and passses it to the play_song function"""

        if not ctx.bot.queue:
            await ctx.send('Qeue is empty, please provide a new song or playlist')
            return await self.bot.change_presence(activity=discord.Game(name='Waiting for a song to play...'))
        else:
            song_link = ctx.bot.queue[0]
            self.play_song(ctx, song_link)
            await current(ctx, song_link, 'current')
            return await set_status(ctx, song_link)


async def setup(bot: discord.ext.commands.Bot) -> None:
    """Function used to set up this cog"""

    await bot.add_cog(Playing(bot))
