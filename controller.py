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


@bot.command()
async def whocares(ctx):
    '''who cares about me, based on that one chart.'''
    await ctx.send("Awaiting more data...")

@bot.command()
async def icare(ctx):
    '''who cares about me, based on that one chart.'''
    await ctx.send("Awaiting more data...")

@bot.command()
async def testing(ctx):
    '''General area for testing.'''
    '''test a reaction tool for polling / answering requests'''

    embed = discord.Embed(title="testing", colour=discord.Colour(0xbf1919), description="description")
    embed.set_image(url="https://cloud.vhs.church/s/iDqtRXRwiPGKZab/download")

    msg = await ctx.send(ctx.message.channel,embed=embed)

    # no ID, do a lookup, this is only for guild
    emoji = discord.utils.get(ctx.guild.emojis, name='geoffquadfist')
    if emoji:
        await msg.add_reaction(emoji)


# Events in this section monitor all new incoming messages
@bot.event
async def on_reaction_add(reaction, user):
    '''Performs an action when a someone reacts to a message'''
    '''Note: this will only respond to messages in current bot history.  it will not trigger on messages prior to running'''
    if user != bot.user:
        channel = reaction.message.channel
        ctx = await bot.get_context(reaction.message)
        print('testing reaction successful.')
        #await ctx.send('{} has added {} to the the message {}'.format(user.name, reaction.emoji, reaction.message.content))

    #await bot.process_commands(reaction.message)


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
        #vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="C:<path_to_file>"))
        print ("okay something worked")
        # Sleep while audio is playing.
        while vc.is_playing():
            time.sleep(.1)
        await vc.disconnect()
    else:
        await ctx.send(str(ctx.author.name) + "is not in a channel.")
    # Delete command after the audio is done playing.
    await ctx.message.delete()

# Custom Help
'''
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Help Menu", colour=discord.Colour(0xff6f00), url="https://github.com/russellaugust/call-of-cthulhu-dicebot", description="Commands available to you.")

    embed.set_thumbnail(url="https://i.pinimg.com/originals/3d/26/47/3d2647dd3f2a03d33e149c8af1c80516.jpg")

    embed.add_field(name="Rolling Dice", value="Below is some of the functionality of this bot.\n\n", inline=False)
    embed.add_field(name="Rolling Against Stats", value="Example:\n\n*.r 1d100 45*\n*.r 45*\n\nReturns what you rolled and how successful the roll was. In the example, 45 is the stat you're rolling against like INT or CON.", inline=False)
    embed.add_field(name="Standard Rolls", value="Examples:\n\n*.r 1d6*\n*.r 1d10+12*\n*2d4+1d6+5*\n\nReturns the results of your roll and completes the math.", inline=False)
    embed.add_field(name="Comments", value="Examples:\n\n*.r 1d6 # int roll for my life*\n\nThis just adds a little context to your roll.  This also gets stored in the database!", inline=False)
    embed.add_field(name="Repeating Rolls", value="Examples:\n\n*.r repeat(1d6+4 #comment, 5)*\n*.r repeat(45, 5)*\n\nThis will execute the roll as many times as in the second field. So 5 times in the above examples.  Unfortunately comments need to be inside the repeat command for now.", inline=False)

    await ctx.author.send(embed=embed)
'''

bot.load_extension('cogs.Dice')

bot.run(cred.discord_key) #Insert your bots token here
