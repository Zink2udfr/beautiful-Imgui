import os
import json
import asyncio
from pathlib import Path
from typing import Any

import discord
from discord.ext import commands

# Local imports
from cogs.tickets import TicketButtonView, TicketEmbed, CloseButton
from cogs.staff import ApplyButton
from cogs.embeds import BuyBtns, rolesdropdwn
from cogs.accountget import InventoryButton

# --- Configuration Loading ---
def load_json_config(path: Path) -> Any:
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {path}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {path}: {e}")
        raise

CONFIG_PATH = Path('assets/config/config.json')
EMOJI_PATH = Path('assets/config/emojis.json')

config = load_json_config(CONFIG_PATH)
emoji = load_json_config(EMOJI_PATH)

# --- Discord Bot Definition ---
class StayAliveBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=commands.when_mentioned_or('?'),
            intents=intents,
            help_command=None
        )

    async def setup_hook(self) -> None:
        # Register persistent views, required for buttons/dropdowns to work after restart
        self.add_view(TicketEmbed())
        self.add_view(TicketButtonView())
        self.add_view(BuyBtns())
        self.add_view(ApplyButton())
        self.add_view(rolesdropdwn())
        self.add_view(InventoryButton([], [], []))
        self.add_view(CloseButton([], []))

# --- Main Execution Logic ---

bot = StayAliveBot()
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{config.get('status', 'the server')}"
        )
    )
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()

async def load_cogs():
    cogs_path = Path('./cogs')
    for file in cogs_path.glob('*.py'):
        await bot.load_extension(f'cogs.{file.stem}')

async def main():
    async with bot:
        await load_cogs()
        await bot.start(config['botToken'])

if __name__ == '__main__':
    asyncio.run(main())
