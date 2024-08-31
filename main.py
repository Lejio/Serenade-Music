import html
from typing import Optional, Union
import urllib.request
import re
import asyncio
import os
import ctypes.util
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

from discord.abc import GuildChannel, PrivateChannel
from discord.ext import commands
from discord import FFmpegPCMAudio, Intents, opus
from discord import Intents, Interaction, Thread

from yt_dlp import YoutubeDL
from pytube import Playlist
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import Spotify

InteractionChannel = Optional[Union[GuildChannel, PrivateChannel, Thread]]

# Ensure Opus is loaded
opus_path = './libopus.0.dylib'
opus.load_opus(opus_path)
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query="
YOUTUBE_URL = "https://www.youtube.com/watch?v="
YOUTUBE_PLAYLIST_URL = "https://www.youtube.com/playlist?list="
SPOTIFY_PLAYLIST_URL = "https://open.spotify.com/playlist"
executor = ThreadPoolExecutor(max_workers=5)
if not opus.is_loaded():
    print("Opus not loaded!")

load_dotenv()
ctypes.util.find_library('opus')


def sanitize_title(title: str) -> str:
    # Decode HTML entities and replace problematic characters
    title = html.unescape(title)  # Decode HTML entities
    # Replace or remove characters not supported by ASCII
    title = title.encode('ascii', 'ignore').decode('utf-8')
    title = re.sub(r'[\\/*?:"<>|]', "", title)  # Remove characters not allowed in file names
    return title

async def add_to_queue_from_search(interaction: Interaction, query: str):
    """Search for a YouTube video by query and add it to the queue."""
    try:
        html = urllib.request.urlopen(YOUTUBE_SEARCH_URL + query.replace(' ', '_'))
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode('utf-8'))
        if not video_ids:
            await interaction.followup.send(f"No results found for '{query}'.")
            return
        url = YOUTUBE_URL + video_ids[0]
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            title = sanitize_title(info['title'])
            client.queue[interaction.guild_id].append({'url': info['url'], 'title': title})
            await interaction.followup.send(f"Added to queue: {title}")
    except Exception as e:
        await interaction.followup.send(f"Error fetching YouTube video for '{query}': {str(e)}")
        
def construct_search_query(name: str, artists: list) -> str:
    """Construct a YouTube search query from a Spotify track's name and artist list."""
    artist_names = ', '.join(artist['name'] for artist in artists)
    return f"{name} by {artist_names}"

