import enum
from secrets import choice
from typing import List
import discord
from discord import app_commands
from discord.ext import commands
import mdtools
import os, uuid, requests, textwrap

class GeneralCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def __make_screenplay__ (self, interaction, ephemeral=False) -> None:
        if isinstance(interaction.channel, discord.Thread):
            # Get all messages from the channel as a list
            all_messages = [f"{message.content}" 
                            async for message in interaction.channel.history(oldest_first=True)]
            
            # extract the code fence from each message individually, and create a new list
            fountain_md = []
            for message in all_messages:
                fences = mdtools.extract_code_fences(message)
                if len(fences) > 0:
                    fountain_md.append('\n\n'.join(fences))
            
            # join each line together with a line break.
            fountain_md_joined = '\n\n'.join(fountain_md)

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
                await interaction.response.send_message(
                    file=discord.File(tempfilename), 
                    ephemeral=ephemeral)

            os.remove(tempfilename) if os.path.exists(tempfilename) else print("The file does not exist")
        else:
            await interaction.response.send_message(
                content="This only works in threads", 
                ephemeral=True)
    

    @app_commands.command(name="hello")
    async def hello(self, interaction: discord.Interaction) -> None:
        """ Say Hello to the bot """
        await interaction.response.send_message(
            content=f"Hi, {interaction.user.mention}, I'm Barnautomaton 3000. I was pieced back together at Miskatonic University and now my brain is in a jar!")


    async def skill_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        
        # get full skills list
        skills = requests.get(f"http://localhost:8000/charactersheet/skills").json()
        
        if current == "": 
            # return blank list first
            return []
        else:
            skills_to_return = [] # blank results
            for skill in skills['skills']:
                
                # check if search is present in both skill name and specialization
                if current.lower() in skill['name'].lower() + skill['specialization'].lower():
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
        hide="Hide result from channel? Only you will see this." )
    async def skill(self, interaction: discord.Interaction, skillid: str, hide: bool = False) -> None:
        """ Skill by id """
        skill = requests.get(f"http://localhost:8000/charactersheet/skill/{skillid}").json()
        category = f"" if skill['category'] == "" else f"[{skill['category']}]"
        specialization = f"" if skill['specialization'] == "" else f"[{skill['specialization']}]"
        name_row_list = [skill['name'], category, specialization]
        name_row = ' '.join(filter(None, name_row_list))
        
        embed = discord.Embed(title=f"{name_row} | {skill['base_points']}%", colour=discord.Colour(0x804423), description=skill['description'])

        await interaction.response.send_message(
            embed=embed,
            ephemeral=hide)

    @app_commands.command(name="make_screenplay")
    async def make_screenplay(self, interaction: discord.Interaction) -> None:
        """ Creates a screenplay from the current channel or thread. """
        await self.__make_screenplay__(interaction, ephemeral=True)

    @app_commands.command(name="fadeout")
    async def fadeout(self, interaction: discord.Interaction) -> None:
        """ End the scene, makes a screenplay and lock the thread. """
        await self.__make_screenplay__(interaction, ephemeral=False)
        if isinstance(interaction.channel, discord.Thread) : await interaction.channel.edit(archived=True, locked=True)

    @app_commands.command(name="template")
    async def template(self, interaction: discord.Interaction) -> None:
        """ Get a template for the screenplay format. """
        content = """
        ```
        NAME
        Dialogue.
        ```
        """

        await interaction.response.send_message(
            content=textwrap.dedent(content),
            ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GeneralCog(bot))
    
    