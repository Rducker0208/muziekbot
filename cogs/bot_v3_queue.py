import os
import random

import discord

from discord.ext import commands
from googleapiclient.discovery import build

from cogs.bot_v3_misc import check_video_status, get_songinfo


YT_API_KEY = os.getenv('YT_API_KEY')
youtube = build('youtube', 'v3', developerKey=YT_API_KEY)


# class voor embed van queue_list
class Queue_list_embed(discord.ui.View):

    def __init__(self, ctx, song_names):
        super().__init__()
        self.ctx = ctx
        self.song_names = song_names
        self.message = None
        self.current_page = 1
        self.seperator = 20
        self.embed_counter = 0
        self.queue_length = len(self.ctx.bot.queue)

    # Functie voor het sturen van de embed
    async def send(self):
        self.message = await self.ctx.send(view=self)  # stuur bericht
        await self.update_message(self.song_names[:self.seperator]) # update bericht tot aan seperator 20 * aantal pagina's # noqa

    # Functie voor het updaten van de embed
    async def update_message(self, data):
        self.update_buttons()  # update knoppen
        await self.message.edit(embed=self.create_embed(data), view=self)  # bewerk bericht

    # Functie voor het muten van buttons
    def update_buttons(self):
        # geen idee wat hier gebeurt eerlijk gezegd
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.previous_button.disabled = True
        else:
            self.first_page_button.disabled = False
            self.previous_button.disabled = False

        if self.queue_length % 20 == 0:
            if self.current_page == int(len(self.song_names) / self.seperator):
                self.next_button.disabled = True
                self.last_page_button.disabled = True
            else:
                self.next_button.disabled = False
                self.last_page_button.disabled = False
        else:
            if self.current_page == int(len(self.song_names) / self.seperator) + 1:
                self.next_button.disabled = True
                self.last_page_button.disabled = True
            else:
                self.next_button.disabled = False
                self.last_page_button.disabled = False

    # Functie voor het tekst toevoegen aan embed
    def create_embed(self, data):
        embed = discord.Embed(title='Current qeue:', colour=discord.Colour.dark_embed())
        current_page = self.current_page
        if self.queue_length % 20 == 0:
            max_page = int(self.queue_length / self.seperator)
        else:
            max_page = int(self.queue_length / self.seperator) + 1
        for song_name in data:
            embed.add_field(name='', value=song_name, inline=False)
            self.embed_counter += 1
        embed.set_footer(text=f'page {current_page}/{max_page}')
        return embed

    @discord.ui.button(label='<<', style=discord.ButtonStyle.primary)
    async def first_page_button(self, interaction: discord.Interaction, button: discord.Button): # noqa
        await interaction.response.defer() # noqa
        self.current_page = 1
        until_item = self.current_page * self.seperator  # laatste item dat moet worden gedisplayed
        from_item = until_item - self.seperator  # eerste item dat moet worden gedisplayed
        await self.update_message(self.song_names[from_item:until_item])

    @discord.ui.button(label='<', style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.current_page -= 1
        until_item = self.current_page * self.seperator
        from_item = until_item - self.seperator
        await self.update_message(self.song_names[from_item:until_item])

    @discord.ui.button(label='>', style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.current_page += 1
        until_item = self.current_page * self.seperator
        from_item = until_item - self.seperator
        await self.update_message(self.song_names[from_item:until_item])

    @discord.ui.button(label='>>', style=discord.ButtonStyle.primary)
    async def last_page_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        if self.queue_length % 20 == 0:
            self.current_page = int(len(self.song_names) / self.seperator)
        else:
            self.current_page = int(len(self.song_names) / self.seperator) + 1
        until_item = self.current_page * self.seperator
        from_item = until_item - self.seperator
        await self.update_message(self.song_names[from_item:until_item])


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

    @commands.command()
    async def queue_list(self, ctx):
        song_names = []
        song_index = 1
        if not ctx.bot.queue:
            return await ctx.send('There is no queue at the moment, please create one.')

        message = await ctx.send('Starting process, this might take some time for big queue\'s.')

        for link in ctx.bot.queue:
            song_id = link[32:]
            song_name, _ = get_songinfo(song_id)
            full_song_name = f"{song_index}. {song_name}"
            song_names.append(full_song_name)
            song_index += 1

        embed = Queue_list_embed(ctx, song_names)
        await embed.send()
        await message.delete()

    @commands.command()
    async def queue_shuffle(self, ctx):
        random.shuffle(ctx.bot.queue)
        return await ctx.send('Successfully shuffled queue')

    @commands.command()
    async def queue_reverse(self, ctx):
        ctx.bot.queue.reverse()
        return await ctx.send('Successfully reversed queue')

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
