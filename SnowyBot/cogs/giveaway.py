import discord, json, asyncio, re, os
from datetime import timedelta, datetime
from discord.ext import commands
from discord import ui, app_commands
from assets.logger import noPerms, error

with open('assets/config/config.json', 'r') as f:
    config = json.load(f)

class EnterButton(discord.ui.View):
    def __init__(self, message_id, channel, prize, end_time):
        super().__init__(timeout=None)
        self.message_id = message_id
        self.channel = channel
        self.prize = prize
        self.end_time = end_time

    @discord.ui.button(label="Enter Giveaway", style=discord.ButtonStyle.primary, custom_id="giveawayButton")
    async def entryButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if self.end_time < datetime.now():
                await interaction.response.send_message("This giveaway has already ended. You can no longer join or leave.", ephemeral=True)
                return

            gwFolder = f"assets/saves/giveaways/{self.message_id}.json"

            if os.path.exists(gwFolder):
                with open(gwFolder, "r") as file:
                    giveaway_data = json.load(file)
                giveaway_entries = giveaway_data["entries"]
                hostUserId = giveaway_data.get("hostUser")  
            else:
                giveaway_entries = []
                hostUserId = None

            user_id = interaction.user.id
            if user_id in giveaway_entries:
                giveaway_entries.remove(user_id)
                response = "You've been removed from the giveaway."
            else:
                giveaway_entries.append(user_id)
                response = "You've been added to the giveaway."

            giveaway_data["entries"] = giveaway_entries
            with open(gwFolder, "w") as file:
                json.dump(giveaway_data, file)

            entries = len(giveaway_entries)
            timestamp = int(self.end_time.timestamp())

            embed = discord.Embed(
                title="__New Giveaway__",
                description=f"> New giveaway hosted in {interaction.guild.name} by <@{hostUserId}>.", 
                color=discord.Color(int("0x0016fa", 16)),
                timestamp=datetime.now()
            )
            embed.add_field(name="Prize", value=self.prize)
            embed.add_field(name="Entries", value=f"{entries} entries")
            embed.add_field(name="Ends", value=f"<t:{timestamp}:R>", inline=False)
            embed.set_footer(icon_url=interaction.guild.icon.url)
            embed.set_thumbnail(url=interaction.guild.icon.url)

            await interaction.message.edit(embed=embed)
            await interaction.response.send_message(response, ephemeral=True)
        except Exception as e:
            await error(interaction, e)

class GWModal(ui.Modal, title="Start a Giveaway"):
    prize = ui.TextInput(label="The prize of the giveaway", placeholder="Ex: Fa valorant account", style=discord.TextStyle.short)
    duration = ui.TextInput(label="The duration of the giveaway", placeholder="Ex: 1h, 30m", style=discord.TextStyle.short)
    channel_id = ui.TextInput(label="Channel id of the giveaway channel", placeholder="Ex: 123456789012345678", style=discord.TextStyle.short)
    winner = ui.TextInput(label="The user id of the winner of the giveaway", placeholder="Ex: 123456789012345678", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            time_pattern = re.compile(r"(\d+)([smhd])")
            time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            
            match = time_pattern.match(self.duration.value)
            if not match:
                await interaction.response.send_message("Invalid duration format. Use 1s, 1m, 1h, or 1d.", ephemeral=True)
                return
            
            time_value = int(match.group(1))
            time_unit = match.group(2)
            duration_seconds = time_value * time_units[time_unit]

            channel = interaction.guild.get_channel(int(self.channel_id.value))
            if not channel:
                await interaction.response.send_message("Please enter a valid channel id.", ephemeral=True)
                return
            
            end_time = datetime.now() + timedelta(seconds=duration_seconds)
            timestamp = int(end_time.timestamp())
            
            embed = discord.Embed(
                title="__New Giveaway__",
                description=f"> New giveaway hosted in {interaction.guild.name} by {interaction.user.mention}.",
                color=discord.Color(int("0x0016fa", 16)),
                timestamp=datetime.now()
            )
            embed.add_field(name="Prize", value=self.prize)
            embed.add_field(name="Entries", value="0 entries")
            embed.add_field(name="Ends", value=f"<t:{timestamp}:R>", inline=False)
            embed.set_footer(icon_url=interaction.guild.icon.url)
            embed.set_thumbnail(url=interaction.guild.icon.url),
            
            message = await channel.send(embed=embed)
        
            view = EnterButton(message.id, channel, self.prize, end_time)
            await message.edit(view=view)  
            
            giveawayFile = f"assets/saves/giveaways/{message.id}.json"
            with open(giveawayFile, "w") as file:
                json.dump({
                    "entries": [],
                    "end_time": end_time.isoformat(),
                    "hostUser": interaction.user.id  
                }, file)

            await interaction.response.send_message(f"Giveaway created in {channel.mention}.", ephemeral=True)
            await asyncio.sleep(duration_seconds)

            with open(f"assets/saves/giveaways/{message.id}.json", "r") as file:
                data = json.load(file)

            entryGet = data.get("entries", [])
            entries = len(entryGet)

            with open(giveawayFile, "r") as file:
                giveaway_data = json.load(file)

            participants = giveaway_data["entries"]
            if participants:
                winner_id = int(self.winner.value)
                embed = discord.Embed(
                    title="__Giveaway Winner__",
                    description=f"Congratulations <@{winner_id}>, You won the giveaway!",
                    color=discord.Color(int("0x0016fa", 16))
                )
                gw_msg = await channel.fetch_message(message.id)
                embed.add_field(name="Prize", value=self.prize)
                embed.add_field(name="Entries", value=f"{entries}")
                embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
                await gw_msg.reply(f"||<@{winner_id}>||", embed=embed)
            else:
                await channel.send("No-one entered the giveaway.")

            os.remove(giveawayFile)
        except Exception as e:
            await error(interaction, e)


class Giveaway(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("[+] Loaded giveaway cog")

    @app_commands.command(name="giveaway-start", description="Start a new giveaway.")
    async def start_giveaway(self, interaction: discord.Interaction):
        try:
            if interaction.guild.get_role(config['ceo']) not in interaction.user.roles:
                await noPerms(interaction)
                return
            
            await interaction.response.send_modal(GWModal())
        except Exception as e:
            print(e)

async def setup(client):
    await client.add_cog(Giveaway(client))