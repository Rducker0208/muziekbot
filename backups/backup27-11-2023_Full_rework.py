# imports
import asyncio
import os
import pprint
import discord
import random
import yt_dlp
import datetime
import lyricsgenius
import ytmusicapi
import uuid

from discord.ext import commands
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Dotenv variables
load_dotenv()
url = os.getenv('DISCORD_URL')
DISCORD_API_TOKEN = os.getenv('DISCORD_API_TOKEN')
YT_API_KEY = os.getenv('YT_API_KEY')
GENIUS_ACCESS_TOKEN = os.getenv('GENIUS_ACCESS_TOKEN')

# Api builds
FFMPEG_PATH = 'C:/ffmpeg/ffmpeg.exe'
youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
yt_api_unofficial = ytmusicapi.YTMusic()

# kill code voor kill command
kill_code = uuid.uuid4()

# TicTacToe squares
empty_ttt_square = ':white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:\n:white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:\n:white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:\n:white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:\n:white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:'  # noqa
cross_ttt_square = ':red_square::white_large_square::white_large_square::white_large_square::red_square:\n:white_large_square::red_square::white_large_square::red_square::white_large_square:\n:white_large_square::white_large_square::red_square::white_large_square::white_large_square:\n:white_large_square::red_square::white_large_square::red_square::white_large_square:\n:red_square::white_large_square::white_large_square::white_large_square::red_square:'  # noqa
square_ttt_square = ':blue_square::blue_square::blue_square::blue_square::blue_square:\n:blue_square::white_large_square::white_large_square::white_large_square::blue_square:\n:blue_square::white_large_square::white_large_square::white_large_square::blue_square:\n:blue_square::white_large_square::white_large_square::white_large_square::blue_square:\n:blue_square::blue_square::blue_square::blue_square::blue_square:'  # noqa

# Booleans
first_run = True

volume_modified = False
delete_buttons = False
info_status = False

id_chosen_pick = None
index_error = None

# Strings
song_link = ''
yt_video_id = ''
song_to_play = ''
source = ''
fetch_message = ''

# Integers
data_len = 0

# Libraries, tuples en lists
squares = {
    '1_1': 'empty',
    '1_2': 'empty',
    '1_3': 'empty',
    '2_1': 'empty',
    '2_2': 'empty',
    '2_3': 'empty',
    '3_1': 'empty',
    '3_2': 'empty',
    '3_3': 'empty',
}

song_ids = []
queue = []


