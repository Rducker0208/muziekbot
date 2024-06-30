import discord
from discord.ext import commands


class Controls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        await join_vc(ctx)

    # Command die bot uit de vc haalt
    @commands.command()
    async def disconnect(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send('Multibot is not in a voicechannel.')
        await ctx.voice_client.disconnect()

    # Command die spelende audio pauseerd
    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send('Multibot is not in a voicechannel.')
        ctx.voice_client.pause()

    # Command die audio weer laat spelen
    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send('Multibot is not in a voicechannel.')
        ctx.voice_client.resume()

    # Command voor het aanspassen van het volume van de spelende muziek
    @commands.command()
    async def volume(self, ctx, content):
        voice = ctx.voice_client
        try:
            volume_to_use = int(content) / 100
        except ValueError:
            return await ctx.send('Please provide a volume between 0 and 100.')
        if voice is None:
            return await ctx.send('Multibot is not in a voicechannel.')
        if not 101 > int(content) >= 0:
            return await ctx.send('Please provide a volume between 0 and 100.')

        # 2de aanpassing van volume of later
        if hasattr(ctx.voice_client.source, 'volume'):
            ctx.voice_client.source.volume = volume_to_use * 2

        # 1ste aanpassing
        else:
            voice.source = discord.PCMVolumeTransformer(voice.source, volume=volume_to_use * 2)

        await ctx.send(f'Volume changed to {content}%')

    # Command die een lied skipt waarna play_from_qeue uit de queue gaat spelen
    @commands.command()
    async def skip(self, ctx):
        ctx.voice_client.stop()


async def setup(bot):
    await bot.add_cog(Controls(bot))


# Command voor het joinen van een vc door de bot
async def join_vc(ctx):
    if hasattr(ctx.author.voice, 'channel'):
        voice_channel = ctx.author.voice.channel
        vc_id = voice_channel.id
        vc_name = '<' + '#' + str(vc_id) + '>'
    else:
        return await ctx.send('Please join a voice channel before using this command')

    if ctx.voice_client is None:  # als bot niet in vc is
        await ctx.send('Joining voice channel: ' + vc_name)
        await voice_channel.connect()
    else:
        if ctx.voice_client.channel == ctx.author.voice.channel:
            pass
        else:
            await ctx.voice_client.move_to(voice_channel)
            await ctx.send(f'Moved to: {vc_name}')


