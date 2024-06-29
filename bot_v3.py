import os, asyncio, pprint, datetime, uuid, discord, random, yt_dlp, ytmusicapi, lyricsgenius

from dotenv import load_dotenv
from googleapiclient.discovery import build
from discord.ext import commands

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

first_run = True
#
# volume_modified = False
# delete_buttons = False
# info_status = False
#
# id_chosen_pick = None
# index_error = None
#
# song_link = ''
# yt_video_id = ''
# song_to_play = ''
# source = ''
# fetch_message = ''
#
# data_len = 0
#
# song_ids = []
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


# Main loop die de bot runnend houdt
def main():
    # Setup
    intents = discord.Intents.default()  # standaard settings
    intents.message_content = True  # mag berichtinhoud lezen
    bot = commands.Bot(command_prefix='mb ', intents=intents)

    # Call Help class met pagina'a die info bevatten over alle commands
    @bot.command()
    async def helpme(ctx):
        help_request = HelpEmbed()  # call embed functie om help embed te maken
        await help_request.send_embed(ctx)

    # Word getriggerd als bot online gaat
    @bot.event
    async def on_ready():
        global queue
        kill_channel = bot.get_channel(1175212011060199524)
        await kill_channel.send(str(kill_code))
        await bot.change_presence(activity=discord.Game(name='Waiting for a song to play...'))
        await bot.load_extension('cogs.bot_v3_controls')
        await bot.load_extension('cogs.bot_v3_playing_music')
        await bot.load_extension('cogs.bot_v3_queue')

        print(str(bot.user) + ' online')

















    # # Command die een enkel lied afspeelt, als er al iets speelt wordt dit gestopt
    # @bot.command()
    # async def play(ctx, *, play_url):
    #     global queue
    #     # , song_to_play, source, fetch_message, first_run
    #     play_url_yt_track = play_url[:32]
    #     if play_url_yt_track == 'https://www.youtube.com/watch?v=':
    #         if play_url[-5:-2] == '&t=':
    #             play_url = play_url[:-5]
    #         else:
    #             pass
    #
    #         if ctx.voice_client is None:
    #             await join(ctx)
    #
    #         play_song(ctx, play_url)
    #
    #         # await
    #
    #
    #
    #
    #
    #
    # # Functie die daadwerkelijk het lied speelt
    # def play_song(ctx, song_to_play_link):
    #     FFMPEG_OPTIONS = {'executable': FFMPEG_PATH,
    #                       'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    #                       'options': '-vn'}
    #     YT_DLP_OPTIONS = {'format': 'bestaudio'}
    #     vc = ctx.voice_client
    #     with yt_dlp.YoutubeDL(YT_DLP_OPTIONS) as ydlp:
    #         if song_to_play_link in queue:
    #             queue.remove(song_to_play_link)
    #         info = ydlp.extract_info("ytsearch:%s" % song_to_play_link, download=False)['entries'][0]
    #         url2 = info['url']
    #         source_to_play = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
    #         vc.play(source_to_play, after=lambda e: asyncio.run_coroutine_threadsafe(play_from_queue(ctx), bot.loop))
    #
    # # Functie voor het spelen van een lied uit de queue
    # async def play_from_queue(ctx):  #speel items uit qeue, herhaalt zich dmv lambda functie
    #     global queue, first_run
    #     print('play from qeue')
    #     if not queue:
    #         await ctx.send('Qeue is empty, please provide a new song or playlist')
    #         return await bot.change_presence(activity=discord.Game(name='Waiting for a song to play...'))
    #     else:
    #         song_to_play = queue[0]
    #         play_song(ctx, song_to_play)
    #         # await current(ctx)
    #         # await set_status()
    #         first_run = True

    bot.run(DISCORD_API_TOKEN)  # run bot


if __name__ == '__main__':
    main()

