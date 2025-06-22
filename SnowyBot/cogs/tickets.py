import discord, json, secrets, os, chat_exporter, ftplib, string
from discord.ext import commands
from discord import ui, app_commands
from assets.logger import noPerms, error

with open('assets/config/config.json', 'r') as f:
    config = json.load(f)

with open('assets/config/emojis.json', 'r') as f:
    emoji = json.load(f)

async def gentranscript(user: discord.User, channel: discord.TextChannel, interaction: discord.Interaction):
    try:
        export = await chat_exporter.export(channel=channel)
        name = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(30))
        file_name = f"{name}-{user.name}-transcript.html"
        file_path = os.path.join(os.getcwd(), file_name)
    
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(export)
    
        try:
            ftp = ftplib.FTP('snowymarket.cc')
            ftp.login('snowyma1', '0ttj7f9QL5')
    
            ftp.cwd('/public_html')
    
            try:
                ftp.mkd('transcripts')
            except ftplib.error_perm:   
                pass
    
            ftp.cwd('transcripts')
    
            with open(file_path, 'rb') as file:
                ftp.storbinary(f'STOR {file_name}', file)
            ftp.quit()
        except ftplib.all_errors as e:
            print(e)
    
        os.remove(file_path)
    
        transcript_url = f"https://snowymarket.cc/transcripts/{file_name}"
        embed4member=discord.Embed(
            title="__Ticket Closed__",
            description="Your ticket in **snowy market** has been closed.",
            color=discord.Color(int("0x0016fa", 16))
        )
        embed4member.add_field(name="Transcript", value=f"[View Transcript]({transcript_url})")
        await user.send(embed=embed4member)
    
        transcriptChannel = interaction.guild.get_channel(config['transcriptChannel'])
        embed = discord.Embed(
            title="__Ticket Closed__",
            description=f"Ticket `{interaction.channel.name}` has been closed by {interaction.user.mention}.",
            color=discord.Color(int("0x0016fa", 16))
        )
        embed.add_field(name="Transcript", value=f"[View Transcript]({transcript_url})")
        await transcriptChannel.send(embed=embed)
    except Exception as e:
        await error(interaction, e)

