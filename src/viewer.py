from discord import Colour, Embed
from discord.ui import View, Button, Select, Item, button
from discord import Embed, InteractionMessage, Interaction, SelectOption
from songembed import QueueEmbed, SongEmbed


# pages if pages else Embed(
#     colour=Colour.blue(),
#     title="Joining voice channel...",
# )
class Chapter(View):
    def __init__(self, pages: list[Embed], timeout: int | None = 100):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.page_len = len(self.pages)
        self.curr_page = 0
        if self.page_len == 1:
            self.nextButton.disabled = True
            
    def set_pages(self, pages: list[Embed]):
        self.pages = pages
        self.page_len = len(self.pages)
        if self.page_len == 1:
            self.nextButton.disabled = True

    async def send(self, message: InteractionMessage, select: Select):
        self.curr_page = 0
        # Make custom select object that is able to do callback functions.
        # Add Embeds to a list and somehow make the buttons show each embed
        self.prevButton.disabled = True
        self.add_item(select)
        await message.edit(embed=self.pages[self.curr_page], view=self)
        self.message = message

    @button(label="Prev")
    async def prevButton(self, interaction: Interaction, button: Button):
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
        await interaction.response.defer()
        self.curr_page += 1

        if self.curr_page + 1 == self.page_len:
            self.nextButton.disabled = True
            self.prevButton.disabled = False
        else:
            self.prevButton.disabled = False

        await self.message.edit(embed=self.pages[self.curr_page], view=self)
        
class SystemContents(dict):
    def __init__(self, songs: list[SongEmbed], paginated_queue: list[QueueEmbed]) -> None:
        if songs:
            self["Queue"] = Chapter(pages=paginated_queue) # This would be a list of paginated songs (Queue Embeds)
            self["Songs"] = Chapter(pages=songs) # This would be a list of Song Embeds, giving more detail about each song.
        else:
            self["Loading"] = Chapter(pages=[Embed(colour=Colour.blue(), title="Loading...")])


class SongBook(Select):
    def __init__(self, songs: list[SongEmbed] | None = None, paginated_queue: list[QueueEmbed] | None = None, message: InteractionMessage = None) -> None:
        self.contents_dictionary = SystemContents(songs, paginated_queue)
        options = [SelectOption(label=v, value=v) for v in self.contents_dictionary]
        super().__init__(min_values=1, max_values=1, options=options)
        self.message = message
        self.options[0].default = True
        self.default_val = self.options[0]
        self.key_values = ["Queue", "Songs"]
        self.songs = songs
        self.paginated_queue = paginated_queue

    async def send(self, songs: list[SongEmbed] | None = None, paginated_queue: list[QueueEmbed] | None = None):
        if songs:
            self.songs = songs
            self.paginated_queue = paginated_queue
        # This should be the default sending of the Embed, therefore it should display the first version of the pokemon every single time.
        print(songs)
        print(paginated_queue)
        queue_viewer = Chapter(self.paginated_queue)
        self.contents_dictionary = SystemContents(songs, paginated_queue)
        self.options = [SelectOption(label=v, value=v) for v in self.contents_dictionary]
        self.options[0].default = True
        self.default_val = self.options[0]
        await queue_viewer.send(message=self.message, select=self)
        
    async def callback(self, interaction: Interaction):
        
        # NOTE: You can make the options have emojis!!

        self.default_val.default = False
        chap = None
        value = self.values[0]

        match value:
            case "Queue":
                chap = Chapter(self.paginated_queue)
            case "Songs":
                chap = Chapter(self.songs)
                
        self.options[self.key_values.index(value)].default = True
        self.default_val = self.options[self.key_values.index(value)]

        await interaction.response.defer()
        await chap.send(message=self.message, select=self)