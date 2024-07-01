import os
import datetime

import discord
import lyricsgenius

from discord.ext import commands
from googleapiclient.discovery import build

YT_API_KEY = os.getenv('YT_API_KEY')
GENIUS_ACCESS_TOKEN = os.getenv('GENIUS_ACCESS_TOKEN')

youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)


thumbnail_types = ['maxres', 'high', 'standard', 'default', 'medium']


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kill(self, ctx, content):  # admin_only functie om bot doen te halen
        if ctx.message.author.id == 770658322054643744:
            if str(content) == str(ctx.bot.kill_code):
                await ctx.send(f'shutting down {ctx.bot.user}')
                quit()

    # Functie die lyrics van een lied verzamelt met genius api en deze dan in een embed plaatst
    @commands.command()
    async def lyrics(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send('This command is only usable if there is a song playing.')
        song_id = ctx.bot.current_song[32:]

        data_request = youtube.videos().list(part='snippet', id=song_id)
        data_response = data_request.execute()

        # clean up song name
        song_name = data_response['items'][0]['snippet']['title']

        song_name = song_name.replace('(Official Video)', '')
        song_name = song_name.replace('[Official Video]', '')

        song_name = song_name.split('(')[0]
        song_name = song_name.split('[')[0]

        # find song name using genius api
        song = genius.search_song(song_name)
        if song is None:
            return await ctx.send('Multibot couldn\'t find that song.')

        # clean up found lyrics
        song_lyrics = song.lyrics
        song_lyrics = song_lyrics[2:]
        song_lyrics = song_lyrics.split('Lyrics')[1]
        song_lyrics = song_lyrics.replace('[Recording Info]', '')
        song_lyrics = song_lyrics.replace('Contributors', '')
        song_lyrics = song_lyrics.replace('Embed', '')
        song_lyrics = song_lyrics.replace('You might also like', '\n')

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


async def setup(bot):
    await bot.add_cog(Misc(bot))


def get_songinfo(song_id):
    request = youtube.videos().list(part='snippet', id=song_id)
    response = request.execute()
    song_name = response['items'][0]['snippet']['title']
    song_artist = response['items'][0]['snippet']['channelTitle']

    return song_name, song_artist


# check if video is playable or not
async def check_video_status(video_link):
    video_id = video_link[32:]
    data_request = youtube.videos().list(part='snippet', id=video_id)
    data_request_response = data_request.execute()

    # works if the song is valid
    try:
        _ = data_request_response['items'][0]['snippet']['title']
        return 'valid'
    except IndexError:
        return 'invalid'


# Command die data verzamelt over huidig lied en dit in een embed verstuurt
async def current(ctx, song_link):
    video_id = song_link[32:]
    data_request = youtube.videos().list(part='snippet', id=video_id)
    duration_request = youtube.videos().list(part='contentDetails', id=video_id)
    data_request_response = data_request.execute()
    duration_response = duration_request.execute()

    # song title and artist
    song_name, song_artist = get_songinfo(video_id)

    # release date
    release_date = data_request_response['items'][0]['snippet']['publishedAt'][:10]

    # song duration
    duration = duration_response['items'][0]['contentDetails']['duration'][2:].replace('M', ':').replace('S', '')
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
            thumbnail = data_request_response['items'][0]['snippet']['thumbnails'][thumbnail_type]['url']
            break
        except Exception:  # noqa
            pass
    else:
        await ctx.send('could not get thumbnail')
        thumbnail = None

    # maak embed
    embed = discord.Embed(
        colour=discord.Colour.dark_embed(),
        title='Current song\'s info:',
    )
    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name='Song name: ', value=song_name, inline=False)
    embed.add_field(name='Song duration: ', value=duration, inline=False)
    embed.add_field(name='Song artist: ', value=song_artist, inline=False)
    embed.add_field(name='Song release date: ', value=release_date, inline=False)
    embed.add_field(name='Song url:', value=song_link)

    # Aanvraag tijd
    time_ms = str(datetime.datetime.now())[11:]
    time_final = time_ms[:8]
    embed.set_footer(text=f' Requested by {ctx.message.author} at: {time_final}')
    await ctx.send(embed=embed)


# Zet bot status
async def set_status(ctx, song_link):
    song_id = song_link[32:]
    song_name, artist = get_songinfo(song_id)
    await ctx.bot.change_presence(activity=discord.Game(name=f'Currently playing: {song_name} by: {artist}.'))
