import discord, json
from discord.ext import commands
from discord import app_commands, ui
from assets.logger import noPerms, error

with open('assets/config/config.json', 'r') as f:
    config = json.load(f)

with open('assets/config/emojis.json', 'r') as f:
    emoji = json.load(f)

class ApplyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(style=discord.ButtonStyle.blurple, label="Apply", emoji=emoji['checkmark'], custom_id="apply-button")
    async def apply_button(self, interaction: discord.Interaction, Button: discord.Button):
        await interaction.response.send_modal(applymodal())

class applymodal(ui.Modal, title="Staf Application"): #x9 code
    age = ui.TextInput(label="What is your age", style=discord.TextStyle.short, max_length=2)
    timezone = ui.TextInput(label="What is your timezone", placeholder="Ex: GMT+2", style=discord.TextStyle.short)
    combos = ui.TextInput(label="Do you have any combos/logs", style=discord.TextStyle.short)
    experience = ui.TextInput(label="Do you have any experience", style=discord.TextStyle.short, min_length=10)
    other = ui.TextInput(label="What makes you stand out from others", style=discord.TextStyle.long, min_length=40)

    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user
        management_role = interaction.guild.get_role(config['management'])
        trial_staff = interaction.guild.get_role(config['trial'])

        class DecideButtons(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
            @discord.ui.button(style=discord.ButtonStyle.green, label="Accept", emoji=emoji['checkmark'])
            async def accept_button(self, interaction:discord.Interaction, Button: discord.Button):
                if management_role in interaction.user.roles:
                    if trial_staff not in user.roles:
                        try:
                            await user.add_roles(trial_staff)
                        except Exception as e:
                            await error(interaction, e)
                            return
                        await user.send(embed=discord.Embed(title="__Application Accepted__", description=f"Congrats, we decided to add you to our staff team. You should've received the staff role in our server, please check out the <#1180507830881632277>.", color=discord.Color.green()))
                        await interaction.response.send_message(embed=discord.Embed(description=f"{user.mention}'s application has been accepted by {interaction.user.mention}", color=discord.Color.green()))
                        view_accepted = discord.ui.View()
                        accepted_button = discord.ui.Button(style=discord.ButtonStyle.green, label=f"Application Accepted by {interaction.user.name}", emoji=emoji['checkmark'], disabled=True)
                        view_accepted.add_item(accepted_button)
                        await interaction.message.edit(view=view_accepted)
                    else:
                        await interaction.response.send_message(embed=discord.Embed(description=f"**{user.mention} already has the staff role!**", color=discord.Color.red()))            
                else:
                    await noPerms(interaction)
            @discord.ui.button(style=discord.ButtonStyle.red, label="Decline", emoji=emoji['error'])
            async def deny_button(self, interaction:discord.Interaction, Button: discord.Button):
                if management_role in interaction.user.roles:
                    await user.send(embed=discord.Embed(title="__Application Declined__", description=f"Unfortunatly we decided to not accept you in our staff team, please wait till the next round opens and you will be able to try again.", color=discord.Color.red()))
                    await interaction.response.send_message(embed=discord.Embed(description=f"{user.mention}'s application has been declined by {interaction.user.mention}", color=discord.Color.red()))
                    view_declined = discord.ui.View()
                    declined_button = discord.ui.Button(style=discord.ButtonStyle.red, label=f"Application declined by {interaction.user.name}", emoji=emoji['error'], disabled=True)
                    view_declined.add_item(declined_button)
                    await interaction.message.edit(view=view_declined)
                else:
                    await noPerms(interaction)
        app_embed = discord.Embed(title=f"{interaction.user}'s Application.", description=f"**Answers:**\n\n**Enter your age**\n- {self.age}\n\n**Do you have any experience?**\n- {self.experience}\n\n**What is your timezone**\n- {self.timezone}\n\n**Do you have any combo's, logs or methods**\n- {self.combos}\n\n**What makes you stand out from other**\n- {self.other}", color=discord.Color(int("0x0016fa", 16)))
        
        application_channel_id = config['staffappAppsChannel']
        application_channel = interaction.guild.get_channel(application_channel_id)
        await interaction.response.send_message(embed=discord.Embed(description="**Successfully applied, please check your private messages.**", color=discord.Color.green()), ephemeral=True)
        await interaction.user.send(embed=discord.Embed(title="__Applied successfully__", description=f"Successfully applied for the staff role. Please be patient and wait till our bot sends you a message back, this usually takes around 1-3 business days.", color=discord.Color(int("0x0016fa", 16))))
        await application_channel.send(embed=app_embed, view=DecideButtons())

class Staff(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('[+] Loaded staff cog')

    @app_commands.command(name='give-gen', description='Give the generator role to a specific person')
    @app_commands.describe(type='Generator type that you want to give access to', user='The user you want to give access')
    @app_commands.choices(type=[
        discord.app_commands.Choice(name='Free-generator', value='freegen'),
        discord.app_commands.Choice(name='Invite-generator', value='invgen')
    ])
    async def giveGen(self, interaction: discord.Interaction, type: str, user: discord.User):
        try:
            if interaction.guild.get_role(config['trial']) not in interaction.user.roles:
                await noPerms(interaction)
                return
            
            if type == 'freegen':
                name = "Free Generator"
                id = config['freegen-role']

            elif type == 'invgen':
                name = "Invite Generator"
                id = config['invgen-role']

            genRole = interaction.guild.get_role(id)
            await user.add_roles(genRole)
            await interaction.response.send_message(f"{emoji['checkmark']} | Successfully gave {user.mention} access to the {name}.")
        except Exception as e:
            await error(interaction, e)

    @app_commands.command(name="ban", description="Ban a user in the discord")
    @app_commands.describe(user="The user you want to ban", reason="Reason of the ban")
    async def bancmd(self, interaction: discord.Interaction, user: discord.User, reason: str):
        if interaction.user.guild_permissions.ban_members is False:
            await noPerms(interaction)
            return
    
        if max(role.position for role in interaction.user.roles) <= max(role.position for role in user.roles):
            await interaction.response.send_message(f"{emoji['error']} | You can only ban users with a role lower than yours.", ephemeral=True)
            return
    
        await user.ban(reason=reason)
        await interaction.response.send_message(f"{emoji['checkmark']}| Successfully banned {user.mention}.")
    
    
    @app_commands.command(name="kick", description="kick a user in the discord")
    @app_commands.describe(reason="Reason for the kick")
    async def kickcmd(self, interaction: discord.Interaction, user: discord.User, reason: str):
        if interaction.user.guild_permissions.kick_members is False:
            await noPerms(interaction) 
            return
    
        await user.kick(reason=reason) 
        await interaction.response.send_message(f"{emoji['checkmark']}| Successfully kicked {user.mention}.")


    @app_commands.command(name="staff-app", description="Send the staff application embed")
    @app_commands.describe(channel="The channel you want to send it to")
    async def staffapp(self, interaction: discord.Interaction, channel: discord.TextChannel):
        try:
            if interaction.guild.get_role(config['ceo']) not in interaction.user.roles:
                await noPerms(interaction)
                return
            embed = discord.Embed(
                title="__Staff Application__",
                description="**> To apply to our staff team you must fill out a form. The form will pop up once you click the 'apply' button. make sure to be serious for the highest accept rate**\n\n**> Please be patient and dont ping our staff for updates, we usually take around 1-3 business days to check all app applications**",
                color=discord.Color(int("0x0016fa", 16))
            )
            embed.set_thumbnail(url=interaction.guild.icon.url)
            embed.set_footer(icon_url=interaction.guild.icon.url, text=interaction.guild.name)
            await channel.send(embed=embed, view=ApplyButton())
            await interaction.response.send_message("Successfully sent the embed", ephemeral=True)
        except Exception as e:
            await error(interaction, e)
    
@app_commands.context_menu(name="Ban")
async def ctxban(interaction: discord.Interaction, member: discord.Member):
    if interaction.user.guild_permissions.administrator is False:
        await noPerms(interaction)
        return
    
    if max(role.position for role in interaction.user.roles) <= max(role.position for role in member.roles):
        await interaction.response.send_message(f"{emoji['error']} | You can only ban users with a role lower than yours.", ephemeral=True)
        return 
    
    if member == interaction.user:
        await interaction.response.send_message("You cannot ban yourself")
        return
    
    await member.ban()
    await interaction.response.send_message(f"{emoji['checkmark']} | Sucessfully banned {member.mention}")

@app_commands.context_menu(name="Kick")
async def ctxkick(interaction: discord.Interaction, member: discord.Member):
    if interaction.user.guild_permissions.administrator is False:
        await interaction.response.send_message("You are not allowed to use this")
        return
    
    if max(role.position for role in interaction.user.roles) <= max(role.position for role in member.roles):
        await interaction.response.send_message(f"{emoji['error']} | You can only kick users with a role lower than yours.", ephemeral=True)
        return 
    
    if member == interaction.user:
        await interaction.response.send_message("You cannot kick yourself")
        return
    
    await member.kick()
    await interaction.response.send_message(f"{emoji['checkmark']} | Sucessfully kicked {member.mention}")


@app_commands.context_menu(name="Close Applications")
async def closeapps(interaction: discord.Interaction, message: discord.Message):
    try:
        if interaction.user.guild_permissions.administrator is False:
            await noPerms(interaction)
            return
        
        if not message.embeds or message.embeds[0].title != "__Staff Application__":
            await interaction.response.send_message("Please select the staff applications embed", ephemeral=True)
            return
    
        await message.delete()
    
        embed = discord.Embed(
                title="__Staff Application__",
                description="**> To apply to our staff team you must fill out a form. The form will pop up once you click the 'apply' button. make sure to be serious for the highest accept rate**\n\n**> Please be patient and dont ping our staff for updates, we usually take around 1-3 business days to check all app applications**",
                color=discord.Color(int("0x0016fa", 16))
        )
        button = ui.Button(label="Apply", style=discord.ButtonStyle.blurple, emoji=emoji['checkmark'], disabled=True)
    
        view = ui.View()
        view.add_item(button)
    
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(icon_url=interaction.guild.icon.url, text=interaction.guild.name)
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("Succesfully closed the applications", ephemeral=True)
    except Exception as e:
        await error(interaction, e)

@app_commands.context_menu(name="Open Applications")
async def openapps(interaction: discord.Interaction, message: discord.Message):
    try:
        if interaction.user.guild_permissions.administrator is False:
            noPerms(interaction)
            return
        
        if not message.embeds or message.embeds[0].title != "__Staff Application__":
            await interaction.response.send_message("Please select the staff applications embed", ephemeral=True)
            return
        
        await message.delete()
        embed = discord.Embed(
            title="__Staff Application__",
            description="**> To apply to our staff team you must fill out a form. The form will pop up once you click the 'apply' button. make sure to be serious for the highest accept rate**\n\n**> Please be patient and dont ping our staff for updates, we usually take around 1-3 business days to check all app applications**",
            color=discord.Color(int("0x0016fa", 16))
        )
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(icon_url=interaction.guild.icon.url, text=interaction.guild.name)
        await interaction.channel.send(embed=embed, view=ApplyButton())
        await interaction.response.send_message("Sucessfully re-opened the staff apps", ephemeral=True)
    except Exception as e:
        await error(interaction, e)


async def setup(client):
    await client.add_cog(Staff(client))
    client.tree.add_command(ctxban)
    client.tree.add_command(ctxkick)
    client.tree.add_command(openapps)
    client.tree.add_command(closeapps)