import asyncio
import os
import discord

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('DISCORD_URL')
DISCORD_API_TOKEN = os.getenv('DISCORD_API_TOKEN')

empty_ttt_square = ':white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:\n:white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:\n:white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:\n:white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:\n:white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:'  # noqa
cross_ttt_square = ':red_square::white_large_square::white_large_square::white_large_square::red_square:\n:white_large_square::red_square::white_large_square::red_square::white_large_square:\n:white_large_square::white_large_square::red_square::white_large_square::white_large_square:\n:white_large_square::red_square::white_large_square::red_square::white_large_square:\n:red_square::white_large_square::white_large_square::white_large_square::red_square:'  # noqa
square_ttt_square = ':blue_square::blue_square::blue_square::blue_square::blue_square:\n:blue_square::white_large_square::white_large_square::white_large_square::blue_square:\n:blue_square::white_large_square::white_large_square::white_large_square::blue_square:\n:blue_square::white_large_square::white_large_square::white_large_square::blue_square:\n:blue_square::blue_square::blue_square::blue_square::blue_square:'  # noqa
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
delete_buttons = None


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

    async def challenge(self):
        self.start_message =\
            await self.ctx.send(f'{self.square_player} has been challenged to tic tac toe by: {self.cross_player}')

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
        await self.gameloop()

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

    async def checkwin(self):
        # horizontaal
        if squares.get('1_1') == squares.get('1_2') == squares.get('1_3') and squares.get('1_1') != 'empty':
            print('winner')
            self.winner = squares.get('1_1')
            await self.end_game()
        elif squares.get('2_1') == squares.get('2_2') == squares.get('2_3') and squares.get('2_1') != 'empty':
            print('winner')
            self.winner = squares.get('2_1')
            await self.end_game()
        elif squares.get('3_1') == squares.get('3_2') == squares.get('3_3') and squares.get('3_1') != 'empty':
            print('winner')
            self.winner = squares.get('3_1')
            await self.end_game()

        # verticaal
        elif squares.get('1_1') == squares.get('2_1') == squares.get('3_1') and squares.get('1_1') != 'empty':
            print('winner')
            self.winner = squares.get('1_2')
            await self.end_game()
        elif squares.get('1_2') == squares.get('2_2') == squares.get('3_2') and squares.get('1_2') != 'empty':
            print('winner')
            self.winner = squares.get('1_2')
            await self.end_game()
        elif squares.get('1_3') == squares.get('2_3') == squares.get('3_3') and squares.get('1_3') != 'empty':
            print('winner')
            self.winner = squares.get('1_3')
            await self.end_game()

        # diagonaal
        elif squares.get('1_1') == squares.get('2_2') == squares.get('3_3') and squares.get('1_1') != 'empty':
            print('winner')
            self.winner = squares.get('1_1')
            await self.end_game()
        elif squares.get('1_3') == squares.get('2_2') == squares.get('3_1') and squares.get('1_3') != 'empty':
            print('winner')
            self.winner = squares.get('1_3')
            await self.end_game()

        # gelijkspel
        elif 'empty' not in squares.values():
            await self.tie()

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

    async def end_game(self):
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

    async def gameloop(self):
        # if self.turn == 'cross':
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


def main():
    intents = discord.Intents.default()  # standaard settings
    intents.message_content = True  # mag berichtinhoud lezen
    bot = commands.Bot(command_prefix='mb ', intents=intents)

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
            if delete_buttons is None:
                await asyncio.sleep(0.5)
            else:
                await message.delete()
                break

    bot.run(DISCORD_API_TOKEN)  # run bot


if __name__ == '__main__':
    main()
