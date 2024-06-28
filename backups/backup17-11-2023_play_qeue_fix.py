import asyncio
import os
import pprint
import discord
import random
import yt_dlp
import datetime
from discord.ext import commands
from googleapiclient.discovery import build
from dotenv import load_dotenv

queue = []

load_dotenv()

url = os.getenv('DISCORD_URL')
DISCORD_API_TOKEN = os.getenv('DISCORD_API_TOKEN')
YT_API_KEY = os.getenv('YT_API_KEY')
FFMPEG_PATH = 'C:/ffmpeg/ffmpeg.exe'
youtube = build('youtube', 'v3', developerKey=YT_API_KEY)

song_link = ''
yt_video_id = ''
song_to_play = ''
data_len = 0
info_status = False


class HelpEmbed(discord.ui.View):
    help_page = 1
    current_page = 1

    def __init__(self):
        super().__init__()
        self.message = None

    async def send_embed(self, ctx):
        self.message = await ctx.send(view=self)  # wacht tot bericht is verstuurd
        await self.update_message(current_page=self.current_page)  # stuur request om bericht te updaten

    async def update_message(self, current_page):
        self.update_buttons()
        embed = self.create_embed(current_page=current_page)
        await self.message.edit(embed=embed)  # update bericht

    def update_buttons(self):  # zet knoppen uit als je op die pagina zit
        print(f'current page{self.current_page}')
        if self.current_page == 1:
            self.help_button.disabled = True
        if self.current_page == 2:
            self.play_button.disabled = True
        if self.current_page == 3:
            self.qeue_button.disabled = True

    def create_embed(self, current_page):  # noqa
        embed = None
        print('create')
        print(current_page)
        if current_page == 1:  #content
            print('page 1')
            embed = discord.Embed(colour=discord.Colour.dark_embed(),
                                  title='Help content:')
            embed.add_field(name='Page 1:', value='Current page containing page info.', inline=False)
            embed.add_field(name='Page 2:', value='Info about play commands.', inline=False)
            embed.add_field(name='Page 3:', value='Info about qeue_commands.', inline=False)
        if current_page == 2:  #play_commands
            embed = discord.Embed(colour=discord.Colour.dark_embed(),
                                  title='Play_commands:')
            embed.add_field(name='play [youtube link] ', value='Play a link from youtube.', inline=False)
            embed.add_field(name='play_playlist [youtube playlist link] ', value='Play a playlist from youtube.',
                            inline=False)
        if current_page == 3:  #qeue_commands
            embed = discord.Embed(colour=discord.Colour.dark_embed(),
                                  title='Qeue commands:')
            embed.add_field(name='mb qeue_add [youtube link]:',
                            value='Add a new song to the end of your qeue.', inline=False)
            embed.add_field(name='mb qeue_add_next [youtube link]:',
                            value='Add a new song to the front of your qeue.', inline=False)
            embed.add_field(name='mb qeue_clear:',
                            value='Clear your qeue.', inline=False)
            embed.add_field(name='mb qeue_front [youtube link/qeue number]:',
                            value='Move a song in your qeue to the front.', inline=False)
            embed.add_field(name='mb qeue_info [number in qeue]:',
                            value='Get statistics of the song specified.', inline=False)
            embed.add_field(name='mb qeue_length:',
                            value='Get length of your qeue and the amount of songs in it.', inline=False)
            embed.add_field(name='mb qeue_list:',
                            value='List all items in your qeue.', inline=False)
            embed.add_field(name='mb qeue_play [number in qeue]:',
                            value='Plays the song in your qeue that has the given number.', inline=False)
            embed.add_field(name='mb qeue_reverse:',
                            value='Reverses your qeue.', inline=False)
            embed.add_field(name='mb qeue_shuffle: ',
                            value='Shuffles your qeue randomly.', inline=False)
        print(embed)
        return embed

    @discord.ui.button(label='Help', style=discord.ButtonStyle.primary)
    async def help_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.current_page = 1
        await self.update_message(self.current_page)

    @discord.ui.button(label='Play', style=discord.ButtonStyle.primary)
    async def play_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.current_page = 2
        await self.update_message(self.current_page)

    @discord.ui.button(label='Qeue', style=discord.ButtonStyle.primary)
    async def qeue_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        self.current_page = 3
        await self.update_message(self.current_page)


