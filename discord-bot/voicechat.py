class VoiceChat:
    def __init__(self, ctx):
    '''load stuff here'''

    self.ctx = ctx
    self.channel = channel

    def connect(self):
    """
    Connect to a voice channel
    This command also handles moving the bot to different channels.

    Params:
    - channel: discord.VoiceChannel [Optional]
        The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
        will be made.
    """
    if not self.channel:
        try:
            self.channel = self.ctx.author.voice.channel
        except AttributeError:
            raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

    vc = self.ctx.voice_client

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

    await ctx.send(f'Connected to: **{channel}**', delete_after=20)
    



