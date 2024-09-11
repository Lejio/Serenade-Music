<div align="center">
  <img alt="Serenade Music Logo" src="https://raw.githubusercontent.com/Lejio/Serenade-Music/1cf7040ee03df9a5229f5f94804f887b6c3f1354/serenade_music_logo.svg">
</div>

<h1 align="center">Discord Music Bot Template</h1>

<p align="center">Serenade Music is a Discord bot that allows you to play music in your server. The bot is written is Python and utilizes the latest Discord.py library. You can Serenade Music as a template to build your own bot with similar music functionalities.</p>

## Setup

First clone the repository

```
git clone git@github.com:Lejio/Serenade-Music.git
cd ./Serenade-Music
```

Then create and activate your python virtual environment.

Next, run the following command to install all the python dependencies:

```
pip install -r requirements.txt
```

In order for the audio to work, you must install the correct versions of libopus audio codec and FFmpeg.

libopus: https://opus-codec.org/

FFmpeg: https://www.ffmpeg.org/

Serenade Music is currently only tested with Libopus 1.5.2

Compile both libopus and FFmpeg for your specific operating system.

Finally, create a new .env file to store all your discord and spotify keys.

```
DISCORD_TOKEN="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
SPOTIFY_CLIENT_ID="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
SPOTIFY_CLIENT_SECRET="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

---

### Features under construction:

- [ ] Play from Spotify
- [ ] Search songs
- [ ] Add playlists


