from typing import Optional, Union
import urllib.request
import re
import asyncio
import os
import ctypes.util
import json
from datetime import datetime

from dotenv import load_dotenv

from discord.abc import GuildChannel, PrivateChannel
import logging
from discord.ext import commands
from discord import Colour, Embed, FFmpegPCMAudio, Intents, opus
from discord import Intents, Interaction, Thread
from requestor import QueueItem, Requestor, RequestorDict
from book import SongBook
from songembed import QueueEmbed, SongEmbed
from testembed import TestEmbed

from yt_dlp import YoutubeDL
from pytube import Playlist
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import Spotify

# Type hint for the channel
InteractionChannel = Optional[Union[GuildChannel, PrivateChannel, Thread]]

# Ensure Opus is loaded
opus_path = './libopus.0.dylib'
opus.load_opus(opus_path)
if not opus.is_loaded():
    print("Opus not loaded!")

# YoutubeDL Options
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True', 'compat_opts': ['no-youtube-sig'], 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# FFMPEG Options
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

# Constants
YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query="
YOUTUBE_URL = "https://www.youtube.com/watch?v="
YOUTUBE_PLAYLIST_URL = "https://www.youtube.com/playlist?list="
SPOTIFY_PLAYLIST_URL = "https://open.spotify.com/playlist"
CHANNEL_ID = "channel_id"
MESSAGE_ID = "message_id"
TITLE = "title"
URL = "url"
EMBED = "embed"
NAME = "name"
QUEUE = "queue"
BOOK = "book"

ENCODING = 'utf-8'

# Load environment variables
load_dotenv()
# Double check if the Opus library is loaded
ctypes.util.find_library('opus')

def construct_pages(requestor: Requestor):
    songs = [item[EMBED] for item in requestor.queue]  # Extract the embeds from the queue
    paginated_queue: list[QueueEmbed] = []
    pagination_size = 5  # Number of songs per page

    # Create chunks of songs, 5 per chunk
    for i in range(0, len(songs), pagination_size):
        paginated_queue.append(QueueEmbed(list_songs=songs[i:i + pagination_size]))

    return paginated_queue, songs


def add_to_queue_from_search(query: str, requestor: Requestor) -> bool:
    """Adds a song to the queue from a search string.\n
    
    The query is used to search for a song on YouTube. The first video URL is then added to the queue.\n
    Ex: query = "Simple by BBHF"\n
    This function is used in junction with construct_search_query().\n

    Args:
        query (str): The search string.
        guild_id (int): The guild ID.
    Returns:
        bool: Returns true if the song was added to the queue, false otherwise.
    """
    
    # print("Search keyword:", query)
    encoded_query = urllib.parse.quote(query) # Parses query and changes all non-english characters into percent encoding
    search_keyword = YOUTUBE_SEARCH_URL + encoded_query # Appends the encoded query to the YouTube search URL
    html = urllib.request.urlopen(search_keyword) # Opens the URL
    # print("Inside query search:", search_keyword)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode(ENCODING)) # Finds all video IDs in the HTML
    
    if not video_ids: # If no video IDs are found, return False
        return False
    
    url = YOUTUBE_URL + video_ids[0] # Constructs the URL of the first video result
    # print("URL search:", url)
    with YoutubeDL(YDL_OPTIONS) as ydl:
        unsanitized_info = ydl.extract_info(url, download=False) # Extracts the info of the video
        info = json.loads(json.dumps(ydl.sanitize_info(unsanitized_info)))
        title = info[TITLE] # Extracts the title of the video
        # print(title)
        song = SongEmbed(song=info)
        qitem: QueueItem = {URL: url, TITLE: title, EMBED: song}
        requestor.queue.append(qitem) # Appends the video URL and title to the queue

