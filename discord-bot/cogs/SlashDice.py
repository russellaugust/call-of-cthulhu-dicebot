import discord
from discord import app_commands
from discord.ext import commands
import requests, diceroller, mathtools, settings, random, os, asyncio, json
from slugify import slugify
from diceroller import DiceRolls
import cocapi
from typing import List

API_LINK = "http://localhost:8000/api/"

#discord.opus.load_opus('opus')

    
def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True

class MyCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.song_queue = []
        self.settings = settings.Settings()
        
    async def opposingroll_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        rolls_history = cocapi.get_rolls_history(interaction.channel.id, 8)
        
        autofill_rolls = [app_commands.Choice(
            name=f"{roll.get('player').get('discord_name')} - {roll.get('result')} - {roll.get('comment')}",
            value=int(roll.get('id')) )
                          for roll in rolls_history if roll.get('result')]
        
        return autofill_rolls[0:24]
        
    async def roll_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        """ skill, stats and favorites list"""
        
        player = cocapi.get_or_create_player(json={
                "name": "",
                "discord_name": interaction.user.name,
                "discord_id": interaction.user.id })
        
        
        character = requests.get(f"http://localhost:8000/api/character/{player.get('character')}").json()

        # blank source
        options = []
        
        # return a list of starred skills and stats
        if current == "": 
            if player.get('character'):
                character_stats = requests.get(f"http://localhost:8000/character-stats/{player.get('character')}").json()
                
                favorite_skills = [app_commands.Choice(
                    name=f"{skill.get('name')} ({skill.get('points')})",
                    value=json.dumps( {"type"  : f"{skill.get('name')}",
                                       "value" : f"{skill.get('points')}"} ))
                                   for skill in character.get('characterskill_set') 
                                   if skill.get('favorite')]
                stats = [app_commands.Choice(
                    name=f"{stat_name} ({stat_value})", 
                    value=json.dumps( {"type"   : f"{stat_name}",
                                       "value"  : f"{stat_value}"} ))
                         for stat_name, stat_value in character_stats.items()]
                options += favorite_skills + stats

        # return a list of starred skills and stats
        elif current == "stats" or current == "characteristics": 
            if player.get('character'):
                character_stats = requests.get(f"http://localhost:8000/character-stats/{player.get('character')}").json()
                
                options += [app_commands.Choice(
                    name=f"{stat_name} ({stat_value})", 
                    value=json.dumps( {"type"   : f"{stat_name}",
                                       "value"  : f"{stat_value}"} ))
                        for stat_name, stat_value in character_stats.items()]
            
        # rolling a stat
        elif current.isnumeric():
            options.append(
                app_commands.Choice(
                    name=f"Will roll a 1D100 against {current}",
                    value=json.dumps( {"type"   : f"rolling...",
                                       "value"  : f"{current}"} )))
        
        # elif diceroller is valid diceroller.DiceRolls(current):
            # return 
            
        else:
            if player.get('character'):
                        
                character_stats = requests.get(f"http://localhost:8000/character-stats/{player.get('character')}").json()
                
                skills = [{"name"   : skill.get('name'),
                           "points" : skill.get('points') }
                          for skill in character.get('characterskill_set', [])]
                stats = [{"name"   : stat_name,
                          "points" : stat_value }
                         for stat_name, stat_value in character_stats.items()]
                all_options = skills + stats
                
                for option in all_options:
                    # check if search is present in both skill name and specialization
                    if current.lower() in option.get('name', '').lower():
                        options.append( app_commands.Choice(
                            name=f"{option.get('name')} ({option.get('points')})",
                            value=json.dumps( {"type"   : f"{option.get('name')}",
                                               "value"  : f"{option.get('points')}"} )))
        
        return options[0:24]

        
    @app_commands.command(name="roll")
    @app_commands.autocomplete(roll=roll_autocomplete, opposing=opposingroll_autocomplete)
    @app_commands.describe(
        roll="What to roll. If you have a character, stats and skills will populate.",
        description="Describe what you're doing.",
        repeat="How many times do you want to peform this roll?",
        keep="How many of the repeating rolls do you want to keep? e.g. -1 is lowest roll, +2 is highest 2 rolls.",
        opposing="If this is an opposed roll, select the roll you are opposing.",
        hidden="Enable to roll just for yourself.")
    async def roll(self, interaction: discord.Interaction, roll: str, 
                   description: str = "", repeat: int = 1, keep: int = 0, 
                   opposing: int = -1, hidden: bool = False):
        """ Roll dice or using your character's stats and skills. """

        # awful hack to get the roller to work right. 
        roll = roll if is_json(roll) else json.dumps({"type" : "rolling...", "value" : str(roll)})
        roll = json.loads(roll) if isinstance(json.loads(roll), dict) else {"type" : "rolling...", "value" : str(roll)}
        diceresult = diceroller.DiceRolls(roll.get('value'), repeat=repeat, keep=keep, comment=description)
        
        embed = self.__roll_with_format__(interaction=interaction, rolls=diceresult, rolltype=roll.get('type'))
        
        # embed a GIF or image when needed
        embed = self.__successlevel_image__(embed, diceresult.getroll())

        # read the results if announce is on and the bot is in a channel
        self.__announce_roll__(interaction, diceresult.getroll())
        
        # add the rolls to the database
        self.__add_to_db__(interaction, diceresult)
        
        # dramatic pause for fumbles and criticals  
        await asyncio.sleep(4) if diceresult.getroll().get_success() == "fumble" or diceresult.getroll().get_success() == "critical" else None
        
        # TODO: make opposing rolls look nicer.
        if opposing > -1:
            opposing_roll = cocapi.get_roll(id=opposing)
            embed.add_field(name=f"Roll 1: {opposing_roll.get('comment')}", value=f"{opposing_roll.get('success')}", inline=True)
            embed.add_field(name=f"Roll 2 {interaction.user.name}", value=f"{diceresult.getroll().get_success()}", inline=True)
        
        # send response
        await interaction.response.send_message(embed=embed, ephemeral=hidden)

    @app_commands.command(name="roll_advantage")
    @app_commands.autocomplete(roll=roll_autocomplete)
    @app_commands.describe(
        roll="What to roll. If you have a character, stats and skills will populate.",
        description="Describe what you're doing.",
        repeat="How many times do you want to peform this roll?",
        keep="How many of the repeating rolls do you want to keep? e.g. -1 is lowest roll, +2 is highest 2 rolls.",
        opposing="If this is an opposed roll, select the roll you are opposing.")
    async def roll_advantage(self, interaction: discord.Interaction, roll: str, 
                   description: str = "", repeat: int = 1, keep: int = 0, 
                   opposing: int = 0):
        """ Roll with Advantage / Bonus """
        
        # awful hack to get the roller to work right. 
        roll = json.loads(roll) if isinstance(json.loads(roll), dict) else {"type" : "rolling...", "value" : str(roll)}
        diceresult = diceroller.DiceRolls(roll.get('value'), repeat=2, keep=-1, comment=description)
        
        embed = self.__roll_with_format__(interaction=interaction, 
                                          rolls=diceresult, 
                                          additional_comment=f" - *with advantage*")
        
        not_omitted = diceresult.not_omitted_rolls()[0]
        embed = self.__successlevel_image__(embed, not_omitted)
        self.__announce_roll__(interaction, not_omitted)
        
        # add the rolls to the database
        self.__add_to_db__(interaction, diceresult)

        await interaction.response.send_message(embed=embed, ephemeral=False)


    @app_commands.command(name="roll_disadvantage")
    @app_commands.autocomplete(roll=roll_autocomplete)
    @app_commands.describe(
        roll="What to roll. If you have a character, stats and skills will populate.",
        description="Describe what you're doing.",
        repeat="How many times do you want to peform this roll?",
        keep="How many of the repeating rolls do you want to keep? e.g. -1 is lowest roll, +2 is highest 2 rolls.",
        opposing="If this is an opposed roll, select the roll you are opposing.")
    async def roll_disadvantage(self, interaction: discord.Interaction, roll: str, 
                   description: str = "", repeat: int = 1, keep: int = 0, 
                   opposing: int = 0):
        """ Roll with Disadvantage / Penalty """
        
        # awful hack to get the roller to work right. 
        roll = json.loads(roll) if isinstance(json.loads(roll), dict) else {"type" : "rolling...", "value" : str(roll)}
        diceresult = diceroller.DiceRolls(roll.get('value'), repeat=2, keep=1, comment=description)

        embed = self.__roll_with_format__(interaction=interaction, rolls=diceresult, additional_comment=f" - *with disadvantage*")

        not_omitted = diceresult.not_omitted_rolls()[0]
        embed = self.__successlevel_image__(embed, not_omitted)
        self.__announce_roll__(interaction, not_omitted)
        
        # add the rolls to the database
        self.__add_to_db__(interaction, diceresult)

        await interaction.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(name="roll_test")
    @app_commands.describe(stat='Entered number will be the resulting die roll, testing only.')
    async def roll_test(self, interaction: discord.Interaction, stat: int, comment: str = ""):
        """ Command for testing roll results only. """
        if interaction.user.top_role.permissions.administrator:  
            diceresult = diceroller.DiceRolls(str(stat), repeat=2, keep=-1)
            diceresult.override_sumtotal(stat)
            embed = self.__roll_with_format__(interaction=interaction, rolls=diceresult, additional_comment=f" - *TEST ONLY*")
            
            not_omitted = diceresult.not_omitted_rolls()[0]
            embed = self.__successlevel_image__(embed, not_omitted)
            self.__announce_roll__(interaction, not_omitted)

            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        else:
            await interaction.response.send_message(content="Sorry, but you are not an admin.", ephemeral=True)

    @app_commands.command(name="roll_improvements")
    @app_commands.describe(stats='Stats to Improve, can be one or more and must be separated by a space.')
    async def roll_improvements(self, interaction: discord.Interaction, stats: str):
        """ Roll Improvements (no character sheet implemntation yet) """

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
    
    
    def __roll_with_format__(self, interaction, rolls, rolltype="", additional_comment="") -> discord.Embed:
        
        # FAIL: the sum of the rolls is NONE, which indicates there was a problem in the syntax or code.  Produces error.
        if rolls.getroll().error():
            embed = discord.Embed(colour=discord.Colour(0xbf1919), 
                                  description="*SPROÜTS!*   That's some bad syntax.")

        # FAIL: if someone accidentally writes d00, which means roll a zero-sided die
        elif "d00" in rolls.getroll().get_argument():
            embed = discord.Embed(colour=discord.Colour(0xbf1919), 
                                  description="This is embarrassing... I doubt you meant to roll that.")

        # PASS: If the success field in the first dice roll is filled in, then that means it had to be a stat roll with a 1d100 so it. 
        elif rolls.getroll().stat_exists():
            pass

        description = ""
        color = 0x0968ed

        for roll in rolls.getrolls():
            description += roll.get_string() + "\n"
            color = color if roll.is_omitted() else roll.get_success_color()

        comment = rolls.getroll().get_comment() if rolls.getroll().get_comment() else ""
            
        comment = rolltype if comment == "" else comment
        embed = discord.Embed(title=f"{comment}{additional_comment}", colour=discord.Colour(color), description=description)
        
        # TODO gotta get the roller names on the roll
        player = cocapi.get_or_create_player(json={
                "name": "",
                "discord_name": interaction.user.name,
                "discord_id": interaction.user.id })
        
        author_avatar_url = interaction.user.avatar.url or interaction.user.display_avatar.url
        
        if player.get('character'):
            character = cocapi.character(player.get('character'))    
            embed.set_author(name=f"{character.get('alias')} ({interaction.user.display_name})", icon_url=author_avatar_url)
        else:
            embed.set_author(name=interaction.user.display_name, icon_url=author_avatar_url)
        return embed
    
    def __add_to_db__(self, interaction: discord.Interaction, rolls: DiceRolls):
        """
        Save the roll to the remote database.
        """

        # check if player is in the system, if not add.
        player = cocapi.get_or_create_player(json={
            "name": "",
            "discord_name": interaction.user.name,
            "discord_id": interaction.user.id })
        
        # check if this particular channel is in the system, if not, add.
        parent_id = interaction.channel.parent_id if isinstance(interaction.channel, discord.Thread) else None
        
        channel = cocapi.get_or_create_channel(json={
            "name": interaction.channel.name,
            "channel_id": interaction.channel.id,
            "parent_id": parent_id })

        all_rolls = [
            {
                "messagetime": interaction.created_at.isoformat(),
                "argument": roll.get_argument(),
                "equation": roll.get_equation(),
                "result": roll.get_sumtotal(),
                "stat": roll.get_stat(),
                "success": roll.get_success(),
                "comment": roll.get_comment(),
                "omit": roll.is_omitted(),
                "player": player.get('id'),
                "discordchannel": channel.get('id')
            }
            for roll in rolls.getrolls()]
        
        for roll in all_rolls:
            cocapi.create_roll(json=roll)

    def __successlevel_image__(self, embed, roll) -> discord.Embed:
        # returns a discord.embed image with a gif that matches the roll success
        
        #raise ValueError('not class RollResult.') if roll is not diceroller.RollResult else None
        if roll.get_success() == "lucky success":
            embed.set_image(url=self.settings.gif_random_lucky)
        elif roll.get_success() == "critical":
            embed.set_image(url=self.settings.gif_random_critical)
        elif roll.get_success() == "fumble":
            embed.set_image(url=self.settings.gif_random_fumble)
        return embed

    def __announce_roll__(self, interaction: discord.Interaction, roll):
        vc = interaction.guild.voice_client
        if self.settings.announce and vc and roll.stat_exists():
            success = roll.get_success() if roll.get_success() is not None else ""
            success_slugify = slugify(success, lowercase=True)

            voicefolder = self.settings.current_voice_path
            max_vo_variations = self.count_files_starting_with(voicefolder, success_slugify)

            path = f'{voicefolder}/{success_slugify}-{random.randint(1,max_vo_variations)}.mp3'
            self.song_queue.append(path)

            if not vc.is_playing():
                self.song_queue.insert(0, "audio/diceroll1.mp3")
                self.song_queue.insert(len(self.song_queue)-1, "audio/DramaticSting1.mp3") if success == "critical" or success == "fumble" else None
                
                # Play audio in channel
                self.play_next(interaction)


    def play_next(self, interaction):
        if len(self.song_queue) >= 1:
            vc = interaction.guild.voice_client

            # play sound
            vc.play(discord.FFmpegPCMAudio(source=self.song_queue[0]), after=lambda e: self.play_next(interaction))

            # Lets set the volume to 1
            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = self.settings.voice_volume

            del self.song_queue[0]

    def count_files_starting_with(self, folder, starting):
        counter = 0
        for file in os.listdir(folder):
            counter += 1 if file.startswith(starting) else 0
        return counter

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MyCog(bot))