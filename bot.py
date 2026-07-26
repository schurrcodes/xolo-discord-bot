import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import sys

load_dotenv()
token = os.getenv("BOT_TOKEN")

# Handler for Logging. Output in bot.log with UTF-8 encoding and only write.
file_handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
console_handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(
    level=logging.INFO, handlers=[file_handler, console_handler]
)
intents=discord.Intents.default()
intents.message_content=True
intents.members=True # Text and Poll Payloads

# Def Bot instances/intents
bot = commands.Bot(command_prefix="!", intents=intents)

# When Ready, Bot Syncs commands to Discord Servers
@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name}") #Changed bot.user to bot.user.name
    try:
        synced=await bot.tree.sync()
        logging.info(f"Synced {len(synced)} commands.")
    except Exception as e:
        logging.exception(f"Failed to sync commands: {e}")

# Ping command that replies with Pong! (Future: Will add latency in ms)
@bot.tree.command(name="ping", description="Replies with Pong!")
async def ping(interaction: discord.Interaction):
    try:
        logging.info(f"{interaction.user} used /ping")
        await interaction.response.send_message("Pong!")
    except Exception as e:
        logging.exception(e)

# Greeting command that replies with Hello and mentions the user who used the command.
@bot.tree.command(name="greet", description="Replies with Hello!")
async def greet(interaction: discord.Interaction):
    try:
        logging.info(f"{interaction.user} used /greet")
        await interaction.response.send_message(f"Hello {interaction.user.mention}")
    except Exception as e:
        logging.exception(e)

# Command to give userinfo about the user who used the command.
@bot.tree.command(name="userinfo", description="Gives info about the user who used the command.")
async def userinfo(interaction: discord.Interaction):
    try:
        logging.info(f"{interaction.user} used /userinfo") # Log user interaction
        user = interaction.user # Get the user who used the command
        embed = discord.Embed(title=f"User Info for {user.name}", color=discord.Color.blue())
        embed.add_field(name="Username", value=user.name, inline=True) # username of the user
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True) #When the user joined the server
        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)  #When was user's discord account created

        roles = [role.name for role in user.roles if role.name != "@everyone"] # Get all roles of the user except @everyone
        embed.add_field(name="Roles",value=", ".join(roles) if roles else "No Roles", inline=False) # If user has no roles, display No Roles

        # Display user's avatar and display name
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=f"Display Name: {user.display_name}")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        logging.exception(e)
  
