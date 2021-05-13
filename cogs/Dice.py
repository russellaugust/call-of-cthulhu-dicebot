import discord, random, asyncio, os
from slugify import slugify
from discord.ext import commands
import diceroller
import mathtools
from settings import Settings
from database import Database

class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []
        self.settings = Settings()
        self.db = Database(self.settings.database_path)

        print ('test')
        
    @commands.command(  pass_context=True, 
                        aliases=['r'],
                        brief="Rolls the dice.  e.g. 1D100 45 # INT",  
                        description="The ROLL command works by selecting the dice you want (1D100) and modifiers (+1) an optional stat (45) and a comment (# pump some lead into that goon!)"
                        )
    async def roll(self, ctx, *, arg=None):
        '''main roll command. this will allow the user to roll dice assuming some basic syntax is used.'''

        # if the user only types the command !r, it roll a 1d100
        arg = arg if arg else "1D100"
        
        # rolls the dice and gets stores the result as a list
        dice = diceroller.DiceRolls(arg)
        print (dice)
        description = ""

        # ADD TO DB: putting all results in the database.  It skips when there's nothing, including failures and syntax errors!
        for roll in dice.getrolls():

            # if ^test is present in the comment, the roll will not be store in the db (for testing purposes)
            if dice.getroll().get_comment() is not None and "^test" in dice.getroll().get_comment():
                print ("Roll NOT added to Database!")
            else:
                self.db.add_roll(str(ctx.author), ctx.author.display_name, arg, roll.get_equation(), roll.get_sumtotal(), roll.get_stat(), roll.get_success(), roll.get_comment(), str(ctx.guild), str(ctx.channel))
                print("{} {} {} {} {} {} {} {} {} {}".format(ctx.guild, ctx.channel, ctx.author, ctx.author.display_name, arg, roll.get_equation(), roll.get_sumtotal(), roll.get_stat(), roll.get_success(), roll.get_comment()))

        # FAIL: in this event, the sum of the rolls is NONE, which indicates there was a problem in the syntax or code.  Produces error.
        if dice.getroll().get_sumtotal() == None:
            embed = discord.Embed(colour=discord.Colour(0xbf1919), description="*SPROÜTS!*   That's some bad syntax.")

        # FAIL: condition if someone accidentally writes d00, which means roll a zero-sided die
        elif "d00" in dice.getroll().get_argument():
            embed = discord.Embed(colour=discord.Colour(0xbf1919), description="This is embarrassing... Check that roll and try again.")

        # PASS: If the success field in the first dice roll is filled in, then that means it had to be a stat roll with a 1d100 so it. 
        elif dice.getroll().stat_exists():
            for roll in dice.getrolls():
                description += "{} is a ***{}***\n".format(roll.get_sumtotal(), roll.get_success())
            
            # sets the color to the level of success. if there's more than 1 roll, then use a special color
            colour = dice.getroll().get_success_color() if dice.get_roll_count() == 1 else 0x0968ed
                    
            embed = discord.Embed(title=roll.get_comment() if roll.get_comment() else "", colour=discord.Colour(colour), description=description)
            
            # embed a GIF or image for these special situations
            if dice.getroll().get_success() == "lucky success":
                embed.set_image(url=self.settings.gif_lucky)
            elif dice.getroll().get_success() == "critical":
                embed.set_image(url=self.settings.gif_critical)
            elif dice.getroll().get_success() == "fumble":
                embed.set_image(url=self.settings.gif_fumble)

            # read the results if announce is on and the bot is in a channel
            vc = ctx.voice_client
            if self.settings.announce and vc:
                success = dice.getroll().get_success() if dice.getroll().get_success() is not None else ""
                success_slugify = slugify(success, lowercase=True)

                voicefolder = "audio/diceroll-voice/eldritch"
                max_vo_variations = self.count_files_starting_with(voicefolder, success_slugify)

                path = f'{voicefolder}/{success_slugify}-{random.randint(1,max_vo_variations)}.mp3'
                self.song_queue.append(path)

                try:
                    print(self.song_queue)
                    if not vc.is_playing():
                        self.song_queue.insert(0, "audio/diceroll1.mp3")
                        self.song_queue.insert(len(self.song_queue)-1, "audio/DramaticSting1.mp3") if success == "critical" or success == "fumble" else None
                        
                        # Play audio in channel
                        self.play_next(ctx)

                # Handle the exceptions that can occur, i don't entirely understand this though, so I commented it out
                except discord.ClientException as e:
                    await ctx.send(f"A client exception occured:\n`{e}`")
                except TypeError as e:
                    await ctx.send(f"TypeError exception:\n`{e}`")
                except discord.opus.OpusNotLoaded as e:
                    await ctx.send(f"OpusNotLoaded exception: \n`{e}`")            
        
        # PASS: this is every other roll condition. 
        else:
            for roll in dice.getrolls():
                description += f"{roll.get_string()}\n"

            embed = discord.Embed(
                title=roll.get_comment() if roll.get_comment() else "",
                colour=discord.Colour(0x24ed60), 
                description=description
                )

        # dramatic pause for fumbles and criticals  
        await asyncio.sleep(4) if dice.getroll().get_success() == "fumble" or dice.getroll().get_success() == "critical" else None
        
        author_avatar_url = ctx.author.avatar_url or ctx.author.default_avatar_url
        embed.set_author(name=ctx.author.display_name, icon_url=author_avatar_url)
        await ctx.send(embed=embed)

    @commands.command(pass_context=True, aliases=['r+', 'b'])
    async def bonus(self, ctx, *, arg=None):

        # if the user only types the command !r, it roll a 1d100
        if not arg:
            arg = "1D100"
        
        dice1 = diceroller.DiceRolls(arg).getroll()
        dice2 = diceroller.DiceRolls(arg).getroll()

        description = f"{dice1.get_string()}\n~~{dice2.get_string()}~~" if dice1.get_sumtotal() <= dice2.get_sumtotal() else f"~~{dice1.get_string()}~~\n{dice2.get_string()}"
        color = dice1.get_success_color() if dice1.get_sumtotal() <= dice2.get_sumtotal() else dice2.get_success_color()

        embed = discord.Embed(title=dice1.get_comment(), colour=color, description=description)
        author_avatar_url = ctx.author.avatar_url or ctx.author.default_avatar_url
        embed.set_author(name=ctx.author.display_name, icon_url=author_avatar_url)

        comment = dice1.get_comment() if dice1.get_comment() else ""
        embed = discord.Embed(
            title=f"{comment} - with bonus.",
            colour=discord.Colour(0x24ed60), 
            description=description
            )

        await ctx.send(embed=embed)

    @commands.command(pass_context=True, aliases=['r-', 'p'])
    async def penalty(self, ctx, *, arg=None):

        # if the user only types the command !r, it roll a 1d100
        if not arg:
            arg = "1D100"
        
        dice1 = diceroller.DiceRolls(arg).getroll()
        dice2 = diceroller.DiceRolls(arg).getroll()

        description = f"{dice1.get_string()}\n~~{dice2.get_string()}~~" if dice1.get_sumtotal() >= dice2.get_sumtotal() else f"~~{dice1.get_string()}~~\n{dice2.get_string()}"
        color = dice1.get_success_color() if dice1.get_sumtotal() >= dice2.get_sumtotal() else dice2.get_success_color()

        embed = discord.Embed(title=dice1.get_comment(), colour=color, description=description)
        author_avatar_url = ctx.author.avatar_url or ctx.author.default_avatar_url
        embed.set_author(name=ctx.author.display_name, icon_url=author_avatar_url)

        comment = dice1.get_comment() if dice1.get_comment() else ""
        embed = discord.Embed(
            title=f"{comment} - with penalty.",
            colour=discord.Colour(0x24ed60), 
            description=description
            )

        await ctx.send(embed=embed)

    @commands.command(pass_context=True, aliases=['rp', 'rpt'])
    async def repeat(self, ctx, *, arg=None):
        await ctx.send("not yet implemented.")

    @commands.command(aliases=['i'], 
                      brief='-i [STATS TO IMPROVE] e.g. -i 50, or -i 30 50 40 30 for multiple stats.',  
                      description="This is for when you're improving a stat.  it rolls a 1d100 against the stat. If the roll is above the stat, it will roll a 1Dx (from settings) and adds it to the stat. .i or .improve will work.\n\n-i [STATS TO IMPROVE] e.g. -i 50, or -i 30 50 40 30 for multiple stats.")
    async def improve(self, ctx, *, arg=None):
        description = ""
        stats = arg.split(" ")
        roll = self.settings.dice_improve
        for stat in stats:
            if mathtools.RepresentsInt(stat):
                dice = diceroller.DiceRolls(stat) # roll against the stat
                if dice.getroll().get_sumtotal() >= int(stat): # if the total roll is greater than the stat
                    stat_improve_roll = diceroller.DiceRolls(roll)
                    stat_improvement = stat_improve_roll.getroll().get_sumtotal() + int(stat)
                    description += f"\nStat with {int(stat)} is now {stat_improvement} (1D100={dice.getroll().get_sumtotal()}, {roll}={stat_improve_roll.getroll().get_sumtotal()})"
                else:
                    description += f"\nStat with {int(stat)} is not improving (1D100={dice.getroll().get_sumtotal()})"

        if description == "":
            description = "No stats improved. Sorry!"

        embed = discord.Embed(colour=discord.Colour(0x24ed60), description=description)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.default_avatar_url)    
        await ctx.send(embed=embed)

    def play_next(self, ctx):
        if len(self.song_queue) >= 1:
            vc = ctx.voice_client

            # play sound
            vc.play(discord.FFmpegPCMAudio(source=self.song_queue[0]), after=lambda e: self.play_next(ctx))

            # Lets set the volume to 1
            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = self.settings.voice_volume

            del self.song_queue[0]

    def count_files_starting_with(self, folder, starting):
        counter = 0
        for file in os.listdir(folder):
            counter += 1 if file.startswith(starting) else 0
        return counter

def setup(bot):
    bot.add_cog(Dice(bot))