# class voor embed met hulpagina's
class HelpEmbed(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.message = None
        self.embed = None
        self.help_page = 1
        self.current_page = 1

    # functie voor het versturen van de embed wanneer deze class word gecalled
    async def send_embed(self, ctx):
        self.message = await ctx.send(view=self)  # wacht tot bericht is verstuurd
        await self.update_message()  # stuur request om bericht te updaten

    # Functie om embed te updaten
    async def update_message(self):
        self.update_buttons()
        self.create_embed()
        await self.message.edit(embed=self.embed, view=self)  # update bericht

    # Functie om knoppen te muten als gebruiker al op die pagina is
    def update_buttons(self):
        if self.current_page == 1:
            self.help_button.disabled = True
            self.play_button.disabled = False
            self.queue_button.disabled = False
            self.other_button.disabled = False
        if self.current_page == 2:
            self.play_button.disabled = True
            self.help_button.disabled = False
            self.queue_button.disabled = False
            self.other_button.disabled = False
        if self.current_page == 3:
            self.queue_button.disabled = True
            self.play_button.disabled = False
            self.help_button.disabled = False
            self.other_button.disabled = False
        if self.current_page == 4:
            self.queue_button.disabled = False
            self.play_button.disabled = False
            self.help_button.disabled = False
            self.other_button.disabled = True

    # Functie om de embed te maken
    def create_embed(self):
        # Inhoud pagina
        if self.current_page == 1:
            self.embed = discord.Embed(colour=discord.Colour.dark_embed(),
                                       title='Help content:')
            self.embed.add_field(name='Page 1:', value='Current page containing page info', inline=False)
            self.embed.add_field(name='Page 2:', value='Info about play commands', inline=False)
            self.embed.add_field(name='Page 3:', value='Info about queue commands', inline=False)
            self.embed.add_field(name='Page 4', value='Info about other commands', inline=False)

        # Play commands pagina
        if self.current_page == 2:
            self.embed = discord.Embed(colour=discord.Colour.dark_embed(),
                                       title='Play_commands:')
            self.embed.add_field(name='play [youtube link/search query] ', value='Play a link from youtube',
                                 inline=False)
            self.embed.add_field(name='play_playlist [youtube playlist link] ', value='Play a playlist from youtube',
                                 inline=False)
            self.embed.add_field(name='mb top1000', value='Plays a playlist with Veronica\'s top 1000', inline=False)

        # Queue commands pagina
        if self.current_page == 3:
            self.embed = discord.Embed(colour=discord.Colour.dark_embed(),
                                       title='queue commands:')
            self.embed.add_field(name='mb queue_add [youtube link/search query]:',
                                 value='Add a new song to the end of your queue', inline=False)
            self.embed.add_field(name='mb queue_add_next [youtube link/search query]:',
                                 value='Add a new song to the front of your queue', inline=False)
            self.embed.add_field(name='mb queue_add_playlist [youtube playlist link]:',
                                 value='Add a new playlist to the end of your queue', inline=False)
            self.embed.add_field(name='mb queue_add_playlist_front [youtube playlist link]:',
                                 value='Add a new playlist q to the front of your queue', inline=False)
            self.embed.add_field(name='mb queue_clear:',
                                 value='Clear your queue.', inline=False)
            self.embed.add_field(name='mb queue_front [youtube link/queue number]:',
                                 value='Move a song in your queue to the front', inline=False)
            self.embed.add_field(name='mb queue_info [number in queue]:',
                                 value='Get statistics of the song specified', inline=False)
            self.embed.add_field(name='mb queue_length:',
                                 value='Get length of your queue and the amount of songs in it', inline=False)
            self.embed.add_field(name='mb queue_list:',
                                 value='List all items in your queue', inline=False)
            self.embed.add_field(name='mb queue_play [number in queue]:',
                                 value='Plays the song in your queue that has the given number', inline=False)
            self.embed.add_field(name='mb queue_reverse:',
                                 value='Reverses your queue', inline=False)
            self.embed.add_field(name='mb queue_shuffle: ',
                                 value='Shuffles your queue randomly', inline=False)

        # Andere commands pagina
        if self.current_page == 4:
            self.embed = discord.Embed(colour=discord.Colour.dark_embed(),
                                       title='Other commands:')
            self.embed.add_field(name='mb lyrics', value='Gets lyrics of the current song', inline=False)
            self.embed.add_field(name='mb volume [number from 0 to 100]',
                                 value='Sets bot volume, pass 0 to mute the bot', inline=False)

    # Knop voor help pagina
    @discord.ui.button(label='Help', style=discord.ButtonStyle.primary)
    async def help_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.current_page = 1
        await self.update_message()

    # Knop voor play pagina
    @discord.ui.button(label='Play', style=discord.ButtonStyle.primary)
    async def play_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.current_page = 2
        await self.update_message()

    # Knop voor queue pagina
    @discord.ui.button(label='Queue', style=discord.ButtonStyle.primary)
    async def queue_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.current_page = 3
        await self.update_message()

    # Knop voor andere commands pagina
    @discord.ui.button(label='Other', style=discord.ButtonStyle.primary)
    async def other_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.current_page = 4
        await self.update_message()


# class voor embed om lied te kiezen
class PicksongEmbed(discord.ui.View):
    def __init__(self, ctx, search_string, bot, add_to_qeue, qeue):  # noqa
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
        self.qeue = qeue

    # zelfde als current maar herhaalt wegens problemen
    async def current(self):
        data_request = youtube.videos().list(part='snippet', id=self.chosen_id)
        duration_request = youtube.videos().list(part='contentDetails', id=self.chosen_id)
        duration_response = duration_request.execute()
        data_request_response = data_request.execute()

        # lied naam
        song_name = data_request_response['items'][0]['snippet']['title']

        # lied artiest
        artist = data_request_response['items'][0]['snippet']['channelTitle']

        # lied lengte
        duration = duration_response['items'][0]['contentDetails']['duration'][2:].replace('M', ':').replace('S', '')
        if ':' not in duration:
            duration = f'{duration} seconds'

        # als lied 1 cijfer na : heeft bijv 3:7 verander dit in 3:07
        elif duration[-2] == ':':
            last_duration_letter = duration[-1]
            duration = duration.replace(duration[-1], '0')
            duration = duration + last_duration_letter

        # als lied precies een min ** n is bijv: 6:
        elif duration[-1] == ':':
            duration = f'{duration}{0}{0}'

        # release date
        release_date = data_request_response['items'][0]['snippet']['publishedAt'][:10]

        # thumbnail, probeer hoge kwaliteit te krijgen maar als deze niet bestaat ga dan steeds lager
        try:
            thumbnail = data_request_response['items'][0]['snippet']['thumbnails']['maxres']['url']
        except Exception:  # noqa
            try:
                thumbnail = data_request_response['items'][0]['snippet']['thumbnails']['high']['url']
            except Exception: # noqa
                try:
                    thumbnail = data_request_response['items'][0]['snippet']['thumbnails']['standard']['url']
                except Exception: # noqa
                    try:
                        thumbnail = data_request_response['items'][0]['snippet']['thumbnails']['default']['url']
                    except Exception:  # noqa
                        try:
                            thumbnail = data_request_response['items'][0]['snippet']['thumbnails']['medium']['url']
                        except Exception:  # noqa
                            await self.ctx.send('could not get thumbnail')
                            thumbnail = None

        # embed zelf
        embed = discord.Embed(
            colour=discord.Colour.dark_embed(),
            title='Current song\'s info:',
        )
        embed.set_thumbnail(url=thumbnail)
        embed.add_field(name='Song name: ', value=song_name, inline=False)
        embed.add_field(name='Song duration: ', value=duration, inline=False)
        embed.add_field(name='Song artist: ', value=artist, inline=False)
        embed.add_field(name='Song release date: ', value=release_date, inline=False)
        embed.add_field(name='Song url:', value=f'https://www.youtube.com/watch?v={self.chosen_id}')
        time_ms = str(datetime.datetime.now())[11:]
        time_final = time_ms[:8]
        embed.set_footer(text=f' Requested by: {self.ctx.message.author} at: {time_final}')
        await self.ctx.send(embed=embed)

    # Functie die embed met buttons stuurt
    async def send(self):
        embed = await self.create_embed()
        self.message = await self.ctx.send(embed=embed, view=self)  # update bericht

    # Functie die message delete en lied toevoegd aan queue
    async def update_message(self):
        global queue, song_to_play
        if self.add_to_qeue is True:
            queue.append(f'https://www.youtube.com/watch?v={self.chosen_id}')
            await self.message.delete()
        elif self.add_to_qeue == 'front':
            queue.insert(0, f'https://www.youtube.com/watch?v={self.chosen_id}')
            await self.message.delete()
        else:
            await self.message.delete()
            song_to_play = f'https://www.youtube.com/watch?v={self.chosen_id}'

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
        for song in self.song_ids:
            name_request = youtube.videos().list(part='snippet', id=song)
            name_request_response = name_request.execute()
            song_name = name_request_response['items'][0]['snippet']['title']
            artist_name = name_request_response['items'][0]['snippet']['channelTitle']
            self.song_options.append(f'{song_name} by: {artist_name}')

        # voeg tekst toe aan embed
        for song_option in self.song_options:
            embed.add_field(name='',
                            value=f'{self.song_counter}.{song_option}',
                            inline=False)
            self.song_counter += 1
        return embed

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


# class voor embed van queue_list
class PaginationView(discord.ui.View):
    current_page = 1
    seperator = 20
    embed_counter = 0
    data = None  # data = queue

    def __init__(self):
        super().__init__()
        self.message = None

    # Functie voor het sturen van de embed
    async def send(self, ctx):
        global data_len
        data_len = len(self.data)  # lengte van qeue
        self.message = await ctx.send(view=self)  # stuur bericht
        await self.update_message(self.data[:self.seperator])  # update bericht tot aan seperator 20 * aantal pagina's

    # Functie voor het updaten van de embed
    async def update_message(self, data):
        self.update_buttons()  # update knoppen
        await self.message.edit(embed=self.create_embed(data), view=self)  # bewerk bericht

    # Functie voor het muten van buttons
    def update_buttons(self):
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.previous_button.disabled = True
        else:
            self.first_page_button.disabled = False
            self.previous_button.disabled = False
        if data_len % 20 == 0:
            if self.current_page == int(len(self.data) / self.seperator):
                self.next_button.disabled = True
                self.last_page_button.disabled = True
            else:
                self.next_button.disabled = False
                self.last_page_button.disabled = False
        else:
            if self.current_page == int(len(self.data) / self.seperator) + 1:
                self.next_button.disabled = True
                self.last_page_button.disabled = True
            else:
                self.next_button.disabled = False
                self.last_page_button.disabled = False

    # Functie voor het tekst toevoegen aan embed
    def create_embed(self, data):
        embed_counter = 0
        embed = discord.Embed(title='Current qeue:', colour=discord.Colour.dark_embed())
        current_page = self.current_page
        if data_len % 20 == 0:
            max_page = int(data_len / self.seperator)
        else:
            max_page = int(data_len / self.seperator) + 1
        for song_name in data:
            embed.add_field(name='', value=song_name, inline=False)
            embed_counter += 1
        embed.set_footer(text=f'page {current_page}/{max_page}')
        return embed

    @discord.ui.button(label='<<', style=discord.ButtonStyle.primary)
    async def first_page_button(self, interaction: discord.Interaction, button: discord.Button): # noqa
        await interaction.response.defer() # noqa
        self.current_page = 1
        until_item = self.current_page * self.seperator  # laatste item dat moet worden gedisplayed
        from_item = until_item - self.seperator  # eerste item dat moet worden gedisplayed
        await self.update_message(self.data[from_item:until_item])

    @discord.ui.button(label='<', style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.current_page -= 1
        until_item = self.current_page * self.seperator
        from_item = until_item - self.seperator
        await self.update_message(self.data[from_item:until_item])

    @discord.ui.button(label='>', style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.current_page += 1
        until_item = self.current_page * self.seperator
        from_item = until_item - self.seperator
        await self.update_message(self.data[from_item:until_item])

    @discord.ui.button(label='>>', style=discord.ButtonStyle.primary)
    async def last_page_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        if data_len % 20 == 0:
            self.current_page = int(len(self.data) / self.seperator)
        else:
            self.current_page = int(len(self.data) / self.seperator) + 1
        until_item = self.current_page * self.seperator
        from_item = until_item - self.seperator
        await self.update_message(self.data[from_item:until_item])


# hoofdclass voor TicTacToe minigame
class TicTacToe(discord.ui.View):
    def __init__(self, ctx, cross_player, team_cross_id, square_player, team_square_id):
        super().__init__()
        self.ctx = ctx
        self.cross_player = cross_player
        self.team_cross_id = team_cross_id
        self.square_player = square_player
        self.start_message = None
        self.team_square_id = team_square_id
        self.view = None
        self.embed = None
        self.message = None
        self.mention = None
        self.winner = None
        self.turn = 'cross'
        self.squares = squares

    # Uitdagingsbericht
    async def challenge(self):
        self.start_message =\
            await self.ctx.send(f'{self.square_player} has been challenged to tic tac toe by: {self.cross_player}')

    # Stuur embed
    async def send_embed(self):
        global empty_ttt_square
        self.embed = discord.Embed(title='', colour=discord.Colour.dark_embed())
        self.embed.add_field(name='', value=empty_ttt_square)
        self.embed.add_field(name='', value=empty_ttt_square)
        self.embed.add_field(name='', value=empty_ttt_square)
        self.embed.add_field(name='', value=empty_ttt_square)
        self.embed.add_field(name='', value=empty_ttt_square)
        self.embed.add_field(name='', value=empty_ttt_square)
        self.embed.add_field(name='', value=empty_ttt_square)
        self.embed.add_field(name='', value=empty_ttt_square)
        self.embed.add_field(name='', value=empty_ttt_square)
        self.message = await self.ctx.send(embed=self.embed)
        await self.first_run()

    # Update embed
    async def update_game(self, message, turn):
        square_to_draw = None
        if turn == 'cross':
            self.turn = 'square'
            self.mention = self.cross_player
        else:
            self.turn = 'cross'
            self.mention = self.square_player
        await message.delete()
        self.embed = discord.Embed(title='', colour=discord.Colour.dark_embed())
        for value in self.squares.values():
            if value == 'empty':
                square_to_draw = empty_ttt_square
            elif value == 'cross':
                square_to_draw = cross_ttt_square
            elif value == 'square':
                square_to_draw = square_ttt_square
            self.embed.add_field(name='', value=square_to_draw)
        self.message = await self.ctx.send(embed=self.embed)
        rows = Rows(self.ctx, self.message, self.embed, self.turn,
                    self.team_cross_id, self.team_square_id,
                    self.cross_player, self.square_player)
        rows.mute_buttons()
        print('after_mute_function')
        await self.message.edit(content=f'{self.mention}\'s turn', embed=self.embed,
                                view=rows)  # noqa
        await self.checkwin()

    # Check of iemand heeft gewonnen
    async def checkwin(self):
        # horizontaal
        if squares.get('1_1') == squares.get('1_2') == squares.get('1_3') and squares.get('1_1') != 'empty':
            print('winner')
            self.winner = squares.get('1_1')
            await self.win_embed()
        elif squares.get('2_1') == squares.get('2_2') == squares.get('2_3') and squares.get('2_1') != 'empty':
            print('winner')
            self.winner = squares.get('2_1')
            await self.win_embed()
        elif squares.get('3_1') == squares.get('3_2') == squares.get('3_3') and squares.get('3_1') != 'empty':
            print('winner')
            self.winner = squares.get('3_1')
            await self.win_embed()

        # verticaal
        elif squares.get('1_1') == squares.get('2_1') == squares.get('3_1') and squares.get('1_1') != 'empty':
            print('winner')
            self.winner = squares.get('1_2')
            await self.win_embed()
        elif squares.get('1_2') == squares.get('2_2') == squares.get('3_2') and squares.get('1_2') != 'empty':
            print('winner')
            self.winner = squares.get('1_2')
            await self.win_embed()
        elif squares.get('1_3') == squares.get('2_3') == squares.get('3_3') and squares.get('1_3') != 'empty':
            print('winner')
            self.winner = squares.get('1_3')
            await self.win_embed()

        # diagonaal
        elif squares.get('1_1') == squares.get('2_2') == squares.get('3_3') and squares.get('1_1') != 'empty':
            print('winner')
            self.winner = squares.get('1_1')
            await self.win_embed()
        elif squares.get('1_3') == squares.get('2_2') == squares.get('3_1') and squares.get('1_3') != 'empty':
            print('winner')
            self.winner = squares.get('1_3')
            await self.win_embed()

        # gelijkspel
        elif 'empty' not in squares.values():
            await self.tie()

    # Als er niemand heeft gewonnen check voor gelijkspel
    async def tie(self):
        global squares
        tie_embed = discord.Embed(title='Tie')
        tie_embed.add_field(name='', value='The game ended in a tie.')
        await self.message.edit(content='Game done', embed=self.embed, view=None)
        await self.ctx.send(embed=tie_embed)
        squares = {
            '1_1': 'empty',
            '1_2': 'empty',
            '1_3': 'empty',
            '2_1': 'empty',
            '2_2': 'empty',
            '2_3': 'empty',
            '3_1': 'empty',
            '3_2': 'empty',
            '3_3': 'empty',
        }

    # Stuur win embed
    async def win_embed(self):
        global squares
        print(f'Winner is: {self.winner}')
        win_embed = discord.Embed(title='Winner!')
        if self.winner == 'cross':
            winner_text = f'{self.cross_player} (team cross)'
            loser_text = f'{self.square_player} (team square)'
        else:
            winner_text = f'{self.square_player} (team square)'
            loser_text = f'{self.cross_player} (team cross)'
        win_embed.add_field(name='Winner:', value=winner_text)
        win_embed.add_field(name='Loser:', value=loser_text)
        await self.message.edit(content='Game done', embed=self.embed, view=None)
        await self.ctx.send(embed=win_embed)
        squares = {
            '1_1': 'empty',
            '1_2': 'empty',
            '1_3': 'empty',
            '2_1': 'empty',
            '2_2': 'empty',
            '2_3': 'empty',
            '3_1': 'empty',
            '3_2': 'empty',
            '3_3': 'empty',
        }

    # first run van TTT
    async def first_run(self):
        rows = Rows(self.ctx, self.message, self.embed, self.turn,
                    self.team_cross_id, self.team_square_id,
                    self.cross_player, self.square_player)
        rows.mute_buttons()
        await self.message.edit(content=f'{self.cross_player}\'s turn', embed=self.embed,
                                view=rows)

    @discord.ui.button(label='Accept', style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction):
        global delete_buttons
        delete_buttons = True
        interaction_id = interaction.user.id
        await self.start_message.delete()
        if str(interaction_id) == str(self.team_square_id):
            await self.send_embed()

    @discord.ui.button(label='Reject', style=discord.ButtonStyle.red)
    async def reject_button(self, interaction: discord.Interaction):
        global delete_buttons
        interaction_id = interaction.user.id
        if str(interaction_id) == str(self.team_square_id):
            await self.send_embed()
        delete_buttons = True
        await self.start_message.delete()


# Subclass van TTT die regelt voor de 3 rows buttons
class Rows(discord.ui.View):
    def __init__(self, ctx, message, embed, turn, team_cross_id, team_square_id, team_cross_player, team_square_player):
        super().__init__()
        self.ctx = ctx
        self.message = message
        self.embed = embed
        self.turn = turn
        self.team_cross_id = team_cross_id
        self.team_square_id = team_square_id
        self.team_cross_player = team_cross_player
        self.team_square_player = team_square_player

    # Functie voor het muten van buttons
    def mute_buttons(self):
        print('mute_function')
        print(squares)
        if squares.get('1_1') != 'empty' and squares.get('1_2') != 'empty' and squares.get('1_3') != 'empty':
            self.row_1_button.disabled = True
        if squares.get('2_1') != 'empty' and squares.get('2_2') != 'empty' and squares.get('2_3') != 'empty':
            self.row_2_button.disabled = True
        if squares.get('3_1') != 'empty' and squares.get('3_2') != 'empty' and squares.get('3_3') != 'empty':
            self.row_3_button.disabled = True

    @discord.ui.button(label='Row 1', style=discord.ButtonStyle.primary)
    async def row_1_button(self, interaction: discord.Interaction):
        print(self.row_1_button.disabled)
        if self.turn == 'cross' and interaction.user.id == self.team_cross_id or self.turn == 'square' and str(
                interaction.user.id) == self.team_square_id:
            row_1 = Row1(self.ctx, self.embed, self.message, self.turn,
                         self.team_cross_id, self.team_square_id,
                         self.team_cross_player, self.team_square_player)
            row_1.mute_buttons()
            await interaction.response.edit_message(embed=self.embed, view=row_1)  # noqa

    @discord.ui.button(label='Row 2', style=discord.ButtonStyle.primary)
    async def row_2_button(self, interaction: discord.Interaction):
        print(self.turn)
        print(interaction.user.id)
        print(self.team_square_id)
        if self.turn == 'cross' and interaction.user.id == self.team_cross_id or self.turn == 'square' and str(
                interaction.user.id) == self.team_square_id:
            row_2 = Row2(self.ctx, self.embed, self.message, self.turn,
                         self.team_cross_id, self.team_square_id,
                         self.team_cross_player, self.team_square_player)
            row_2.mute_buttons()
            await interaction.response.edit_message(embed=self.embed, view=row_2)  # noqa

    @discord.ui.button(label='Row 3', style=discord.ButtonStyle.primary)
    async def row_3_button(self, interaction: discord.Interaction):
        if self.turn == 'cross' and interaction.user.id == self.team_cross_id or self.turn == 'square' and str(
                interaction.user.id) == self.team_square_id:
            row_3 = Row3(self.ctx, self.embed, self.message, self.turn,
                         self.team_cross_id, self.team_square_id,
                         self.team_cross_player, self.team_square_player)
            row_3.mute_buttons()
            await interaction.response.edit_message(embed=self.embed, view=row_3)  # noqa


# Subclass van TTT die regelt voor de 3 tiles van row 1
class Row1(discord.ui.View):
    def __init__(self, ctx, embed, message, turn, team_cross_id, team_square_id, cross_player, square_player):
        super().__init__()
        self.ctx = ctx
        self.squares = squares
        self.embed = embed
        self.message = message
        self.turn = turn
        self.team_cross_id = team_cross_id
        self.team_square_id = team_square_id
        self.cross_player = cross_player
        self.square_player = square_player

    # Functie voor het muten van buttons
    def mute_buttons(self):
        if squares.get('1_1') != 'empty':
            self.r1_t1.disabled = True
        if squares.get('1_2') != 'empty':
            self.r1_t2.disabled = True
        if squares.get('1_3') != 'empty':
            self.r1_t3.disabled = True

    @discord.ui.button(label='<', style=discord.ButtonStyle.primary)
    async def back_button(self, interaction: discord.Interaction):
        if self.turn == 'cross' and interaction.user.id == self.team_cross_id or self.turn == 'square' and str(
                interaction.user.id) == self.team_square_id:
            rows = Rows(self.ctx, self.message, self.embed, self.turn,
                        self.team_cross_id, self.team_square_id,
                        self.cross_player, self.square_player)
            await interaction.response.edit_message(embed=self.embed, view=rows)  # noqa
            rows.mute_buttons()

    @discord.ui.button(label='Tile 1', style=discord.ButtonStyle.primary)
    async def r1_t1(self, interaction: discord.Interaction):
        print(self.turn)
        print(interaction.user.id)
        print(self.team_square_id)
        print(self.team_cross_id)
        await interaction.response.defer()  # noqa
        if self.turn == 'cross' and interaction.user.id == self.team_cross_id and squares.get('1_1') == 'empty':
            squares.update({'1_1': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)
        elif self.turn == 'square' and str(interaction.user.id) == self.team_square_id and squares.get(
                '1_1') == 'empty':
            squares.update({'1_1': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)

    @discord.ui.button(label='Tile 2', style=discord.ButtonStyle.primary)
    async def r1_t2(self, interaction: discord.Interaction):
        await interaction.response.defer()  # noqa
        if self.turn == 'cross' and interaction.user.id == self.team_cross_id and squares.get('1_2') == 'empty':
            squares.update({'1_2': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)
        elif self.turn == 'square' and str(interaction.user.id) == self.team_square_id and squares.get(
                '1_2') == 'empty':
            squares.update({'1_2': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)

    @discord.ui.button(label='Tile 3', style=discord.ButtonStyle.primary)
    async def r1_t3(self, interaction: discord.Interaction):
        print(self.turn)
        print(interaction.user.id)
        print(self.team_square_id)
        print(self.team_cross_id)
        await interaction.response.defer()  # noqa
        if self.turn == 'cross' and interaction.user.id == self.team_cross_id and squares.get('1_3') == 'empty':
            squares.update({'1_3': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)
        elif self.turn == 'square' and str(interaction.user.id) == self.team_square_id and squares.get(
                '1_3') == 'empty':
            squares.update({'1_3': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)


# Subclass van TTT die regelt voor de 3 tiles van row 2
class Row2(discord.ui.View):
    def __init__(self, ctx, embed, message, turn, team_cross_id, team_square_id, cross_player, square_player):
        super().__init__()
        self.ctx = ctx
        self.squares = squares
        self.embed = embed
        self.message = message
        self.turn = turn
        self.team_cross_id = team_cross_id
        self.team_square_id = team_square_id
        self.cross_player = cross_player
        self.square_player = square_player

    # Functie voor het muten van buttons
    def mute_buttons(self):
        if squares.get('2_1') != 'empty':
            self.r2_t1.disabled = True
        if squares.get('2_2') != 'empty':
            self.r2_t2.disabled = True
        if squares.get('2_3') != 'empty':
            self.r2_t3.disabled = True

    @discord.ui.button(label='<', style=discord.ButtonStyle.primary)
    async def back_button(self, interaction: discord.Interaction):
        rows = Rows(self.ctx, self.message, self.embed, self.turn,
                    self.team_cross_id, self.team_square_id,
                    self.cross_player, self.square_player)
        await interaction.response.edit_message(embed=self.embed, view=rows)  # noqa
        rows.mute_buttons()

    @discord.ui.button(label='Tile 1', style=discord.ButtonStyle.primary)
    async def r2_t1(self, interaction: discord.Interaction):
        await interaction.response.defer()  # noqa
        if self.turn == 'cross' and interaction.user.id == self.team_cross_id and squares.get('2_1') == 'empty':
            squares.update({'2_1': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)
        elif self.turn == 'square' and str(interaction.user.id) == self.team_square_id and squares.get(
                '2_1') == 'empty':
            squares.update({'2_1': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)

    @discord.ui.button(label='Tile 2', style=discord.ButtonStyle.primary)
    async def r2_t2(self, interaction: discord.Interaction):
        await interaction.response.defer()  # noqa
        if self.turn == 'cross' and interaction.user.id == self.team_cross_id and squares.get('2_2') == 'empty':
            squares.update({'2_2': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)
        elif self.turn == 'square' and str(interaction.user.id) == self.team_square_id and squares.get(
                '2_2') == 'empty':
            squares.update({'2_2': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)

    @discord.ui.button(label='Tile 3', style=discord.ButtonStyle.primary)
    async def r2_t3(self, interaction: discord.Interaction):
        await interaction.response.defer()  # noqa
        if self.turn == 'cross' and interaction.user.id == self.team_cross_id and squares.get('2_3') == 'empty':
            squares.update({'2_3': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)
        elif self.turn == 'square' and str(interaction.user.id) == self.team_square_id and squares.get(
                '2_3') == 'empty':
            squares.update({'2_3': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)


# Subclass van TTT die regelt voor de 3 tiles van row 3
class Row3(discord.ui.View):
    def __init__(self, ctx, embed, message, turn, team_cross_id, team_square_id, cross_player, square_player):
        super().__init__()
        self.ctx = ctx
        self.squares = squares
        self.embed = embed
        self.message = message
        self.turn = turn
        self.team_cross_id = team_cross_id
        self.team_square_id = team_square_id
        self.cross_player = cross_player
        self.square_player = square_player

    # Functie voor het muten van buttons
    def mute_buttons(self):
        if squares.get('3_1') != 'empty':
            self.r3_t1.disabled = True
        if squares.get('3_2') != 'empty':
            self.r3_t2.disabled = True
        if squares.get('3_3') != 'empty':
            self.r3_t3.disabled = True

    @discord.ui.button(label='<', style=discord.ButtonStyle.primary)
    async def back_button(self, interaction: discord.Interaction):
        rows = Rows(self.ctx, self.message, self.embed, self.turn,
                    self.team_cross_id, self.team_square_id,
                    self.cross_player, self.square_player)
        rows.mute_buttons()
        await interaction.response.edit_message(embed=self.embed, view=rows)  # noqa

    @discord.ui.button(label='Tile 1', style=discord.ButtonStyle.primary)
    async def r3_t1(self, interaction: discord.Interaction):
        await interaction.response.defer()  # noqa
        if self.turn == 'cross' and interaction.user.id == self.team_cross_id and squares.get('3_1') == 'empty':
            squares.update({'3_1': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)
        elif self.turn == 'square' and str(interaction.user.id) == self.team_square_id and squares.get(
                '3_1') == 'empty':
            squares.update({'3_1': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)

    @discord.ui.button(label='Tile 2', style=discord.ButtonStyle.primary)
    async def r3_t2(self, interaction: discord.Interaction):
        await interaction.response.defer()  # noqa
        if self.turn == 'cross' and interaction.user.id == self.team_cross_id and squares.get('3_2') == 'empty':
            squares.update({'3_2': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)
        elif self.turn == 'square' and str(interaction.user.id) == self.team_square_id and squares.get(
                '3_2') == 'empty':
            squares.update({'3_2': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)

    @discord.ui.button(label='Tile 3', style=discord.ButtonStyle.primary)
    async def r3_t3(self, interaction: discord.Interaction):
        await interaction.response.defer()  # noqa
        if self.turn == 'cross' and interaction.user.id == self.team_cross_id and squares.get('3_3') == 'empty':
            squares.update({'3_3': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)
        elif self.turn == 'square' and str(interaction.user.id) == self.team_square_id and squares.get(
                '3_3') == 'empty':
            squares.update({'3_3': self.turn})
            ttt = TicTacToe(self.ctx, self.cross_player, self.team_cross_id, self.square_player, self.team_square_id)
            await TicTacToe.update_game(ttt, self.message, self.turn)


# Main game loop
def main():
    # Setup
    intents = discord.Intents.default()  # standaard settings
    intents.message_content = True  # mag berichtinhoud lezen
    bot = commands.Bot(command_prefix='mb ', intents=intents)

    # Word getriggerd als bot online gaat
    @bot.event
    async def on_ready():
        print(str(bot.user) + ' online')
        kill_channel = bot.get_channel(1175212011060199524)
        await kill_channel.send(str(kill_code))
        await bot.change_presence(activity=discord.Game(name='Waiting for a song to play...'))

    # Call Help class met pagina'a die info bevatten over alle commands
    @bot.command()
    async def helpme(ctx):
        help_request = HelpEmbed()  # call embed functie om help embed te maken
        await help_request.send_embed(ctx)

    # Command voor het joinen van een vc door de bot
    @bot.command()
    async def join(ctx):
        voice_channel = ctx.author.voice.channel
        vc_id = voice_channel.id
        vc_name = '<' + '#' + str(vc_id) + '>'
        if ctx.voice_client is None:  # als bot niet in vc is
            await ctx.send('Joining voice channel: ' + vc_name)
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)
            await ctx.send(f'Moved to: {vc_name}')

    # Command voor het aanspassen van het volume van de spelende muziek
    @bot.command()
    async def volume(ctx, content):
        global first_run, song_to_play
        voice = ctx.voice_client
        volume_to_use = int(content) / 100
        if voice is None:
            return await ctx.send('Multibot is not in a voicechannel.')
        if not 101 > int(content) >= 0:
            return await ctx.send('Please provide a volume between 0 and 100.')
        if first_run is False:
            ctx.voice_client.source.volume = volume_to_use * 2
        else:
            voice.source = discord.PCMVolumeTransformer(voice.source, volume=volume_to_use * 2)
            first_run = False
        await ctx.send(f'Volume changed to {content}%')

    # Command die spelende audio pauseerd
    @bot.command()
    async def pause(ctx):
        ctx.voice_client.pause()

    # Command die audio weer laat spelen
    @bot.command()
    async def resume(ctx):
        ctx.voice_client.resume()

    # Command die een lied skipt waarna play_from_qeue uit de queue gaat spelen
    @bot.command()
    async def skip(ctx):
        global queue
        ctx.voice_client.stop()

    # Comman die bot uit de vc haalt
    @bot.command()
    async def disconnect(ctx):
        await ctx.voice_client.disconnect()

    # Command die data verzamelt over huidig lied en dit in een embed verstuurt
    @bot.command()
    async def current(ctx):
        global info_status, index_error
        # Als deze functie word opgreroepen dmv de qeue_info functie
        if info_status is True:
            video_id = song_link[32:]  # alles na 32ste letter
            info_status = False
        else:
            video_id = song_to_play[32:]
        data_request = youtube.videos().list(part='snippet', id=video_id)
        duration_request = youtube.videos().list(part='contentDetails', id=video_id)
        data_request_response = data_request.execute()
        duration_response = duration_request.execute()

        # lied naam
        try:
            song_name = data_request_response['items'][0]['snippet']['title']
        except IndexError:
            index_error = True
            return index_error

        # lied artiest
        artist = data_request_response['items'][0]['snippet']['channelTitle']

        # Release date
        release_date = data_request_response['items'][0]['snippet']['publishedAt'][:10]

        # lied duratie
        duration = duration_response['items'][0]['contentDetails']['duration'][2:].replace('M', ':').replace('S', '')
        if ':' not in duration:
            duration = f'{duration} seconds'
        elif duration[-2] == ':':  # als lied 1 cijfer na : heeft bijv 3:7 verander dit in 3:07
            last_duration_letter = duration[-1]
            duration = duration.replace(duration[-1], '0')
            duration = duration + last_duration_letter
        elif duration[-1] == ':':  # als lied precies een min ** n is bijv: 6:
            duration = f'{duration}{0}{0}'

        # Thumnail
        # probeer hoge kwaliteit te krijgen en pak anders een lagere kwaliteit
        try:
            thumbnail = data_request_response['items'][0]['snippet']['thumbnails']['maxres']['url']
        except Exception:  # noqa
            try:
                thumbnail = data_request_response['items'][0]['snippet']['thumbnails']['high']['url']
            except Exception: # noqa
                try:
                    thumbnail = data_request_response['items'][0]['snippet']['thumbnails']['standard']['url']
                except Exception: # noqa
                    try:
                        thumbnail = data_request_response['items'][0]['snippet']['thumbnails']['default']['url']
                    except Exception:  # noqa
                        try:
                            thumbnail = data_request_response['items'][0]['snippet']['thumbnails']['medium']['url']
                        except Exception:  # noqa
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
        embed.add_field(name='Song artist: ', value=artist, inline=False)
        embed.add_field(name='Song release date: ', value=release_date, inline=False)
        embed.add_field(name='Song url:', value=song_to_play)

        # Aanvraag tijd
        time_ms = str(datetime.datetime.now())[11:]
        time_final = time_ms[:8]
        embed.set_footer(text=f' Requested by: {ctx.message.author} at: {time_final}')
        await ctx.send(embed=embed)

    # Command die een speellijst speelt met de Veronica top 1000
    @bot.command()
    async def top1000(ctx):
        global queue
        if ctx.voice_client is None:
            await join(ctx)
        playlist_url = 'https://www.youtube.com/playlist?list=PLvubIPSEU2C7zVgsSJT4N-qfqol_boAm6'
        pl_id = playlist_url[38:]
        if queue is []:
            add_to_queue(pl_id, insert_at_front=False)
        await ctx.send('Added top1000 to qeue')
        if ctx.voice_client.is_playing() is False:
            await play_from_queue(ctx)

    # Command die een enkel lied afspeelt, als er al iets speelt wordt dit gestopt
    @bot.command()
    async def play(ctx, *, play_url):
        global queue, song_to_play, source, fetch_message, first_run
        play_url_yt_track = play_url[:32]
        if play_url_yt_track == 'https://www.youtube.com/watch?v=':
            if play_url[-5:-2] == '&t=':
                play_url = play_url[:-5]
            await join(ctx)
            play_song(ctx, play_url)
            await current(ctx)
            await set_status()
            if index_error is True:
                return await ctx.send('Please provide a valid youtube url.')
            first_run = True
        elif play_url[8:33] == 'www.youtube.com/playlist?':
            return await ctx.send('Please provide a search qeury, a video url or use the playlist commands.')
        else:
            if ctx.author.voice is None:
                return await ctx.send('You are not in a voice channel.')
            song_to_play = None
            fetch_message = await ctx.send('Fetching results'
                                           ', please wait for the embed with options to spawn to avoid errors.')
            search_qeury = play_url
            song_embed = PicksongEmbed(ctx, search_qeury, bot, False, queue)
            await song_embed.send()
            while True:
                if song_to_play is None:
                    await asyncio.sleep(0.1)
                else:
                    await fetch_message.delete()
                    await join(ctx)
                    play_song(ctx, song_to_play)
                    await current(ctx)
                    await set_status()
                    break

    # Command voor het spelen van een playlist
    @bot.command()
    async def play_playlist(ctx, pl_url):  # functie die playlist items in een qeue plaatst
        global queue
        if queue:
            return await ctx.send('There already is a qeue, please use the "qeue_add_playlist" or'
                                  ' "qeue_add_playlist_front" to add playlists to your qeue')
        site_name = pl_url[8:33]
        playlist_id = pl_url[38:]
        if site_name != 'www.youtube.com/playlist?':
            await ctx.send('Please provide a valid playlist url.')
        if ctx.author.voice is None:
            return await ctx.send('You are not in a vc.')
        await join(ctx)
        queue = add_to_queue(playlist_id, insert_at_front=False)
        await play_from_queue(ctx)

    # Command voor het toevoegen van een lied aan de queue
    @bot.command()
    async def qeue_add(ctx, *, qeue_url):  # voeg een url toe aan qeue
        global queue, song_to_play, fetch_message
        print(queue)
        if not queue:
            queue = []
        if qeue_url[:32] == 'https://www.youtube.com/watch?v=':
            if qeue_url not in queue:
                if qeue_url[-5:-2] == '&t=':
                    qeue_url = qeue_url[:-5]
                video_id = qeue_url[32:]
                try:
                    song_name = get_song_name(video_id)
                    queue.append(qeue_url)
                    await ctx.send(f'added {song_name} to qeue')
                except IndexError:
                    return await ctx.send('PLeade provide a valid youtube url.')
                if ctx.voice_client is None:
                    await join(ctx)
                    await play_from_queue(ctx)
        elif qeue_url[8:33] == 'www.youtube.com/playlist?':
            return await ctx.send('PLease provide a search qeury, a video url or use the playlist commands.')
        else:
            if ctx.author.voice is None:
                return await ctx.send('You are not in a voice channel.')
            if ctx.voice_client is None:
                await join(ctx)
            fetch_message = await ctx.send('Fetching results,'
                                           ' please wait for the embed with options to spawn to avoid errors.')
            qeue_len = len(queue)
            search_qeury = qeue_url
            song_embed = PicksongEmbed(ctx, search_qeury, bot, True, queue)
            await song_embed.send()
            while True:
                if len(queue) == qeue_len:
                    await asyncio.sleep(0.1)
                else:
                    await fetch_message.delete()
                    break
            song_to_play = queue[-1]
            song_id = song_to_play[32:]
            song_title = get_song_name(song_id)
            await ctx.send(f'Added {song_title} to qeue.')
            await play_from_queue(ctx)

    # Command voor het toevoegen van een lied aan de voorkant van queue
    @bot.command()
    async def qeue_add_next(ctx, *, qeue_add_url):  # voeg een url toe aan qeue maar vorran ipv achteraan
        global queue, fetch_message, song_to_play
        if qeue_add_url[:32] == 'https://www.youtube.com/watch?v=':
            if ctx.author.voice is None:
                return await ctx.send('You are not in a voice chat, please join one to use this command.')
            if qeue_add_url not in queue:
                if qeue_add_url[-5:-2] == '&t=':
                    qeue_add_url = qeue_add_url[:-5]
                    print(qeue_add_url)
                try:
                    song_name = get_song_name(qeue_add_url[32:])
                    queue.insert(0, qeue_add_url)
                except IndexError:
                    return await ctx.send('Please provide a valid youtube url')
                await ctx.send(f'added {song_name} as next song in your qeue.')
                if ctx.voice_client is None:
                    await join(ctx)
                    await play_from_queue(ctx)
            else:
                await ctx.send('This song is already in your qeue.')
        elif qeue_add_url[8:33] == 'www.youtube.com/playlist?':
            return await ctx.send('PLease provide a search qeury, a video url or use the playlist commands.')
        else:
            if ctx.author.voice is None:
                return await ctx.send('You are not in a voice channel.')
            if ctx.voice_client is None:
                await join(ctx)
            fetch_message = await ctx.send('Fetching results,'
                                           ' please wait for the embed with options to spawn to avoid errors.')
            qeue_len = len(queue)
            search_qeury = qeue_add_url
            song_embed = PicksongEmbed(ctx, search_qeury, bot, 'front', queue)
            await song_embed.send()
            while True:
                if len(queue) == qeue_len:
                    await asyncio.sleep(0.5)
                else:
                    await fetch_message.delete()
                    break
            song_to_play = queue[0]
            song_id = song_to_play[32:]
            song_title = get_song_name(song_id)
            await ctx.send(f'Added {song_title} to qeue.')
            await play_from_queue(ctx)

    # Command voor het toevoegen van een playlist aan de queue
    @bot.command()
    async def qeue_add_playlist(ctx, content):
        global queue
        if content[8:33] != 'www.youtube.com/playlist?':
            return await ctx.send('Please provide a valid youtube url')
        playlist_id = content[38:]
        add_to_queue(playlist_id, insert_at_front=False)
        playlist_name = youtube.playlists().list(id=playlist_id,
                                                 part='snippet')
        playlist_name_response = playlist_name.execute()
        playlist_name = playlist_name_response['items'][0]['snippet']['title']
        await ctx.send(f'Added playlist to qeue: {playlist_name}')

    # Command voor het toevoegen van een playlist aan het begin van de queue
    @bot.command()
    async def qeue_add_playlist_front(ctx, content):
        global queue
        if content[8:33] != 'www.youtube.com/playlist?':
            return await ctx.send('Please provide a valid youtube url')
        playlist_id = content[38:]
        add_to_queue(playlist_id, insert_at_front=True)
        playlist_name = youtube.playlists().list(id=playlist_id,
                                                 part='snippet')
        playlist_name_response = playlist_name.execute()
        playlist_name = playlist_name_response['items'][0]['snippet']['title']
        await ctx.send(f'Added playlist to front of the qeue: {playlist_name}')

    # Functie voor het wipen van de queue
    @bot.command()
    async def qeue_clear(ctx):
        global queue
        queue = []
        await ctx.send('Queue cleared')

    # Command die een lied, aangegeven via een link of queue nummer naar het begin van de queue moved
    @bot.command()
    async def qeue_front(ctx, content):
        global queue
        song_number = 0
        number = False
        link = False
        if content in queue:
            link = True
        if int(content) <= len(queue):
            song_number = int(content) - 1
            number = True
        if queue and number is True or queue and link is True:
            if number is True:
                content = queue[song_number]
            queue.remove(content)
            queue.insert(0, content)
            name_request = youtube.videos().list(part='snippet', id=content[32:])
            name_request_execution = name_request.execute()
            song_name = name_request_execution['items'][0]['snippet']['title']
            await ctx.send(f'Moved {song_name} to the next spot in your qeue.')
        else:
            if not queue:
                await ctx.send('You dont have a qeue at the moment, please create one to use this command.')
                return
            elif content not in queue or int(content) <= len(queue):
                await ctx.send('Please pass a valid url or qeue number.')

    # Command die via de 'current' functie een embed met data stuurt over het lied aangeduid met een queue nummer
    @bot.command()
    async def qeue_info(ctx, content):
        global queue, info_status, song_link
        try:
            song_link = queue[int(content) - 1]
            info_status = True
            await current(ctx)
        except Exception:  # noqa
            await ctx.send('That is not a valid song number.')

    # Functie die de lengte van queue berekent
    @bot.command()
    async def qeue_length(ctx):  # verzamel data over het aantal liedjes en tijdsduur van qeue
        global queue
        if not queue:
            return await ctx.send('You do not have a qeue at the moment please create one to use this command.')
        total_minutes:  int = 0
        final_hours: int = 0
        final_minutes: int = 0
        total_seconds: int = 0
        counter: int = 1
        for item in queue:
            video_id = item[32:]
            length_request = youtube.videos().list(part='contentDetails', id=video_id)
            length_response = length_request.execute()
            duration = length_response['items'][0]['contentDetails']['duration'][2:].replace('M', ':').replace('S', '')
            counter += 1
            if duration[-1] == ':':
                seconds: int = 0
                minutes: int = duration[0]
            elif duration[-2] == ':':
                seconds: int = duration[-1]
                minutes: int = duration[0]
            else:
                seconds: int = duration[2:]
                minutes: int = duration[0]

            total_minutes += int(minutes)
            total_seconds += int(seconds)

            converted_seconds = int(int(total_seconds) / 60)
            final_minutes = int(total_minutes) - int(final_hours * 60) + int(converted_seconds)
            final_hours = int(int(total_minutes) / 60)

        embed = discord.Embed(colour=discord.Colour.dark_embed(),
                              title='Qeue length')
        embed.add_field(name='Qeue Length:', value=f'{final_hours} hours and {final_minutes} minutes.', inline=False)
        embed.add_field(name='Qeue songs:', value=len(queue), inline=False)
        time_ms = str(datetime.datetime.now())[11:]
        time_final = time_ms[:8]
        embed.set_footer(text=f' Requested by: {ctx.message.author} at: {time_final}')
        await ctx.send(embed=embed)

    # Functie die alle items van je queue in een embed zet
    @bot.command()
    async def qeue_list(ctx):  #maak een embed aan met elk item in qeue
        global queue
        if not queue:
            return await ctx.send('There is no queue at the moment, please create one.')
        embed_counter = 1
        song_counter = 1
        song_id_list = []
        song_names = []
        message = await ctx.send('Starting process, this might take some time for big queue\'s.')
        for song in queue:
            song_counter += 1
            song_id = song[32:]
            song_id_list.append(song_id)
        for song_id in song_id_list:
            try:
                song_name = get_song_name(song_id)
                full_song_name = f"{embed_counter}. {song_name}"
                song_names.append(full_song_name)
                embed_counter += 1
            except IndexError:
                pass
        pagination = PaginationView()
        pagination.data = song_names
        await pagination.send(ctx)
        await message.delete()

    # Functie die een lied uit de queue speelt
    @bot.command()
    async def qeue_play(ctx, content):
        global queue, song_to_play, source
        if not queue:
            return await ctx.send('There is no qeue at the moment, please create one.')
        elif ctx.voice_client is None:
            return await ctx.send('You are not in a vc')
        elif int(content) <= len(queue):
            song_number = int(content) - 1
            song_to_play = queue[song_number]
            queue.remove(song_to_play)
            queue.insert(0, song_to_play)
            ctx.voice_client.stop()
        else:
            await ctx.send('That is not a valid qeue item')

    # Functie die queue reversed
    @bot.command()
    async def qeue_reverse(ctx):  # reverse qeue
        global queue
        if not queue:
            return await ctx.send('You dont have a qeue at the moment, please create one to use this command')
        else:
            queue.reverse()
            await ctx.send('Qeue reversed')

    # Functie die queue shuffled
    @bot.command()
    async def qeue_shuffle(ctx):  # shuffle qeue
        if not queue:
            return await ctx.send('You dont have a qeue at the moment, please create one to use this command')
        else:
            random.shuffle(queue)
            await ctx.send('Qeue shuffled')

    # Functie die lyrics van een lied verzamelt met genius api en deze dan in een embed plaatst
    @bot.command()
    async def lyrics(ctx):
        if ctx.voice_client is None:
            return await ctx.send('This command is only usable if there is a song playing.')
        song_id = song_to_play[32:]
        data_request = youtube.videos().list(part='snippet', id=song_id)
        data_request_response = data_request.execute()
        song_name = data_request_response['items'][0]['snippet']['title']
        song_name = song_name.split('(')[0]
        song_name = song_name.split('[')[0]
        song_name = song_name.replace('(Official Video)', '')
        song_name = song_name.replace('[Official Video]', '')
        song = genius.search_song(song_name)
        if song is None:
            return await ctx.send('Multibot couldn\'t find that song.')
        song_lyrics = song.lyrics
        song_lyrics = song_lyrics[2:]
        song_lyrics = song_lyrics.replace('Contributors', '')
        song_lyrics = song_lyrics.split('Lyrics')[1]
        song_lyrics = song_lyrics.replace('Embed', '')
        song_lyrics = song_lyrics.replace('You might also like', '\n')
        if song_lyrics[-1].isdigit() is True:
            if song_lyrics[-2].isdigit() is True:
                if song_lyrics[-3].isdigit() is True:
                    song_lyrics = song_lyrics[:-3]
                else:
                    song_lyrics = song_lyrics[:-2]
            else:
                song_lyrics = song_lyrics[:-1]
        if not len(song_lyrics) >= 4000:
            print('under')
            embed = discord.Embed(colour=discord.Colour.dark_embed(),
                                  title=f'Lyrics of: {song_name}')
            embed.description = str(song_lyrics)
            await ctx.send(embed=embed)
        else:
            return await ctx.send('Multibot doesn\'t support song lyrics over 4000 characters, sorry for'
                                  ' the inconvenience')

    # TicTacToe minigame
    @bot.command()
    async def ttt(ctx, opponent):
        global delete_buttons
        delete_buttons = None
        team_cross_id = ctx.author.id
        cross_player = f'<@{team_cross_id}>'
        team_square_id = opponent[2:][:-1]
        square_player = opponent
        ttt_game = TicTacToe(ctx, cross_player, team_cross_id, square_player, team_square_id)
        await ttt_game.challenge()
        message = await ctx.send(view=ttt_game)
        while True:
            if delete_buttons is False:
                await asyncio.sleep(0.5)
            else:
                await message.delete()
                break

    # Functie voor het toevoegen van een lied aan de queue
    def add_to_queue(playlist_id, insert_at_front):
        global yt_video_id, queue
        # verzamel playlist items
        counter = 0
        final_run = False
        playlist_request = youtube.playlistItems().list(part='snippet',
                                                        playlistId=playlist_id,
                                                        maxResults=50)
        response = playlist_request.execute()
        next_page_token = ''

        # voeg item toe aan queue en verzamel nextpage token
        while True:
            try:
                yt_video_id = response['items'][counter]['snippet']['resourceId']['videoId']
                try:
                    next_page_token = response['nextPageToken']
                # Als er geen nextpage token is dus bij playlists van 50 videos of minder
                except KeyError:
                    final_run = True
                yt_url = str('https://www.youtube.com/watch?v=') + str(yt_video_id)
                if insert_at_front is True:
                    queue.insert(0, yt_url)
                else:
                    queue.append(yt_url)
                counter += 1
            # als je aan het einde van de pagina met playlist item resultaten bent
            except IndexError:
                if final_run is True:
                    return queue
                while True:
                    # herhaal wat hierboven gebeurd alleen dan met volgende pagina met resultaten
                    counter = 0
                    playlist_request = youtube.playlistItems().list(part='snippet',
                                                                    playlistId=playlist_id,
                                                                    pageToken=next_page_token,
                                                                    maxResults=50)
                    response = playlist_request.execute()
                    while True:
                        try:
                            yt_video_id = response['items'][counter]['snippet']['resourceId']['videoId']
                            yt_url = str('https://www.youtube.com/watch?v=') + str(yt_video_id)
                            if insert_at_front is True:
                                queue.insert(0, yt_url)
                            else:
                                queue.append(yt_url)
                            counter += 1
                        except IndexError:
                            try:
                                next_page_token = response['nextPageToken']
                                break
                            except KeyError:
                                return queue

    # Functie voor het spelen van een lied uit de queue
    async def play_from_queue(ctx):  #speel items uit qeue, herhaalt zich dmv lambda functie
        global queue, song_to_play, source, first_run
        print('play from qeue')
        if not queue:
            await ctx.send('Qeue is empty, please provide a new song or playlist')
            return await bot.change_presence(activity=discord.Game(name='Waiting for a song to play...'))
        else:
            song_to_play = queue[0]
            play_song(ctx, song_to_play)
            await current(ctx)
            await set_status()
            first_run = True

    # Zet bot status
    async def set_status():
        global song_to_play
        id_from_song_to_set = song_to_play[32:]
        song_name = get_song_name(id_from_song_to_set)
        artist = get_song_artist(id_from_song_to_set)
        await bot.change_presence(activity=discord.Game(name=f'Currently playing: {song_name} by: {artist}.'))

    # Functie die daadwerkelijk het lied speelt
    def play_song(ctx, song_to_play_link):
        FFMPEG_OPTIONS = {'executable': FFMPEG_PATH,
                          'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        YT_DLP_OPTIONS = {'format': 'bestaudio'}
        vc = ctx.voice_client
        with yt_dlp.YoutubeDL(YT_DLP_OPTIONS) as ydlp:
            if song_to_play_link in queue:
                queue.remove(song_to_play_link)
            info = ydlp.extract_info("ytsearch:%s" % song_to_play_link, download=False)['entries'][0]
            url2 = info['url']
            source_to_play = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
            vc.play(source_to_play, after=lambda e: asyncio.run_coroutine_threadsafe(play_from_queue(ctx), bot.loop))

    # Zoek song naam met youtube api
    def get_song_name(song_id):
        name_request = youtube.videos().list(part='snippet', id=song_id)
        name_execution = name_request.execute()
        song_name = name_execution['items'][0]['snippet']['title']
        return song_name

    # Zoek song uploader met youtube api
    def get_song_artist(song_id):
        artist_request = youtube.videos().list(part='snippet', id=song_id)
        artist_execution = artist_request.execute()
        artist = artist_execution['items'][0]['snippet']['channelTitle']
        return artist

    @bot.command()
    async def test_play(ctx):
        global queue
        if ctx.author.voice is None:
            return await ctx.send('You are not in a voice channel')
        await join(ctx)
        queue.append('https://www.youtube.com/watch?v=_3M9w7WwyXU')
        await play_from_queue(ctx)

    bot.run(DISCORD_API_TOKEN)  # run bot


if __name__ == '__main__':
    main()
