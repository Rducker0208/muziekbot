import os
from discord.ext import commands
from googleapiclient.discovery import build


YT_API_KEY = os.getenv('YT_API_KEY')


class Queuing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.youtube = build('youtube', 'v3', developerKey=YT_API_KEY)

    # Functie voor het toevoegen van een lied aan de queue
    def add_to_queue(self, queue, playlist_id, insert_at_front):  # noqa
        next_page_token = None

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
                    queue.insert(0, yt_url)
                else:
                    queue.append(yt_url)

            try:
                next_page_token = playlist_response['nextPageToken']
            except KeyError:
                break

        return queue


async def setup(bot):
    await bot.add_cog(Queuing(bot))