async def add_to_queue_async(query: str, requestor: Requestor) -> bool:
    """Asyncio wrapper for add_to_queue_from_search().\n
    Helps with the blocking nature of add_to_queue_from_search().\n
    
    Adds a song to the queue from a search string.
    
    The query is used to search for a song on YouTube. The first video URL is then added to the queue.\n
    Ex: query = "Simple by BBHF"\n
    This function is used in junction with construct_search_query().

    Args:
        query (str): The search string
        guild_id (int): The guild ID

    Returns:
        bool: Returns true if the song was added to the queue, false otherwise.
    """
    return await asyncio.to_thread(add_to_queue_from_search, query, requestor)
        
def construct_search_query(name: str, artists: list) -> str:
    """Constructs a search query from a song name and a list of artists.\n

    Args:
        name (str): Name of the song
        artists (list): List of artists

    Returns:
        str: The constructed search query in the format "name by artist1, artist2, artist3"
    """
    artist_names = ', '.join(artist[NAME] for artist in artists)
    return f"{name} by {artist_names}"

class SerenadeMusic(commands.Bot):
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
            
    def after_song_ends(self, error: Exception | None, guild_id, requestor: Requestor) -> None:
        if error:
            print(f"Error occurred: {error}")
        else:
            print("Song has finished playing.")
            # Only pop if the queue is not empty
            if requestor.queue:
                print("Popping in after_song_ends")
                requestor.queue.pop(0)
            print("Stuff left in Queue", requestor.queue)
            # Ensure coroutine is properly awaited
            asyncio.run_coroutine_threadsafe(self.play_next(guild_id, requestor), self.loop)


    async def play_next(self, guild_id: int, requestor: Requestor) -> None:
        # try:
            if len(requestor.queue) > 0:
                voice = self.get_guild(guild_id).voice_client
                if voice and not voice.is_playing():
                    next_song: QueueItem = self.queue[guild_id]['queue'][0]
                    with YoutubeDL(YDL_OPTIONS) as ydl:
                        unsanitized_info = ydl.extract_info(next_song['url'], download=False)
                        URL = unsanitized_info['url']
                        info = json.loads(json.dumps(ydl.sanitize_info(unsanitized_info)))

                        self.current_song = next_song['title']

                    ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
                    voice.play(FFmpegPCMAudio(URL, executable=ffmpeg_path, **FFMPEG_OPTIONS), after=lambda e: self.after_song_ends(e, guild_id, requestor))
            else:
                print("Queue is empty, nothing to play next.")
                pag_queue, songs = construct_pages(requestor)
                print("Before sending", songs, pag_queue)
                await requestor.book.send(songs=songs, paginated_queue=pag_queue, client=client)
        # except Exception as e:
        #     print(f"Error in play_next: {e}")


client = SerenadeMusic()

@client.tree.command(
    name="join",
    description="Join the voice channel of the user."
)
async def join(interaction: Interaction):
    channel = interaction.user.voice.channel
    voice = interaction.guild.voice_client
    await interaction.response.send_message(embed=Embed(colour=Colour.blue(), title="Joining voice channel..."))
    message = None
    
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        
    message = await interaction.original_response()
        
    songs = [TestEmbed(name=interaction.user.display_name, icon=interaction.user.display_icon),
             TestEmbed(name=interaction.user.display_name, icon=interaction.user.display_icon)]
    
    paginated_queue = [TestEmbed(name="Goofy Shit", icon=interaction.user.display_icon),
             TestEmbed(name="LMAO", icon=interaction.user.display_icon)]
    testview = SongBook(songs=songs, paginated_queue=paginated_queue, message_id=message.id, channel_id=interaction.channel_id)
    
    await testview.send()

