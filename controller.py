import discord
from discord.ext import commands
import random, time, datetime
import database, diceroller
import credentials as cred

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command(pass_context=True)
async def r(ctx, *, arg):
    
    dice = diceroller.DiceRolls(arg)
    description = ""

    # putting all results in the database.  It skips nothing, including failures and syntax errors!
    for roll in dice.getrolls():
        print("{} {} {} {} {} {} {} {}".format(ctx.author, ctx.author.nick, arg, roll.get_equation(), roll.get_sumtotal(), roll.get_stat(), roll.get_success(), roll.get_comment()))
        database.add_roll(str(ctx.author), ctx.author.nick, arg, roll.get_equation(), roll.get_sumtotal(), roll.get_stat(), roll.get_success(), roll.get_comment())

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
            if roll.get_comment() is None:
                description += "{}: {} = {} against a {}\n***{}***\n".format(ctx.author.mention, roll.get_equation(), roll.get_sumtotal(), roll.get_stat(), roll.get_success())
            else:
                description += "{}: {} = {} against a {} for {}\n***{}***\n".format(ctx.author.mention, roll.get_equation(), roll.get_sumtotal(), roll.get_stat(), roll.get_comment(), roll.get_success())
                
        embed = discord.Embed(
            colour=discord.Colour(0x24ed60), 
            description=description
            )
    
    # PASS: this is every other roll condition.
    else:
        for roll in dice.getrolls():
            if roll.get_comment() is None:
                description += "{}: {} = {}\n".format(ctx.author.mention, roll.get_equation(), roll.get_sumtotal())
            else:
                description += "{}: {} = {} for {}\n".format(ctx.author.mention, roll.get_equation(), roll.get_sumtotal(), roll.get_comment())

        embed = discord.Embed(
            colour=discord.Colour(0x24ed60), 
            description=description
            )

    await ctx.send(embed=embed)

@bot.command()
async def licorice(ctx):
    phrase = "Generic Licorice: It’s not like straight licorice!"
    licorice_twist_ranking = ["Cherry", "Blue Raspberry", "Mixed Berry", "Tropical", "Blood Orange", "Raspberry", "Green Apple", "Watermelon", "Root Beer", "Peach", "Chocolate", "Red Licorice", "Black Licorice", "Pina Colada"]
    await ctx.send("Ro Chooses: {}".format(random.choice(licorice_twist_ranking)))

@bot.command()
async def mystery(ctx):
    '''returns an image from ARE YOU AFRAID OF THE DARK in the same font.  THE MYSTERY OF THE BLAH BLAH BLAH'''
    '''this could also randomize images from various TV shows, but that might be more work.  Although do the AYAOTD typeface is probably equally difficult.'''

bot.run(cred.discord_key) #Insert your bots token here