class PaginationView(discord.ui.View):
    print('pagination function')
    current_page = 1
    seperator = 20
    embed_counter = 0
    data = None

    def __init__(self):
        super().__init__()
        self.message = None

    async def send(self, ctx):
        global data_len
        data_len = len(self.data)  # lengte van qeue
        self.message = await ctx.send(view=self)  # stuur bericht
        await self.update_message(self.data[:self.seperator])  # update bericht tot aan seperator 20 * aantal pagina's

    async def update_message(self, data):
        self.update_buttons()  # update knoppen
        await self.message.edit(embed=self.create_embed(data), view=self)  # bewerk bericht

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

    def create_embed(self, data):
        embed_counter = 0
        embed = discord.Embed(title='Current qeue:', colour=discord.Colour.dark_embed())
        current_page = self.current_page
        # max_page = int(len(self.data) / self.seperator) + 1
        if data_len % 20 == 0:
            max_page = int(data_len / self.seperator)
        else:
            max_page = int(data_len / self.seperator) + 1
        print(f'max page: {max_page}')
        print(f'len(data): {len(data)}')
        print(self.data)
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
        print(self.current_page)
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


def main():
    intents = discord.Intents.default()  # standaard settings
    intents.message_content = True  # mag berichtinhoud lezen
    bot = commands.Bot(command_prefix='mb ', intents=intents)

    @bot.event
    async def on_ready():  # vanzelfsprekend
        print(str(bot.user) + ' online')

    @bot.command()
    async def helpme(ctx):  # creert een embed met daarin informatie over commands
        help_request = HelpEmbed()  # call embed functie om help embed te maken
        await help_request.send_embed(ctx)

    @bot.command()
    async def join(ctx):  # functie om bot een vc te laten joinen
        if ctx.author.voice is None:
            await ctx.send('You are not in a voice channel')
            return
        voice_channel = ctx.author.voice.channel
        vc_id = voice_channel.id
        vc_name = '<' + '#' + str(vc_id) + '>'
        if ctx.voice_client is None:  # als bot niet in vc is
            await ctx.send('Joining voice channel: ' + vc_name)
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

    @bot.command()
    async def pause(ctx):  # functie die spelende audio blokkeert
        await ctx.voice_client.pause()

    @bot.command()
    async def resume(ctx):  # functie die audio weer laat spelen
        await ctx.voice_client.resume()

    @bot.command()
    async def skip(ctx):  # skip een lied waarna play_from_qeue uit de qeue gaat spelen
        global queue
        ctx.voice_client.stop()

    @bot.command()
    async def disconnect(ctx):  # disconnect uit de vc
        await ctx.voice_client.disconnect()

    @bot.command()
    async def current(ctx):  # geeft een embed met data over het opgegeven lied
        if info_status is True:  # als deze functie word opgreroepen dmv de qeue_info functie
            video_id = song_link[32:]  # alles na 32ste letter
        else:
            video_id = song_to_play[32:]
        data_request = youtube.videos().list(part='snippet', id=video_id)
        duration_request = youtube.videos().list(part='contentDetails', id=video_id)
        duration_response = duration_request.execute()
        data_request_response = data_request.execute()
        # pprint.pprint(data_request_response)
        song_name = data_request_response['items'][0]['snippet']['title']
        artist = data_request_response['items'][0]['snippet']['channelTitle']
        duration = duration_response['items'][0]['contentDetails']['duration'][2:].replace('M', ':').replace('S', '')
        if duration[-2] == ':':  # als lied 1 cijfer na : heeft bijv 3:7 verander dit in 3:07
            last_duration_letter = duration[-1]
            duration = duration.replace(duration[-1], '0')
            duration = duration + last_duration_letter
        release_date = data_request_response['items'][0]['snippet']['publishedAt'][:10]
        try:
            thumbnail = data_request_response['items'][0]['snippet']['thumbnails']['maxres']['url']
        except Exception:  # noqa
            thumbnail = data_request_response['items'][0]['snippet']['thumbnails']['standard']['url']
        pprint.pprint(thumbnail)
        print(song_name)
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
        time_ms = str(datetime.datetime.now())[11:]
        time_final = time_ms[:8]
        embed.set_footer(text=f' Requested by: {ctx.message.author} at: {time_final}')
        await ctx.send(embed=embed)

    @bot.command()
    async def play(ctx, play_url):  # speelt een lied af, heeft prioriteit over qeue en cancels lied als er een speelt
        global queue, song_to_play
        print('play')
        play_url_yt_track = play_url[:32]
        if play_url_yt_track != 'https://www.youtube.com/watch?v=':
            await ctx.send('That is not a valid youtube link.')
            return
        await join(ctx)
        print(play_url_yt_track)
        FFMPEG_OPTIONS = {'executable': FFMPEG_PATH,
                          'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        YT_DLP_OPTIONS = {'format': 'bestaudio'}
        vc = ctx.voice_client
        with yt_dlp.YoutubeDL(YT_DLP_OPTIONS) as ydlp:
            song_to_play = play_url
            ctx.voice_client.stop()
            info = ydlp.extract_info("ytsearch:%s" % play_url, download=False)['entries'][0]
            url2 = info['url']
            source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
            print('`1')
            await current(ctx)
            # vc.play(source, after=lambda e: play_from_que(ctx))
            vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_from_que(ctx), bot.loop))

    @bot.command()
    async def play_playlist(ctx, pl_url):  # functie die playlist items in een qeue plaatst
        global queue
        if qeue:
            await ctx.send('There already is a qeue, please use the "qeue_add_playlist" or "qeue_add_playlist_front"'
                           ' to add playlists to your qeue')
            return
        await join(ctx)
        site_name = pl_url[8:33]
        playlist_id = pl_url[38:]
        platform = None
        if site_name == 'open.spotify.com/playlist':
            platform = 'Spotify'
        if site_name == 'www.youtube.com/playlist?':
            platform = 'Youtube'
        qeue = create_qeue(playlist_id, platform)
        await play_from_que(ctx)

    def create_qeue(playlist_id, platform):  #creer qeue en voeg items eraan toe
        global yt_video_id, queue
        counter = 0
        final_run = False
        qeue = []
        if platform == 'Youtube':
            playlist_request = youtube.playlistItems().list(part='snippet',
                                                            playlistId=playlist_id,
                                                            maxResults=50)
            response = playlist_request.execute()
            next_page_token = ''
            while True:
                try:
                    yt_video_id = response['items'][counter]['snippet']['resourceId']['videoId']
                    try:
                        next_page_token = response['nextPageToken']
                    except KeyError:
                        final_run = True
                    yt_url = str('https://www.youtube.com/watch?v=') + str(yt_video_id)
                    # print(yt_url)
                    qeue.append(yt_url)
                    counter += 1
                except IndexError:
                    if final_run is True:
                        return qeue
                    while True:
                        # try:
                        counter = 0
                        print('next_request')
                        playlist_request = youtube.playlistItems().list(part='snippet',
                                                                        playlistId=playlist_id,
                                                                        pageToken=next_page_token,
                                                                        maxResults=50)
                        print('before_execute')
                        response = playlist_request.execute()
                        print('after_execute')
                        while True:
                            try:
                                yt_video_id = response['items'][counter]['snippet']['resourceId']['videoId']
                                print(yt_video_id)
                                # pprint.pprint(id)
                                yt_url = str('https://www.youtube.com/watch?v=') + str(yt_video_id)
                                # print(yt_url)
                                qeue.append(yt_url)
                                counter += 1
                            except IndexError:
                                print('Indexerror')
                                try:
                                    next_page_token = response['nextPageToken']
                                    break
                                except KeyError:
                                    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                                    print(qeue)
                                    return qeue

    async def play_from_que(ctx):  #speel items uit qeue, herhaalt zich dmv lambda functie
        global queue, song_to_play
        print('play from qeue')
        FFMPEG_OPTIONS = {'executable': FFMPEG_PATH,
                          'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        YT_DLP_OPTIONS = {'format': 'bestaudio'}
        vc = ctx.voice_client
        print('____1_____')
        await ctx.send('test')
        if not qeue:
            await ctx.send('Qeue is empty, please provide a new song or playlist')
            return
        else:
            if ctx.voice_client.is_playing() is True:
                ctx.voice_client.stop()
            else:
                pass
            print('____2_____')
            with yt_dlp.YoutubeDL(YT_DLP_OPTIONS) as ydlp:
                print('____3_____')
                song_to_play = qeue[0]
                qeue.remove(song_to_play)
                info = ydlp.extract_info("ytsearch:%s" % song_to_play, download=False)['entries'][0]
                url2 = info['url']
                source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
                print('2')
                await current(ctx)
                vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_from_que(ctx), bot.loop))

    @bot.command()
    async def qeue_add(ctx, qeue_url):  # voeg een url toe aan qeue
        global queue
        if qeue_url[:32] != 'https://www.youtube.com/watch?v=':
            await ctx.send('Please provide a valid youtube url')
            return
        if qeue is not None and qeue_url not in qeue:
            qeue.append(qeue_url)
            video_id = qeue_url[32:]
            print(video_id)
            name_request = youtube.videos().list(part='snippet', id=video_id)
            name_request_execution = name_request.execute()
            pprint.pprint(name_request_execution)
            song_name = name_request_execution['items'][0]['snippet']['title']
            await ctx.send(f'added {song_name} to qeue')

    @bot.command()
    async def qeue_add_next(ctx, qeue_add_url):  # voeg een url toe aan qeue maar vorran ipv achteraan
        global queue
        if qeue_add_url[:32] != 'https://www.youtube.com/watch?v=':
            await ctx.send('Please provide a valid youtube url')
            return
        if qeue and qeue_add_url not in qeue:
            qeue.insert(0, qeue_add_url)
            name_request = youtube.videos().list(part='snippet', id=qeue_add_url[32:])
            name_request_execution = name_request.execute()
            song_name = name_request_execution['items'][0]['snippet']['title']
            await ctx.send(f'added {song_name} as next song in your qeue.')
        else:
            await ctx.send('This song is already in your qeue.')

    @bot.command()
    async def qeue_clear(ctx):  # wiped qeue
        global queue
        print(qeue)
        qeue = []
        print(qeue)
        await ctx.send('Qeue cleared')

    @bot.command()
    async def qeue_front(ctx, content):
        global queue
        song_number = 0
        number = False
        link = False
        if content in qeue:
            link = True
        if int(content) <= len(qeue):
            song_number = int(content) - 1
            number = True
        if qeue and number is True or link is True:
            if number is True:
                content = qeue[song_number]
            qeue.remove(content)
            qeue.insert(0, content)
            name_request = youtube.videos().list(part='snippet', id=content[32:])
            name_request_execution = name_request.execute()
            song_name = name_request_execution['items'][0]['snippet']['title']
            await ctx.send(f'Moved {song_name} to the next spot in your qeue.')
        else:
            if not qeue:
                await ctx.send('You dont have a qeue at the moment, please create one to use this command.')
                return
            elif content not in qeue or int(content) <= len(qeue):
                await ctx.send('Please pass a valid url or qeue number.')

    @bot.command()
    async def qeue_info(ctx, content):  # stuur via de current functie data over je lied
        global queue, info_status, song_link
        try:
            song_link = qeue[int(content) - 1]
            info_status = True
            print('3')
            await current(ctx)
        except Exception:  # noqa
            await ctx.send('That is not a valid song number.')

    @bot.command()
    async def qeue_length(ctx):  # verzamel data over het aantal liedjes en tijdsduur van qeue
        global queue
        if not qeue:
            await ctx.send('You do not have a qeue at the moment please create one to use this command.')
            return
        total_minutes:  int = 0
        final_hours: int = 0
        final_minutes: int = 0
        total_seconds: int = 0
        counter: int = 1
        print(len(qeue))
        for item in qeue:
            video_id = item[32:]
            length_request = youtube.videos().list(part='contentDetails', id=video_id)
            length_response = length_request.execute()
            # pprint.pprint(length_response)
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
        embed.add_field(name='Qeue songs:', value=len(qeue), inline=False)
        time_ms = str(datetime.datetime.now())[11:]
        time_final = time_ms[:8]
        embed.set_footer(text=f' Requested by: {ctx.message.author} at: {time_final}')
        await ctx.send(embed=embed)

    @bot.command()
    async def qeue_list(ctx):  #maak een embed aan met elk item in qeue
        global queue
        if not qeue:
            await ctx.send('There is no qeue at the moment, please create one.')
            return
        embed_counter = 1
        song_counter = 1
        song_id_list = []
        song_names = []
        print(qeue)
        for song in qeue:
            song_counter += 1
            song_id = song[32:]
            song_id_list.append(song_id)
        print(song_id_list)
        for song_id in song_id_list:
            try:
                name_request = youtube.videos().list(part='snippet', id=song_id)
                name_request_execution = name_request.execute()
                song_name = name_request_execution['items'][0]['snippet']['title']
                full_song_name = f"{embed_counter}. {song_name}"
                song_names.append(full_song_name)
                embed_counter += 1
            except IndexError:
                print('error excepted')
        print(song_names)
        pagination = PaginationView()
        pagination.data = song_names
        await pagination.send(ctx)

    @bot.command()
    async def qeue_play(ctx, content):  # speel item uit qeue met nummer dat gegeven wordt
        global queue
        if not qeue:
            await ctx.send('There is no qeue at the moment, please create one.')
            return
        if int(content) <= len(qeue):
            song_number = int(content) - 1
            qeue_song_to_play = qeue[song_number]
            qeue.remove(qeue_song_to_play)
            FFMPEG_OPTIONS = {'executable': FFMPEG_PATH,
                              'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                              'options': '-vn'}
            YT_DLP_OPTIONS = {'format': 'bestaudio'}
            vc = ctx.voice_client
            with yt_dlp.YoutubeDL(YT_DLP_OPTIONS) as ydlp:
                # info = ydlp.extract_info(url, download=False)
                ctx.voice_client.stop()
                info = ydlp.extract_info("ytsearch:%s" % qeue_song_to_play, download=False)['entries'][0]
                url2 = info['url']
                source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
                await current(ctx)
                vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_from_que(ctx), bot.loop))
        else:
            await ctx.send('That is not a valid qeue item')

    @bot.command()
    async def qeue_reverse(ctx):  # reverse qeue
        global queue
        print(qeue)
        if not qeue:
            await ctx.send('You dont have a qeue at the moment, please create one to use this command')
            return
        else:
            print(qeue)
            qeue.reverse()
            print(qeue)
            await ctx.send('Qeue reversed')

    @bot.command()
    async def qeue_shuffle(ctx):  # shuffle qeue
        print(queue)
        if not queue:
            await ctx.send('You dont have a qeue at the moment, please create one to use this command')
            return
        else:
            random.shuffle(queue)
            await ctx.send('Qeue shuffled')
            print(queue)

    bot.run(DISCORD_API_TOKEN)  # run bot


if __name__ == '__main__':
    main()
