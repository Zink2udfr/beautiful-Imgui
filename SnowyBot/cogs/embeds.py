import discord, json, requests
from discord.ext import commands
from discord import app_commands, ui
from cogs.tickets import buyingmodal
from assets.logger import noPerms, error

with open('assets/config/config.json', 'r') as f:
    config = json.load(f)

with open('assets/config/emojis.json', 'r') as f:
    emoji = json.load(f)

class BuyBtns(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Buy", style=discord.ButtonStyle.primary, emoji=emoji['buy'], custom_id="buytn")
    async def buybtn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(buyingmodal())

class roles(discord.ui.Select):
    def __init__(self, **kwargs):
        super().__init__(placeholder="Select an option", options=[
            discord.SelectOption(label="Drops", description="Get notified whenever there is a new drop", value="drops", emoji="🎁"),
            discord.SelectOption(label="Giveaway", description="Get notified whenever there is a new giveaway", value="giveaway", emoji="🎉"),
            discord.SelectOption(label="Event", description="Get notified whenever there is a new event", value="event", emoji="🎪"),
            discord.SelectOption(label="Announce", description="Get notified whenever there is a new announcement", value="ann", emoji="📢")
            ], **kwargs)
        

    async def callback(self, interaction: discord.Interaction):
            payment = interaction.data['values'][0]
            if payment == "drops":
                  drop_ping = interaction.guild.get_role(config['dropsRole'])
                  if drop_ping not in interaction.user.roles:
                      try:
                        await interaction.user.add_roles(drop_ping)
                      except Exception as e:
                        await error(interaction, e)   
                        return 
                      await interaction.response.send_message(f"**> Added {drop_ping.mention} role**", ephemeral=True)
                  else:
                      try:
                        await interaction.user.remove_roles(drop_ping)
                      except Exception as e:
                        await error(interaction, e)   
                        return 
                      await interaction.response.send_message(f"**> Removed {drop_ping.mention} role**", ephemeral=True)
            elif payment == "giveaway":
                  gw_ping = interaction.guild.get_role(config['giveawayRole'])
                  if gw_ping not in interaction.user.roles:
                      try:
                        await interaction.user.add_roles(gw_ping)
                      except Exception as e:
                        await error(interaction, e)   
                        return 
                      await interaction.response.send_message(f"**> Added {gw_ping.mention} role**", ephemeral=True)
                  else:
                      try:
                        await interaction.user.remove_roles(gw_ping)
                      except Exception as e:
                        await error(interaction, e)   
                        return 
                      await interaction.response.send_message(f"**> Removed {gw_ping.mention} role**", ephemeral=True)
            elif payment == "event":
                       ev_ping = interaction.guild.get_role(config['eventRole'])
                       if ev_ping not in interaction.user.roles:
                           try:
                             await interaction.user.add_roles(ev_ping)
                           except Exception as e:
                             await error(interaction, e)   
                             return 
                           await interaction.response.send_message(f"**> Added {ev_ping.mention} role**", ephemeral=True)
                       else:
                           try:
                             await interaction.user.remove_roles(ev_ping)
                           except Exception as e:
                             await error(interaction, e)   
                             return 
                           await interaction.response.send_message(f"**> Removed {ev_ping.mention} role**", ephemeral=True)  
            elif payment == "ann":
                       ann_ping = interaction.guild.get_role(config['announceRole'])
                       if ann_ping not in interaction.user.roles:
                           try:
                             await interaction.user.add_roles(ann_ping)
                           except Exception as e:
                             await error(interaction, e)   
                             return 
                           await interaction.response.send_message(f"**> Added {ann_ping.mention} role**", ephemeral=True)
                       else:
                           try:
                             await interaction.user.remove_roles(ann_ping)
                           except Exception as e:
                             await error(interaction, e)   
                             return 
                           await interaction.response.send_message(f"**> Removed {ann_ping.mention} role**", ephemeral=True)

class rolesdropdwn(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(roles(custom_id="role_s")) 


async def bundle_embed(interaction: discord.Interaction, channel2send: discord.TextChannel):
    embed = discord.Embed(
        title="Snowy Bundles",
        description="Planning on creating your own successful valorant selling server? Let us help you! We have a few bundles you can buy to help start with your business.",
        color=discord.Color(int("0x0016fa", 16))
    )
    embed.add_field(name="Extreme Bundle:", value="**- Nexus Checker\n- 10Gb of High Speed Proxies\n- Lifetime shop in Snowy Market\n- 50% discount on combos forever\n- Server setup for you\n- Price - $150**", inline=False)
    embed.add_field(name="Lite Bundle:", value="**- Nexus Checker\n- 10Gb of High Speed Proxies\n- 1 week shop in Snowy Market\n- 20% discount on combos forever\n- Price - $50**", inline=False)
    embed.add_field(name="Extra's", value=f"**- 10Gb of more proxies - $10\n\nTo buy one of the bundles, please create a <#{config['ticketChannel']}>.**", inline=False)
    embed.set_thumbnail(url=interaction.guild.icon.url)
    embed.set_footer(icon_url=interaction.guild.icon.url, text=interaction.guild.name)

    view = BuyBtns()

    await channel2send.send(embed=embed, view=view)
    await interaction.response.send_message(f"Successfully sent the embed. ( {channel2send.mention} )", ephemeral=True)

async def mm_embed(interaction: discord.Interaction, channel2send: discord.TextChannel):
    embed = discord.Embed(
        title="__MiddleMan__",
        description=f"**- 3$ + 5% of the price\n- Secure every trade or payment\n- Fast Service\n- We can Middleman Accounts, Money, Method and everything\n- We'll check everything to be sure that you're giving legit things!\n\nOpen a <#{config['ticketChannel']}> to use our service.**",
        color=discord.Color(int("0x0016fa", 16))
    )
    view = BuyBtns()
    await channel2send.send(embed=embed, view=view)
    await interaction.response.send_message(f"Successfully sent the embed. ( {channel2send.mention} )", ephemeral=True)

async def fa_embed(interaction: discord.Interaction, channel2send: discord.TextChannel):
    try:
        embed = discord.Embed(
            title="__Full Access Accounts__",
            description=f"**Fa Valorant\n[{emoji['money']}] Prices based on...\n\n"
                        f"[{emoji['arrow']}] Account Rank\n[{emoji['arrow']}] Amount of Skins\n"
                        f"[{emoji['arrow']}] Quality of Skins\n[{emoji['arrow']}] Account Region\n"
                        f"[{emoji['crystal']}] Account safety\n\n——————————————————————-\nFa Fortnite\n"
                        f"[{emoji['money']}] Prices based on...\n\n[{emoji['arrow']}] Skins\n"
                        f"[{emoji['arrow']}] Amount of Skins\n[{emoji['arrow']}] Vbucks on the account\n"
                        f"[{emoji['crystal']}] Account safety\n——————————————————————-\n\n"
                        "Note:\n1. You will be shown a list of names of skins about the account, "
                        "ranks and a lot of info about the account.\n\n"
                        "2. Warranty will be given depending on your budget and we will note if "
                        "you will be given a warranty or not.\n\n"
                        "3. Minimum budget of all accounts is 10$ unless we make an exception.\n\n"
                        f"Open a <#{config['ticketChannel']}> to purchase.**",
            color=discord.Color(int("0x0016fa", 16))
        )
        embed.set_thumbnail(url=interaction.guild.icon.url)
    
        view = BuyBtns()
    
        await channel2send.send(embed=embed, view=view)
        await interaction.response.send_message(f"Successfully sent the embed. ({channel2send.mention})", ephemeral=True)
    
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
        print(e)


async def proxies_embed(interaction: discord.Interaction, channel2send: discord.TextChannel):
    embed = discord.Embed(
        title="__Riot Proxies__",
        description="> **10GB = 10$**\n> **20GB = 15$**\n> **30GB = 25$**\n> **50GB = 35$**\n\n> **1 DAY = 19$**\n> **3 DAYS = 30$**\n> **7 DAYS = 45$**",
        color=discord.Color(int("0x0016fa", 16))
    )
    view = BuyBtns()
    await channel2send.send(embed=embed, view=view)
    await interaction.response.send_message(f"Successfully sent the embed. ( {channel2send.mention} )", ephemeral=True)   

async def checker_embed(interaction: discord.Interaction, channel2send: discord.TextChannel):
    embed = discord.Embed(
        title="Nexus Checker",
        description="**> Paypal = 12$\n> Crypto = 8$**",
        color=discord.Color(int("0x0016fa", 16))
    )
    embed.add_field(name="Orion Checker", value=f"**> Paypal & Crypto = 25$\n\nOpen a <#{config['ticketChannel']}> to puchase.**")
    view = BuyBtns()
    await channel2send.send(embed=embed, view=view)
    await interaction.response.send_message(f"Successfully sent the embed. ( {channel2send.mention} )", ephemeral=True) 

async def combos_embed(interaction: discord.Interaction, channel2send: discord.TextChannel):
    try:
        embed = discord.Embed( 
            title="Combos", 
            description=f""" 
**Super Ultra High quality combos **

{emoji['money']}
> {emoji['crystal']}  10k=$15
> {emoji['crystal']}  20k=$30
> {emoji['crystal']}  30k=$40
> {emoji['crystal']}  40k=$50
> {emoji['crystal']}  50k=$55
> {emoji['crystal']}  60k=$65
> {emoji['crystal']}  100k=$85


{config['blueline']} {config['blueline']} {config['blueline']} {config['blueline']} {config['blueline']} {config['blueline']} {config['blueline']} {config['blueline']} {config['blueline']} {config['blueline']} {config['blueline']} {config['blueline']} {config['blueline']} {config['blueline']} {config['blueline']} {config['blueline']} {config['blueline']}

**Ultra High Quality Combos 1k skinned per 10k**

{emoji['money']}
> {emoji['crystal']}  10k=$10
> {emoji['crystal']}  20k=$15
> {emoji['crystal']}  30k=$20
> {emoji['crystal']}  40k=$30
> {emoji['crystal']}  50k=$40
> {emoji['crystal']}  100k=$60



```What are combos
Combos are list of accounts, with format User:Pass, made for valorant.```
""",
    color=discord.Color(int("0x0016fa", 16)))

        embed.set_footer(icon_url=interaction.guild.icon.url, text=interaction.guild.name)
        embed.set_thumbnail(url=interaction.guild.icon.url)
        view = BuyBtns()
        await channel2send.send(embed=embed, view=view)
        await interaction.response.send_message(f"Successfully sent the embed. ({channel2send.mention})", ephemeral=True)
    
    except Exception as e:
        await error(interaction, e)

async def backup_embed(interaction: discord.Interaction, channel2send: discord.TextChannel):
    embed = discord.Embed(
        title="__Backup__",
        description="**Join our backup server to stay with us after a termination.**",
        color=discord.Color(int("0x0016fa", 16))
    )
    embed.add_field(name="Discord:", value="[.gg/snowymp](https://discord.gg/snwy)")
    embed.add_field(name="Telegram:", value="https://t.me/snowymp")
    embed.set_thumbnail(url=interaction.guild.icon.url)
    embed.set_footer(icon_url=interaction.guild.icon.url, text=interaction.guild.name)
    await channel2send.send(embed=embed)
    await interaction.response.send_message(f"Successfully sent the embed. ( {channel2send.mention} )", ephemeral=True) 

async def geninfo_embed(interaction: discord.Interaction, channel2send: discord.TextChannel):
    try:
        
        embed = discord.Embed(
            title="Gen infos",
            description="""
**Free Gen (1-150 Skins)

> Vote for Snowy in the three links below to receive "free Gen" role! Click the links and enjoy the rewards!

Invite Gen (50-150 Skins)

> Invite 7 friends to our server, and you'll unlock "Invite Gen" role! Start inviting and enjoy our Gen!

Booster Gen (100-200++ Skins)

> Boost our server and you'll unlock "Boost Gen" role! Boost and enjoy our Gen!**
""",
            color=discord.Color(int("0x0016fa", 16))
        )
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_image(url=interaction.guild.banner.url)
        embed.set_footer(icon_url=interaction.guild.icon.url, text=interaction.guild.name)
    
        button1 = ui.Button(label="Vote 1", url="https://discadia.com/server/snowyinc/")
        button2 = ui.Button(label="Vote 2", url="https://discords.com/servers/snowyx10k")
        button3 = ui.Button(label="Vote 3", url="https://disboard.org/server/1267937759423762434")
    
        view = ui.View(timeout=None)
        view.add_item(button1)
        view.add_item(button2)
        view.add_item(button3)
    
        await channel2send.send(embed=embed, view=view)
        await interaction.response.send_message(f"Successfully sent the embed. ( {channel2send.mention} )", ephemeral=True)
    except Exception as e:
        await error(interaction, e)



async def rules_embed(interaction: discord.Interaction, channel2send: discord.TextChannel):
    embed = discord.Embed(
        description="""
# RULES

> **1.) We will not give the account until the transaction is fully confirmed.**

> **2.) We will not provide refunds for payments sent from bank, or card.**

> **3.) We will not provide refunds for any Full Access accounts where the transaction is more than one day old.**

> **4.) We will not provide refunds for nexus lifetime where the transaction is more than one day old**

> **5.) We will not provide refunds for any products other than an account or Nexus.**

> **6.) Buying and/or Middle-Man fees are not refundable under any circumstances.**

> **7.) We do not cover any fees you may have whilst sending.**

> **8.) We can refuse services without a given reason.**

> **9.) We cannot be held responsible for any misuse of our products by customers**

> **10.) By redeeming an account you consent to any issues you may further have, compensation may only be provided if it is a problem on our side our the account credentials do not work 120 seconds after the purchase.**

> **11.) We are not responsible for any pullbacks for our accounts, After you have logged into the account, we are not held responsible for anything that happens after.**

> **12.) We retain the right to modify our Terms of Service at any point in time..**

> **13.) Upon purchasing from us, regardless of the platform, you are deemed to have accepted these TOS automatically.**
""",
        color=discord.Color(int("0x0016fa", 16))
    )
    embed.set_thumbnail(url=interaction.guild.icon.url)
    embed.set_image(url=interaction.guild.banner.url)
    embed.set_footer(icon_url=interaction.guild.icon.url, text=interaction.guild.name)


    await channel2send.send(embed=embed)
    await interaction.response.send_message(f"Successfully sent the embed. ( {channel2send.mention} )", ephemeral=True)

class crembedmodal(ui.Modal, title="Embed"):
    titel = ui.TextInput(label="Enter your title", placeholder="Optional", style=discord.TextStyle.short, required=False)
    description = ui.TextInput(label="Enter your description", style=discord.TextStyle.long)
    footer = ui.TextInput(label="Enter your footer", placeholder="Optional", style=discord.TextStyle.short, required=False)

    def __init__(self, interaction, colour, thumbnail, banner, pings):
        super().__init__()
        self.interaction = interaction
        self.colour = colour
        self.thumbnail = thumbnail
        self.banner = banner
        self.pings = pings

    async def on_submit(self, interaction: discord.Interaction):
        colour = self.colour
        if colour == 'snowyblue':
            clr = discord.Color(int("0x0016fa", 16))
        elif colour == 'blue':
            clr = discord.Color.blue()
        elif colour == 'blurple':
            clr = discord.Color.blurple()
        elif colour == 'standard':
            clr = None

        embed = discord.Embed(
            title=self.titel.value,
            description=self.description.value,
            color=clr
        )

        if self.footer.value:
            embed.set_footer(icon_url=interaction.guild.icon.url, text=self.footer.value)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        if self.banner:
            embed.set_image(url=self.banner)
        if self.pings:
            await interaction.channel.send(content=f"{self.pings}", embed=embed)
        else:
            await interaction.channel.send(embed=embed)

        await interaction.response.send_message(embed=discord.Embed(description="Successfully created announcement"), ephemeral=True)

class Embeds(commands.Cog):
    def  __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[+] Loaded embed cog")


    @app_commands.command(name="verify-embed", description="Send the verification embed")
    @app_commands.describe(channel="The channel where you want to display the embed")
    async def verify(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.guild.get_role(config['ceo']) not in interaction.user.roles:
                await noPerms(interaction)
                return
        
        embed = discord.Embed(
            title="__Verification__",
            description="**> To get access to the rest of our server, you must verify with guild mergers.\n\n- Why guild mergers\n\n> We use guild mergers to restore our server incase of a termination so we don't lose our success.**",
            color=discord.Color(int("0x0016fa", 16))
        )
        embed.set_footer(icon_url=interaction.guild.icon.url, text=interaction.guild.name)
        embed.set_thumbnail(url=interaction.guild.icon.url)
    
        button = ui.Button(url="https://discord.com/oauth2/authorize?client_id=1310728990989877359&redirect_uri=https://restorecord.com/api/callback&response_type=code&scope=identify+guilds.join&state=1316964412766294027&prompt=none", label="Verify")
        view = ui.View(timeout=None)
        view.add_item(button)
    
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message("Sucessfully sent verification embed.", ephemeral=True)

    @app_commands.command(name="send-embeds", description="Send an embed to a specific channel.")
    @app_commands.describe(type="Select the embed you want to send.", channel="The channel you want to send the embed to")
    @app_commands.choices(type=[
        discord.app_commands.Choice(name='Bundle-Embed', value='bundle'),
        discord.app_commands.Choice(name='Middleman-Embed', value='mm'),
        discord.app_commands.Choice(name='Fa-Embed', value='fa'),
        discord.app_commands.Choice(name='Proxies-Embed', value='proxies'),
        discord.app_commands.Choice(name='Checker-Embed', value='checker'),
        discord.app_commands.Choice(name='Combos-Embed', value='combos'),
        discord.app_commands.Choice(name='Geninfo-Embed', value='geninfo'),
        discord.app_commands.Choice(name='Backup-Embed', value='backup'),
        discord.app_commands.Choice(name='Rules-Embed', value='rules'),
    ])
    async def embeds(self, interaction: discord.Interaction, type: str, channel: discord.TextChannel):
    
        if interaction.guild.get_role(config['ceo']) not in interaction.user.roles:
            await noPerms(interaction)
            return
    
        if type == 'bundle':
          try:
            await bundle_embed(interaction, channel)
          except Exception as e:
            print(e)
        elif type == 'mm':
            await mm_embed(interaction, channel)
        elif type == 'fa':
            await fa_embed(interaction, channel)
        elif type == 'proxies':
            await proxies_embed(interaction, channel)
        elif type == 'checker':
            await checker_embed(interaction, channel)
        elif type == 'combos':
            await combos_embed(interaction, channel)
        elif type == 'backup':
            await backup_embed(interaction, channel)
        elif type == 'geninfo':
            await geninfo_embed(interaction, channel)
        elif type == 'rules':
            await rules_embed(interaction, channel)

    @app_commands.command(name="create-embed", description="Create an embed")
    @app_commands.describe(colour="The color of your embed", thumbnail="The thumbnail of your embed (url)", banner="The banner of your embed (url)", pings="The role you want to mention")
    @app_commands.choices(colour=[
        discord.app_commands.Choice(name='Snowy Blue', value='snowyblue'),
        discord.app_commands.Choice(name='Blue', value='blue'),
        discord.app_commands.Choice(name='Blurple', value='blurple'),
        discord.app_commands.Choice(name='Standard', value='standard'),
    ])
    async def crembed(
        self,
        interaction: discord.Interaction,
        colour: str,
        thumbnail: str = None,
        banner: str = None,
        pings: discord.Role = None
    ):
        if interaction.user.guild_permissions.administrator is False:
            await noPerms(interaction)
            return
            
        modal = crembedmodal(interaction, colour, thumbnail, banner, pings)
        await interaction.response.send_modal(modal)

    @app_commands.command(name='panel', description="Send the reaction role panel")
    @app_commands.describe(channel="The channel you want to send the embed to")
    async def panel(self, interaction:discord.Interaction, channel: discord.TextChannel):
            if interaction.user.guild_permissions.administrator is False:
                await interaction.response.send_message("You are not allowed to use this command", ephemeral=True)
            embed=discord.Embed(color=discord.Color.blurple(),title='Ping Roles', description="**Choose your pings roles using the buttons below:\n- 🎁 Drops\n- 🎉 Giveaways\n- 🎪 Events\n- 📢 Annoucement**")
            await channel.send(embed=embed, view=rolesdropdwn())
            await interaction.response.send_message("Sent", ephemeral=True)
    


async def setup(client):
    await client.add_cog(Embeds(client))