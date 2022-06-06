import discord
from discord import app_commands
from discord.ext import commands
import requests, diceroller, mathtools, settings

def __roll_with_format__(interaction, rolls, additional_comment=""):

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

    #author_avatar_url = interaction.user.avatar.url or interaction.user.display_avatar.url
    #embed.set_author(name=interaction.user.display_name, icon_url=author_avatar_url)
    #embed.set_author(name=f"{ctx.author.display_name} - {comment}{additional_comment}", icon_url=author_avatar_url)

    return embed

class MyCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings = settings.Settings()

    @app_commands.command()
    @app_commands.describe(dice='Dice or stat to roll.')
    async def roll(self, interaction: discord.Interaction, dice: str, comment: str = "", repeat: int = 1, keep: int = 0):
        """ Basic Dice Rolls """
        diceresult = diceroller.DiceRolls(dice, repeat=repeat, keep=keep)
        embed = __roll_with_format__(interaction=interaction, rolls=diceresult, additional_comment=comment)
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(name="roll_advantage")
    @app_commands.describe(dice='Dice or stat to roll.')
    async def roll_advantage(self, interaction: discord.Interaction, dice: str, comment: str = ""):
        """ Roll Dice with Advantage / Bonus """
        diceresult = diceroller.DiceRolls(dice, repeat=2, keep=-1)
        embed = __roll_with_format__(interaction=interaction, rolls=diceresult, additional_comment=comment)
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(name="roll_disadvantage")
    @app_commands.describe(dice='Dice or stat to roll.')
    async def roll_disadvantage(self, interaction: discord.Interaction, dice: str, comment: str = ""):
        """ Roll Dice with Disadvantage / Penalty """
        diceresult = diceroller.DiceRolls(dice, repeat=2, keep=1)
        embed = __roll_with_format__(interaction=interaction, rolls=diceresult, additional_comment=comment)
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(name="roll_improvements")
    @app_commands.describe(stats='Stats to Improve, can be one or more and must be separated by a space.')
    async def roll_improvements(self, interaction: discord.Interaction, stats: str):
        """ Roll Improvements """

        description = ""
        stats = stats.split(" ")
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
        #author_avatar_url = interaction.user.avatar.url or interaction.user.display_avatar.url
        #embed.set_author(name=interaction.user.display_name, icon_url=author_avatar_url)
        await interaction.response.send_message(embed=embed)

        diceresult = diceroller.DiceRolls(dice, repeat=2, keep=1)
        embed = __roll_with_format__(interaction=interaction, rolls=diceresult)
        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MyCog(bot))