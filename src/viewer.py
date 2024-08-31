from discord import Embed
from discord.ui import View, Button, Select, Item, button
from discord import Embed, InteractionMessage, Interaction, SelectOption
from songembed import SongEmbed

class SongViewer(View):
    def __init__(self, pages: list[Embed], timeout: int):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.page_len = len(pages)

    async def send(self, message: InteractionMessage):
        self.curr_page = 0
        # Make custom select object that is able to do callback functions.
        # Add Embeds to a list and somehow make the buttons show each embed
        self.prevButton.disabled = True
        await message.edit(embed=self.pages[self.curr_page], view=self)
        self.message = message

    @button(label="Prev")
    async def prevButton(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        self.curr_page -= 1
        # print('Previous new page:', self.curr_page)

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
        # print('Next new page:', self.curr_page)

        if self.curr_page + 1 == self.page_len:
            # print('Disabling')
            self.nextButton.disabled = True
            self.prevButton.disabled = False
        else:
            self.prevButton.disabled = False

        await self.message.edit(embed=self.pages[self.curr_page], view=self)


class ViewerSelection(Select):
    # Takes in the message and edits it based on the version selected.
    def __init__(self, selections: list) -> None:
        options = [SelectOption(label=v, value=v) for v in selections]
        super().__init__(min_values=1, max_values=1, options=options)

        self.options[0].default = True

    async def callback(self, interaction: Interaction):
        await interaction.response.send_message(
            f"Selected: {self.values[0]}", ephemeral=True
        )