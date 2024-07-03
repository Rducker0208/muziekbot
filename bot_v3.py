import discord
import lyricsgenius
import os
import uuid
import ytmusicapi

from discord.ext import commands
from dotenv import load_dotenv
from googleapiclient.discovery import build


# Dotenv variables
load_dotenv()
url = os.getenv('DISCORD_URL')
DISCORD_API_TOKEN = os.getenv('DISCORD_API_TOKEN')
YT_API_KEY = os.getenv('YT_API_KEY')
GENIUS_ACCESS_TOKEN = os.getenv('GENIUS_ACCESS_TOKEN')

# Api builds
FFMPEG_PATH = 'C:/ffmpeg/ffmpeg.exe'
youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
yt_api_unofficial = ytmusicapi.YTMusic()
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)

# kill code voor kill command
kill_code = uuid.uuid4()

# Cogs
cog_list = ['cogs.bot_v3_controls', 'cogs.bot_v3_playing_music', 'cogs.bot_v3_queue', 'cogs.bot_v3_misc']


# Main loop die de bot runnend houdt
def main():
    # Setup
    intents = discord.Intents.default()  # standaard settings
    intents.message_content = True  # mag berichtinhoud lezen
    bot = commands.Bot(command_prefix='mb ', intents=intents)

    # bot variables (overal toegankelijk)
    bot.queue = []
    bot.kill_code = kill_code
    bot.current_song = None

    # Word getriggerd als bot online gaat
    @bot.event
    async def on_ready():
        # stuur code om bot instant down te halen
        kill_channel = bot.get_channel(1175212011060199524)
        await kill_channel.send(str(kill_code))

        # verander discord status van bot
        await bot.change_presence(activity=discord.Game(name='Waiting for a song to play...'))

        # laad command cogs
        for cog in cog_list:
            try:
                await bot.load_extension(cog)
            except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                pass

        print(str(bot.user) + ' online')

    bot.run(DISCORD_API_TOKEN)  # run bot


if __name__ == '__main__':
    main()
