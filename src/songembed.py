from datetime import datetime
from typing import Any, Literal
from discord import Colour, Embed
from discord.ui import View, Button, Select, Item
import json


class SongEmbed(Embed):
    def __init__(self, song, author, **kwargs):
        super().__init__(**kwargs)
        self.id = song["id"]
        self.title = song["title"]
        self._thumbnails = song["thumbnails"]
        self.artist = song["artist"] if "artist" in song else song["uploader"]
        self.duration = song["duration"]
        self.url = song["webpage_url"]
        self.request_user = author
        

        # self.set_image(url=self._thumbnail)
        for i in range(len(self._thumbnails) - 1, -1, -1):
            if ".jpg" in self._thumbnails[i]["url"] or ".png" in self._thumbnails[i]["url"]:
                self.set_thumbnail(url=self._thumbnails[i]["url"])
                break

        self.set_author(name="Serenade Music")

    def __getitem__(self, key):
        # Dictionary-style access for attributes
        return getattr(self, key)

    def __setitem__(self, key, value):
        # Allows setting attributes using dictionary-style access
        setattr(self, key, value)
        
    def __str__(self):
        # Returns a string representation of the dictionary
        return str(self.to_dict())

    # def to_dict(self):
    #     return {
    #         "id": self.id,
    #         "title": self.title,
    #         "formats": self.formats,
    #         "thumbnails": self.thumbnails,
    #         "thumbnail": self.thumbnail,
    #         "description": self.description,
    #         "channel_id": self.channel_id,
    #         "channel_url": self.channel_url,
    #         "duration": self.duration,
    #         "view_count": self.view_count,
    #         "average_rating": self.average_rating,
    #         "age_limit": self.age_limit,
    #         "webpage_url": self.webpage_url,
    #         "categories": self.categories,
    #         "tags": self.tags,
    #         "playable_in_embed": self.playable_in_embed,
    #         "live_status": self.live_status,
    #         "release_timestamp": self.release_timestamp,
    #         "_format_sort_fields": self._format_sort_fields,
    #         "automatic_captions": self.automatic_captions,
    #         "subtitles": self.subtitles,
    #         "album": self.album,
    #         "artists": self.artists,
    #         "track": self.track,
    #         "release_date": self.release_date,
    #         "release_year": self.release_year,
    #         "comment_count": self.comment_count,
    #         "chapters": self.chapters,
    #         "heatmap": self.heatmap,
    #         "like_count": self.like_count,
    #         "channel": self.channel,
    #         "channel_follower_count": self.channel_follower_count,
    #         "channel_is_verified": self.channel_is_verified,
    #         "uploader": self.uploader,
    #         "uploader_id": self.uploader_id,
    #         "uploader_url": self.uploader_url,
    #         "upload_date": self.upload_date,
    #         "creators": self.creators,
    #         "alt_title": self.alt_title,
    #         "availability": self.availability,
    #         "original_url": self.original_url,
    #         "webpage_url_basename": self.webpage_url_basename,
    #         "webpage_url_domain": self.webpage_url_domain,
    #         "extractor": self.extractor,
    #         "extractor_key": self.extractor_key,
    #         "playlist": self.playlist,
    #         "playlist_index": self.playlist_index,
    #         "display_id": self.display_id,
    #         "fulltitle": self.fulltitle,
    #         "duration_string": self.duration_string,
    #         "is_live": self.is_live,
    #         "was_live": self.was_live,
    #         "artist": self.artist,
    #         "creator": self.creator,
    #         "requested_subtitles": self.requested_subtitles,
    #         "_has_drm": self._has_drm,
    #         "epoch": self.epoch,
    #         "asr": self.asr,
    #         "filesize": self.filesize,
    #         "format_id": self.format_id,
    #         "format_note": self.format_note,
    #         "source_preference": self.source_preference,
    #         "fps": self.fps,
    #         "audio_channels": self.audio_channels,
    #         "height": self.height,
    #         "quality": self.quality,
    #         "has_drm": self.has_drm,
    #         "tbr": self.tbr,
    #         "filesize_approx": self.filesize_approx,
    #         "url": self.url,
    #         "width": self.width,
    #         "language": self.language,
    #         "language_preference": self.language_preference,
    #         "preference": self.preference,
    #         "ext": self.ext,
    #         "vcodec": self.vcodec,
    #         "acodec": self.acodec,
    #         "dynamic_range": self.dynamic_range,
    #         "container": self.container,
    #         "downloader_options": self.downloader_options,
    #         "protocol": self.protocol,
    #         "resolution": self.resolution,
    #         "aspect_ratio": self.aspect_ratio,
    #         "http_headers": self.http_headers,
    #         "audio_ext": self.audio_ext,
    #         "video_ext": self.video_ext,
    #         "vbr": self.vbr,
    #         "abr": self.abr,
    #         "format": self.format,
    #         "_type": self._type,
    #         "_version": self._version,
    #     }

    # @classmethod
    # def from_dict(cls, data):
        return cls(
            id=data["id"],
            title=data["title"],
            formats=data["formats"],
            thumbnails=data["thumbnails"],
            thumbnail=data["thumbnail"],
            description=data["description"],
            channel_id=data["channel_id"],
            channel_url=data["channel_url"],
            duration=data["duration"],
            view_count=data["view_count"],
            average_rating=data["average_rating"],
            age_limit=data["age_limit"],
            webpage_url=data["webpage_url"],
            categories=data["categories"],
            tags=data["tags"],
            playable_in_embed=data["playable_in_embed"],
            live_status=data["live_status"],
            release_timestamp=data["release_timestamp"],
            _format_sort_fields=data["_format_sort_fields"],
            automatic_captions=data["automatic_captions"],
            subtitles=data["subtitles"],
            album=data["album"],
            artists=data["artists"],
            track=data["track"],
            release_date=data["release_date"],
            release_year=data["release_year"],
            comment_count=data["comment_count"],
            chapters=data["chapters"],
            heatmap=data["heatmap"],
            like_count=data["like_count"],
            channel=data["channel"],
            channel_follower_count=data["channel_follower_count"],
            channel_is_verified=data["channel_is_verified"],
            uploader=data["uploader"],
            uploader_id=data["uploader_id"],
            uploader_url=data["uploader_url"],
            upload_date=data["upload_date"],
            creators=data["creators"],
            alt_title=data["alt_title"],
            availability=data["availability"],
            original_url=data["original_url"],
            webpage_url_basename=data["webpage_url_basename"],
            webpage_url_domain=data["webpage_url_domain"],
            extractor=data["extractor"],
            extractor_key=data["extractor_key"],
            playlist=data["playlist"],
            playlist_index=data["playlist_index"],
            display_id=data["display_id"],
            fulltitle=data["fulltitle"],
            duration_string=data["duration_string"],
            is_live=data["is_live"],
            was_live=data["was_live"],
            artist=data["artist"],
            creator=data["creator"],
            requested_subtitles=data["requested_subtitles"],
            _has_drm=data["_has_drm"],
            epoch=data["epoch"],
            asr=data["asr"],
            filesize=data["filesize"],
            format_id=data["format_id"],
            format_note=data["format_note"],
            source_preference=data["source_preference"],
            fps=data["fps"],
            audio_channels=data["audio_channels"],
            height=data["height"],
            quality=data["quality"],
            has_drm=data["has_drm"],
            tbr=data["tbr"],
            filesize_approx=data["filesize_approx"],
            url=data["url"],
            width=data["width"],
            language=data["language"],
            language_preference=data["language_preference"],
            preference=data["preference"],
            ext=data["ext"],
            vcodec=data["vcodec"],
            acodec=data["acodec"],
            dynamic_range=data["dynamic_range"],
            container=data["container"],
            downloader_options=data["downloader_options"],
            protocol=data["protocol"],
            resolution=data["resolution"],
            aspect_ratio=data["aspect_ratio"],
            http_headers=data["http_headers"],
            audio_ext=data["audio_ext"],
            video_ext=data["video_ext"],
            vbr=data["vbr"],
            abr=data["abr"],
            format=data["format"],
            _type=data["_type"],
            _version=data["_version"],
        )


