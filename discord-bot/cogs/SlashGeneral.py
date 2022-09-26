import enum
from secrets import choice
from typing import List
import discord
from discord import app_commands
from discord.ext import commands
import mdtools
import os, uuid, requests, textwrap
import cocapi

class FF_Menu(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        
    @discord.ui.button(label="Send Message", style=discord.ButtonStyle.grey)
    async def menu1(self, button: discord.ui.Button, interaction:discord.Integration):
        print ("working")
        await button.response.send_message("CLICKED")

class GeneralCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        
        # load bot
        self.bot = bot
        
        # load context menus
        self.ctx_menu = app_commands.ContextMenu(
                name='Bot Notification',
                callback=self.my_cool_context_menu,
            )
        self.bot.tree.add_command(self.ctx_menu)

    async def __make_screenplay__ (self, 
                                   interaction, 
                                   ephemeral=False) -> None:
        
        if isinstance(interaction.channel, discord.Thread):
            # Get all messages from the channel as a list
            all_messages = [f"{message.content}" 
                            async for message in interaction.channel.history(
                                oldest_first=True)]
            
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
    
    async def skill_autocomplete(self, 
                                 interaction: discord.Interaction, 
                                 current: str) -> List[app_commands.Choice[str]]:
        
        # get full skills list
        skills = requests.get(f"http://localhost:8000/api/skill").json()
        
        skills_to_return = [] # blank results
        
        if current == "": 
            pass
        else:
            for skill in skills:
                
                # check if search is present in both skill name and specialization
                if current.lower() in skill['name'].lower() + skill['specialization'].lower():
                    name = skill['name']
                    specialization = f"" if skill['specialization'] == "" else f"[{skill['specialization']}]"
                    skills_to_return.append(
                        app_commands.Choice(
                            name=' '.join(filter(None, [name, specialization])),
                            value=int(skill['id']) ) )
            
        return skills_to_return[0:24]
    
    async def skillset_autocomplete(self, 
                                    interaction: discord.Interaction, 
                                    current: str) -> List[app_commands.Choice[str]]:

        # get full skills list
        skillsets = cocapi.get_skillsets()
        
        skills_to_return = [] # blank results
        
        for skillset in skillsets:
            if current.lower() in skillset['name'].lower():
                skills_to_return.append(
                    app_commands.Choice(
                        name=skillset.get('name', ""),
                        value=skillset.get('id')))
            
        return skills_to_return[0:24]

    async def char_stats_autocomplete(self, 
                                      interaction: discord.Interaction, 
                                      current: str) -> List[app_commands.Choice[str]]:
        for_return = []

        player = cocapi.get_or_create_player(json={
            "name": "",
            "discord_name": interaction.user.name,
            "discord_id": interaction.user.id })
        
        character = cocapi.character(player.get('character'))
        
        if character:
                
            character_stats = requests.get(f"http://localhost:8000/character-stats/{player.get('character')}").json()
            
            for_return = [app_commands.Choice(
                name=f"{stat_name} ({stat_value})", 
                value=str(stat_name))
                    for stat_name, stat_value in character_stats.items() 
                    if current == "" or current.lower() in stat_name.lower()]
                            
        return for_return[0:24]
    
    async def char_skill_autocomplete(self, 
                                           interaction: discord.Interaction, 
                                           current: str) -> List[app_commands.Choice[str]]:
        for_return = []

        player = cocapi.get_or_create_player(json={
            "name": "",
            "discord_name": interaction.user.name,
            "discord_id": interaction.user.id })

        character = cocapi.character(player.get('character'))
        
        if character:
                        
            for_return = [app_commands.Choice(
                name=f"{skill.get('name')} ({skill.get('points')})",
                value=int(skill.get('id')))
                    for skill in character.get('characterskill_set', [])
                    if current.lower() in skill['name'].lower()]
                            
        return for_return[0:24]
    
    async def attach_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        
        # get full skills list
        characters = requests.get(f"http://localhost:8000/api/character/").json()
        for_return = []
        
        if current == "": 
            # return list of characters.
            for character in characters:
                if character.get('player_fk'):
                    for_return.append(app_commands.Choice(
                        name=f"{character['investigator_name']} (TAKEN)",
                        value=str(character['id'])))
                else:
                    for_return.append(app_commands.Choice(
                        name=f"{character['investigator_name']}",
                        value=str(character['id'])))
        else:
            for character in characters:
                
                # check if search is present in both skill name and specialization
                if current.lower() in character['investigator_name'].lower():
                    for_return.append(app_commands.Choice(
                        name=character['investigator_name'],
                        value=str(character['id'])))
            
        return for_return[0:24]

    @app_commands.command(name="menu_test")
    async def menu_test(self, interaction: discord.Interaction) -> None:
        """ Menu Testing """
        view = FF_Menu()
        await interaction.response.send_message(
            content=f"Hi, {interaction.user.mention}, I'm Barnautomaton 3000. I was pieced back together at Miskatonic University and now my brain is in a jar!",
            view=view
            )

    @app_commands.command(name="hello")
    async def hello(self, interaction: discord.Interaction) -> None:
        """ Say Hello to the bot """
        await interaction.response.send_message(
            content=f"Hi, {interaction.user.mention}, I'm Barnautomaton 3000. I was pieced back together at Miskatonic University and now my brain is in a jar!")

    @app_commands.command(name="skill_info")
    @app_commands.autocomplete(skill=skill_autocomplete)
    @app_commands.describe(
        skill="Skill info. Only top 25 are visible, type to find more.",
        hide="Hide result from channel? Only you will see this." )
    async def skill_info(self, interaction: discord.Interaction, skill: int, hide: bool = True) -> None:
        """ Get detailed information on a skill. """
        skill_json = requests.get(f"http://localhost:8000/api/skill/{skill}").json()
        category = f"" if skill_json['category'] == "" else f"[{skill_json['category']}]"
        specialization = f"" if skill_json['specialization'] == "" else f"[{skill_json['specialization']}]"
        name_row_list = [skill_json['name'], category, specialization]
        name_row = ' '.join(filter(None, name_row_list))
        
        embed = discord.Embed(title=f"{name_row} | {skill_json['base_points']}%", colour=discord.Colour(0x804423), description=skill_json['description'])

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
        
    @app_commands.command(name="character_create")
    @app_commands.describe(
        skillset="What preset character skillset would you like to attach?")
    @app_commands.autocomplete(skillset=skillset_autocomplete)
    async def character_create(self, 
                               interaction: discord.Interaction, 
                               investigator_name: str,
                               alias: str,
                               occupation: str,
                               birthplace: str,
                               sex: str,
                               age: int,
                               strength: int,
                               intelligence: int,
                               appearance: int,
                               dexterity: int,
                               education: int,
                               size: int,
                               constitution: int,
                               power: int,
                               luck: int,
                               hp: int,
                               magic: int,
                               san: int,
                               skillset: int,
                               ) -> None:
        """ Create a new character by inputting stats. """
        
        # get or add player to DB
        player = cocapi.get_or_create_player(json={
            "name": "",
            "discord_name": interaction.user.name,
            "discord_id": interaction.user.id })
        
        # TODO If the player already has a character, just make new character.  if the player does NOT, auto-connect it. 
        
        # add new character to DB
        character = cocapi.create_character(json={
            "passcode": "",
            "investigator_name": investigator_name,
            "investigator_alias": alias,
            "occupation": occupation,
            "birthplace": birthplace,
            "sex": sex,
            "age": age,
            "strength": strength,
            "intelligence": intelligence,
            "appearance": appearance,
            "dexterity": dexterity,
            "education": education,
            "size": size,
            "constitution": constitution,
            "power": power,
            "luck": luck,
            "hp": hp,
            "magic": magic,
            "san": san,
            "san_daystart": san,
            "temporary_insanity": False,
            "indefinite_insanity": False,
            "dying_unconcious": False,
            "dying_majorwound": False,
            "location_fk": None,
            "player_fk": None
            })
        
        # edit the character by updating the skillset they're attached to.
        cocapi.attach_skillset_to_character(
            character_id=character.get('id'), 
            skillset_id=skillset)
        
        embed = discord.Embed(title=f"{character.get('investigator_name')} created!", 
                              colour=discord.Colour(0x804423))
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="character_attach")
    @app_commands.autocomplete(character=attach_autocomplete)
    @app_commands.describe(
        character="Which character are you taking control?")
    async def character_attach(self, 
                               interaction: discord.Interaction, 
                               character: str) -> None:
        """ Attach a character to yourself. """
        
        player = cocapi.get_or_create_player(json={
            "name": "",
            "discord_name": interaction.user.name,
            "discord_id": interaction.user.id })
        
        # set default embed
        embed = discord.Embed(title=f"Character is already in use.", 
                              description=f"", 
                              colour=discord.Colour(0x804423))
        
        # get the chosen character
        character_json = cocapi.character(character)
        
        # does the chosen character have a player?
        if character_json.get('player_fk'):
            embed.title = f"Character is already in use."
        else:
            # does the player choosing have a character already?
            if player.get('character'):
                requests.get(f"http://localhost:8000/player/{interaction.user.id}/release_character").json()
                
            requests.get(f"http://localhost:8000/character/{character}/attach_player/{interaction.user.id}").json()
            new_character = cocapi.character(character)
            embed.title = f"You are now {new_character.get('investigator_name')}"
                
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="character_release")
    async def character_release(self, 
                                interaction: discord.Interaction) -> None:
        """ Releases the character you currenty have (if you have one). """
        success = requests.get(f"http://localhost:8000/player/{interaction.user.id}/release_character").json()
        
        embed = discord.Embed(title=f"{interaction.user.name} released a character: {success.get('success')}", 
                              colour=discord.Colour(0x804423))

        await interaction.response.send_message(embed=embed, 
                                                ephemeral=True)
        

    @app_commands.command(name="character_change_name")
    @app_commands.describe(name="Character's full name", 
                           alias="Character's shorthand name (as it appears in the script).")
    async def character_change_name(self, 
                                    interaction: discord.Interaction, 
                                    name: str = "", 
                                    alias: str = "") -> None:
        """ Edit your name and alias. """
        player = cocapi.get_or_create_player(json={
            "name": "",
            "discord_name": interaction.user.name,
            "discord_id": interaction.user.id })        
        
        if player.get('character'):
            character = cocapi.character(player.get('character'))

            name  = character.get('investigator_name') if name == "" else name
            alias = character.get('investigator_alias') if alias == "" else alias
            
            cocapi.change_stat(
                id=character.get('id'),
                json={"investigator_name": name,
                      "investigator_alias": alias })
            
            embed = discord.Embed(title=f"You are now {name} aka {alias}.", 
                                  colour=discord.Colour(0x804423))

        else:
            embed = discord.Embed(title="You have no character attached. You are nobody.", 
                                  colour=discord.Colour(0x804423))
            
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="character_sheet")
    async def character_sheet(self, interaction: discord.Interaction) -> None:
        """ View your character sheet. """
        
        def split(a, n):
            k, m = divmod(len(a), n)
            return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))
        
        player = cocapi.get_or_create_player(json={
            "name": "",
            "discord_name": interaction.user.name,
            "discord_id": interaction.user.id })
        
        embed = discord.Embed(title=f"Error?", 
                              description="Error?",
                              colour=discord.Colour(0x804423))
        
        if player.get('character'):
            character = cocapi.character(player.get('character'))
            
            description = f"""
                {character.get('occupation')} | {character.get('age')} | {character.get('sex')}
                
                **STR** {character.get('strength')} | **INT** {character.get('intelligence')} | **APP** {character.get('appearance')} | **DEX** {character.get('dexterity')}
                **EDU** {character.get('education')} | **SIZ** {character.get('size')} | **CON** {character.get('constitution')} | **POW** {character.get('power')}
                **MOV** {character.get('move')} | **DMG BONUS** {character.get('damage_bonus')} | **BUILD** {character.get('build')}

                **HP** {character.get('hp')} / {character.get('hp_max')}
                **SAN** {character.get('san')} / {character.get('san_max')}  ||  **DAY**: {character.get('san_daystart')}
                **LUCK** {character.get('luck')}
                
                **MAGIC** {character.get('magic')} / {character.get('magic_max')}
                
                """
                
            embed = discord.Embed(
                
                title=f"{character.get('investigator_name')}", 
                description=textwrap.dedent(description),
                colour=discord.Colour(0x804423))
            
            # split the skills list into 3 columns
            newlist = sorted(character.get('characterskill_set'), key=lambda d: d['name']) 
            skill_columns = list(split(newlist, 3))
            
            for column in skill_columns:
                skills_list = ""
                for skill in column:
                    skills_list += f"{skill.get('name')} {skill.get('points')}\n"
                    
                embed.add_field(name=f"SKILLS", value=f"{skills_list}", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        
    @app_commands.command(name="who_am_i")
    async def who_am_i(self, interaction: discord.Interaction) -> None:
        """ Who am I currently playing as? """
        
        player = cocapi.get_or_create_player(json={
            "name": "",
            "discord_name": interaction.user.name,
            "discord_id": interaction.user.id })
        
        embed = discord.Embed(title=f"You are nobody.", 
                              colour=discord.Colour(0x804423))
        
        if player.get('character'):
            character = cocapi.character(player.get('character'))
            embed = discord.Embed(title=f"You are {character.get('investigator_name')}", 
                                  colour=discord.Colour(0x804423))
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

        
    @app_commands.command(name="change_stat")
    @app_commands.autocomplete(stat=char_stats_autocomplete)
    @app_commands.describe(
        stat="Characteristic modify.",
        modify="New characteristic value.")
    async def change_stat(self, 
                          interaction: discord.Interaction, 
                          stat: str, 
                          modify: int) -> None:
        """ Modify your character's characteristics. """

        player = cocapi.get_or_create_player(json={
            "name": "",
            "discord_name": interaction.user.name,
            "discord_id": interaction.user.id })
        
        character = cocapi.character(player.get('character'))

        cocapi.change_stat(
            id=character.get('id'),
            json={stat: modify})
        embed = discord.Embed(title=f"{stat} now {modify}.", 
                              colour=discord.Colour(0x804423))
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @app_commands.command(name="add_skill")
    @app_commands.autocomplete(skill=skill_autocomplete)
    @app_commands.describe(
        skill="Skill to add.")
    async def add_skill(self, interaction: discord.Interaction, skill: int) -> None:
        """ Add a skill to your character. """
        
        embed = discord.Embed(title=f"ERROR", 
                              colour=discord.Colour(0x804423))
        
        player = cocapi.get_or_create_player(json={
            "name": "",
            "discord_name": interaction.user.name,
            "discord_id": interaction.user.id })
        
        if player.get('character'):
            character = cocapi.character(id=player.get('character'))
            # apply the new fields to the skill
            cocapi.add_charskill(json={"skill_fk": skill,
                                       "character_fk": character.get('id') })
        
            embed = discord.Embed(title=f"Skill added.", 
                                  colour=discord.Colour(0x804423))
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @app_commands.command(name="change_skill")
    @app_commands.autocomplete(skill=char_skill_autocomplete)
    @app_commands.describe(
        skill="Skill to check or modify.",
        name="Modify the name as it appears on your character sheet, e.g. Language(Other) could be Spanish.",
        stat="New skill value.",
        delete="Delete the selected skill from your character sheet.")
    async def change_skill(self, 
                           interaction: discord.Interaction, 
                           skill: int, 
                           name: str = "", 
                           stat: int = -1, 
                           delete: bool = False) -> None:
        """ Modify your character's skills. """
        
        charskill = requests.get(f"http://localhost:8000/api/characterskill/{skill}").json()
            
        # sets the stat to the default if its not included
        stat = stat if stat >= 0 else charskill.get('points')
        
        # set name to old name unless changed
        name = charskill.get('name') if name == "" else name
            
        # get the new experience points based on what the user enters
        difference = stat - charskill.get('points')
        new_experience = charskill.get('experience_points') + difference
        
        # apply the new fields to the skill
        new_skill = cocapi.change_charskill(
            id=skill,json={"name_override": name,
                           "experience_points": new_experience })
        
        # delete the skill if delete is selected
        if delete:
            cocapi.delete_charskill(id=skill)
        
        embed = discord.Embed(title=f"Skill: {new_skill.get('name')} now {new_skill.get('points')}", 
                              colour=discord.Colour(0x804423))
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @app_commands.command(name="skill_favorite")
    @app_commands.autocomplete(skill=char_skill_autocomplete)
    @app_commands.describe(
        skill="Skill to favorite or unfavorite.",
        favorite="True to favorite, False to unfavorite.")
    async def skill_favorite(self, 
                             interaction: discord.Interaction, 
                             skill: int, 
                             favorite: bool) -> None:
        """ Add skill to favorites list. """
        
        # apply the new fields to the skill
        cocapi.change_charskill(id=skill, json={ "favorite": favorite })
        
        embed = discord.Embed(title=f"Skill Favorited: {favorite}.", 
                              colour=discord.Colour(0x804423))
        
        await interaction.response.send_message(embed=embed, 
                                                ephemeral=True)


    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="admin_rolls_testing")
    async def admin_rolls_testing(self, 
                                  interaction: discord.Interaction, 
                                  totalmsgs: int) -> None:        
        """ Testing for admin use only."""
        
        rolls = cocapi.get_rolls_history(interaction.channel.id, 4)
        
        embed = discord.Embed(title=f"check logs.", 
                              colour=discord.Colour(0x804423))
        print(rolls)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="admin_testing")
    async def admin_testing(self, 
                            interaction: discord.Interaction, 
                            totalmsgs: int) -> None:
        """ Testing for admin use only."""
        
        embed = discord.Embed(title=f"You are not an admin.", 
                              colour=discord.Colour(0x804423))
        
        if interaction.user.id == 222234033650794497:        
            async for message in interaction.channel.history(limit=totalmsgs):
                
                # reference = message.reference.message_id if message.reference is not None and not message.is_system else None

                # check if player is in the system, if not add.
                player = cocapi.get_or_create_player(json={
                    "name": "",
                    "discord_name": message.author.name,
                    "discord_id": message.author.id })
                
                print (player)
                
                # check if this particular channel is in the system, if not, add.
                channel = cocapi.get_or_create_channel(json={
                    "name": message.channel.name,
                    "channel_id": message.channel.id,
                    "parent_id": 0 })                
                
                print (channel)
                
                # save the message to the db
                newmessage = cocapi.create_message(json={
                    "messagetime": message.created_at.isoformat(),
                    "discord_id": message.id,
                    "content": message.content,
                    "reply_msg_id": message.reference.message_id if message.reference is not None else None,
                    "player": player.get('id'),
                    "discordchannel": channel.get('id') })
                
                print (newmessage)
                        
            embed = discord.Embed(title=f"Added messages to DB.", colour=discord.Colour(0x804423))
            
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="admin_reply")
    async def admin_reply(self, 
                          interaction: discord.Interaction, 
                          custom_msg: str, 
                          msg_id: str) -> None:
        """ Testing for admin use only."""
        
        msg_id_int = int(msg_id)
        msg = await interaction.channel.fetch_message(msg_id_int)
        
        new_message = f"Howdy! Found a formatting error in this message:\n{msg.jump_url} \n{custom_msg}"
        
        await msg.author.send(new_message)
        await interaction.response.send_message(f'Message sent.\n{new_message}', ephemeral=True)

    # @app_commands.checks.has_permissions(ban_members=True)
    # @app_commands.guilds(12345)
    @app_commands.checks.has_permissions(administrator=True)
    async def my_cool_context_menu(self, 
                                   interaction: discord.Interaction, 
                                   message: discord.Message) -> None:
        # await message.reply.send_message("test!", ephemeral=True)
        await message.author.send("test!")
        await interaction.response.send_message('Message sent.', ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GeneralCog(bot))
    
    