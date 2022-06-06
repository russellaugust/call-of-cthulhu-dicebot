from discord.ext import commands, tasks
import discord
import aiohttp
import mdtools

MY_GUILD = discord.Object(id=461323119391539210)
APPLICATION_ID = 975984617981100083
TOKEN = 'OTc1OTg0NjE3OTgxMTAwMDgz.GAcna-.4xOSYIr6J-XP6aWlyDK2vVG5kLBkUHdCNT5B8M'

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

    # @tasks.loop(minutes=10)
    # async def background_task(self):
    #     print('Running background task...')

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
        if message.content == "tell me about trains":
            await message.channel.send('one time my friends all got on a ghost train and some of them **died.**')

    async def on_message_edit(self, before, after):
        pass
        

intents = discord.Intents.default()
intents.message_content = True
bot = CoCBot(intents=intents, application_id=APPLICATION_ID)

bot.run(TOKEN)