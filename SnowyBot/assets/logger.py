import discord
from datetime import datetime

def timestamp() -> str:
    return datetime.now().strftime("%d-%m-20%y %H:%M:%S")

async def noPerms(interaction: discord.Interaction):
    await interaction.response.send_message("You do not have permissions to use this command.", ephemeral=True)

async def error(interaction: discord.Interaction, error: Exception):
    try:
        await interaction.response.send_message(f"There was an error, please report this in a ticket. ({str(error)})", ephemeral=True)
        time = timestamp()
        print(f"[{time}] Error: {str(error)}")
    except Exception as e:
        print(e)