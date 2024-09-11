# Serenade-Music

Serenade Music is a Discord bot that allows you to play music in your server.

The bot is written is Python and utilizes the latest Discord.py library.

You can Serenade Music as a template to build your own bot with similar music functionalities.

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


