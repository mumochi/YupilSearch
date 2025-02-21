# Runs a Discord bot client with a command for fuzzy searching of VOD transcripts.
from concurrent.futures import ProcessPoolExecutor
import asyncio
import sqlite3
from fuzzywuzzy import fuzz
import discord
from discord import app_commands as ac
from discord.ext import commands
from discord import Embed, ButtonStyle
from discord.ui import View, button
from functools import partial

CPU_COUNT = 4
SCORE_THRESHOLD = 75

guild_obj = discord.Object(id="") # Discord server ID

conn = sqlite3.connect("transcripts.db")
c = conn.cursor()
c.execute("""SELECT * FROM vods WHERE (LENGTH(text) - LENGTH(REPLACE(text, ' ', ''))) >= 3;""")
output = c.fetchall()
c.close()

class BotClient(commands.Bot):
    def __init__(self, *, command_prefix: str, intents: discord.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=guild_obj)
        await self.tree.sync(guild=guild_obj)

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = BotClient(command_prefix='/', intents=intents)
tree = bot.tree

class PaginatorView(View):
    def __init__(self, embeds):
        super().__init__()
        self.embeds = embeds
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
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
        await interaction.channel.send(message_to_send)
        await interaction.response.defer()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

def score_row(row, query):
    context = row[0]  # Transcript text
    if fuzz.token_set_ratio(context, query) >= SCORE_THRESHOLD:
        vod_id = row[3]
        vod_time = int(row[1])
        url = f"https://www.youtube.com/watch?v={vod_id}&t={vod_time}"
        return discord.Embed(title=f"Query: {query}", description=f"**Transcript context**: {context}\nURL: {url}")
    return None

@tree.command(
    name="search",
    description="Searches VOD transcripts for query."
)
@ac.describe(
    query="Word or phrase to search."
)
async def search(ctx: commands.Context, query: str):
    await ctx.response.defer(ephemeral=True)
    loop = asyncio.get_running_loop()

    with ProcessPoolExecutor(max_workers=CPU_COUNT) as executor:
        chunk_size = len(output) // (CPU_COUNT * 8) or 1
        # Use partial to bind query to score_row
        score_with_query = partial(score_row, query=query)
        results = await loop.run_in_executor(
            None,
            lambda: list(executor.map(score_with_query, output, chunksize=chunk_size))
        )

    embeds = [embed for embed in results if embed is not None]

    if not embeds:
        embeds.append(Embed(title=f"Query: {query}", description="No matches found."))
        await ctx.followup.send(embed=embeds[0])
    else:
        view = PaginatorView(embeds)
        await ctx.followup.send(embed=embeds[0], view=view)

bot.run("") # Discord bot key
