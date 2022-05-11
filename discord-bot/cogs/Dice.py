import discord, random, asyncio, os
from slugify import slugify
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
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

    def __roll_with_format__(self, ctx, rolls, additional_comment=""):

        # FAIL: the sum of the rolls is NONE, which indicates there was a problem in the syntax or code.  Produces error.
        if rolls.getroll().error():
            embed = discord.Embed(colour=discord.Colour(0xbf1919), description="*SPROÜTS!*   That's some bad syntax.")

        # FAIL: if someone accidentally writes d00, which means roll a zero-sided die
        elif "d00" in rolls.getroll().get_argument():
            embed = discord.Embed(colour=discord.Colour(0xbf1919), description="This is embarrassing... I doubt you meant to roll that.")

        # PASS: If the success field in the first dice roll is filled in, then that means it had to be a stat roll with a 1d100 so it. 
        elif rolls.getroll().stat_exists():
            pass

        description = ""
        color = 0x0968ed

        for roll in rolls.getrolls():
            description += roll.get_string() + "\n"
            color = color if roll.is_omitted() else roll.get_success_color()

        comment = rolls.getroll().get_comment() if rolls.getroll().get_comment() else ""
        embed = discord.Embed(title=f"{comment}{additional_comment}", colour=discord.Colour(color), description=description)

        author_avatar_url = ctx.author.avatar_url or ctx.author.default_avatar_url
        embed.set_author(name=ctx.author.display_name, icon_url=author_avatar_url)

        return embed

    def __successlevel_image__(self, embed, roll):
        # returns a discord.embed image with a gif that matches the roll success
        #if roll is not diceroller.RollResult:
        #    raise ValueError('not class RollResult.')
        if roll.get_success() == "lucky success":
            embed.set_image(url=self.settings.gif_random_lucky)
        elif roll.get_success() == "critical":
            embed.set_image(url=self.settings.gif_random_critical)
        elif roll.get_success() == "fumble":
            embed.set_image(url=self.settings.gif_random_fumble)
        return embed

    def __announce_roll__(self, ctx, rolls):
        vc = ctx.voice_client
        if self.settings.announce and vc and rolls.getroll().stat_exists():
            success = rolls.getroll().get_success() if rolls.getroll().get_success() is not None else ""
            success_slugify = slugify(success, lowercase=True)

            voicefolder = self.settings.current_voice_path
            max_vo_variations = self.count_files_starting_with(voicefolder, success_slugify)

            path = f'{voicefolder}/{success_slugify}-{random.randint(1,max_vo_variations)}.mp3'
            self.song_queue.append(path)

            if not vc.is_playing():
                self.song_queue.insert(0, "audio/diceroll1.mp3")
                self.song_queue.insert(len(self.song_queue)-1, "audio/DramaticSting1.mp3") if success == "critical" or success == "fumble" else None
                
                # Play audio in channel
                self.play_next(ctx)
        
    @commands.command(  pass_context=True, 
                        name='roll',
                        aliases=['r'],
                        brief="Rolls the dice.  e.g. 1D100 45 # INT",  
                        description="The ROLL command works by selecting the dice you want (1D100) and modifiers (+1) an optional stat (45) and a comment (# pump some lead into that goon!)"
                        )
    async def rollcommand(self, ctx, *, arg=None):

        # rolls the dice and stores the result as a list. if no argument, roll the default
        dice = diceroller.DiceRolls(arg if arg else self.settings.dice_default)
        embed = self.__roll_with_format__(ctx=ctx, rolls=dice)

        # ADD TO DB: putting all results in the database.  It skips when there's nothing, including failures and syntax errors!
        for roll in dice.getrolls():

            # if ^test is present in the comment, the roll will not be store in the db (for testing purposes)
            if dice.getroll().get_comment() is not None and "^test" in dice.getroll().get_comment():
                print ("Roll NOT added to Database!")
            elif self.settings.database_enabled:
                self.db.add_roll(str(ctx.author), ctx.author.display_name, arg, roll.get_equation(), roll.get_sumtotal(), roll.get_stat(), roll.get_success(), roll.get_comment(), str(ctx.guild), str(ctx.channel))
                print("{} {} {} {} {} {} {} {} {} {}".format(ctx.guild, ctx.channel, ctx.author, ctx.author.display_name, arg, roll.get_equation(), roll.get_sumtotal(), roll.get_stat(), roll.get_success(), roll.get_comment()))

        # embed a GIF or image for these special situations
        embed = self.__successlevel_image__(embed, dice.getroll())
            
        # read the results if announce is on and the bot is in a channel
        self.__announce_roll__(ctx, dice)          
        
        # dramatic pause for fumbles and criticals  
        await asyncio.sleep(4) if dice.getroll().get_success() == "fumble" or dice.getroll().get_success() == "critical" else None
        
        author_avatar_url = ctx.author.avatar_url or ctx.author.default_avatar_url
        embed.set_author(name=ctx.author.display_name, icon_url=author_avatar_url)
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command(pass_context=True)
    async def test(self, ctx, *, arg=None):
        dice = diceroller.DiceRolls(arg if arg else self.settings.dice_default, repeat=1, keep=0)
        dice.override_sumtotal(int(arg))
        embed = self.__roll_with_format__(ctx=ctx, rolls=dice, additional_comment=" - testing only.")
        embed = self.__successlevel_image__(embed, dice.getroll())
        await ctx.send(embed=embed)

    @commands.command(pass_context=True, aliases=['r+', 'b'])
    async def bonus(self, ctx, *, arg=None):
        dice = diceroller.DiceRolls(arg if arg else self.settings.dice_default, repeat=2, keep=-1)
        embed = self.__roll_with_format__(ctx=ctx, rolls=dice, additional_comment=" - with bonus.")
        await ctx.send(embed=embed)

    @commands.command(pass_context=True, aliases=['r-', 'p'])
    async def penalty(self, ctx, *, arg=None):
        dice = diceroller.DiceRolls(arg if arg else self.settings.dice_default, repeat=2, keep=1)
        embed = self.__roll_with_format__(ctx=ctx, rolls=dice, additional_comment=" - with penalty.")
        await ctx.send(embed=embed)

    @commands.command(pass_context=True, aliases=['rp', 'rpt'])
    async def repeat(self, ctx, *, arg=None):
        dice = diceroller.DiceRolls(arg if arg else self.settings.dice_default, repeat=10, keep=0)
        embed = self.__roll_with_format__(ctx=ctx, rolls=dice, additional_comment=" - repeat.")
        await ctx.send(embed=embed)

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

    @commands.group(aliases=['h'])
    async def history(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Need more...')

    @history.command(aliases=['xx'])
    async def success(self, ctx, *, arg=None):
        if mathtools.RepresentsInt(arg): #is the argument an integer value
            rolls = self.db.get_entries_as_string(number_of_entries=int(arg))
            description = "LAST ROLLS\n"
            for roll in rolls:
                description += f"{roll}\n"
            embed = discord.Embed(colour=discord.Colour(0x24ed60), description=description)
            await ctx.send(embed=embed)
        else:
            await ctx.send("bad syntax.")

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