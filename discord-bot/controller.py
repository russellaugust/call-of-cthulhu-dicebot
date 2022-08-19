from discord.ext import commands, tasks
import credentials as cred
import discord
import aiohttp, requests, logging
import mdtools
import cocapi

MY_GUILD = discord.Object(id=cred.guild)
APPLICATION_ID = cred.application_id
TOKEN = cred.token
API_LINK = "http://localhost:8000/charactersheet/"
VALID_CHANNELS = [976000529006227456, 967962823797932042]

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)

class CoCBot(commands.Bot):
    def __init__(self, *, intents: discord.Intents, application_id: int):
        super().__init__(command_prefix='.', intents=intents, application_id=application_id)
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
        
        if message.channel.id in VALID_CHANNELS or parent_id in VALID_CHANNELS:
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

            # TODO: add message to database
            if message.content.startswith('BANANABREAD'):
                archived = message.channel.archived_threads()
                async for archive in archived:
                    print(archive)
            
            if message.content == "LOAD ALL":
                print("working to load all messages in channel or thread...")

                async for message in message.channel.history(limit=200):
                    
                    # reference = message.reference.message_id if message.reference is not None and not message.is_system else None

                    # check if player is in the system, if not add.
                    player = cocapi.get_or_create_player(json={
                        "name": "",
                        "discord_name": message.author.name,
                        "discord_id": message.author.id })
                    
                    # check if this particular channel is in the system, if not, add.
                    channel = cocapi.get_or_create_channel(json={
                        "name": message.channel.name,
                        "channel_id": message.channel.id,
                        "parent_id": 0 })                
                    
                    # save the message to the db
                    newmessage = cocapi.create_message(json={
                        "messagetime": message.created_at.isoformat(),
                        "discord_id": message.id,
                        "content": message.content,
                        "reply_msg_id": message.reference.message_id if message.reference is not None else None,
                        "player": player.get('id'),
                        "discordchannel": channel.get('id') })
        
    async def on_raw_message_edit(self, payload):
        content = payload.data.get('content', '')
        message = cocapi.message_content_update(discord_id=payload.message_id, content=content)
        
    async def on_raw_message_delete(self, payload):
        cocapi.message_delete(discord_id=payload.message_id)
    
        

intents = discord.Intents.default()
intents.message_content = True
bot = CoCBot(intents=intents, application_id=APPLICATION_ID)

bot.run(TOKEN)