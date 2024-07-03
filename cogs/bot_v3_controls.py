import discord
from discord.ext import commands


class Controls(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot: discord.ext.commands.Bot = bot

    @commands.command()
    async def join(self, ctx: discord.ext.commands.Context.voice_client):
        """Make muziekbot join your current vc"""
        await join_vc(ctx)

    @commands.command()
    async def disconnect(self, ctx: discord.ext.commands.Context.voice_client):
        """Make muziekbot leave the current vc"""

        if ctx.voice_client is None:
            return await ctx.send('Muziekbot is not in a voicechannel')
        await ctx.voice_client.disconnect()

    @commands.command()
    async def pause(self, ctx: discord.ext.commands.Context.voice_client):
        """Pause currently playing music"""

        if ctx.voice_client is None:
            return await ctx.send('Muziekbot is not in a voicechannel')
        ctx.voice_client.pause()

    @commands.command()
    async def resume(self, ctx: discord.ext.commands.Context.voice_client):
        """Resume previously paused music"""

        if ctx.voice_client is None:
            return await ctx.send('Muziekbot is not in a voicechannel')
        ctx.voice_client.resume()

    @commands.command()
    async def volume(self,
                     ctx: discord.ext.commands.Context.voice_client,
                     volume: str = commands.parameter(description=': Desired % of max volume')):
        """Change the volume of muziekbot's audio output"""

        voice_client = ctx.voice_client

        if voice_client is None:
            return await ctx.send('Multibot is not in a voicechannel')

        # check of volume een nummer is en tussen de bruikbare waardes ligt
        if volume.isnumeric() and 100 >= int(volume) >= 0:
            volume_to_use = int(volume) / 100
        else:
            return await ctx.send('Please provide a volume between 0 and 100')

        # 2de aanpassing van volume of later -> voice_client.source.volume is in de eerste aanpassing aangemaakt
        if hasattr(ctx.voice_client.source, 'volume'):
            ctx.voice_client.source.volume = volume_to_use * 2

        # 1ste aanpassing
        else:
            voice_client.source = discord.PCMVolumeTransformer(voice_client.source, volume=volume_to_use * 2)

        await ctx.send(f'Volume changed to {volume}%')

    @volume.error
    async def volume_error(self, ctx: discord.ext.commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send('The command you are using is missing an argument, please check the help command'
                                  ' for all required arguments')

    # Command die een lied skipt waarna play_from_qeue uit de queue gaat spelen
    @commands.command()
    async def skip(self, ctx: discord.ext.commands.Context.voice_client):
        """Skip the currently playing song"""

        ctx.voice_client.stop()


async def setup(bot: discord.ext.commands.Bot):
    """Function used to set up this cog"""

    await bot.add_cog(Controls(bot))


async def join_vc(ctx: discord.ext.commands.Context.voice_client):
    """Function that joins the user's current vc, can be called by other functions or the join command"""

    # Check of command aanroeper in een vc zit
    if hasattr(ctx.author.voice, 'channel'):
        voice_channel = ctx.author.voice.channel
        vc_id = voice_channel.id
        vc_name = '<' + '#' + str(vc_id) + '>'
    else:
        return await ctx.send('Please join a voice channel before using this command')

    # Check of muziekbot al in een vc zit en bepaal welk bericht er gestuurd moet worden
    if ctx.voice_client is None:
        await ctx.send('Joining voice channel: ' + vc_name)
        await voice_channel.connect()
    else:
        if ctx.voice_client.channel == ctx.author.voice.channel:
            pass
        else:
            await ctx.voice_client.move_to(voice_channel)
            await ctx.send(f'Moved to: {vc_name}')
