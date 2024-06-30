import os

from discord.ext import commands
from googleapiclient.discovery import build

from cogs.bot_v3_misc import check_video_status

YT_API_KEY = os.getenv('YT_API_KEY')
youtube = build('youtube', 'v3', developerKey=YT_API_KEY)


class Queuing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.youtube = build('youtube', 'v3', developerKey=YT_API_KEY)

    # command om een enkel lied in queue te plaatsen
    @commands.command()
    async def queue(self, ctx, location, song_link):

        # &list= duidt een playlist aan
        if '&list=' in song_link:
            return await ctx.send('Please provide a search qeury, a video url or use the playlist commands.')

        elif 'https://www.youtube.com/watch?v=' in song_link:
            song_link = song_link.split('&t=')[0]
            if await check_video_status(song_link) == 'valid':
                if location == 'front':
                    ctx.bot.queue.insert(0, song_link)
                else:
                    ctx.bot.queue.append(song_link)
                return await ctx.send('Sucessfully queued song.')
            else:
                return await ctx.send('Please provide a valid youtube url.')
        else:
            return await ctx.send('Please provide a valid youtube url containing https://www.youtube.com/watch?v=.')

    # command om een volledige playlist in queue te plaatsen
    @commands.command()
    async def queue_playlist(self, ctx, location, playlist_link):
        if 'www.youtube.com/playlist' not in playlist_link:
            return await ctx.send('Please provide a valid playlist url.')
        playlist_id = playlist_link[38:]

        # check of playlist link geldig is
        try:
            playlist_name = youtube.playlists().list(id=playlist_id,
                                                     part='snippet')
            playlist_name_response = playlist_name.execute()
            playlist_name = playlist_name_response['items'][0]['snippet']['title']
        except IndexError:
            return await ctx.send('Please provide a valid playlist url.')

        if location == 'front':
            ctx.bot.queue = self.add_playlist_to_queue(ctx.bot.queue, playlist_id, insert_at_front=True)
        else:
            ctx.bot.queue = self.add_playlist_to_queue(ctx.bot.queue, playlist_id, insert_at_front=False)

        return await ctx.send(f'Added playlist to qeue: {playlist_name}')

    # Functie voor het toevoegen van een lied aan de queue
    def add_playlist_to_queue(self, queue, playlist_id, insert_at_front):  # noqa
        next_page_token = None
        new_queue = []

        while True:
            if next_page_token:
                playlist_request = self.youtube.playlistItems().list(part='snippet',
                                                                     playlistId=playlist_id,
                                                                     pageToken=next_page_token,
                                                                     maxResults=50)
            else:
                playlist_request = self.youtube.playlistItems().list(part='snippet',
                                                                     playlistId=playlist_id,
                                                                     maxResults=50)

            playlist_response = playlist_request.execute()
            items_on_page = len(playlist_response['items'])

            for item in range(items_on_page):
                yt_video_id = playlist_response['items'][item]['snippet']['resourceId']['videoId']
                yt_url = f"https://www.youtube.com/watch?v={yt_video_id}"

                if insert_at_front is True:
                    new_queue.append(yt_url)
                else:
                    queue.append(yt_url)

            try:
                next_page_token = playlist_response['nextPageToken']
            except KeyError:
                break

        if insert_at_front is True:
            queue.extend(new_queue)
        return queue


async def setup(bot):
    await bot.add_cog(Queuing(bot))
