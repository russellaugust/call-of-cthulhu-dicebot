import discord
from discord import app_commands
from discord.ext import commands
import requests, diceroller, mathtools, settings, random, os, asyncio
from slugify import slugify
from diceroller import DiceRolls
import cocapi

API_LINK = "http://localhost:8000/charactersheet/"

#discord.opus.load_opus('opus')

class MyCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.song_queue = []
        self.settings = settings.Settings()

    @app_commands.command()
    @app_commands.describe(dice='Dice or stat to roll.')
    async def roll(self, interaction: discord.Interaction, dice: str, comment: str = "", repeat: int = 1, keep: int = 0):
        """ Basic Dice Rolls """
        diceresult = diceroller.DiceRolls(dice, repeat=repeat, keep=keep, comment=comment)
        
        embed = self.__roll_with_format__(interaction=interaction, rolls=diceresult)
        
        # embed a GIF or image when needed
        embed = self.__successlevel_image__(embed, diceresult.getroll())

        # read the results if announce is on and the bot is in a channel
        self.__announce_roll__(interaction, diceresult.getroll())
        
        # add the rolls to the database
        self.__add_to_db__(interaction, diceresult)
        
        # dramatic pause for fumbles and criticals  
        await asyncio.sleep(4) if diceresult.getroll().get_success() == "fumble" or diceresult.getroll().get_success() == "critical" else None

        # send response
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(name="roll_advantage")
    @app_commands.describe(dice='Dice or stat to roll.')
    async def roll_advantage(self, interaction: discord.Interaction, dice: str, comment: str = ""):
        """ Roll Dice with Advantage / Bonus """
        diceresult = diceroller.DiceRolls(dice, repeat=2, keep=-1)
        embed = self.__roll_with_format__(interaction=interaction, rolls=diceresult, additional_comment=f" - *with advantage*")
        
        not_omitted = diceresult.not_omitted_rolls()[0]
        embed = self.__successlevel_image__(embed, not_omitted)
        self.__announce_roll__(interaction, not_omitted)
        
        # add the rolls to the database
        self.__add_to_db__(interaction, diceresult)

        await interaction.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(name="roll_disadvantage")
    @app_commands.describe(dice='Dice or stat to roll.')
    async def roll_disadvantage(self, interaction: discord.Interaction, dice: str, comment: str = ""):
        """ Roll Dice with Disadvantage / Penalty """
        diceresult = diceroller.DiceRolls(dice, repeat=2, keep=1)
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
        diceresult = diceroller.DiceRolls(str(stat), repeat=2, keep=-1)
        diceresult.override_sumtotal(stat)
        embed = self.__roll_with_format__(interaction=interaction, rolls=diceresult, additional_comment=f" - *TEST ONLY*")
        
        not_omitted = diceresult.not_omitted_rolls()[0]
        embed = self.__successlevel_image__(embed, not_omitted)
        self.__announce_roll__(interaction, not_omitted)

        await interaction.response.send_message(embed=embed, ephemeral=True)

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
    
    
    # # TODO this is wrong, using old copy of def, revise to use a skil list for the PLAYER'S CHARACTER
    # async def character_skill_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    #     skills = requests.get(f"http://localhost:8000/charactersheet/skills").json()
        
    #     # TODO This should list the favorites first! Good place for this.
    #     if current == "": 
    #         return []
    #     else:
    #         skills_to_return = [] # blank results
    #         for skill in skills['skills']:
    #             if current.lower() in skill['name'].lower():
    #                 name = skill['name']
    #                 specialization = f"" if skill['specialization'] == "" else f"[{skill['specialization']}]"
    #                 skills_to_return.append(
    #                     app_commands.Choice(
    #                         name=' '.join(filter(None, [name, specialization])),
    #                         value=str(skill['id']) ) )
    #         return skills_to_return[0:24]

    # @app_commands.command(name="my_roll")
    # @app_commands.autocomplete(skillid=character_skill_autocomplete)
    # @app_commands.describe(
    #     skill='Roll for players with character sheets.')
    # async def my_roll(self, interaction: discord.Interaction, skillid: str, comment: str = "", repeat: int = 1, keep: int = 0) -> None:
    #     """ Roll for players with character sheets"""
    #     skill = requests.get(f"http://localhost:8000/charactersheet/skill/{skillid}").json()
    #     category = f"" if skill['category'] == "" else f"[{skill['category']}]"
    #     specialization = f"" if skill['specialization'] == "" else f"[{skill['specialization']}]"
    #     name_row_list = [skill['name'], category, specialization]
    #     name_row = ' '.join(filter(None, name_row_list))
        
    #     embed = discord.Embed(title=f"{name_row} | {skill['base_points']}%", colour=discord.Colour(0x804423), description=skill['description'])

    #     await interaction.response.send_message(
    #         embed=embed,
    #         ephemeral=False)

    
    # async def my_roll(self, interaction: discord.Interaction, dice: str, comment: str = "", repeat: int = 1, keep: int = 0):
    #     """ Basic Dice Rolls """
    #     diceresult = diceroller.DiceRolls(dice, repeat=repeat, keep=keep)
        
    #     embed = self.__roll_with_format__(interaction=interaction, rolls=diceresult, additional_comment=comment)
        
    #     # embed a GIF or image when needed
    #     embed = self.__successlevel_image__(embed, diceresult.getroll())
            
    #     # read the results if announce is on and the bot is in a channel
    #     self.__announce_roll__(interaction, diceresult.getroll())
        
    #     # dramatic pause for fumbles and criticals  
    #     await asyncio.sleep(4) if diceresult.getroll().get_success() == "fumble" or diceresult.getroll().get_success() == "critical" else None

    #     # send response
    #     await interaction.response.send_message(embed=embed, ephemeral=False)

    def __roll_with_format__(self, interaction, rolls, additional_comment=""):

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
        embed = discord.Embed(title=f"{comment}{additional_comment}", colour=discord.Colour(color), description=description)

        #author_avatar_url = interaction.user.avatar.url or interaction.user.display_avatar.url
        #embed.set_author(name=interaction.user.display_name, icon_url=author_avatar_url)
        #embed.set_author(name=f"{ctx.author.display_name} - {comment}{additional_comment}", icon_url=author_avatar_url)

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

    def __successlevel_image__(self, embed, roll):
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