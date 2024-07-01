import asyncio
import os

import discord
import yt_dlp
import ytmusicapi

from discord.ext import commands
from cogs.bot_v3_controls import join_vc
from cogs.bot_v3_queue import Queuing
from cogs.bot_v3_misc import current, set_status, check_video_status, get_songinfo

from googleapiclient.discovery import build

YT_API_KEY = os.getenv('YT_API_KEY')
youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
yt_api_unofficial = ytmusicapi.YTMusic()
FFMPEG_PATH = 'C:/ffmpeg/ffmpeg.exe'
working_video = True
song_to_play = None


# class voor embed om lied te kiezen
class PicksongEmbed(discord.ui.View):
    def __init__(self, ctx, search_string, bot, add_to_qeue):  # noqa
        super().__init__()
        self.message = None
        self.chosen_id = None
        self.id_chosen_pick = None
        self.embed_counter = 0
        self.api_counter = 0
        self.song_counter = 1
        self.song_ids = []
        self.song_options = []
        self.search_string = search_string
        self.ctx = ctx
        self.bot = bot
        self.add_to_qeue = add_to_qeue

    # Functie die embed met buttons stuurt
    async def send(self):
        embed = await self.create_embed()
        self.message = await self.ctx.send(embed=embed, view=self)  # update bericht

    # Functie die ervoor zorgt dat de embed data bevat
    async def create_embed(self):
        embed = discord.Embed(title='Pick a song:',
                              colour=discord.Colour.dark_embed())

        # verzamel top 5 liedjes aan de hand van search string
        for i in range(5):
            try:
                videoId = yt_api_unofficial.search(self.search_string)[self.api_counter]['videoId']
            except KeyError:
                try:
                    videoId = yt_api_unofficial.search(self.search_string)[self.api_counter + 1]['videoId']
                except KeyError:
                    try:
                        videoId = yt_api_unofficial.search(self.search_string)[self.api_counter + 2]['videoId']
                    except KeyError:
                        return await self.ctx.send('Couldn\'t find that song, please check your spelling and retry.')
            self.song_ids.append(videoId)
            self.api_counter += 1

        # verander eerder verzamelde ids in namen
        for song_id in self.song_ids:
            song_title, song_artist = get_songinfo(song_id)
            self.song_options.append(f'{song_title} by: {song_artist}')

        # voeg tekst toe aan embed
        for song_option in self.song_options:
            embed.add_field(name='',
                            value=f'{self.song_counter}.{song_option}',
                            inline=False)
            self.song_counter += 1
        return embed

    async def update_message(self):
        global song_to_play
        song_to_play = None
        if self.add_to_qeue is True:
            self.ctx.bot.append(f'https://www.youtube.com/watch?v={self.chosen_id}')
            await self.message.delete()
        elif self.add_to_qeue == 'front':
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
    def __init__(self, bot):
        self.bot = bot
        self.queuing = Queuing(self.bot)

    # Command die een speellijst speelt met de Veronica top 1000
    @commands.command()
    async def top1000(self, ctx):
        if ctx.voice_client is None:
            await join_vc(ctx)
        playlist_id = 'PLIwZ2BK481_17wMRlFBpj4thz-m7gGdF9'
        ctx.bot.queue = self.queuing.add_playlist_to_queue([], playlist_id, False)

        await ctx.send('Added top1000 to qeue')
        if ctx.voice_client.is_playing() is False:
            await self.play_from_queue(ctx)

    # Command die een enkel lied afspeelt, als er al iets speelt wordt dit gestopt
    @commands.command()
    async def play(self, ctx, *, yt_url):
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
                await current(ctx, yt_url)
                await set_status(ctx, yt_url)
                self.play_song(ctx, yt_url)
            else:
                return await ctx.send('Please provide a valid youtube url.')

        else:
            fetch_message = await ctx.send('Fetching results'
                                           ', please wait for the embed with options to spawn to avoid errors.')
            search_query = yt_url
            song_embed = PicksongEmbed(ctx, search_query, ctx.bot, False)
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
                        await current(ctx, song_to_play)
                        await set_status(ctx, song_to_play)
                        self.play_song(ctx, song_to_play)
                    break

    # begin met afspelen van queue
    @commands.command()
    async def start_queue(self, ctx):
        if not hasattr(ctx.author.voice, 'channel'):
            return await ctx.send('Please join a voice channel before using this command')
        await join_vc(ctx)
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
            ctx.bot.current_song = song_to_play_link
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
