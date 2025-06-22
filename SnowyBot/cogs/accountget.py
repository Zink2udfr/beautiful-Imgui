import discord, json, requests
from discord import app_commands
from discord.ext import commands
from assets.logger import error, noPerms


def getUuid():
    skins_response = requests.get("https://valorant-api.com/v1/weapons/skins")
    skins_data = skins_response.json()
    getSkins = {skin["uuid"]: skin["displayName"] for skin in skins_data["data"]}

    buddies_response = requests.get("https://valorant-api.com/v1/buddies")
    buddies_data = buddies_response.json()
    getBuddies = {buddy["uuid"]: buddy["displayName"] for buddy in buddies_data["data"]}

    agents_response = requests.get("https://valorant-api.com/v1/agents")
    agents_data = agents_response.json()
    getAgents = {agent["uuid"]: agent["displayName"] for agent in agents_data["data"]}

    return getSkins, getBuddies, getAgents

getSkins, getBuddies, getAgents = getUuid()

def uuid2skiname(item_ids, mapping):
    return [mapping.get(item_id, f"Unknown skin: {item_id}") for item_id in item_ids]


class InventoryButton(discord.ui.View):
    def __init__(self, weapon_skin_names, buddy_names, agent_names):
        super().__init__(timeout=None)
        self.weapon_skin_names = weapon_skin_names
        self.buddy_names = buddy_names
        self.agent_names = agent_names

    @discord.ui.button(label="Skins", style=discord.ButtonStyle.primary, custom_id="skins_val")
    async def show_skins(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            content="Skins:\n" + "\n".join(self.weapon_skin_names) if self.weapon_skin_names else "None",
            ephemeral=True
        )

    @discord.ui.button(label="Buddies", style=discord.ButtonStyle.primary, custom_id="buddies")
    async def show_buddies(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            content="Buddies:\n" + "\n".join(self.buddy_names) if self.buddy_names else "None",
            ephemeral=True
        )

    @discord.ui.button(label="Agents", style=discord.ButtonStyle.primary, custom_id="agents")
    async def show_agents(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            content="Agents:\n" + "\n".join(self.agent_names) if self.agent_names else "None",
            ephemeral=True
        )


class FnInventory(discord.ui.View):
    def __init__(self, skins, pickaxes, dances, gliders):
        super().__init__(timeout=None)
        self.skins = skins
        self.pickaxes = pickaxes
        self.dances = dances
        self.gliders = gliders

    def get2K(self, content):
        return content[:2000]

    @discord.ui.button(label="Skins", style=discord.ButtonStyle.primary, custom_id="skins_fn")
    async def show_skins(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "Skins:\n" + "\n".join([f"{skin['title']}" for skin in self.skins])
            if self.skins
            else "None"
        )
        await interaction.response.send_message(
            content=self.get2K(content), ephemeral=True
        )

    @discord.ui.button(label="Pickaxes", style=discord.ButtonStyle.primary, custom_id="pickaxes")
    async def show_pickaxes(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "Pickaxes:\n" + "\n".join([f"{pickaxe['title']}" for pickaxe in self.pickaxes])
            if self.pickaxes
            else "None"
        )
        await interaction.response.send_message(
            content=self.get2K(content), ephemeral=True
        )

    @discord.ui.button(label="Dances", style=discord.ButtonStyle.primary, custom_id="dances")
    async def show_dances(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "Dances:\n" + "\n".join([f"{dance['title']}" for dance in self.dances])
            if self.dances
            else "None"
        )
        await interaction.response.send_message(
            content=self.get2K(content), ephemeral=True
        )

    @discord.ui.button(label="Gliders", style=discord.ButtonStyle.primary, custom_id="gliders")
    async def show_gliders(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "Gliders:\n" + "\n".join([f"{glider['title']}" for glider in self.gliders])
            if self.gliders
            else "None"
        )
        await interaction.response.send_message(
            content=self.get2K(content), ephemeral=True
        )



