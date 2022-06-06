from discord.ext import commands, tasks
import credentials as cred
import discord
import aiohttp, requests
import mdtools

MY_GUILD = discord.Object(id=cred.guild)
APPLICATION_ID = cred.application_id
TOKEN = cred.token

class CoCBot(commands.Bot):
    def __init__(self, *, intents: discord.Intents, application_id: int):
        super().__init__(command_prefix='.', intents=intents, application_id=application_id)
        self.initial_extensions = [
            'cogs.SlashDice',
            'cogs.SlashGeneral',
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
        if message.content == 'tree sync':
            await message.channel.send('commands synced.')
            await self.tree.sync()
        if message.content == "check channel type thread":
            await message.channel.send(f'Check Channel Type: {isinstance(message.channel, discord.Thread)}')
        if message.content == "trains":
            #trains = requests.get(f"http://localhost:8000/charactersheet/trainfacts").json()
            await message.channel.send('Did someone say *trains*?')

    async def on_message_edit(self, before, after):
        print (after.content)
        pass
        

intents = discord.Intents.default()
intents.message_content = True
bot = CoCBot(intents=intents, application_id=APPLICATION_ID)

bot.run(TOKEN)