# Runs a Discord bot client with a command for fuzzy searching of VOD transcripts.
import json
import sqlite3
from fuzzywuzzy import fuzz
import discord
from discord import app_commands as ac
from discord.ext import commands
from discord import Embed, ButtonStyle
from discord.ui import View, button

SCORE_THRESHOLD = 75

guild_obj = discord.Object(id = "") # Discord server ID

conn = sqlite3.connect("transcripts.db")
c = conn.cursor()
c.execute("""SELECT * FROM vods""")
output = c.fetchall()
c.close()

# Bot client class with one-time setup
class BotClient(commands.Bot):
    def __init__(self, *, command_prefix: str, intents: discord.Intents):
        super().__init__(command_prefix = command_prefix, intents = intents)

    async def setup_hook(self):
        self.tree.copy_global_to(guild = guild_obj)
        await self.tree.sync(guild = guild_obj)

# Set bot intents and bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = BotClient(command_prefix = '/', intents = intents)
tree = bot.tree

class PaginatorView(View):
    def __init__(self, embeds):
        super().__init__()
        self.embeds = embeds
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
        # Disable buttons if there's nowhere to go
        self.left.disabled = self.current_page == 0
        self.right.disabled = self.current_page == len(self.embeds) - 1

    @button(label='←', style=ButtonStyle.primary)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @button(label='→', style=ButtonStyle.primary)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @button(label='Youtube Embed', style=ButtonStyle.red)
    async def send_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        current_embed = self.embeds[self.current_page]
        message_to_send = current_embed.description.split("\nURL: ")[1]
        # Send the predefined message to the channel
        await interaction.channel.send(message_to_send)
        # Acknowledge the interaction without changing the current message
        await interaction.response.defer()

@tree.command(
    name = "search",
    description="Searches VOD transcripts for query."
)
@ac.describe(
        query = "Word or phrase to search."
)
async def search(ctx: commands.Context, query: str):
    embeds = []
    await ctx.response.defer()
    for i in range(len(output)):
        context = output[i][0]
        if context.count(" ") > 2:
            if fuzz.token_set_ratio(output[i][0], query) >= SCORE_THRESHOLD:
                vod_id = output[i][3]
                vod_time = int(output[i][1])
                url = f"https://www.youtube.com/watch?v={vod_id}&t={vod_time}"
                embeds.append(discord.Embed(title=f"Query: {query}",
                                            description=f"**Transcript context**: {output[i][0]}\nURL: {url}"))

    if len(embeds) == 0:
        embeds.append(Embed(title=f"Query: {query}",
                            description="No matches found."))
        await ctx.followup.send(embed=embeds[0])
    else:
        view = PaginatorView(embeds)
        await ctx.followup.send(embed=embeds[0], view=view)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
  
bot.run('') # Discord bot token