class SystemMusic(commands.Bot):
    def __init__(self, command_prefix=".", description: str | None = None, intents=Intents.all()) -> None:
        super().__init__(command_prefix, description=description, intents=intents)
        self.queue = {}
        self.client_credentials_manager: SpotifyClientCredentials = SpotifyClientCredentials(client_id=os.environ.get('SPOTIFY_CLIENT_ID'), client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET'))
        self.sp: Spotify = Spotify(client_credentials_manager=self.client_credentials_manager)
        self.current_song: str | None = None

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

    async def play_next(self, guild_id: int, channel: InteractionChannel) -> None:
        if len(self.queue[guild_id]) > 0:
            voice = self.get_guild(guild_id).voice_client
            if voice and not voice.is_playing():
                next_song = self.queue[guild_id].pop(0)
                with YoutubeDL(YDL_OPTIONS) as ydl:
                    unsanitized_info = ydl.extract_info(next_song['url'], download=False)
                    URL = unsanitized_info['url']
                    info = json.loads(json.dumps(ydl.sanitize_info(unsanitized_info)))
                    # print(info)
                    # if info['title'] != "videoplayback" and info['title'] != None:
                    self.current_song = next_song['title']
                        # print(self.current_song)
                ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
                voice.play(FFmpegPCMAudio(URL, executable=ffmpeg_path, **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(guild_id, channel), self.loop))
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
    # Check if the guild has a queue
    if interaction.guild_id not in client.queue:
        client.queue[interaction.guild_id] = []
        
    # Get the voice channel of the user
    # text_channel = interaction.channel
    await interaction.response.defer()
    # Get the voice channel of the user
    channel = interaction.user.voice.channel
    # Get the voice client of the guild
    voice = interaction.guild.voice_client
    
    # Path to the ffmpeg executable
    # ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
    # Check if the bot is already in a voice channel
    if voice and voice.is_connected():
        # Move the bot to the user's voice channel
        await voice.move_to(channel)
    else:
        # Connect the bot to the user's voice channel
        voice = await channel.connect()

    # Check if the user provided a URL or search keyword
    if url == None and search == None:
        await interaction.followup.send("Please provide a URL or search keyword.")
        return
    elif url != None and search == None:
        playlist = []
        if YOUTUBE_PLAYLIST_URL in url:
            print("Youtube Playlist URL")
            p = Playlist(url)
            for video in p.videos:
                playlist.append(f"{video.title} by {video.author}")
                client.queue[interaction.guild_id].append({'url': video.watch_url, 'title': video.title})
            await client.play_next(interaction.guild_id, interaction.channel)
            await interaction.followup.send(f"Playlist added to queue: {playlist}")
            return
            
        elif SPOTIFY_PLAYLIST_URL in url or "open.spotify.com/track" in url:
            try:
                if "playlist" in url:
                    print("Spotify Playlist URL")
                    spotify_pl = client.sp.playlist(url)
                    if spotify_pl is None:
                        await interaction.followup.send("Invalid Spotify playlist URL.")
                        return

                    # Process Spotify Playlist
                    for song in spotify_pl['tracks']['items']:
                        track = song['track']
                        title = construct_search_query(track['name'], track['artists'])
                        print("Title of song:", title)
                        playlist.append(title)
                        await add_to_queue_from_search(interaction, title)
                else:
                    # Process a Single Spotify Track
                    print("Spotify Track URL")
                    track = client.sp.track(url)
                    title = construct_search_query(track['name'], track['artists'])
                    print("Title of song:", title)
                    await add_to_queue_from_search(interaction, title)

                await interaction.followup.send(f"Spotify song(s) added to queue: {playlist}")
                await client.play_next(interaction.guild_id, interaction.channel)
                return
            except Exception as e:
                await interaction.followup.send(f"Error processing Spotify URL: {str(e)}")
                return
            
    elif url == None and search != None:
        html = urllib.request.urlopen(YOUTUBE_SEARCH_URL + search.replace(' ', '_'))
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        url = YOUTUBE_URL + video_ids[0]
        # print(url)
        # return
        
    with YoutubeDL(YDL_OPTIONS) as ydl:
        unsanitized_info = ydl.extract_info(url, download=False)
        URL = unsanitized_info['url']
        info = json.loads(json.dumps(ydl.sanitize_info(unsanitized_info)))
        # print(info)
        title = info['title']
        client.queue[interaction.guild_id].append({'url': URL, 'title': title})
    if not voice.is_playing():
        # voice.play(FFmpegPCMAudio(URL, executable=ffmpeg_path, **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(client.play_next(interaction.guild_id, interaction.channel), client.loop))
        # await interaction.response.send_message(f'Now playing: {title}')
        await interaction.followup.send(f'Now playing: {title}')
        await client.play_next(interaction.guild_id, interaction.channel)
        # await interaction.response.send_message(f'Now playing: {title}')
        return
    else:
        client.queue[interaction.guild_id].append({'url': URL, 'title': title})
        await interaction.followup.send(f"Added to queue: {title}")
        return

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
    await interaction.response.defer()
    if voice.is_playing():
        voice.stop()
        await interaction.followup.send(f"Skipping {client.current_song}")
        await client.play_next(interaction.guild_id, interaction.channel)
        # print(f"Songs left in queue: {client.queue[interaction.guild_id]}")
    else:
        await interaction.response.send_message("Bot is not playing anything.")

client.run(os.environ.get('DISCORD_TOKEN'))