@client.tree.command(
    name="play",
    description="Play music from Youtube and Spotify."
)
async def play(interaction: Interaction, url: str | None = None, search: str | None = None):
    # Check if the guild has a queue
    
    if url == None and search == None:
        await interaction.response.send_message(embed=Embed(colour=Colour.red(), title="Please provide a URL or search keyword."), ephemeral=True)
        return
    
    if interaction.guild_id not in client.queue:
        await interaction.response.send_message(embed=Embed(colour=Colour.blue(), title="Loading..."))
        msg = await interaction.original_response()
        requestor: RequestorDict = {
        "queue": [],
        CHANNEL_ID: interaction.channel.id,  # or a GuildChannel/PrivateChannel/Thread object
        MESSAGE_ID: msg.id,
        BOOK: SongBook(message_id=msg.id, channel_id=interaction.channel.id)
        }
        client.queue[interaction.guild_id] = requestor
        
    elif interaction.channel_id != client.queue[interaction.guild_id][CHANNEL_ID]:
        await interaction.response.send_message(embed=Embed(colour=Colour.red(), title="Please use the same text channel for the queue."), ephemeral=True)
        return
        
    requestor: Requestor = Requestor(client.queue[interaction.guild_id])
    # Get the voice channel of the user
    channel = interaction.user.voice.channel
    # Get the voice client of the guild
    voice = interaction.guild.voice_client
    
    # Path to the ffmpeg executable
    # Check if the bot is already in a voice channel
    if voice and voice.is_connected():
        # Move the bot to the user's voice channel
        await voice.move_to(channel)
    else:
        # Connect the bot to the user's voice channel
        voice = await channel.connect()

    # Check if the user provided a URL or search keyword
    
    if url is not None and search is None:
        playlist = []
        if YOUTUBE_PLAYLIST_URL in url:
            print("Loading playlist...")
            ydl_opts = {
                'extract_flat': True,  # Extract playlist video URLs without downloading
                'skip_download': True,  # Skip downloading video data
                'quiet': True
            }

            # Use yt_dlp to get the playlist information
            with YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(url, download=False)
            
            # Check if the playlist contains entries (videos)
            if 'entries' in playlist_info:
                for entry in playlist_info['entries']:
                    video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                    print("Loading video:", video_url)

                    # Extract full metadata for each video in the playlist
                    with YoutubeDL(YDL_OPTIONS) as ydl:
                        video_info = ydl.extract_info(video_url, download=False)
                    
                    # Extract relevant information from video metadata
                    song = SongEmbed(song=video_info, author=interaction.user.mention)
                    qitem: QueueItem = {'url': video_url, 'title': video_info['title'], 'embed': song, 'author': interaction.user.mention}
                    requestor.queue.append(qitem)
                    playlist.append(f"{video_info['title']} by {video_info.get('uploader', 'Unknown')}")
            
                    # Play the next song if not currently playing
                    pag_queue, songs = construct_pages(requestor)
                    await requestor.book.send(songs=songs, paginated_queue=pag_queue, client=client)
                    if not voice.is_playing():
                        await client.play_next(guild_id=interaction.guild_id, requestor=requestor)
            return

            
        # ================== SPOTIFY ==================
        elif SPOTIFY_PLAYLIST_URL in url or "open.spotify.com/track" in url or "open.spotify.com/album" in url:
            # try:
                if "playlist" in url or "album" in url:
                    spotify_pl = client.sp.playlist(url) if "playlist" in url else client.sp.album(url)
                    if spotify_pl is None:
                        if channel:
                            await channel.send(embed=Embed(colour=Colour.red(), title="Cannot find Spotify playlist."), ephemeral=True)
                        else:
                            print("Cannot find Spotify playlist and cannot find original message.")
                        return

                    # Process Spotify Playlist
                    for song in spotify_pl['tracks']['items']:
                        track = song['track']
                        title = construct_search_query(track['name'], track['artists'])
                        playlist.append(title)
                        # =============== Add to Queue ===============
                        await add_to_queue_async(query=title, requestor=requestor)
                        if not voice.is_playing():
                            await client.play_next(interaction.guild_id, requestor)

                else:
                    # Process a Single Spotify Track
                    track = client.sp.track(url)
                    title = construct_search_query(track['name'], track['artists'])
                    print("Spotify Track:", title)
                    await add_to_queue_async(query=title, requestor=requestor)
                    if not voice.is_playing():
                        await client.play_next(interaction.guild_id, requestor)
                
                # req_channel = client.get_channel(requestor.channel_id)
                # req_message = await req_channel.fetch_message(requestor.message_id)
                # await requestor.text_channel.send(f"Spotify song(s) added to queue: {playlist}")
                await client.play_next(interaction.guild_id, requestor)
                return
            # except Exception as e:
            #     await interaction.followup.send(f"Error processing Spotify URL: {str(e)}")
            #     return
            
    elif url == None and search != None:
        html = urllib.request.urlopen(YOUTUBE_SEARCH_URL + search.replace(' ', '_'))
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        url = YOUTUBE_URL + video_ids[0]
        
    with YoutubeDL(YDL_OPTIONS) as ydl:
        unsanitized_info = ydl.extract_info(url, download=False)
        song_origin_url = unsanitized_info[URL]
        info = json.loads(json.dumps(ydl.sanitize_info(unsanitized_info)))
        title = info[TITLE]
        song = SongEmbed(song=info, author=interaction.user.mention)
        qitem: QueueItem = {URL: song_origin_url, TITLE: title, EMBED: song}
        requestor.queue.append(qitem)
        
    if not voice.is_playing():
        # await interaction.followup.send(f'Now playing: {title}')
        pag_queue, songs = construct_pages(requestor)
        await requestor.book.send(songs=songs, paginated_queue=pag_queue, client=client)
        await client.play_next(interaction.guild_id, requestor)
        return
    else:
        pag_queue, songs = construct_pages(requestor)
        await requestor.book.send(songs=songs, paginated_queue=pag_queue, client=client)
        return
    
