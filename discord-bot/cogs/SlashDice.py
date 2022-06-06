import discord
from discord import app_commands
from discord.ext import commands
import requests, diceroller

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

    author_avatar_url = interaction.user.avatar.url or interaction.user.display_avatar.url
    embed.set_author(name=interaction.user.display_name, icon_url=author_avatar_url)
    #embed.set_author(name=f"{ctx.author.display_name} - {comment}{additional_comment}", icon_url=author_avatar_url)

    return embed

class MyCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

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
    @app_commands.describe(dice='Stats to Improve, can be one or more.')
    async def roll_improvements(self, interaction: discord.Interaction, dice: str):
        """ Roll Improvements """
        diceresult = diceroller.DiceRolls(dice, repeat=2, keep=1)
        embed = __roll_with_format__(interaction=interaction, rolls=diceresult)
        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MyCog(bot))