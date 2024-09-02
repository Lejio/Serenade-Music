from discord import Colour, Embed
from discord.ui import View, Button, Select, Item, button
from discord import Embed, InteractionMessage, Interaction, SelectOption
from discord.ext import commands
from songembed import QueueEmbed, SongEmbed
import uuid


# pages if pages else Embed(
#     colour=Colour.blue(),
#     title="Joining voice channel...",
# )
class Chapter(View):
    def __init__(self, pages: list[Embed], timeout: int | None = None):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.page_len = len(self.pages)
        self.curr_page = 0
        if self.page_len == 1:
            self.nextButton.disabled = True
            
        # Dynamically assign unique custom_ids for the buttons
        self.prevButton.custom_id = str(uuid.uuid4())
        self.nextButton.custom_id = str(uuid.uuid4())
        
        # print(self.prevButton.custom_id)
            
    def set_pages(self, pages: list[Embed]):
        self.pages = pages
        self.page_len = len(self.pages)
        self.prevButton.disabled = True
        if self.page_len > 1:
            self.nextButton.disabled = False
        else:
            self.nextButton.disabled = True

    async def send(self, message: InteractionMessage, select: Select, pages: list[Embed] = None):
        self.curr_page = 0
        # Make custom select object that is able to do callback functions.
        # Add Embeds to a list and somehow make the buttons show each embed
        self.prevButton.disabled = True
        if pages:
            self.pages = pages
            self.page_len = len(self.pages)
        self.add_item(select)
        if self.page_len == 1:
            self.nextButton.disabled = True
            
        print(self.prevButton.custom_id)
        await message.edit(embed=self.pages[self.curr_page], view=self)
        self.message = message

    @button(label="Prev")
    async def prevButton(self, interaction: Interaction, button: Button):
        print("Interaction in", self.prevButton.custom_id)
        await interaction.response.defer()
        self.curr_page -= 1

        if self.curr_page == 0:
            # print('Disabling')
            self.prevButton.disabled = True
            self.nextButton.disabled = False
        else:
            self.nextButton.disabled = False

        await self.message.edit(embed=self.pages[self.curr_page], view=self)

    @button(label="Next")
    async def nextButton(self, interaction: Interaction, button: Button):
        print("Interaction in", self.nextButton.custom_id)
        await interaction.response.defer()
        self.curr_page += 1

        if self.curr_page + 1 == self.page_len:
            self.nextButton.disabled = True
            self.prevButton.disabled = False
        else:
            self.prevButton.disabled = False

        await self.message.edit(embed=self.pages[self.curr_page], view=self)


class SerenadeContents(dict):
    def __init__(self, songs: list[SongEmbed] | None, paginated_queue: list[QueueEmbed] | None) -> None:
        if songs:
            if "Queue" in self:
                self["Queue"].set_page(paginated_queue)  # Update existing instance
            else:
                self["Queue"] = Chapter(pages=paginated_queue)  # Create new instance

            if "Songs" in self:
                self["Songs"].set_page(songs)  # Update existing instance
            else:
                self["Songs"] = Chapter(pages=songs)  # Create new instance
        else:
            if "Loading" in self:
                self["Loading"].set_page([Embed(colour=Colour.blue(), title="Loading...")])  # Update existing instance
            else:
                self["Loading"] = Chapter(pages=[Embed(colour=Colour.blue(), title="Loading...")])  # Create new instance
            if "Queue" in self:
                self["Queue"].set_page([QueueEmbed(list_songs=[])])
            else:
                self["Queue"] = Chapter(pages=[QueueEmbed(list_songs=[])])
            


class SongBook(Select):
    def __init__(self, songs: list[SongEmbed] | None = None, paginated_queue: list[QueueEmbed] | None = None, message_id: int = int, channel_id: int = int) -> None:
        self.contents_dictionary = SerenadeContents(songs, paginated_queue)
        options = [SelectOption(label=v, value=v) for v in self.contents_dictionary]
        super().__init__(min_values=1, max_values=1, options=options)
        self.options[0].default = True
        self.default_val = self.options[0]
        self.channel_id = channel_id
        self.message_id = message_id
        self.key_values = ["Queue", "Songs"]
        self.songs = songs
        self.paginated_queue = paginated_queue

    async def send(self, client: commands.Bot, songs: list[SongEmbed] | None = None, paginated_queue: list[QueueEmbed] | None = None):
        if songs is not None:
            self.songs = songs
            self.paginated_queue = paginated_queue
        
        ref_channel = client.get_channel(self.channel_id)
        ref_message = await ref_channel.fetch_message(self.message_id)
        self.contents_dictionary = SerenadeContents(songs, paginated_queue)

        queue_viewer = self.contents_dictionary["Queue"]
        self.options = [SelectOption(label=v, value=v) for v in self.contents_dictionary]
        self.options[0].default = True
        self.default_val = self.options[0]
        self.custom_id = str(uuid.uuid4())
        await queue_viewer.send(message=ref_message, select=self, pages=self.paginated_queue)
        
    async def callback(self, interaction: Interaction):
        
        # NOTE: You can make the options have emojis!!

        self.default_val.default = False
        chap: Chapter = None
        value = self.values[0]

        match value:
            case "Queue":
                chap = Chapter(pages=self.paginated_queue)
            case "Songs":
                chap = Chapter(pages=self.songs)
            
        self.options[self.key_values.index(value)].default = True
        self.default_val = self.options[self.key_values.index(value)]
        
        await interaction.response.send_message("Switching to " + value, ephemeral=True, delete_after=1)
        await chap.send(message=self.message, select=self, pages=self.songs if value == "Songs" else self.paginated_queue)