class CloseButton(discord.ui.View):
    def __init__(self, user: discord.Member, channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.user = user  
        self.channel = channel

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, custom_id="close_ticket", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if not self.user or not self.channel:
                await interaction.response.send_message("> Please use the /close command to make sure a transcript will be generated.", ephemeral=True)
                return
            await interaction.response.send_message(f"This ticket has been closed by {interaction.user.mention}")
            await gentranscript(self.user, self.channel, interaction)
            await self.channel.delete()
        except Exception as e:
            await error(interaction, e)


class buyingmodal(ui.Modal, title="Buying Ticket"):
    product = ui.TextInput(label="Enter the product that you want to buy", placeholder="Ex: Fortnite Full Acess", style=discord.TextStyle.short)
    budget = ui.TextInput(label="Enter your budget", placeholder="20$", style=discord.TextStyle.short)
    region = ui.TextInput(label="Enter your region", placeholder="Europe", style=discord.TextStyle.short, required=True)
    payment = ui.TextInput(label="Enter your payment method", placeholder="Ltc, PayPal, etc", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            user = interaction.user
            guild = interaction.guild    
        
            nxt = config['ticketCount'] + 1
    
            #if len(category.channels) >= 50:
               # category = discord.utils.get(guild.categories, name="・─── ・Overflow Buying・─── ・")
                
            #channel3 = await guild.create_text_channel(f"buying-{nxt}", overwrites=overwrites, category=category)

            ticketsChannel = interaction.guild.get_channel(config['ticketChannel'])
            buyingThread = await ticketsChannel.create_thread(name=f"buying-{nxt}", type=discord.ChannelType.private_thread)
            await buyingThread.add_user(interaction.user)
            tijn = interaction.guild.get_member(1336046250809757789)
            await buyingThread.add_user(tijn)

            with open('assets/config/config.json', 'r') as f:
                crnt_nmber = json.load(f)

            crnt_nmber['ticketCount'] += 1
            
            with open('assets/config/config.json', 'w') as f:
                json.dump(crnt_nmber, f, indent=4)  
            config['ticketCount'] += 1
            thumbnail_url = interaction.guild.icon.url
    
            embed = discord.Embed(
                title="__**Buying Ticket**__",
                description=f"Thanks for creating a buying ticket {user.mention}. Please wait until our support team responds.",
                color=discord.Color(int("0x0016fa", 16))
            )
            embed.add_field(name="Product", value=f"```{self.product.value}```", inline=False)
            embed.add_field(name="Region", value=f"```{self.region.value}```", inline=False)
            embed.add_field(name="Payment", value=f"```{self.payment.value} - ${self.budget.value}```", inline=False)
            embed.set_thumbnail(url=thumbnail_url)
            embed.set_footer(icon_url=thumbnail_url, text=interaction.guild.name)
            
            view = CloseButton(user, buyingThread)
            await buyingThread.send(embed=embed, view=view)
            boi = await buyingThread.send(f"||{interaction.user.mention} <@&{config['ownerRole']}>||")
            await boi.delete()
    
            button = ui.Button(label="Ticket", url=f"https://discord.com/channels/{interaction.guild.id}/{buyingThread.id}")
            view2 = ui.View(timeout=None)
            view2.add_item(button)
            await interaction.response.send_message(embed=discord.Embed(title="__Ticket Created__", description="Buying ticket created, click the button below to enter your ticket channel."), view=view2, ephemeral=True)
        except Exception as e:
            await error(interaction, e)



class rewardmodal(ui.Modal, title="Reward Ticket"):
    sort = ui.TextInput(label="What are you claiming", placeholder="Drop / Reward", style=discord.TextStyle.short)
    prize = ui.TextInput(label="Enter your prize", placeholder="Verify reward", style=discord.TextStyle.short)
    region = ui.TextInput(label="Enter your region", placeholder="Europe", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):    
        try:
            user = interaction.user
            guild = interaction.guild    
            trial = interaction.guild.get_role(config['trial'])
        
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, attach_files=True, embed_links=True),
                user: discord.PermissionOverwrite(read_messages=True),
                trial: discord.PermissionOverwrite(read_messages=True)
            }
            category = discord.utils.get(guild.categories, name="・─── ・Rewards・─── ・")
    
            if len(category.channels) >= 50:
                category = discord.utils.get(guild.categories, name="・─── ・Overflow Reward・─── ・")
                
            channel2 = await guild.create_text_channel(f"reward-{user.name}", overwrites=overwrites, category=category)
            thumbnail_url = interaction.guild.icon.url
    
            embed = discord.Embed(
                title="__**Reward Ticket**__",
                description=f"Congrats on winning your reward {user.mention}! Please be patient for our staff to answer and __**DO NOT**__ ping our staff.",
                color=discord.Color(int("0x0016fa", 16))
            )
            embed.add_field(name="Prize:", value=f"```{self.prize.value}```")
            embed.add_field(name="Region:", value=f"```{self.region.value}```")
            embed.set_thumbnail(url=thumbnail_url)
            embed.set_footer(icon_url=thumbnail_url, text=interaction.guild.name)
        
            view = CloseButton(user, channel2)  
            await channel2.send(embed=embed, view=view)
    
            button = ui.Button(label="Ticket", url=f"https://discord.com/channels/{interaction.guild.id}/{channel2.id}")
            view2 = ui.View(timeout=None)
            view2.add_item(button)
            await interaction.response.send_message(embed=discord.Embed(title="__Ticket Created__", description="Reward ticket created, click the button below to enter your ticket channel."), view=view2, ephemeral=True)
        except Exception as e:
            await error(interaction, e)

