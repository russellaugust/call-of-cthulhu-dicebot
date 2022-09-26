from discord.ext import commands, tasks
import credentials as cred
import discord
import aiohttp, requests, logging
import mdtools
import cocapi

MY_GUILD = discord.Object(id=cred.guild)
APPLICATION_ID = cred.application_id
TOKEN = cred.token
API_LINK = "http://localhost:8000/api/"
VALID_CHANNELS = cred.channels

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)

class CoCBot(commands.Bot):
    def __init__(self, *, intents: discord.Intents, application_id: int):
        super().__init__(command_prefix='.', intents=intents, 
                         application_id=application_id)
        self.initial_extensions = [
            'cogs.SlashDice',
            'cogs.SlashGeneral',
            'cogs.SlashVoice',
        ]

    async def setup_hook(self):
        # self.background_task.start()
        self.session = aiohttp.ClientSession()
        for ext in self.initial_extensions:
            await self.load_extension(ext)
        # await self.tree.sync(guild=MY_GUILD)
        # await self.tree.sync()

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_ready(self):
        print('Ready!')
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        # content.message will only work if the intent is set to true and its enabled in the bot settings
        
        
        parent_id = message.channel.parent_id if isinstance(message.channel, discord.Thread) else None
        
        # if channel is part of approved group and not a DM (ephemerals are DMs)
        if ((message.channel.id in VALID_CHANNELS 
             or parent_id in VALID_CHANNELS) 
            and not isinstance(message.channel, discord.DMChannel)):
            
            # check if player is in the system, if not add.
            player = cocapi.get_or_create_player(json={
                "name": "",
                "discord_name": message.author.name,
                "discord_id": message.author.id })
            
            # check if this particular channel is in the system, if not, add.
            channel = cocapi.get_or_create_channel(json={
                "name": message.channel.name,
                "channel_id": message.channel.id,
                "parent_id": parent_id })

            # save the message to the db
            newmessage = cocapi.create_message(json={
                "messagetime": message.created_at.isoformat(),
                "discord_id": message.id,
                "content": message.content,
                "reply_msg_id": message.reference.message_id if message.reference is not None else None,
                "player": player.get('id'),
                "discordchannel": channel.get('id') })
        
        # ignore the bot
        if not message.author.bot:
            
            if message.content == 'tree sync':
                await message.channel.send('commands synced.')
                await self.tree.sync()
            
            if message.content == "check channel type thread":
                await message.channel.send(f'Check Channel Type: {isinstance(message.channel, discord.Thread)}')
            
            if message.content == "trains":
                #trains = requests.get(f"{API_LINK}trainfacts").json()
                await message.channel.send('Did someone say *trains*?')
        
    async def on_raw_message_edit(self, payload):
        content = payload.data.get('content', '')
        message = cocapi.message_content_update(discord_id=payload.message_id, 
                                                content=content)
        
    async def on_raw_message_delete(self, payload):
        cocapi.message_delete(discord_id=payload.message_id)
        
    # This context menu command only works on messages
    @discord.app_commands.context_menu(name='Report to Moderators')
    async def report_message(interaction: discord.Interaction, message: discord.Message):
        # We're sending this response message with ephemeral=True, so only the command executor can see it
        await interaction.response.send_message(
            f'Thanks for reporting this message by {message.author.mention} to our moderators.', 
            ephemeral=True
        )

        # Handle report by sending it into a log channel
        log_channel = interaction.guild.get_channel(0)  # replace with your channel id

        embed = discord.Embed(title='Reported Message')
        if message.content:
            embed.description = message.content

        embed.set_author(name=message.author.display_name, 
                         icon_url=message.author.display_avatar.url)
        
        embed.timestamp = message.created_at

        url_view = discord.ui.View()
        url_view.add_item(discord.ui.Button(label='Go to Message', 
                                            style=discord.ButtonStyle.url, 
                                            url=message.jump_url))

        await log_channel.send(embed=embed, view=url_view)
    
intents = discord.Intents.default()
intents.message_content = True
bot = CoCBot(intents=intents, application_id=APPLICATION_ID)

bot.run(TOKEN)