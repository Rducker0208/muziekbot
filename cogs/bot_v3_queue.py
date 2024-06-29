import discord, os
from discord.ext import commands
from googleapiclient.discovery import build

YT_API_KEY = os.getenv('YT_API_KEY')


class Queuing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.youtube = build('youtube', 'v3', developerKey=YT_API_KEY)

    # Functie voor het toevoegen van een lied aan de queue
    def add_to_queue(self, playlist_id, insert_at_front):  # noqa
        # verzamel lengte van playlist
        length_request = self.youtube.playlists().list(part='snippet')
        print(length_request)




        # verzamel playlist items
        # counter = 0
        # final_run = False
        # playlist_request = self.youtube.playlistItems().list(part='snippet',
        #                                                      playlistId=playlist_id,
        #                                                      maxResults=50)
        # response = playlist_request.execute()
        # print(response)
        # next_page_token = ''

        # while True:
        #     pass

async def setup(bot):
    await bot.add_cog(Queuing(bot))
