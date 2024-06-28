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

load_dotenv()
url = os.getenv('DISCORD_URL')
DISCORD_API_TOKEN = os.getenv('DISCORD_API_TOKEN')


def main():
    intents = discord.Intents.default()  # standaard settings
    intents.message_content = True  # mag berichtinhoud lezen
    bot = commands.Bot(command_prefix='mb ', intents=intents)

    @bot.command()
    async def spin(ctx, *args):
        pass

    bot.run(DISCORD_API_TOKEN)  # run bot


if __name__ == '__main__':
    main()
