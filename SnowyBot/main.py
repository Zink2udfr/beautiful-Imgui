import discord, json, os, asyncio
from discord.ext import commands
from cogs.tickets import TicketButtonView, TicketEmbed, CloseButton
from cogs.staff import ApplyButton
from cogs.embeds import BuyBtns, rolesdropdwn
from cogs.accountget import InventoryButton

with open('assets/config/config.json', 'r') as f:
    config = json.load(f)

with open('assets/config/emojis.json', 'r') as f:
    emoji = json.load(f)


class stayAlive(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=commands.when_mentioned_or('?'), intents=intents, help_command=None)
    async def setup_hook(self) -> None:
        self.add_view(TicketEmbed())
        self.add_view(TicketButtonView())
        self.add_view(BuyBtns())
        self.add_view(ApplyButton())
        self.add_view(rolesdropdwn())
        self.add_view(InventoryButton([], [], []))
        self.add_view(CloseButton([], []))

client = stayAlive()
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{config['status']}"))
    print(f'Logged in as {client.user}')
    await client.tree.sync()


async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')

async def main():
    async with client:
        await load()
        await client.start(config['botToken'])

asyncio.run(main())