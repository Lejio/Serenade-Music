import os
import ctypes.util
from datetime import datetime
from dotenv import load_dotenv

from discord.ext import commands
from discord import FFmpegPCMAudio, Intents, opus
from discord import Intents, Interaction

from yt_dlp import YoutubeDL

# Ensure Opus is loaded
# opus_path = './opus-1.5.2/.libs/libopus.0.dylib'  # For Windows, it could be 'C:/path/to/libopus-0.dll'
opus_path = './libopus.0.dylib'
opus.load_opus(opus_path)
if not opus.is_loaded():
    print("Opus not loaded!")
    # Replace the path with the actual path to the opus library if necessary


load_dotenv()
ctypes.util.find_library('opus')

class SystemMusic(commands.Bot):
    def __init__(self, command_prefix=".", description: str | None = None, intents=Intents.all()) -> None:
        super().__init__(command_prefix, description=description, intents=intents)
        
    async def on_ready(self) -> None:
        print(f'Successfully Logged in at {datetime.now()}.')
        print('Ready to ball.')
        try:
            synced = await self.tree.sync()
            print(f'Synced {len(synced)} command(s).')
        except Exception as e:
            print(f'Error syncing commands: {e}')
        
    
client = SystemMusic()

@client.tree.command(
    name="join",
    description="Join the voice channel of the user."
)
async def join(interaction: Interaction):
    
    channel = interaction.user.voice.channel
    voice = interaction.guild.voice_client
    
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        
    interaction.response.send_message("Joined the channel.")
    
@client.tree.command(
    name="play",
    description="Play sound from a youtube URL."
)
async def play(interaction: Interaction, url: str):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
    channel = interaction.user.voice.channel
    voice = interaction.guild.voice_client
    ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    if not voice.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['url']
        voice.play(FFmpegPCMAudio(URL, executable=ffmpeg_path, **FFMPEG_OPTIONS))
        await interaction.response.send_message('Bot is playing')

    else:
        await interaction.response.send_message("Bot is already playing")
        return
    
@client.tree.command(
    name="stop",
    description="Stop the bot from playing."
)
async def stop(interaction: Interaction):
    voice = interaction.guild.voice_client
    
    if voice.is_playing():
        await voice.disconnect()
        voice.cleanup()
        await interaction.response.send_message("Bot stopped playing.")
    else:
        await interaction.response.send_message("Bot is not playing anything.")

@client.tree.command(
    name="pause",
    description="Pause the bot from playing."
)
async def pause(interaction: Interaction):
    voice = interaction.guild.voice_client
    
    if voice.is_playing():
        voice.pause()
        await interaction.response.send_message("Bot paused.")
    else:
        await interaction.response.send_message("Bot is not playing anything.")

@client.tree.command(
    name="resume",
    description="Resume the bot from playing."
)
async def resume(interaction: Interaction):
    voice = interaction.guild.voice_client
    
    if not voice.is_playing():
        voice.resume()
        await interaction.response.send_message("Bot resumed.")
    else:
        await interaction.response.send_message("Bot is not playing anything.")

client.run(os.environ.get('DISCORD_TOKEN'))