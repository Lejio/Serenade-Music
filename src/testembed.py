from discord import Embed, Colour


class TestEmbed(Embed):
    def __init__(self, name, icon, **kwargs):
        super().__init__(**kwargs, colour=Colour.blue(), title="Test Embed", description="This is a test embed.")
        self.set_author(name=name, icon_url=icon)
        self.add_field(name="Field1", value="Value1", inline=False)
        self.add_field(name="Field2", value="Value2", inline=False)
        self.add_field(name="Field3", value="Value3", inline=False)