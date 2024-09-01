from typing import Optional, TypedDict, Union
from discord.abc import GuildChannel, PrivateChannel
from discord import Thread
from viewer import SongBook
from songembed import SongEmbed

InteractionChannel = Optional[Union[GuildChannel, PrivateChannel, Thread]]

class QueueItem(TypedDict):
    title: str
    url: str
    embed: SongEmbed

class RequestorDict(TypedDict):
    queue: list[QueueItem]
    text_channel: InteractionChannel
    viewer: SongBook

class Requestor:
    
    def __init__(self, init: RequestorDict) -> None:
        self.queue = init['queue']
        self.text_channel = init['text_channel']
        self.viewer = init['viewer']
    
    def __getitem__(self, key):
        # Dictionary-style access for attributes
        return getattr(self, key)

    def __setitem__(self, key, value):
        # Allows setting attributes using dictionary-style access
        setattr(self, key, value)
        
    def to_dict(self):
        return {
            "queue": self.queue,
            "text_channel": self.text_channel,
            "viewer": self.viewer,
        }
        
    @classmethod
    def from_dict(cls, data):
        return cls(
            queue=data['queue'],
            text_channel=data['text_channel'],
            viewer=data['viewer'],
        )
        