class AccFinder(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[+] Loaded account cog")

    @app_commands.command(name="get-account", description="Get an account from the account database")
    @app_commands.describe(game="The game of the account", title="The title of the account in the database")
    @app_commands.choices(game=[
        discord.app_commands.Choice(name='Fortnite', value='fn'),
        discord.app_commands.Choice(name='Valorant', value='valo')
    ])
    async def getacc(self, interaction: discord.Interaction, game: str, title: str):
        try:
            if interaction.user.guild_permissions.administrator is False:
                await noPerms(interaction)
                return
            headers = {
                "accept": "application/json",
                "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiJ9.eyJzdWIiOjczNzY4NzAsImlzcyI6Imx6dCIsImV4cCI6MCwiaWF0IjoxNzM1NzU3NzQ3LCJqdGkiOjcxNDUzNywic2NvcGUiOiJiYXNpYyByZWFkIHBvc3QgY29udmVyc2F0ZSBtYXJrZXQifQ.KKjQfEPUmvqB-ALN7khaJY0iJb9kSmkw8oSpbgFlVKqFjaDe71hCBsnNxbYYUHgwinY4BtzuFb19_zlOai7yl-0FkbcYqay-2HjC0GiXeQc7wQDi4FDhnPgkMe_EDNeDr0UMtbX2gC-PwLhW6IW6ejuF91GqUjb2reCZMLs7n3U"
            }

            if game == "valo":
                accurl = f'https://api.lzt.market/riot?title={title}'
                response = requests.get(accurl, headers=headers)

                if response.status_code == 200:
                    data = response.json()

                    if data.get("items"):
                        item = data["items"][0]
                        weapon_skin_ids = item["valorantInventory"].get("WeaponSkins", [])
                        buddy_ids = item["valorantInventory"].get("Buddy", [])
                        agent_ids = item["valorantInventory"].get("Agent", [])

                        weapon_skin_names = uuid2skiname(weapon_skin_ids, getSkins)
                        buddy_names = uuid2skiname(buddy_ids, getBuddies)
                        agent_names = uuid2skiname(agent_ids, getAgents)

                        embed = discord.Embed(
                            title="__Valorant Account__",
                            color=discord.Color.default()
                        )
                        embed.add_field(name="Region", value=item["valorantRegionPhrase"])
                        embed.add_field(name="Username", value=item["riot_username"])
                        embed.add_field(name="Rank", value=item["valorantRankTitle"])
                        embed.add_field(name="Valorant Points (VP)", value=item["riot_valorant_wallet_vp"])
                        embed.add_field(name="Radianite Points (RP)", value=item["riot_valorant_wallet_rp"])
                        embed.add_field(name="Skin Count", value=item["riot_valorant_skin_count"])
                        embed.add_field(name="Knife Count", value=item["riot_valorant_knife"])
                        embed.add_field(name="Account Level", value=item["riot_valorant_level"])
                        embed.add_field(name="Tracker Link", value=f"[Click here]({item['accountLink']})")
                        embed.set_thumbnail(url=interaction.guild.icon.url)

                        await interaction.channel.send(embed=embed, view=InventoryButton(weapon_skin_names, buddy_names, agent_names))
                        await interaction.response.send_message("Account sent", ephemeral=True)
                    else:
                        await interaction.response.send_message("Invalid account, make sure to use the correct title.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"API error, status code: {response.status_code}", ephemeral=True)

            elif game == "fn":
                accurl = f'https://api.lzt.market/fortnite?title={title}'
                response = requests.get(accurl, headers=headers)

                if response.status_code == 200:
                    data = response.json()

                    if data.get("items"):
                        item = data["items"][0]
                        skins = item.get("fortniteSkins", [])
                        pickaxes = item.get("fortnitePickaxe", [])
                        dances = item.get("fortniteDance", [])
                        gliders = item.get("fortniteGliders", [])

                        embed = discord.Embed(
                            title="__Fortnite Account__",
                            color=discord.Color.from_rgb(255, 255, 255)
                        )
                        embed.add_field(name="Platform", value=item["fortnite_platform"])
                        embed.add_field(name="Vbucks", value=item["fortnite_balance"])
                        embed.add_field(name="Skin Count", value=item["fortnite_skin_count"])
                        embed.add_field(name="Pickaxe Count", value=item["fortnite_pickaxe_count"])
                        embed.add_field(name="Dance Count", value=item["fortnite_dance_count"])
                        embed.add_field(name="Glider Count", value=item["fortnite_glider_count"])
                        embed.add_field(name="Account Level", value=item["fortnite_level"])
                        embed.set_thumbnail(url=interaction.guild.icon.url)

                        await interaction.channel.send(embed=embed, view=FnInventory(skins, pickaxes, dances, gliders))
                        await interaction.response.send_message("Account sent", ephemeral=True)
                    else:
                        await interaction.response.send_message("Invalid account, make sure to use the correct title.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"API error, status code: {response.status_code}", ephemeral=True)
        except Exception as e:
            await error(interaction, e)



async def setup(client):
    await client.add_cog(AccFinder(client))
