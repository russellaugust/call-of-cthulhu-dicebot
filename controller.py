import discord
from discord.ext import commands
import random, time, datetime, asyncio
import database, diceroller
import credentials as cred
import mathtools
from gtts import gTTS
import ffmpeg

bot = commands.Bot(command_prefix=['.','!'], description="Call of Cthulhu Dicebot", help_command=None)

@bot.event
async def on_ready():
    print('Logged in as {0.user}... we are alive!'.format(bot))

@bot.command(pass_context=True)
async def r(ctx, *, arg=None):
    '''main roll command. this will allow the user to roll dice assuming some basic syntax is used.'''
    
    # if the user only types the command !r, it roll a 1d100
    if not arg:
        arg = "1D100"
    
    dice = diceroller.DiceRolls(arg)
    #description = "{}: ".format(ctx.author.mention)
    description = ""

    # putting all results in the database.  It skips when there's nothing, including failures and syntax errors!
    for roll in dice.getrolls():
        print("{} {} {} {} {} {} {} {} {} {}".format(ctx.guild, ctx.channel, ctx.author, ctx.author.display_name, arg, roll.get_equation(), roll.get_sumtotal(), roll.get_stat(), roll.get_success(), roll.get_comment()))

        # comment that keeps the roll of the db for testing purposes
        if dice.getroll().get_comment() is not None:
            if "^test" not in dice.getroll().get_comment():
                print ("Roll added to Database!")
                database.add_roll(str(ctx.author), ctx.author.display_name, arg, roll.get_equation(), roll.get_sumtotal(), roll.get_stat(), roll.get_success(), roll.get_comment())

    # FAIL: in this event, the sum of the rolls is NONE, which indicates there was a problem in the syntax or code.  Produces error.
    if dice.getroll().get_sumtotal() == None:
        licorice = database.get_random_licorice()
        embed = discord.Embed(
            colour=discord.Colour(0xbf1919), 
            description="*SPROÜTS!*   That's some bad syntax. Have a piece of [{} Licorice]({}) while you fix that.".format(licorice[0], licorice[1]), 
            )

    # FAIL: condition if someone accidentally writes d00, which means roll a zero-sided die
    elif "d00" in dice.getroll().get_argument():
        embed = discord.Embed(
            colour=discord.Colour(0xbf1919), 
            description="Good lord, this is embarrassing... Check that roll and try again.", 
            )

    # PASS: If the success field in the first dice roll is filled in, then that means it had to be a stat roll with a 1d100 so it. 
    elif dice.getroll().get_success() is not None:
        for roll in dice.getrolls():
            description += "{} is a ***{}***\n".format(roll.get_sumtotal(), roll.get_success())
        
        colour = dice.getroll().get_success_color() if dice.get_roll_count() == 1 else 0x0968ed
                
        embed = discord.Embed(
            title=roll.get_comment(),
            colour=discord.Colour(colour), 
            description=description
            )
        
        # if the state is a lucky success, show some fireworks!
        if int(roll.get_sumtotal()) == int(roll.get_stat()):
            embed.set_image(url="https://media.giphy.com/media/26tOZ42Mg6pbTUPHW/giphy.gif")

        elif int(roll.get_sumtotal()) == int(1):
            embed.set_image(url="https://media.giphy.com/media/hSoZSJanVL4k9fVz0e/giphy.gif")
            #embed.set_image(url="https://media.giphy.com/media/xUPGcEDVIQQS6hBbSo/giphy.gif")
        
        elif int(roll.get_sumtotal()) == int(100):
            embed.set_image(url="https://media.giphy.com/media/xT9Igoo05UKCnnXGtq/giphy.gif")
    
    # PASS: this is every other roll condition.
    else:
        for roll in dice.getrolls():
            description += "{} = {}\n".format(roll.get_equation(), roll.get_sumtotal())

        embed = discord.Embed(
            title=roll.get_comment(),
            colour=discord.Colour(0x24ed60), 
            description=description
            )

    embed.set_author(name=ctx.author.display_name, url=database.get_random_licorice()[1], icon_url=ctx.author.default_avatar_url)
    await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def lastrolls(ctx, *, arg=None):

    if mathtools.RepresentsInt(arg): #is the argument an integer value
        rolls = database.get_entry(number_of_entries=int(arg))
        description = "LAST ROLLS\n"
        for roll in rolls:
            print (roll)
            description += "{}\n".format(roll)

        embed = discord.Embed(
            colour=discord.Colour(0x24ed60), 
            description=description
            )

        await ctx.send(embed=embed)
    
    else:
        await ctx.send("bad syntax.")


