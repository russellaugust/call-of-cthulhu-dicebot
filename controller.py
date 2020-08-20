import discord
from discord.ext import commands
import random, time, datetime
import database, diceroller
import credentials as cred

bot = commands.Bot(command_prefix='.', description="Call of Cthulhu Dicebot", help_command=None)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command(pass_context=True)
async def r(ctx, *, arg=None):
    '''main roll command. this will allow the user to roll dice assuming some basic syntax is used.'''
    
    if not arg:
        arg = "1D100"
    
    dice = diceroller.DiceRolls(arg)
    #description = "{}: ".format(ctx.author.mention)
    description = ""

    # putting all results in the database.  It skips nothing, including failures and syntax errors!
    for roll in dice.getrolls():
        print("{} {} {} {} {} {} {} {}".format(ctx.author, ctx.author.display_name, arg, roll.get_equation(), roll.get_sumtotal(), roll.get_stat(), roll.get_success(), roll.get_comment()))
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

@bot.command()
async def licorice(ctx):
    phrase = "Generic Licorice: It’s not like straight licorice!"
    licorice_twist_ranking = ["Cherry", "Blue Raspberry", "Mixed Berry", "Tropical", "Blood Orange", "Raspberry", "Green Apple", "Watermelon", "Root Beer", "Peach", "Chocolate", "Red", "Black", "Pina Colada"]
    await ctx.send("Have you tasted the delicious: {} licorice?".format(random.choice(licorice_twist_ranking)))

@bot.command()
async def mystery(ctx):
    '''returns an image from ARE YOU AFRAID OF THE DARK in the same font.  THE MYSTERY OF THE BLAH BLAH BLAH'''
    '''this could also randomize images from various TV shows, but that might be more work.  Although do the AYAOTD typeface is probably equally difficult.'''

@bot.command()
async def examples(ctx):
    '''displays examples of how all rolls look.'''
    
@bot.command()
async def pocky(ctx):
    '''displays examples of how all rolls look.'''
    await ctx.send("Awaiting more data...")

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