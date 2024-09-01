from datetime import datetime
from typing import Any, Literal
from discord import Colour, Embed
from discord.ui import View, Button, Select, Item
import json


class SongEmbed(Embed):
    def __init__(self, song, **kwargs):
        super().__init__(**kwargs)
        # print(song)
        print("ID", song["id"])
        self.id = song["id"]
        print("Title", song["title"])
        self.title = song["title"]
        print("Thumbnail", song["thumbnail"])
        self._thumbnail = song["thumbnail"]
        print("Artist", song["artist"] if "artist" in song else song["uploader"])
        self.artist = song["artist"] if "artist" in song else song["uploader"]
        print("Duration", song["duration"])
        self.duration = song["duration"]
        print("Webpage URL", song["webpage_url"])
        self.webpage_url = song["webpage_url"]
        
        self.set_image(url=self._thumbnail)
        self.add_field(name="Title", value=self.title, inline=False)
        self.add_field(name="Artist", value=self.artist, inline=False)

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
        
        for song in list_songs:
            self.song_entry(song)

    def song_entry(self, song: SongEmbed):
        song_title_link = f"[{song.title}]({song.url})"
        self.add_field(name=song_title_link, value=song.artist, inline=False)
        self.add_field(name="Duration", value=song.duration, inline=False)
        self.add_field(name="", value="", inline=False)
        
        
# self.id = song["id"]
# self.title = song["title"]
# self.formats = song["formats"]
# self.thumbnails = song["thumbnails"]
# self.thumbnail = song["thumbnail"]
# self.description = song["description"]
# self.channel_id = song["channel_id"]
# self.channel_url = song["channel_url"]
# self.duration = song["duration"]
# self.view_count = song["view_count"]
# self.average_rating = song["average_rating"]
# self.age_limit = song["age_limit"]
# self.webpage_url = song["webpage_url"]
# self.categories = song["categories"]
# self.tags = song["tags"]
# self.playable_in_embed = song["playable_in_embed"]
# self.live_status = song["live_status"]
# self.release_timestamp = song["release_timestamp"]
# self._format_sort_fields = song["_format_sort_fields"]
# self.automatic_captions = song["automatic_captions"]
# self.subtitles = song["subtitles"]
# self.album = song["album"]
# self.artists = song["artists"]
# self.track = song["track"]
# self.release_date = song["release_date"]
# self.release_year = song["release_year"]
# self.comment_count = song["comment_count"]
# self.chapters = song["chapters"]
# self.heatmap = song["heatmap"]
# self.like_count = song["like_count"]
# self.channel = song["channel"]
# self.channel_follower_count = song["channel_follower_count"]
# self.channel_is_verified = song["channel_is_verified"]
# self.uploader = song["uploader"]
# self.uploader_id = song["uploader_id"]
# self.uploader_url = song["uploader_url"]
# self.upload_date = song["upload_date"]
# self.creators = song["creators"]
# self.alt_title = song["alt_title"]
# self.availability = song["availability"]
# self.original_url = song["original_url"]
# self.webpage_url_basename = song["webpage_url_basename"]
# self.webpage_url_domain = song["webpage_url_domain"]
# self.extractor = song["extractor"]
# self.extractor_key = song["extractor_key"]
# self.playlist = song["playlist"]
# self.playlist_index = song["playlist_index"]
# self.display_id = song["display_id"]
# self.fulltitle = song["fulltitle"]
# self.duration_string = song["duration_string"]
# self.is_live = song["is_live"]
# self.was_live = song["was_live"]
# self.artist = song["artist"]
# self.creator = song["creator"]
# self.requested_subtitles = song["requested_subtitles"]
# self._has_drm = song["_has_drm"]
# self.epoch = song["epoch"]
# self.asr = song["asr"]
# self.filesize = song["filesize"]
# self.format_id = song["format_id"]
# self.format_note = song["format_note"]
# self.source_preference = song["source_preference"]
# self.fps = song["fps"]
# self.audio_channels = song["audio_channels"]
# self.height = song["height"]
# self.quality = song["quality"]
# self.has_drm = song["has_drm"]
# self.tbr = song["tbr"]
# self.filesize_approx = song["filesize_approx"]
# self.url = song["url"]
# self.width = song["width"]
# self.language = song["language"]
# self.language_preference = song["language_preference"]
# self.preference = song["preference"]
# self.ext = song["ext"]
# self.vcodec = song["vcodec"]
# self.acodec = song["acodec"]
# self.dynamic_range = song["dynamic_range"]
# self.container = song["container"]
# self.downloader_options = song["downloader_options"]
# self.protocol = song["protocol"]
# self.resolution = song["resolution"]
# self.aspect_ratio = song["aspect_ratio"]
# self.http_headers = song["http_headers"]
# self.audio_ext = song["audio_ext"]
# self.video_ext = song["video_ext"]
# self.vbr = song["vbr"]
# self.abr = song["abr"]
# self.format = song["format"]
# self._type = song["_type"]
# self._version = song["_version"]
# print("Self", self)