@bot.command()
async def licorice(ctx):
    licorice_twist_ranking = ["Cherry", "Blue Raspberry", "Mixed Berry", "Tropical", "Blood Orange", "Raspberry", "Green Apple", "Watermelon", "Root Beer", "Peach", "Chocolate", "Red", "Black", "Pina Colada"]
    await ctx.send("Have you tasted the delicious: {} licorice?".format(random.choice(licorice_twist_ranking)))

@bot.command()
async def mystery(ctx):
    '''returns an image from ARE YOU AFRAID OF THE DARK in the same font.  THE MYSTERY OF THE BLAH BLAH BLAH'''
    '''this could also randomize images from various TV shows, but that might be more work.  Although do the AYAOTD typeface is probably equally difficult.'''

@bot.command()
async def testing(ctx):
    '''General area for testing.'''
    
@bot.command()
async def pocky(ctx):
    '''Returns a thing about pocky flavors.'''
    await ctx.send("Awaiting more data...")

@bot.command()
async def whocares(ctx):
    '''who cares about me, based on that one chart.'''
    await ctx.send("Awaiting more data...")

@bot.command()
async def icare(ctx):
    '''who cares about me, based on that one chart.'''
    await ctx.send("Awaiting more data...")


# Voice Channel Section
class VoiceConnectionError(commands.CommandError):
    pass

class InvalidVoiceChannel(VoiceConnectionError):
    pass

@bot.command()
async def connect(ctx, *, channel: discord.VoiceChannel=None):
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

@bot.command()
async def vocalroll(ctx, *, text=None):
    """
    A command which saves `text` into a speech file with
    gtts and then plays it back in the current voice channel.

    Params:
     - text [Optional]
        This will be the text we speak in the voice channel
    """
    if not text:
        # We have nothing to speak
        await ctx.send(f"Hey {ctx.author.mention}, I need to know what to say please.")
        return

    vc = ctx.voice_client # We use it more then once, so make it an easy variable
    if not vc:
        # We are not currently in a voice channel
        await ctx.send("I need to be in a voice channel to do this, please use the connect command.")
        return
    
    # get dice roll
    dice = diceroller.DiceRolls(text)

    sumtotal = dice.getroll().get_sumtotal() if dice.getroll().get_sumtotal() is not None else ""
    success = dice.getroll().get_success() if dice.getroll().get_success() is not None else ""

    readout = "You rolled {}. that's a {}".format(sumtotal, success)

    # Lets prepare our text, and then save the audio file
    tts = gTTS(text=readout, lang="en")
    tts.save("text.mp3")

    try:
        # Lets play that mp3 file in the voice channel
        vc.play(discord.FFmpegPCMAudio('text.mp3'), after=lambda e: print(f"Finished playing: {e}"))
        #vc.play(discord.FFmpegPCMAudio('audio/god.mp3'), after=lambda e: print(f"Finished playing: {e}"))

        # Lets set the volume to 1
        vc.source = discord.PCMVolumeTransformer(vc.source)
        vc.source.volume = 1

    # Handle the exceptions that can occur
    except ClientException as e:
        await ctx.send(f"A client exception occured:\n`{e}`")
    except TypeError as e:
        await ctx.send(f"TypeError exception:\n`{e}`")
    except OpusNotLoaded as e:
        await ctx.send(f"OpusNotLoaded exception: \n`{e}`")

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

# Help Only
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Help Menu", colour=discord.Colour(0xff6f00), url="https://github.com/russellaugust/call-of-cthulhu-dicebot", description="Commands available to you.")

    embed.set_thumbnail(url="https://i.pinimg.com/originals/3d/26/47/3d2647dd3f2a03d33e149c8af1c80516.jpg")

    embed.add_field(name="Rolling Dice", value="Below is some of the functionality of this bot.\n\n", inline=False)
    embed.add_field(name="Rolling Against Stats", value="Example:\n\n*/r 1d100 45*\n*/r 45*\n\nReturns what you rolled and how successful the roll was. In the example, 45 is the stat you're rolling against like INT or CON.", inline=False)
    embed.add_field(name="Standard Rolls", value="Examples:\n\n*/r 1d6*\n*/r 1d10+12*\n*2d4+1d6+5*\n\nReturns the results of your roll and completes the math.", inline=False)
    embed.add_field(name="Comments", value="Examples:\n\n*/r 1d6 # int roll for my life*\n\nThis just adds a little context to your roll.  This also gets stored in the database!", inline=False)
    embed.add_field(name="Repeating Rolls", value="Examples:\n\n*/r repeat(1d6+4 #comment, 5)*\n*/r repeat(45, 5)*\n\nThis will execute the roll as many times as in the second field. So 5 times in the above examples.  Unfortunately comments need to be inside the repeat command for now.", inline=False)

    await ctx.author.send(embed=embed)


bot.run(cred.discord_key) #Insert your bots token here