# Command to give serverinfo about the server
@bot.tree.command(name="serverinfo", description="Gives info about the server.")
async def serverinfo(interaction: discord.Interaction):
    try:
        logging.info(f"{interaction.user} used /serverinfo") # Log user interaction
        guild = interaction.guild # Get the guild (server) where the command was used.
        embed = discord.Embed(title=f"Server Info for {guild.name}", color=discord.Color.blue())
        embed.add_field(name="Server Icon", value=guild.icon.url, inline=True) # Display server icon
        embed.add_field(name="Server Name", value=guild.name, inline=True) # Display server name
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Server Owner", value=guild.owner, inline=True) # Display server owner
        embed.add_field(name="Server Created At", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S")) # Display server creation date 
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        logging.exception(e)

#----------------------------------
# Officer/Permission Based Commands 
#----------------------------------

# =============================
# GIVE ROLE COMMAND
# A command that gives a role to the user.
# =============================
@bot.tree.command(name="giverole", description="Gives a role to a user.")
@app_commands.default_permissions(manage_roles=True)
@app_commands.checks.has_permissions(manage_roles=True)
async def giverole(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    try:
        if (interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.manage_roles):
            # Check if the user already has the role
            if role in user.roles:
                await interaction.response.send_message(f"{user.name} already has the role {role.name}", ephemeral=True)
                return
            try:
                await user.add_roles(role) # add the role to the user 
            except discord.Forbidden:
                await interaction.response.send_message(f"Failed to give {role.name} to {user.name}. I may not have permission to manage that role.", ephemeral=True)

            logging.info(f"{interaction.user} with role {interaction.user.top_role.name} used /giverole to give {role.name} to {user.name}") # Log user interaction
            await interaction.response.send_message(f"Gave {role.name} to {user.name}", ephemeral=True)
        else:
            logging.info(f"{interaction.user} with role {interaction.user.top_role.name} tried to use /giverole to give {role.name} to {user.name} but does not have permission.") # Log the user interaction
            await interaction.response.send_message(f"You do not have permission to use that command.", ephemeral=True)
    except Exception as e:
        logging.exception(e)

# =============================
# REMOVE ROLE COMMAND
# A command that removes a role from user.
# =============================
@bot.tree.command(name="removerole", description="Removes a role from a user.")
@app_commands.default_permissions(manage_roles=True)
@app_commands.checks.has_permissions(manage_roles=True)
async def removerole(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    try:
        if (interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.manage_roles):
            # Check if the user has the role
            if role not in user.roles:
                await interaction.response.send_message(f"{user.name} does not have the role {role.name}. No need to remove.", ephemeral=True)
                return
            try:
                await user.remove_roles(role) # built-in function that removes the role from the user
            except discord.Forbidden:
                await interaction.response.send_message(f"Failed to remove {role.name} from {user.name}. I may not have permission to manage that role.", ephemeral=True)
            logging.info(f"{interaction.user} with role {interaction.user.top_role.name} used /removerole to remove {role.name} from {user.name}") # Log user interaction
            await interaction.response.send_message(f"Removed {role.name} from {user.name}", ephemeral=True)
        else:
            logging.info(f"{interaction.user} with role {interaction.user.top_role.name} tried to use /removerole to remove {role.name} from {user.name} but does not have permission.") # Log user interaction
            await interaction.response.send_message(f"You do not have permission to use that command.", ephemeral=True)
    except Exception as e:
        logging.exception(e)

# =============================
# EMBED COMMAND
# A command that embeds a message.(FUTURE: add markdown file parameter, let it write down the text below)
# =============================
@bot.tree.command(name="embed", description="Embeds a message in the server.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.checks.has_permissions(manage_messages=True)
async def embed(interaction: discord.Interaction, title: str, description: str):
    try:
        if (interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.manage_messages):
            embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
            logging.info(f"{interaction.user} with role {interaction.user.top_role.name} used /embed with title: {title} and description: {description}")
            await interaction.response.send_message(embed=embed)
        else:
            logging.info(f"{interaction.user} with role {interaction.user.top_role.name} tried to use /embed with title: {title} and description: {description} but does not have permission.")
            await interaction.response.send_message("You do not have permission to use that command.", ephemeral=True)
    except Exception as e:
        logging.exception(e)

# =============================
# SAY COMMAND
# A command that repeats a message (Future: Add message saves).
# =============================
@bot.tree.command(name="say", description="Repeats what the user says.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.checks.has_permissions(manage_messages=True)
async def say(interaction: discord.Interaction, message: str):
    # Search roles with specific permissions 
    # e.g., (Administrator, Manage Messages specifically) 
    # and check if the user has any of those roles. 
    # If yes, allow the command to be used. 
    # If Possible Don't show the command to users who don't have the required permissions.

    try:
        if (interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.manage_messages):
            logging.info(f"{interaction.user} with role {interaction.user.top_role.name} used /say with message: {message}") # Log user interaction
            await interaction.response.send_message(message)
        else:
            logging.info(f"{interaction.user} with role {interaction.user.top_role.name} tried to use /say with message: {message} but does not have permission.") # Log the user interaction
            await interaction.response.send_message("You do not have permission to use that command.", ephemeral=True)
    except Exception as e:
        logging.exception(e)

# Command that deletes a certain number of messages in the channel.

# Command that creates a poll in the server with a quesiton and up to 5 options. The user can vote by reacting to the message with the corresponding emoji.

# =============================
# KICK COMMAND
# A command that kicks the user from the server.
# =============================
@bot.tree.command(name="kick", description="Kicks a user from the server.")
@app_commands.default_permissions(kick_members=True) # This decorator ensures that only users with the kick_members permission can use this command.
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str=None):
    try:
        if (interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.kick_members):
            try:
                await user.kick(reason=reason) # build-in function that kicks the user from the server
                logging.info(f"{interaction.user} with role {interaction.user.top_role.name} used /kick to kick {user.name} for reason: {reason}") # Log user interaction
                await interaction.response.send_message(f"Kicked {user.name} from the server for reason: {reason}", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message(f"Failed to kick {user.name}. I may not have permission to kick that user.", ephemeral=True)
        else:
            logging.info(f"{interaction.user} with role {interaction.user.top_role.name} tried to use /kick to kick {user.name} for reason: {reason} but does not have permission.") # Log user interaction
            await interaction.response.send_message("You do not have permission to use that command.", ephemeral=True)
    except Exception as e:
        logging.exception(e)

# =============================
# BAN COMMAND
# A command that bans the user from the server.
# =============================
@bot.tree.command(name="ban", description="Bans a user from the server.")
@app_commands.default_permissions(ban_members=True)# This decorator ensures that only users with banning permissions can use this command
@app_commands.checks.has_permissions(ban_members=True) # Backend shield for bypassing UI
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str=None):
    # Prevent banning youself
    if user == interaction.user:
        await interaction.response.send_message("You cannot ban yourself.", ephemeral=True)

    # Checks if the bot is trying to ban someone higher or equal in role hierarchry
    if interaction.guild.me.top_role <= user.top_role:
        await interaction.response.send_message(f"Failed to ban {user.name}. My highest role is not high enough.", ephemeral=True)
        return

    try:
        # Ban the specific user
        await user.ban(reason=reason)
        logging.info(f"{interaction.user} with role {interaction.user.top_role.name} used /ban to ban {user.name} for reason: {reason}")
        await interaction.response.send_message(f"Banned {user.name} from the server for reason: {reason}", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"Failed to ban {user.name}. I do not have permission to ban this user.", ephemeral=True)
    except Exception as e:
        logging.exception(e)

# =============================
# UNBAN COMMAND
# A command that unbans user from the server.
# =============================
@bot.tree.command(name="unban", description="Unbans a user from the server.")
@app_commands.default_permissions(ban_members=True)# This decorator ensures that only users with banning permissions can use this command
@app_commands.checks.has_permissions(ban_members=True) # Backend Shield for Bypassing UI in case
async def unban(interaction: discord.Interaction, user: discord.User):
    try:
       await interaction.guild.unban(user)
       logging.info(f"{interaction.user} with role {interaction.user.top_role.name} used /unban to unban {user.name}")
       await interaction.response.send_message(f"Unbanned {user.name} from the server.", ephemeral=True)
    except discord.NotFound:
        await interaction.response.send_message(f"That user is not currently banned or doesn't exist", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"Failed to unban {user.name}. I do not have permission to unban users.", ephemeral=True)
    except Exception as e:
        logging.exception(e)

# Command that mutes a user in the server.

# Command that unmutes a user in the server.

# Command that warns a user in the server.

# Command that shows the warnings of a user in the server.

# Command that clears the warnings of a user in the server.

# --------------------------------
# Club Purpose Commands WITH Permission Checks
# --------------------------------

# Command that announces certain messages in the server similar to embed but with more parameters
@bot.tree.command(name="announce", description="Announces a message in the server.")
@app_commands.default_permissions(manage_messages=True)
async def announce(interaction: discord.Interaction, title: str, meeting: str, description: str, section1: str, section2: str=None, section3: str=None, color: str="#0000FF"):
    try:
        if (interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.manage_messages):
            color = int(color.replace("#", ""), 16) # convert hex color to int
            # Check if the color input is a valid hex color code (between 0x000000 and 0xFFFFFF)
            if (color < 0 or color > 0xFFFFFF):
                await interaction.response.send_message("Invalid color. Please provide a valid hex color code.", ephemeral=True)
                return
            embed = discord.Embed(title=title, description=description, color=color)
            embed.add_field(name="Meeting Information", value=meeting, inline=False)
            # -------------------------------------------
            # Add additional sections if they are provided
            # -------------------------------------------
            if section1:
                embed.add_field(name="", value=section1, inline=False)
            if section2:
                embed.add_field(name="", value=section2, inline=False)
            if section3:
                embed.add_field(name="", value=section3, inline=False)

            logging.info(f"{interaction.user} with role {interaction.user.top_role.name} used /announce with title: {title}, meeting: {meeting}, description: {description}, section1: {section1}, section2: {section2}, section3: {section3}, color: {color}")
            await interaction.response.send_message(embed=embed)
        else:
            logging.info(f"{interaction.user} with role {interaction.user.top_role.name} tried to use /announce with title: {title}, meeting: {meeting}, description: {description}, section1: {section1}, section2: {section2}, section3: {section3}, color: {color} but does not have permission.")
            await interaction.response.send_message("You do not have permission to use that command.", ephemeral=True)
    except Exception as e:
        logging.exception(e)

# =============================
# GLOBAL ERROR HANDLES
# =============================
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        # Log the failed attempt 
        logging.info(f"{interaction.user} with id: ({interaction.user.id})with the role {interaction.user.top_role.name} tried to use /{interaction.command.name} but lacked permissions.")
        # Tell the user that they don't have permissions
        await interaction.response.send_message("You do not have permission to use that command", ephemeral=True)
    else:
        # Fall back for another unexpected slash command
        logging.error(f"Unhandled command error: {error}")

# =============================
# OWNER CHECK
# =============================

def is_owner():
    async def predicate(interaction: discord.Interaction) -> bool:
        return bot.is_owner(interaction.user)
    return app_commands.check(predicate)

# =============================
# SYNCING COMMANDS
# Only permissible to bot owner
# =============================
@bot.tree.command(name="sync", description="Syncs the bot commands. Only bot owner can use this command.")
@is_owner() # This decorator ensures that only the bot owner can use this command.
async def sync(interaction: discord.Interaction):
    try:
        synced = await bot.tree.sync()
        logging.info(f"{interaction.user} used /sync to sync {len(synced)} commands.")
        await interaction.response.send_message(f"Synced {len(synced)} commands.", ephemeral=True)
    except Exception as e:
        logging.exception(e)
# =============================
# EXECUTE BOT
# =============================
bot.run(token)