class QueueEmbed(Embed):
    def __init__(
        self,
        *,
        list_songs: list[SongEmbed],
        colour: int | Colour | None = None,
        color: int | Colour | None = None,
        title: Any | None = None,
        type: (
            Literal["rich"]
            | Literal["image"]
            | Literal["video"]
            | Literal["gifv"]
            | Literal["article"]
            | Literal["link"]
        ) = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None
    ):
        super().__init__(
            colour=colour,
            color=color,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )
        self.title = ":notes: Serenade Player :notes:"
        self.description="Use the webview :desktop: or `\play` command to add songs! You can use the search option or use the url option for specific songs! Youtube and Spotify songs supported."
        for song in range(len(list_songs)):
            self.song_entry(list_songs[song], song)

    def song_entry(self, song: SongEmbed, song_index: int):
        song_title_link = f"[{song.title}]({song.url})"
        self.add_field(name=f"{f'Playing :cd:' if song_index == 0 else f'{song_index + 1} in Queue'}:",
                value=song_title_link,
                inline=True)
        self.add_field(name="Requested By:",
                        value=song.request_user,
                        inline=True)
        self.add_field(name="Duration",
                        value=f"{song.duration // 60}:{song.duration % 60:02d}",
                        inline=True)
        self.add_field(name="", value="", inline=False)