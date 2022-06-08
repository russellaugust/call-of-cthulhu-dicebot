import discord
from discord import app_commands
from discord.ext import commands
import settings, asyncio

# Voice Channel Section
class VoiceConnectionError(commands.CommandError):
    pass

class InvalidVoiceChannel(VoiceConnectionError):
    pass

class VoiceCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings = settings.Settings()

    @app_commands.command()
    async def announce(self, interaction: discord.Interaction, announce_on: bool):
        self.settings.announce = announce_on
        await interaction.response.send_message("Announce Rolls in Voice Chat is now set to {}".format(announce_on))

    # Voice Channel Section
    class VoiceConnectionError(commands.CommandError):
        pass

    class InvalidVoiceChannel(VoiceConnectionError):
        pass


    @app_commands.command()
    async def join(self, interaction: discord.Interaction, channel: discord.VoiceChannel=None):
        """
        Connect to a voice channel
        This command also handles moving the bot to different channels.

        Params:
        - channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        """
        if not channel:
            try:
                channel = interaction.author.voice.channel
            except AttributeError:
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = interaction.guild.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

        await interaction.response.send_message(f'Connected to: **{channel}**')


    @app_commands.command()
    async def disconnect(self, interaction: discord.Interaction):
        """ Disconnect from a voice channel, if in one """
        vc = interaction.guild.voice_client

        if not vc:
            await interaction.response.send_message("I am not in a voice channel.")
            return

        await vc.disconnect()
        await interaction.response.send_message("I have left the voice channel!")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(VoiceCog(bot))