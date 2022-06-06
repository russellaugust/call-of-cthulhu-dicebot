import enum
from secrets import choice
from typing import List
import discord
from discord import app_commands
from discord.ext import commands
import mdtools
import os, uuid, requests

def skill_list():
    skills = requests.get(f"http://localhost:8000/charactersheet/skills").json()
    return [app_commands.Choice(name=skill['name'], value=skill['id']) for skill in skills['skills']]

class GeneralCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def __make_and_send_screenplay__ (self, interaction) -> None:
        if isinstance(interaction.channel, discord.Thread):
            all_messages = [f"{message.content}" async for message in interaction.channel.history(oldest_first=True)]
            fountain_md = mdtools.extract_code_fences('\n'.join(all_messages))
            fountain_md_joined = '\n'.join(fountain_md)

            # make fountain file
            tempfilename = f"{interaction.channel.name}_{uuid.uuid4()}.fountain"
            f = open(tempfilename, "w")
            f.write(fountain_md_joined)
            f.close()

            if len(fountain_md) == 0:
                await interaction.response.send_message(
                    content="There appears to be no screenplay formatted items here.", 
                    ephemeral=True)
            else:                
                await interaction.response.send_message(file=discord.File(tempfilename))

            os.remove(tempfilename) if os.path.exists(tempfilename) else print("The file does not exist")
        else:
            await interaction.response.send_message(content="This only works in threads", ephemeral=True)
    
    @app_commands.command(name="hello")
    async def hello(self, interaction: discord.Interaction) -> None:
        """ Say Hello to the bot """
        await interaction.response.send_message(f"Hi, {interaction.user.mention}, I'm Barnautomaton 3000. I was pieced back together at Miskatonic University and now my brain is in a jar!")

    async def skill_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        skills = requests.get(f"http://localhost:8000/charactersheet/skills").json()
        if current == "": 
            return [app_commands.Choice(name="", value="")]
        else:
            skills_to_return = []
            for skill in skills['skills']:
                if current.lower() in skill['name'].lower():
                    name = skill['name']
                    specialization = f"" if skill['specialization'] == "" else f"[{skill['specialization']}]"
                    skills_to_return.append(
                        app_commands.Choice(
                            name=' '.join(filter(None, [name, specialization])),
                            value=str(skill['id']) ) )
            return skills_to_return[0:24]

    @app_commands.command(name="skill")
    @app_commands.autocomplete(skillid=skill_autocomplete)
    @app_commands.describe(
        skillid="Skill info.  Only top 25 are visible, type to find more.",
        hide="Hide result from channel? Only you will see this."
    )
    async def skill(self, interaction: discord.Interaction, skillid: str, hide: bool = False) -> None:
        """ Skill by id """
        skill = requests.get(f"http://localhost:8000/charactersheet/skill/{skillid}").json()
        category = f"" if skill['category'] == "" else f"[{skill['category']}]"
        specialization = f"" if skill['specialization'] == "" else f"[{skill['specialization']}]"
        name_row_list = [skill['name'], category, specialization]
        name_row = ' '.join(filter(None, name_row_list))
        await interaction.response.send_message(
            content=f"**{name_row}** | {skill['base_points']}%\n{skill['description']}",
            ephemeral=hide)

    @app_commands.command(name="make_screenplay")
    async def make_screenplay(self, interaction: discord.Interaction) -> None:
        """ Creates a screenplay from the current channel or thread. """
        await self.__make_and_send_screenplay__(interaction)

    @app_commands.command(name="fadeout")
    async def fadeout(self, interaction: discord.Interaction) -> None:
        """ End the scene, makes a screenplay and lock the thread. """
        await self.__make_and_send_screenplay__(interaction)
        if isinstance(interaction.channel, discord.Thread) : await interaction.channel.edit(archived=True, locked=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GeneralCog(bot))