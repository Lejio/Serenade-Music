from typing import Optional, TypedDict, Union
from discord.abc import GuildChannel, PrivateChannel
from discord import Thread, User
from book import SongBook
from songembed import SongEmbed

InteractionChannel = Optional[Union[GuildChannel, PrivateChannel, Thread]]

class QueueItem(TypedDict):
    """Song item in the queue.\n
    title: str\n
    url: str\n
    embed: SongEmbed\n
    author: User\n

    Args:
        TypedDict (_type_): _description_
    """
    title: str
    url: str
    embed: SongEmbed
    author: User

class RequestorDict(TypedDict):
    queue: list[QueueItem]
    channel_id: int
    message_id: int 
    book: SongBook

class Requestor:
    
    def __init__(self, init: RequestorDict) -> None:
        self.queue = init['queue']
        self.channel_id = init['channel_id']
        self.message_id = init['message_id']
        self.book = init['book']
    
    def __getitem__(self, key):
        # Dictionary-style access for attributes
        return getattr(self, key)

    def __setitem__(self, key, value):
        # Allows setting attributes using dictionary-style access
        setattr(self, key, value)
        
    def to_dict(self):
        return {
            "queue": self.queue,
            "channel_id": self.channel_id,
            "message_id": self.message_id,
            "book": self.book,
        }
        
    @classmethod
    def from_dict(cls, data):
        return cls(
            queue=data['queue'],
            channel_id=data['channel_id'],
            message_id=data['message_id'],
            book=data['book'],
        )
        