import discord
from discord.ext import commands
from discord.utils import get
from discord.errors import ClientException
from discord.errors import DiscordException
from discord.opus import OpusNotLoaded

from gtts import gTTS
import ffmpeg
from slugify import slugify

import random, time, datetime, asyncio
from database import Database
import diceroller
import credentials as cred
from settings import Settings
import mathtools

bot = commands.Bot(command_prefix=['.','!'], description="Call of Cthulhu Dicebot", help_command=None)
settings = Settings()
db = Database(settings.database_path)
song_queue = []

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

    # ADD TO DB: putting all results in the database.  It skips when there's nothing, including failures and syntax errors!
    for roll in dice.getrolls():
        print("{} {} {} {} {} {} {} {} {} {}".format(ctx.guild, ctx.channel, ctx.author, ctx.author.display_name, arg, roll.get_equation(), roll.get_sumtotal(), roll.get_stat(), roll.get_success(), roll.get_comment()))

        # if ^test is present in the comment, the roll will not be store in the db (for testing purposes)
        if dice.getroll().get_comment() is not None and "^test" in dice.getroll().get_comment():
            print ("Roll NOT added to Database!")
        else:
            db.add_roll(str(ctx.author), ctx.author.display_name, arg, roll.get_equation(), roll.get_sumtotal(), roll.get_stat(), roll.get_success(), roll.get_comment(), str(ctx.guild), str(ctx.channel))

    # FAIL: in this event, the sum of the rolls is NONE, which indicates there was a problem in the syntax or code.  Produces error.
    if dice.getroll().get_sumtotal() == None:
        licorice = db.get_random_licorice()
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
        
        # sets the color to the level of success. if there's more than 1 roll, then use a special color
        colour = dice.getroll().get_success_color() if dice.get_roll_count() == 1 else 0x0968ed
                
        embed = discord.Embed(
            title=roll.get_comment(),
            colour=discord.Colour(colour), 
            description=description
            )
        
        # if the state is a lucky success, show some fireworks!
        if dice.getroll().get_success() == "lucky success":
            embed.set_image(url="https://media.giphy.com/media/26tOZ42Mg6pbTUPHW/giphy.gif")

        elif dice.getroll().get_success() == "critical":
            #embed.set_image(url="https://media.giphy.com/media/hSoZSJanVL4k9fVz0e/giphy.gif")
            embed.set_image(url="https://media.giphy.com/media/xUPGcEDVIQQS6hBbSo/giphy.gif")
        
        elif dice.getroll().get_success() == "fumble":
            embed.set_image(url="https://media.giphy.com/media/xT9Igoo05UKCnnXGtq/giphy.gif")

        if settings.announce:
            vc = ctx.voice_client # We use it more then once, so make it an easy variable
            if not vc:
                await ctx.send("I need to be in a voice channel to do this, please use the connect command.")
                return
            
            success = dice.getroll().get_success() if dice.getroll().get_success() is not None else ""
            success_slugify = slugify(success, lowercase=True)

            path = 'audio/diceroll-vo/{}-{}.mp3'.format(success_slugify, random.randint(1,4))
            song_queue.append(path)

            try:
                if not vc.is_playing():
                    song_queue.insert(0, "audio/diceroll1.mp3")
                    song_queue.insert(len(song_queue)-1, "audio/DramaticSting1.mp3") if success == "critical" or success == "fumble" else None
                    
                    # Play audio in channel
                    play_next(ctx)

            # Handle the exceptions that can occur, i don't entirely understand this though, so I commented it out
            except ClientException as e:
                await ctx.send(f"A client exception occured:\n`{e}`")
            except TypeError as e:
                await ctx.send(f"TypeError exception:\n`{e}`")
            except OpusNotLoaded as e:
                await ctx.send(f"OpusNotLoaded exception: \n`{e}`")            
    
    # PASS: this is every other roll condition. 
    else:
        for roll in dice.getrolls():
            description += "{} = {}\n".format(roll.get_equation(), roll.get_sumtotal())

        embed = discord.Embed(
            title=roll.get_comment(),
            colour=discord.Colour(0x24ed60), 
            description=description
            )

    await asyncio.sleep(4) if dice.getroll().get_success() == "fumble" or dice.getroll().get_success() == "critical" else None
    embed.set_author(name=ctx.author.display_name, url=db.get_random_licorice()[1], icon_url=ctx.author.default_avatar_url)
    await ctx.send(embed=embed)

def play_next(ctx):
    if len(song_queue) >= 1:
        vc = ctx.voice_client

        # play sound
        vc.play(discord.FFmpegPCMAudio(source=song_queue[0]), after=lambda e: play_next(ctx))

        # Lets set the volume to 1
        vc.source = discord.PCMVolumeTransformer(vc.source)
        vc.source.volume = settings.voice_volume

        del song_queue[0]

@bot.command(pass_context=True)
async def lastrolls(ctx, *, arg=None):

    if mathtools.RepresentsInt(arg): #is the argument an integer value
        rolls = db.get_entries_as_string(number_of_entries=int(arg))
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

@bot.command(pass_context=True)
async def announce(ctx, *, arg=None):
    if mathtools.RepresentsBool(arg): #is the arg string a boolean value
        settings.announce = mathtools.convertToBool(arg)
        await ctx.send("Announce Rolls in Voice Chat is now set to {}".format(arg))
    else:
        await ctx.send("Invalid Syntax: {}".format(arg))

@bot.command()
async def licorice(ctx):
    licorice_twist_ranking = ["Cherry", "Blue Raspberry", "Mixed Berry", "Tropical", "Blood Orange", "Raspberry", "Green Apple", "Watermelon", "Root Beer", "Peach", "Chocolate", "Red", "Black", "Pina Colada"]
    await ctx.send("Have you tasted the delicious: {} licorice?".format(random.choice(licorice_twist_ranking)))
     
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

@bot.command()
async def testing(ctx):
    '''General area for testing.'''
    '''test a reaction tool for polling / answering requests'''

    embed = discord.Embed(title="testing", colour=discord.Colour(0xbf1919), description="description")

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
        await ctx.send('{} has added {} to the the message {}'.format(user.name, reaction.emoji, reaction.message.content))

    #await bot.process_commands(reaction.message)

# @bot.event
# async def on_message(message):
#     ctx = await bot.get_context(message)
#     await ctx.send("i'll respond to everything.")
#     await bot.process_commands(message)


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