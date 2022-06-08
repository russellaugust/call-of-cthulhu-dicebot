import discord
from discord.ext import commands
import time, asyncio
import credentials as cred
from settings import Settings
import mathtools

bot = commands.Bot(command_prefix=['.','!'], description="Call of Cthulhu Dicebot")
settings = Settings()

@bot.event
async def on_ready():
    print('Logged in as {0.user}... we are alive!'.format(bot))


@bot.command(pass_context=True, aliases=['s'])
async def set(ctx, *, arg=None):
    '''
    Set improve dice roll
    set voices for dice
    set 
    '''

    if arg is None or arg == "help":
        settings_dict = settings.dictionary_of_properties()
        properties = f"Below are all settings.  Use the name of the setting to change them. e.g. `{ctx.invoked_with} property True`\n"

        # gets the length of the longest word so the text aligns correctly, not good for mobile though
        longest = 0
        for key in settings_dict:
            longest = len(key) if len(key) > longest else longest

        for key in settings_dict:
            # beginning = f"{key}"
            # middle = ""
            # middle += ' '*(longest-len(key)+1)
            # properties += f"{beginning}{middle}{settings_dict[key]}\n"
            properties += f"{key}:  `{settings_dict[key]}`\n"
            
        await ctx.send(f"{properties}")
    else:
        await ctx.send("under construction")

@bot.command(pass_context=True,
             brief='Does the bot speak in an audio channel? [True|False]',  
             description="Allows the bot to speak in audio channels.  This can either be True or False."
             )
async def announce(ctx, *, arg=None):
    if mathtools.RepresentsBool(arg): #is the arg string a boolean value
        settings.announce = mathtools.convertToBool(arg)
        await ctx.send("Announce Rolls in Voice Chat is now set to {}".format(arg))
    else:
        await ctx.send("Invalid Syntax: {}".format(arg))

# Voice Channel Section
class VoiceConnectionError(commands.CommandError):
    pass

class InvalidVoiceChannel(VoiceConnectionError):
    pass


@bot.command()
async def join(ctx, *, channel: discord.VoiceChannel=None):
    """
    Connect to a voice channel
    This command also handles moving the bot to different channels.

    Params:
    - channel: discord.VoiceChannel [Optional]
        The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
        will be made.
    """
    if not channel:
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

    vc = ctx.voice_client

    if vc:
        if vc.channel.id == channel.id:
            return
        try:
            await vc.move_to(channel)
        except asyncio.TimeoutError:
            raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
    else:
        try:
            await channel.connect()
        except asyncio.TimeoutError:
            raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

    await ctx.send(f'Connected to: **{channel}**', delete_after=20)


@bot.command()
async def disconnect(ctx):
    """
    Disconnect from a voice channel, if in one
    """
    vc = ctx.voice_client

    if not vc:
        await ctx.send("I am not in a voice channel.")
        return

    await vc.disconnect()
    await ctx.send("I have left the voice channel!")


@bot.command(name="demoing")
async def demoing(ctx):
    # Gets voice channel of message author
    voice_channel = ctx.author.channel
    if voice_channel != None:
        channel = voice_channel.name
        vc = await voice_channel.connect()
        print ("okay something worked")
        # Sleep while audio is playing.
        while vc.is_playing():
            time.sleep(.1)
        await vc.disconnect()
    else:
        await ctx.send(str(ctx.author.name) + "is not in a channel.")
    # Delete command after the audio is done playing.
    await ctx.message.delete()

bot.load_extension('cogs.Dice')

bot.run(cred.discord_key) #Insert your bots token here
