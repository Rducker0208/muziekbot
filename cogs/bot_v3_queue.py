import os
import random
import datetime

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

    @discord.ui.button(label='delete', style=discord.ButtonStyle.red)
    async def delete_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        await self.message.delete()


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

    # Functie die de lengte van queue berekent
    @commands.command()
    async def queue_length(self, ctx):
        total_seconds = 0
        if not ctx.bot.queue:
            return await ctx.send('Please create a queue before using this command.')

        for song in ctx.bot.queue:
            song_id = song[32:]
            length_request = youtube.videos().list(part='contentDetails', id=song_id)
            length_response = length_request.execute()
            song_duration = (length_response['items'][0]['contentDetails']['duration'][2:].
                             replace('M', ':').replace('S', ''))

            minutes, seconds = song_duration.split(':')
            if not seconds:
                seconds = 0

            total_seconds += (int(minutes) * 60 + int(seconds))

        hours = total_seconds // 3600
        minutes = (total_seconds - (hours * 3600)) // 60
        seconds = total_seconds - (hours * 3600) - (minutes * 60)

        embed = discord.Embed(colour=discord.Colour.dark_embed(),
                              title='Queue length')
        embed.add_field(name='Queue Length:', value=f'{hours} hours, {minutes} minutes and {seconds} seconds',
                        inline=False)
        embed.add_field(name='Songs in queue:', value=len(ctx.bot.queue),
                        inline=False)

        curent_time = str(datetime.datetime.now())[11:-7]
        embed.set_footer(text=f' Requested by {ctx.message.author} at: {curent_time}')
        await ctx.send(embed=embed)

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

    @commands.command()
    async def queue_clear(self, ctx):
        ctx.bot.queue = []
        return await ctx.send('Successfully cleared queue')

    # move een lied naar een andere plaats in de queue
    @commands.command()
    async def move_song(self, ctx, start_index, end_index):
        try:
            if not ctx.bot.queue:
                return await ctx.send('PLease create a queue before using this command')

            try:
                start_index = int(start_index)
            except TypeError:
                return await ctx.send('Please provide a valid start and end location')

            try:
                end_index = int(end_index)
            except TypeError:
                return await ctx.send('Please provide a valid start and end location')

            song = ctx.bot.queue.pop(start_index - 1)
            ctx.bot.queue.insert(end_index - 1, song)

            return await ctx.send('Successfully moved song')

        except IndexError:
            return await ctx.send('Please provide a validstart and end location')

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
