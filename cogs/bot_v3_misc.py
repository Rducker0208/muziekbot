import os
import datetime

import discord
import lyricsgenius

from typing import Callable

from discord.ext import commands
from googleapiclient.discovery import build

YT_API_KEY: str = os.getenv('YT_API_KEY')
GENIUS_ACCESS_TOKEN: str = os.getenv('GENIUS_ACCESS_TOKEN')

youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)


thumbnail_types: list = ['maxres', 'high', 'standard', 'default', 'medium']


class Misc(commands.Cog):
    """Cog containing all miscellaneous commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kill(self, ctx: discord.ext.commands.Context,
                   code: str = commands.parameter(description='kill code')) -> None:
        """Admin only function to instantly take down muziekbot"""

        if ctx.message.author.id == 770658322054643744:
            if code == str(ctx.bot.kill_code):
                await ctx.send(f'shutting down {ctx.bot.user}')
                quit()

    @kill.error
    async def kill_error(self, ctx: discord.ext.commands.Context, error) -> discord.Message | None:
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send('The command you are using is missing an argument, please check the help command'
                                  ' for all required arguments')

    @commands.command()
    async def lyrics(self, ctx: discord.ext.commands.Context) -> discord.Message:
        """Returns the lyrics of the currently playing song"""

        if ctx.voice_client is None:
            return await ctx.send('This command is only usable if there is a song playing.')

        # collect song name from yt api
        song_id: str = ctx.bot.current_song[32:]
        data_request = youtube.videos().list(part='snippet', id=song_id)
        data_response = data_request.execute()

        # clean up song name
        song_name: str = data_response['items'][0]['snippet']['title']

        song_name = song_name.replace('(Official Video)', '')
        song_name = song_name.replace('[Official Video]', '')

        song_name = song_name.split('(')[0]
        song_name = song_name.split('[')[0]

        # find song name using genius api
        song: genius.response_format = genius.search_song(song_name)
        if song is None:
            return await ctx.send('Multibot couldn\'t find that song.')

        # clean up found lyrics
        song_lyrics: str = song.lyrics
        song_lyrics = song_lyrics[2:]
        song_lyrics = song_lyrics.split('Lyrics')[1]
        song_lyrics = song_lyrics.replace('[Recording Info]', '')
        song_lyrics = song_lyrics.replace('Contributors', '')
        song_lyrics = song_lyrics.replace('Embed', '')
        song_lyrics = song_lyrics.replace('You might also like', '\n')
        song_lyrics = song_lyrics.replace('[Ref', '\n[Ref')

        # remove final digits from lyrics if needed
        if song_lyrics[-1].isdigit() is True:
            if song_lyrics[-2].isdigit() is True:
                if song_lyrics[-3].isdigit() is True:
                    song_lyrics = song_lyrics[:-3]
                else:
                    song_lyrics = song_lyrics[:-2]
            else:
                song_lyrics = song_lyrics[:-1]

        # send embed with lyrics
        if not len(song_lyrics) >= 4000:
            embed = discord.Embed(colour=discord.Colour.dark_embed(),
                                  title=f'Lyrics of: {song_name}')
            embed.description = str(song_lyrics)
            await ctx.send(embed=embed)
        else:
            return await ctx.send('Multibot doesn\'t support song lyrics over 4000 characters, sorry for'
                                  ' the inconvenience')

    @commands.command()
    async def song_info(self,
                        ctx: discord.ext.commands.Context,
                        song_index: str = commands.parameter(description='- Position in queue of the song'))\
            -> Callable[[tuple[str, str]], discord.Message] | discord.Message:
        """Show info on a song in queue"""

        # check of er een queue is
        if not ctx.bot.queue:
            return await ctx.send('Please create a queue before using this command')

        # check of song_index een geldig getal is
        if not song_index.isnumeric() or not len(ctx.bot.queue) >= int(song_index) >= 1:
            return await ctx.send('Please provide a valid song number')

        song_link: str = ctx.bot.queue[int(song_index) - 1]
        await current(ctx, song_link, 'queue')

    @song_info.error
    async def song_info_error(self, ctx: discord.ext.commands.Context,
                              error: discord.ext.commands.MissingRequiredArgument) -> discord.Message | None:
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send('The command you are using is missing an argument, please check the help command'
                                  ' for all required arguments')


async def setup(bot: discord.ext.commands.Bot) -> None:
    """Function used to set up this cog"""

    return await bot.add_cog(Misc(bot))


def get_songinfo(song_id: str) -> tuple[str, str]:
    """Function that gets song info from youtube api"""

    request = youtube.videos().list(part='snippet', id=song_id)
    response = request.execute()
    song_name: str = response['items'][0]['snippet']['title']
    song_artist: str = response['items'][0]['snippet']['channelTitle']

    return song_name, song_artist


async def check_video_status(video_link: str) -> str:
    """Function that checks if a video is playable"""

    # get video info from yt
    video_id = video_link[32:]
    data_request = youtube.videos().list(part='snippet', id=video_id)
    data_request_response = data_request.execute()

    # works if the song is valid
    try:
        _: str = data_request_response['items'][0]['snippet']['title']
        return 'valid'
    except IndexError:
        return 'invalid'


async def current(ctx: discord.ext.commands.Context, song_link: str, current_or_queue) -> discord.Message:
    """Obtain song infro from yt api and returns this info in an embed"""

    # get song info from yt api
    video_id: str = song_link[32:]
    data_request = youtube.videos().list(part='snippet', id=video_id)
    duration_request = youtube.videos().list(part='contentDetails', id=video_id)
    data_request_response = data_request.execute()
    duration_response = duration_request.execute()

    # song title and artist
    song_name, song_artist = get_songinfo(video_id)

    # release date
    release_date: str = data_request_response['items'][0]['snippet']['publishedAt'][:10]

    # song duration
    duration: str = duration_response['items'][0]['contentDetails']['duration'][2:].replace('M', ':').replace('S', '')
    if ':' not in duration:
        duration = f'{duration} seconds'
    elif duration[-2] == ':':  # als lied 1 cijfer na : heeft bijv 3:7 verander dit in 3:07
        last_duration_letter = duration[-1]
        duration = duration.replace(duration[-1], '0')
        duration = f'{duration}{last_duration_letter}'
    elif duration[-1] == ':':  # als lied precies een min ** n is bijv: 6:
        duration = f'{duration}{0}{0}'

    # thumbnail image
    for thumbnail_type in thumbnail_types:
        try:
            thumbnail: str | None = data_request_response['items'][0]['snippet']['thumbnails'][thumbnail_type]['url']
            break
        except Exception:  # noqa
            pass
    else:
        await ctx.send('could not get thumbnail')
        thumbnail = None

    if current_or_queue == 'current':
        title = 'Current song\'s info:'
    else:
        title = 'Song info:'

    # maak embed
    embed = discord.Embed(
        colour=discord.Colour.dark_embed(),
        title=title,
    )

    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name='Song name: ', value=song_name, inline=False)
    embed.add_field(name='Song duration: ', value=duration, inline=False)
    embed.add_field(name='Song artist: ', value=song_artist, inline=False)
    embed.add_field(name='Song release date: ', value=release_date, inline=False)
    embed.add_field(name='Song url:', value=song_link)

    # Aanvraag tijd
    curent_time: str = str(datetime.datetime.now())[11:-7]
    embed.set_footer(text=f' Requested by {ctx.message.author} at: {curent_time}')
    return await ctx.send(embed=embed)


async def set_status(ctx: discord.ext.commands.Context, song_link: str) -> None:
    """Set muziekbot's discord status"""

    song_id: str = song_link[32:]
    song_name, artist = get_songinfo(song_id)
    await ctx.bot.change_presence(activity=discord.Game(name=f'Currently playing: {song_name} by: {artist}.'))