class SupportModal(ui.Modal, title="Ticket"):
    problem = ui.TextInput(label="Enter the subject you need help with", placeholder="issue:", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            user = interaction.user
            guild = interaction.guild    
            trial = interaction.guild.get_role(config['trial'])
            
    
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, attach_files=True, embed_links=True),
                user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                trial: discord.PermissionOverwrite(read_messages=True)
            }
            category = discord.utils.get(guild.categories, name="・─── ・Support・─── ・")
    
            if len(category.channels) >= 50:
                category = discord.utils.get(guild.categories, name="・─── ・Overflow Support・─── ・")
    
            channel1 = await guild.create_text_channel(f"support-{user.name}", overwrites=overwrites, category=category)
            thumbnail_url = interaction.guild.icon.url
    
            embed = discord.Embed(
                title="__**Support Ticket**__",
                description=f"Thanks for creating a support ticket {user.mention}. Please wait until our support team responds.",
                color=discord.Color(int("0x0016fa", 16))
            )
            embed.add_field(name="Issue:", value=f"```{self.problem.value}```")
            embed.set_thumbnail(url=thumbnail_url)
            embed.set_footer(icon_url=thumbnail_url, text=interaction.guild.name)
            
            view = CloseButton(user, channel1)
        
            await channel1.send(embed=embed, view=view)
            button = ui.Button(label="Ticket", url=f"https://discord.com/channels/{interaction.guild.id}/{channel1.id}")
            view2 = ui.View(timeout=None)
            view2.add_item(button)
            await interaction.response.send_message(embed=discord.Embed(title="__Ticket Created__", description="Support ticket created, click the button below to enter your ticket channel."), view=view2, ephemeral=True)
        except Exception as e:
            await error(interaction, e)

class TicketType(discord.ui.Select):
    def __init__(self, **kwargs):
        super().__init__(placeholder="Select an option", options=[
            discord.SelectOption(label="Support", description="If you need help with something", emoji=emoji['question']),
            discord.SelectOption(label="Buying", description="If you want to buy something from us", emoji=emoji['buy']),
        ], **kwargs)

    async def callback(self, interaction: discord.Interaction):
        if self.values:
            ticket_type = self.values[0]
            if ticket_type == "Support":
                await interaction.response.send_modal(SupportModal())
            elif ticket_type == "Buying":
                await interaction.response.send_modal(buyingmodal())

        view = TicketEmbed()
        await interaction.message.edit(view=view)

class TicketEmbed(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketType(custom_id="ticket_type")) 

class TicketButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.buying_btn = discord.ui.Button(label="Buying", style=discord.ButtonStyle.blurple, custom_id="buying-btn", emoji=emoji['buy'])
        self.buying_btn.callback = self.buying_cb

        self.support_btn = discord.ui.Button(label="Support", style=discord.ButtonStyle.blurple, custom_id="support-btn", emoji=emoji['question'])
        self.support_btn.callback = self.support_cb


        self.add_item(self.buying_btn)
        self.add_item(self.support_btn)

    async def buying_cb(self, interaction: discord.Interaction):
        await interaction.response.send_modal(buyingmodal())

    async def support_cb(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SupportModal())


async def dropdown_tickets(interaction: discord.Interaction, channel: discord.TextChannel):    
    try:
        embed = discord.Embed(
            title="**__Tickets__**",
            description="> If you need help or if you want to buy something from us, select a ticket type from the dropdown menu and fill in the form.\n\n**- Reminder**\n> We are not online 24/7 so please be patient and wait for an answer.",
            color=discord.Color(int("0x0016fa", 16))
        )
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(icon_url=interaction.guild.icon.url, text=interaction.guild.name)
    
    
        view = TicketEmbed()
    
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Ticket embed sent, check out {channel.mention}.", ephemeral=True)
    except Exception as e:
        await error(interaction, e)



async def btn_tickets(interaction: discord.Interaction, channel: discord.TextChannel):
    try:
        embed = discord.Embed(
            title="**__Tickets__**",
            description="> If you need help or if you want to buy something from us, select a ticket type from the dropdown menu and fill in the form.\n\n**- Reminder**\n> We are not online 24/7 so please be patient and wait for an answer.",
            color=discord.Color(int("0x0016fa", 16))
        )
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(icon_url=interaction.guild.icon.url, text=interaction.guild.name)
    
        ticketbtnview = TicketButtonView()
    
        await channel.send(embed=embed, view=ticketbtnview)
        await interaction.response.send_message(f"Ticket embed sent, check out {channel.mention}.", ephemeral=True)
    except Exception as e:
        await error(interaction, e)

