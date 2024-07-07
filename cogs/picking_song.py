import discord
import ytmusicapi

from cogs.bot_v3_misc import get_songinfo

from discord.ext import commands

yt_api_unofficial = ytmusicapi.YTMusic()


class PicksongEmbed(discord.ui.View):
    """Embed that contains 5 songs which the user can pick 1 off to start playing/queue"""

    def __init__(self, ctx, search_string, add_to_queue):
        super().__init__()
        self.ctx: discord.ext.commands.Context = ctx
        self.search_string: str = search_string
        self.add_to_queue: bool = add_to_queue

        self.message: discord.Message | None = None
        self.chosen_id: str | None = None
        self.song_option_counter: int = 1
        self.song_counter: int = 0
        self.song_ids: list = []
        self.song_options: list = []

    async def send(self) -> None:
        """Function that sends the message including the embed"""

        embed: discord.Embed = await self.create_embed()
        self.message: discord.Message = await self.ctx.send(embed=embed, view=self)

    async def create_embed(self) -> discord.Embed | discord.Message:
        """Function that gets song names/ids and puts them into an embed"""

        embed = discord.Embed(title='Pick a song:',
                              colour=discord.Colour.dark_embed())

        # verzamel top 5 liedjes aan de hand van search string
        for i in range(5):
            try:
                videoId = yt_api_unofficial.search(self.search_string)[self.song_counter]['videoId']
            except KeyError:
                try:
                    videoId = yt_api_unofficial.search(self.search_string)[self.song_counter + 1]['videoId']
                except KeyError:
                    try:
                        videoId = yt_api_unofficial.search(self.search_string)[self.song_counter + 2]['videoId']
                    except KeyError:
                        return await self.ctx.send('Couldn\'t find that song, please check your spelling and retry.')
            self.song_ids.append(videoId)
            self.song_counter += 1

        # verander eerder verzamelde ids in namen
        for song_id in self.song_ids:
            song_title, song_artist = get_songinfo(song_id)
            self.song_options.append(f'{song_title} by: {song_artist}')

        # voeg tekst toe aan embed
        for song_option in self.song_options:
            embed.add_field(name='',
                            value=f'{self.song_option_counter}.{song_option}',
                            inline=False)
            self.song_option_counter += 1

        return embed

    async def update_message(self) -> None:
        """Function that updates the message and deletes it if needed"""

        if self.add_to_queue is True:
            self.ctx.bot.append(f'https://www.youtube.com/watch?v={self.chosen_id}')
            await self.message.delete()
        elif self.add_to_queue == 'front':
            self.ctx.bot.insert(0, f'https://www.youtube.com/watch?v={self.chosen_id}')
            await self.message.delete()
        else:
            await self.message.delete()
            self.ctx.bot.chosen_song = f'https://www.youtube.com/watch?v={self.chosen_id}'

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

    @discord.ui.button(label='cancel', style=discord.ButtonStyle.red)
    async def fifth_song_button(self, interaction: discord.Interaction, button: discord.Button):  # noqa
        await interaction.response.defer()  # noqa
        await self.message.delete()