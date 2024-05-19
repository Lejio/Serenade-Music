import urllib.request
import re
import asyncio
import os
import ctypes.util
import json
from datetime import datetime
from dotenv import load_dotenv

from discord.ext import commands
from discord import FFmpegPCMAudio, Intents, opus
from discord import Intents, Interaction

from yt_dlp import YoutubeDL
from pytube import Playlist
# Ensure Opus is loaded
opus_path = './libopus.0.dylib'
opus.load_opus(opus_path)
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
if not opus.is_loaded():
    print("Opus not loaded!")

load_dotenv()
ctypes.util.find_library('opus')

class SystemMusic(commands.Bot):
    def __init__(self, command_prefix=".", description: str | None = None, intents=Intents.all()) -> None:
        super().__init__(command_prefix, description=description, intents=intents)
        self.queue = {}

    async def on_ready(self) -> None:
        print(f'Successfully Logged in at {datetime.now()}.')
        print('Ready to ball.')
        try:
            synced = await self.tree.sync()
            print(f'Synced {len(synced)} command(s).')
        except Exception as e:
            print(f'Error syncing commands: {e}')
    
    async def on_disconnect(self) -> None:
        print("Bot is disconnecting, cleaning up...")
        # Clean up any active voice clients
        for vc in self.voice_clients:
            await vc.disconnect()

    async def play_next(self, guild_id):
        if len(self.queue[guild_id]) > 0:
            # print(f"The next song is {next_song}")
            voice = self.get_guild(guild_id).voice_client
            if voice and not voice.is_playing():
                next_song = self.queue[guild_id].pop(0)
                with YoutubeDL(YDL_OPTIONS) as ydl:
                    unsanitized_info = ydl.extract_info(next_song['url'], download=False)
                    URL = unsanitized_info['url']
                    info = json.loads(json.dumps(ydl.sanitize_info(unsanitized_info)))
                    title = info['title']
                print(f'Playing next song: {title}')
                ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
                voice.play(FFmpegPCMAudio(URL, executable=ffmpeg_path, **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(guild_id), self.loop))
        else:
            print("Queue is empty, nothing to play next.")

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
        
    await interaction.response.send_message("Joined the channel.")

@client.tree.command(
    name="play",
    description="Play sound from a youtube URL."
)
async def play(interaction: Interaction, url: str | None = None, search: str | None = None):
    if interaction.guild_id not in client.queue:
        client.queue[interaction.guild_id] = []
    text_channel = interaction.channel
    channel = interaction.user.voice.channel
    voice = interaction.guild.voice_client
    ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    if url == None and search == None:
        await interaction.response.send_message("Please provide a URL or search keyword.")
    elif url != None and search == None:
        if "playlist" in url:
            p = Playlist(url)
            playlist = []
            for video in p.videos:
                playlist.append(video.title)
                client.queue[interaction.guild_id].append({'url': video.watch_url, 'title': video.title})
            await text_channel.send(f'Playlist added to queue: {playlist}')
            curr_song = client.queue[interaction.guild_id].pop(0)
            url = curr_song['url']
    elif url == None and search != None:
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search.replace(' ', '_'))
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        url = "https://www.youtube.com/watch?v=" + video_ids[0]
        
    with YoutubeDL(YDL_OPTIONS) as ydl:
        unsanitized_info = ydl.extract_info(url, download=False)
        URL = unsanitized_info['url']
        info = json.loads(json.dumps(ydl.sanitize_info(unsanitized_info)))
        title = info['title']
    if not voice.is_playing():
        voice.play(FFmpegPCMAudio(URL, executable=ffmpeg_path, **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(client.play_next(interaction.guild_id), client.loop))
        await interaction.response.send_message(f'Now playing: {title}')
    else:
        client.queue[interaction.guild_id].append({'url': URL, 'title': title})
        await interaction.response.send_message(f'{title} added to queue.')

@client.tree.command(
    name="stop",
    description="Stop the bot from playing."
)
async def stop(interaction: Interaction):
    voice = interaction.guild.voice_client
    
    if voice.is_playing():
        voice.stop()
        for vc in client.voice_clients:
            await vc.disconnect()
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
    
    if voice.is_paused():
        voice.resume()
        await interaction.response.send_message("Bot resumed.")
    else:
        await interaction.response.send_message("Bot is not playing anything.")
        
@client.tree.command(
    name="skip",
    description="Skip the current song."
)
async def skip(interaction: Interaction):
    voice = interaction.guild.voice_client
    
    if voice.is_playing():
        voice.stop()
        await client.play_next(interaction.guild_id)
        print(f"Songs left in queue: {client.queue[interaction.guild_id]}")
        await interaction.response.send_message("Song skipped.")
    else:
        await interaction.response.send_message("Bot is not playing anything.")

client.run(os.environ.get('DISCORD_TOKEN'))