class Ticketss(commands.Cog):
    def  __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[+] Loaded tickets cog")

    
    @app_commands.command(name="ticket-embed", description="Send the ticket embed to the chosen channel")
    @app_commands.describe(type="Type of ticket", channel="The channel where you want the embed")
    @app_commands.choices(type=[
        discord.app_commands.Choice(name='Button-Embed', value='btn'),
        discord.app_commands.Choice(name='Dropdown-Embed', value='dropdwn')
    ])
    async def ticketss(self, interaction: discord.Interaction, type: str, channel: discord.TextChannel):
        try:
            if interaction.guild.get_role(config['ownerRole']) not in interaction.user.roles:
                await noPerms(interaction)
                return
        
            if type == 'btn':
                await btn_tickets(interaction, channel)
            elif type == 'dropdwn':
                await dropdown_tickets(interaction, channel)
            else:
                await interaction.response.send_message("Invalid option selected.", ephemeral=True)
        except Exception as e:
            await error(interaction, e)

    @app_commands.command(name="close", description="Close a ticket channel")
    async def closeslash(self, interaction: discord.Interaction):
        try:
            if interaction.guild.get_role(config['trial']) not in interaction.user.roles:
                await noPerms(interaction)
                return
    
            channel_name = interaction.channel.name
            allowed_prefixes = ["support-", "reward-", "buying-"]
    
            if not any(channel_name.startswith(prefix) for prefix in allowed_prefixes):
                await interaction.response.send_message(f"{emoji['error']} | This is not a ticket channel", ephemeral=True)
                return
    
            export = await chat_exporter.export(channel=interaction.channel)
            
            name = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(30))
            file_name = f"{name}-{interaction.user.name}-transcript.html"
            file_path = os.path.join(os.getcwd(), file_name)
    
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(export)
    
            try:
                ftp = ftplib.FTP('snowymarket.cc')
                ftp.login('snowyma1', '0ttj7f9QL5')
                ftp.cwd('/public_html')
    
                try:
                    ftp.mkd('transcripts')
                except ftplib.error_perm:
                    pass
    
                ftp.cwd('transcripts')
    
                with open(file_path, 'rb') as file:
                    ftp.storbinary(f'STOR {file_name}', file)
                ftp.quit()
            except ftplib.all_errors as e:
                print(f"FTP error: {e}")
    
            os.remove(file_path)
    
            transcript_url = f"https://snowymarket.cc/transcripts/{file_name}"
    
    
            transcriptChannel = interaction.guild.get_channel(config['transcriptChannel'])
            embed = discord.Embed(
                title="__Ticket Closed__",
                description=f"Ticket `{interaction.channel.name}` has been closed by {interaction.user.mention}.",
                color=discord.Color(int("0x0016fa", 16))
            )
            embed.add_field(name="Transcript", value=f"[View Transcript]({transcript_url})")
            await transcriptChannel.send(embed=embed)
            await interaction.response.send_message(f"Ticket closed by {interaction.user.mention}")
            await interaction.channel.delete()
        except Exception as e:
            await error(interaction, e)
      
    
    
    @app_commands.command(name="close-all", description="Close all ticket channels")
    async def closeall(self, interaction: discord.Interaction):
        if interaction.guild.get_role(config['ceo']) not in interaction.user.roles:
            await noPerms(interaction)
            return
    
        all_channels = interaction.guild.channels
        prefixes_to_close = ["reward-", "buying-", "support-"]
    
        for channel in all_channels:
            if isinstance(channel, discord.TextChannel) and any(channel.name.startswith(prefix) for prefix in prefixes_to_close):
                await channel.delete()
    
    
        return await interaction.response.send_message(f"{emoji['checkmark']} | Successfully closed all ticket channels.", ephemeral=True)
    
async def setup(client):
    await client.add_cog(Ticketss(client))