@client.tree.command(
    name="current-song",
    description="Get the current song playing."
)
async def current_song(interaction: Interaction):
    """Prints the current song playing.

    Args:
        interaction (Interaction): Discord interaction object.
    """
    await interaction.response.send_message(f"Currently playing: {client.current_song}", ephemeral=True, delete_after=30)

@client.tree.command(
    name="stop",
    description="Stop the bot from playing."
)
async def stop(interaction: Interaction):
    """Stops the bot from playing and disconnects from the voice channel.\n
    The bot will also clear the queue for that guild.

    Args:
        interaction (Interaction): Discord interaction object.
    """
    voice = interaction.guild.voice_client # Get the voice client of the guild
    
    if voice.is_playing(): # If the bot is playing, stop it
        voice.stop()
        for vc in client.voice_clients: # Disconnect from the voice channel
            await vc.disconnect()
        client.queue[interaction.guild_id] = {} # Clear the queue
        await interaction.response.send_message("Bot stopped playing.")
    else:
        await interaction.response.send_message("Bot is not playing anything.")

@client.tree.command(
    name="pause",
    description="Pause the bot from playing."
)
async def pause(interaction: Interaction):
    """Pauses the bot from playing.

    Args:
        interaction (Interaction): Discord interaction object.
    """
    voice = interaction.guild.voice_client
    
    if voice.is_playing(): # If the bot is playing, pause it
        voice.pause()
        await interaction.response.send_message("Bot paused.")
    else:
        await interaction.response.send_message("Bot is not playing anything.")

@client.tree.command(
    name="resume",
    description="Resume the bot from playing."
)
async def resume(interaction: Interaction):
    """Resumes the bot from playing.

    Args:
        interaction (Interaction): Discord interaction object.
    """
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
    # await interaction.response.defer()
    if voice:
        if voice.is_playing():
            voice.stop()
            await interaction.response.send_message(f"Skipping {client.current_song}", ephemeral=True, delete_after=3)
            requestor = Requestor(client.queue[interaction.guild_id])
            prag_queue, songs = construct_pages(requestor)
            await requestor.book.send(paginated_queue=prag_queue, songs=songs, client=client)
            
            await client.play_next(interaction.guild_id, requestor)
        else:
            await interaction.response.send_message("Bot is not playing anything.", ephemeral=True, delete_after=3)

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
client.run(os.environ.get('DISCORD_TOKEN'), log_handler=handler)