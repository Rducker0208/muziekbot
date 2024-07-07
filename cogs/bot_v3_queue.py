import os
import random
import datetime
import asyncio

import discord

from discord.ext import commands
from googleapiclient.discovery import build

from cogs.bot_v3_misc import check_video_status, get_songinfo
from cogs.picking_song import PicksongEmbed


YT_API_KEY: str = os.getenv('YT_API_KEY')
youtube = build('youtube', 'v3', developerKey=YT_API_KEY)


class Queue_list_embed(discord.ui.View):
    """Embed that shows the current queue in an embed"""

    def __init__(self, ctx: discord.ext.commands.Context, song_names: list):
        super().__init__()
        self.ctx: discord.ext.commands.Context = ctx
        self.song_names: list = song_names
        self.queue_length: int = len(self.ctx.bot.queue)
        self.seperator: int = 20
        self.current_page: int = 1
        self.embed_counter: int = 0
        self.message = None

    async def send(self) -> None:
        """Function that sends the embed"""

        self.message: discord.Message = await self.ctx.send(view=self)  # stuur bericht
        return await self.update_message(self.song_names[:self.seperator]) # update bericht tot aan seperator 20 * aantal pagina's # noqa

    async def update_message(self, song_names_to_use: list) -> None:
        """Function that updates the embed"""

        self.update_buttons()  # update knoppen
        return await self.message.edit(embed=self.create_embed(song_names_to_use), view=self)  # bewerk bericht

    def update_buttons(self) -> None:
        """Mute page buttons if needed"""

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

    def create_embed(self, song_names_to_use: list) -> discord.Embed:
        """Create the embed and add song names"""

        embed: discord.Embed = discord.Embed(title='Current qeue:', colour=discord.Colour.dark_embed())
        current_page = self.current_page

        if self.queue_length % 20 == 0:
            max_page = int(self.queue_length / self.seperator)
        else:
            max_page = int(self.queue_length / self.seperator) + 1

        for song_name in song_names_to_use:
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
    """Cog that contains all commands used to control muziekbot's queue"""

    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot
        self.youtube = build('youtube', 'v3', developerKey=YT_API_KEY)

    @commands.command()
    async def queue(self, ctx: discord.ext.commands.Context,
                    location: str = commands.parameter(description='- [front/back] location in queue where the song needs to go'),# noqa
                    *,
                    song_link: str = commands.parameter(description='- url of the song'))\
            -> discord.Message:
        """Queue a song via an url"""

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
            fetch_message: discord.Message = await ctx.send('Fetching results'
                                                            ', please wait for the embed with options to spawn to '
                                                            'avoid errors.')
            search_query: str = song_link
            song_embed = PicksongEmbed(ctx, search_query, False)
            await song_embed.send()

            while True:
                if ctx.bot.chosen_song is None:
                    await asyncio.sleep(0.1)
                else:
                    if location == 'front':
                        ctx.bot.queue.insert(0, ctx.bot.chosen_song)
                    else:
                        ctx.bot.queue.append(ctx.bot.chosen_song)

                    ctx.bot.chosen_song = None
                    await fetch_message.delete()
                    return await ctx.send('Succesfully queued song.')

    @queue.error
    async def queue_error(self, ctx: discord.ext.commands.Context, error) -> discord.Message | None:
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send('The command you are using is missing an argument, please check the help command'
                                  ' for all required arguments')

    @commands.command()
    async def queue_playlist(self, ctx: discord.ext.commands.Context,
                             location: str = commands.parameter(description='- [front/back] location in queue where the songs needs to go'), # noqa
                             playlist_link: str = commands.parameter(description='- url of the playlist'))\
            -> discord.Message:
        """Queue an entire playlist"""

        if 'www.youtube.com/playlist' not in playlist_link:
            return await ctx.send('Please provide a valid playlist url.')
        playlist_id = playlist_link[38:]

        # check of playlist link geldig is
        try:
            playlist_name_request = youtube.playlists().list(id=playlist_id,
                                                             part='snippet')
            playlist_name_response = playlist_name_request.execute()
            playlist_name = playlist_name_response['items'][0]['snippet']['title']
        except IndexError:
            return await ctx.send('Please provide a valid playlist url.')

        if location == 'front':
            ctx.bot.queue = self.add_playlist_to_queue(ctx.bot.queue, playlist_id, insert_at_front=True)
        else:
            ctx.bot.queue = self.add_playlist_to_queue(ctx.bot.queue, playlist_id, insert_at_front=False)

        return await ctx.send(f'Added playlist to qeue: {playlist_name}')

    @queue_playlist.error
    async def queue_playlist_error(self, ctx: discord.ext.commands.Context, error) -> discord.Message | None:
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send('The command you are using is missing an argument, please check the help command'
                                  ' for all required arguments')

    @commands.command()
    async def queue_remove(self, ctx: discord.ext.commands.Context,
                           song_index: str = commands.parameter(description='Location of song in queue'))\
            -> discord.Message:
        """Remove a song from queue"""

        if not song_index.isnumeric() or not len(ctx.bot.queue) + 1 >= int(song_index) >= 1:
            return await ctx.send('Please provide a valid song index')
        else:
            song_link = ctx.bot.queue.pop(int(song_index) - 1)
            name, _ = get_songinfo(song_link[32:])
            return await ctx.send(f'Succesfully removed ``{name}`` from queue.')

    @queue_remove.error
    async def queue_remove_error(self, ctx: discord.ext.commands.Context, error) -> discord.Message | None:
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send('The command you are using is missing an argument, please check the help command'
                                  ' for all required arguments')

    @commands.command()
    async def queue_length(self, ctx: discord.ext.commands.Context) -> discord.Message:
        """Calculate the length of the current queue"""

        total_seconds: int = 0

        if not ctx.bot.queue:
            return await ctx.send('Please create a queue before using this command.')

        for song in ctx.bot.queue:
            song_id: str = song[32:]
            length_request = youtube.videos().list(part='contentDetails', id=song_id)
            length_response = length_request.execute()
            song_duration: str = (length_response['items'][0]['contentDetails']['duration'][2:].
                                  replace('M', ':').replace('S', ''))

            minutes, seconds = song_duration.split(':')
            if not seconds:
                seconds = 0

            total_seconds += (int(minutes) * 60 + int(seconds))

        hours: int = total_seconds // 3600
        minutes: int = (total_seconds - (hours * 3600)) // 60
        seconds: int = total_seconds - (hours * 3600) - (minutes * 60)

        embed = discord.Embed(colour=discord.Colour.dark_embed(),
                              title='Queue length')
        embed.add_field(name='Queue Length:', value=f'{hours} hours, {minutes} minutes and {seconds} seconds',
                        inline=False)
        embed.add_field(name='Songs in queue:', value=len(ctx.bot.queue),
                        inline=False)

        curent_time = str(datetime.datetime.now())[11:-7]
        embed.set_footer(text=f' Requested by {ctx.message.author} at: {curent_time}')
        return await ctx.send(embed=embed)

    @commands.command()
    async def queue_list(self, ctx: discord.ext.commands.Context) -> None | discord.Message:
        """Show queue in an embed"""

        song_names: list = []
        song_index: int = 1

        if not ctx.bot.queue:
            return await ctx.send('There is no queue at the moment, please create one.')

        if len(ctx.bot.queue) > 250:
            return await ctx.send('Muziekbot doesn\'t support this command for queues over 250 songs')

        message: discord.Message = await ctx.send('Starting process, this might take some time for big queue\'s.')

        for link in ctx.bot.queue:
            song_id: str = link[32:]
            try:
                song_name, _ = get_songinfo(song_id)
            except IndexError:
                song_name = 'Could not be found'

            full_song_name: str = f"{song_index}. {song_name}"
            song_names.append(full_song_name)
            song_index += 1

        embed = Queue_list_embed(ctx, song_names)
        await embed.send()
        return await message.delete()

    @commands.command()
    async def queue_shuffle(self, ctx: discord.ext.commands.Context) -> discord.Message:
        """Randomly shuffle queue"""

        if not ctx.bot.queue:
            return await ctx.send('Please create a queue before using this command')

        random.shuffle(ctx.bot.queue)
        return await ctx.send('Successfully shuffled queue')

    @commands.command()
    async def queue_reverse(self, ctx: discord.ext.commands.Context) -> discord.Message:
        """Reverse queue"""

        if not ctx.bot.queue:
            return await ctx.send('Please create a queue before using this command')

        ctx.bot.queue.reverse()
        return await ctx.send('Successfully reversed queue')

    @commands.command()
    async def queue_clear(self, ctx: discord.ext.commands.Context) -> discord.Message:
        """Reset queue"""

        if not ctx.bot.queue:
            return await ctx.send('Please create a queue before using this command')

        ctx.bot.queue = []
        return await ctx.send('Successfully cleared queue')

    @commands.command()
    async def move_song(self, ctx: discord.ext.commands.Context,
                        start_index: str = commands.parameter(description='- starting index of the song'),
                        end_index: str = commands.parameter(description='- desired ending index of the song'))\
            -> discord.Message:
        """Move a song to another spot in queue"""

        try:
            if not ctx.bot.queue:
                return await ctx.send('Please create a queue before using this command')

            if start_index.isnumeric() and end_index.isnumeric():
                start_index = int(start_index)
                end_index = int(end_index)
            else:
                return await ctx.send('Please provide a valid start and end location')

            song: str = ctx.bot.queue.pop(start_index - 1)
            ctx.bot.queue.insert(end_index - 1, song)

            return await ctx.send('Successfully moved song')

        except IndexError:
            return await ctx.send('Please provide a validstart and end location')

    @move_song.error
    async def move_song_error(self, ctx: discord.ext.commands.Context, error) -> discord.Message | None:
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send('The command you are using is missing an argument, please check the help command'
                                  ' for all required arguments')

    def add_playlist_to_queue(self, queue: list, playlist_id: str, insert_at_front: bool) -> list:  # noqa
        """Function that adds a playlist to the queue"""

        next_page_token: str | None = None
        new_queue: list = []

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
                yt_video_id: str = playlist_response['items'][item]['snippet']['resourceId']['videoId']
                yt_url: str = f"https://www.youtube.com/watch?v={yt_video_id}"

                if insert_at_front is True:
                    new_queue.append(yt_url)
                else:
                    queue.append(yt_url)

            try:
                next_page_token: str = playlist_response['nextPageToken']
            except KeyError:
                break

        if insert_at_front is True:
            queue.extend(new_queue)

        return queue


async def setup(bot: discord.ext.commands.Bot) -> None:
    """Function used to set up this cog"""

    await bot.add_cog(Queuing(bot))
