import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import datetime
from datetime import datetime, timezone, timedelta
import json
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

# =============================
# JSON STORAGE HELPER
# =============================

DATA_FILES = ["saved_messages.json", "warnings.json"] # STORE SAVE MESSAGES IN JSON

# Loads saved messages within the DATA_FILES by reading
def load_saved_messages() -> dict:
    if not os.path.exists(DATA_FILES[0]):
        return {}
    try:
        with open(DATA_FILES[0], "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
    
# Saves/Writes user message into DATA_FILES
def save_user_message(user_id: int, message: str):
    data = load_saved_messages()
    data[str(user_id)] = message
    with open(DATA_FILES[0], "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Loads warnings from the DATA file by reading
def load_warnings() -> dict:
    if not os.path.exists(DATA_FILES[1]):
        return {}
    try:
        with open(DATA_FILES[1], "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

# Saves the warnings dictionary back into the DATA_FILE
def save_warnings(data: dict):
    with open(DATA_FILES[1], "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
# =============================
# DURATION CONVERSION HELPER
#==============================
def parse_duration(duration_str: str) -> int | None:
    # Parse durations string 60s, 30m, 2h into seconds
    # Check for empty strings, missing values, and non string inputs
    if not duration_str or not isinstance(duration_str, str):
        return None
    duration_str = duration_str.strip()
    if len(duration_str) < 2:
        return None

    # Extract unit and numerical value safely
    unit = duration_str[-1].lower()
    number_part = duration_str[:-1]

    if not number_part.isdigit():
        return None
    
    value = int(number_part)

    # Return converted seconds based on unit
    if unit == 's':
        return value
    elif unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400

    return None

# =============================
# DATETIME Utilities
# =============================
def calculate_timout(seconds: int | float) -> datetime:
    """ safely calculates a future utc timeout using standard datetime. """
    # Guard against non numeric or wrong types
    if not isinstance(seconds, (int, float)):
        return None
    # Guard against negative or wrong time steps
    if seconds <= 0:
        raise ValueError("Timeout duration cannot be negative.")

    # Return the standard datetime calculation
    return datetime.now(timezone.utc) + timedelta(seconds=seconds)

# =============================
# PING COMMAND
# A command that replies with Pong! (Future: will add latency in ms).
# =============================

@bot.tree.command(name="ping", description="Replies with Pong!")
async def ping(interaction: discord.Interaction):
    try:
        logging.info(f"{interaction.user} used /ping")
        await interaction.response.send_message("Pong!")
    except Exception as e:
        logging.exception(e)

# =============================
# GREET COMMAND
# A command that that replies with Hello and mentions the user who used the command.
# =============================

@bot.tree.command(name="greet", description="Replies with Hello!")
async def greet(interaction: discord.Interaction):
    try:
        logging.info(f"{interaction.user} used /greet")
        await interaction.response.send_message(f"Hello {interaction.user.mention}")
    except Exception as e:
        logging.exception(e)

# =============================
# USER INFO COMMAND
# A command to give user info about the user who used the command.
# =============================

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

# =============================
# SERVER INFO COMMAND
# A command to give server info about the server.
# =============================

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
@bot.tree.command(name="say", description="Repeats a message or sends your saved default message.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(message="The message to send (optional): leave blank to send your saved default message")
async def say(interaction: discord.Interaction, message: str | None=None):
    user_id_str = str(interaction.user.id)
    saved_data = load_saved_messages()
    # If the user provided a new message -> update saved message and prep to send
    if message:
        save_user_message(interaction.user.id, message) # Saves new user message
        text_to_send=message
    # If the user didn't provide a message -> use their saved message
    elif user_id_str in saved_data:
        text_to_send = saved_data[user_id_str]
    # If the user didn't provide a message and no saved message exists -> warning
    else:
        await interaction.response.send_message("You do not have a saved message yet. Please provide a message parameter first.", ephemeral=True)
        return
    try:
        # send the message to the channel publicly
        await interaction.channel.send(text_to_send)
        logging.info(
            f"{interaction.user} ({interaction.user.id}) with role {interaction.user.top_role.name} "
            f"used /say with message: {text_to_send}"
        )

        await interaction.response.send_message("Message has been sent.", ephemeral=True)
    except discord.Forbidden:
        if not interaction.response.is_done():
            await interaction.response.send_message("I do not have permissions to send messages in this channel.", ephemeral=True)
        else:
            await interaction.followup.send(
                "Failed to send message. Missing permissions.", 
                ephemeral=True
            )
    except Exception as e:
        logging.exception(e)
        if not interaction.response.is_done():
            await interaction.response.send_message("Some error has occurred while processing the command.", ephemeral=True)

# =============================
# CLEAR COMMAND
# A command that clears between 1 to 100 messages, that are no longer than 14 days old.
# =============================
@bot.tree.command(name="clear", description="Deletes a specificed number of messages from the channel.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(amount="The number of messages to delete (1-100)")
async def clear(interaction: discord.Interaction, amount: int):
    # Check amount limits
    if amount < 1 or amount > 100:
        await interaction.response.send_message("Please provide a number between 1 and 100.", ephemeral=True)
        return
    # Defer the interaction immediately to give the bot time to clear messages.
    await interaction.response.defer(ephemeral=True)

    try:
        # Bulk delete msgs
        deleted = await interaction.channel.purge(limit=amount)
        logging.info(f"{interaction.user} ({interaction.user.id}) cleared {len(deleted)} messages in #{interaction.channel.name}")
        await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("Failed to delete messages. I don't have the permission to run this command.", ephemeral=True)
    except discord.HTTPException as e:
        # return error if trying to bulk delete msgs older than 14 days.
        logging.error(f"Error purging messages: {e}")
        await interaction.followup.send("Failed to delete messages. Note: Discord does not allow bulk deleting messages older than 14 days.", ephemeral=True) 
    except Exception as e:
        logging.exception(e)
        if not interaction.response.is_done():
            await interaction.response.send_message("Some error has occurred while processing the command.", ephemeral=True)

# =============================
# POLL COMMAND
# Command that creates a poll in the server with a quesiton and up to 10 options.
# =============================

@bot.tree.command(name="poll", description="Creates a Discord poll (Up to 10 options).")
@app_commands.default_permissions(create_polls=True)
@app_commands.checks.has_permissions(create_polls=True)
@app_commands.describe(
    question="The poll question",
    option1="First option",
    option2="Second option",
    option3="Third option",
    option4="Fourth option",
    option5="Fifth option",
    option6="Sixth option",
    option7="Seventh option",
    option8="Eighth option",
    option9="Ninth option",
    option10="Tenth option",
    duration="How long the poll lasts in hours (default: 24)",
    multiple="Allow users to select multiple answers? (default: false)"
)
async def poll(
    interaction: discord.Interaction,
    question: str,
    option1: str,
    option2: str,
    option3: str | None=None,
    option4: str | None=None,
    option5: str | None=None,
    option6: str | None=None,
    option7: str | None=None,
    option8: str | None=None,
    option9: str | None=None,
    option10: str | None=None,
    duration: int | None=24,
    multiple: bool | None=False
):

    try:
        # Gather non-empty options intoa list
        raw_options = [option1, option2, option3, option4, option5, option6, option7, option8, option9, option10]
        options = [opt for opt in raw_options if opt is not None]
    
        # create a Discord poll object
        pollObj = discord.Poll(question=question, duration=datetime.timedelta(hours=duration), multiple=multiple)
    
        # Add the provided answers
        for opt in options:
            pollObj.add_answer(text=opt)
    
        logging.info(f"{interaction.user} ({interaction.user.id}) with role {interaction.user.top_role.name} has used /poll.")
    
        # Send confirmation to the command user and post the poll into the channel
        await interaction.response.send_message("Poll has been created.", ephemeral=True)
        await interaction.channel.send(poll=pollObj)
    except Exception as e:
        logging.exception(e)
        if not interaction.response.is_done():
            await interaction.response.send_message("Some error has occurred while processing the command.", ephemeral=True)

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
        if not interaction.response.is_done():
            await interaction.response.send_message("Some error has occurred while processing the command.", ephemeral=True)

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
        return

    # Checks if the bot is trying to ban someone higher or equal in role hierarchry
    if interaction.guild.me.top_role <= user.top_role:
        await interaction.response.send_message(f"Failed to ban {user.name}. My highest role is not high enough.", ephemeral=True)
        return

    # Check moderator role hierarchy to prevent banning higher/equal ranks
    if interaction.user != interaction.guild.owner and interaction.user.top_roles <= user.top_role:
        await interaction.response.send_message(f"Failed to ban {user.name}. You cannot ban someone with an equal or higher role than you.", ephemeral=True)
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
        if not interaction.response.is_done():
            await interaction.response.send_message("Some error has occurred while processing the command.", ephemeral=True)

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
        if not interaction.response.is_done():
            await interaction.response.send_message("Some error has occured while processing the command.",ephemeral=True)

# =============================
# MUTE COMMAND
# =============================
@bot.tree.command(name="mute", description="Timesout/Mutes a user from text/voice channels.")
@app_commands.default_permissions(moderate_members=True)
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.describe(
    user="The user to mute",
    duration="Duration format e.g., 10m, 2h, 1d.",
    reason="Reason for the mute (optional)"
)
async def mute(
    interaction: discord.Interaction,
    user: discord.Member,
    duration: str,
    reason: str | None=None
):
    # Self/Hierarchy protection
    if user == interaction.user:
        await interaction.response.send_message("You cannot mute yourself.", ephemeral=True)
        return
    if interaction.guild.me.top_role <= user.top_role:
        await interaction.response.send_message(f"Failed to mute {user.name}. My highest role is not high enough.", ephemeral=True)
        return

    if interaction.user != interaction.guild.owner and interaction.user.top_role <= user.top_role:
        await interaction.response.send_message(f"Failed to mute {user.name}. You cannot mute someone with an equal or higher role.", ephemeral=True)
        return

    # Parse and validate duration
    # e.g., 10m into seconds
    seconds = parse_duration(duration)
    if seconds is None or seconds < 1:
        await interaction.response.send_message("Wrong duration format. Use numbers followed by 's', 'm', 'h', or 'd'.", ephemeral=True)
        return

    # Calculate the expiration datetime
    timeout_until = calculate_timout(seconds)
    if timeout_until is None:
        await interaction.response.send_message(
            "Invalid duration. Please give a positive duration.", ephemeral=True
        )
        return
    try:
        # Apply timeout
        await user.timeout(timeout_until, reason=reason)

        # Server mute them in voice directly i they are currently in a voice channel
        if user.voice and user.voice.channel:
            try:
                # Edit member data
                await user.edit(mute=True,reason=reason)
            except discord.HTTPException:
                pass
        logging.info(f"{interaction.user} ({interaction.user.id}) muted {user.name} for {duration} for reason: {reason}")
        await interaction.response.send_message(f"Muted {user.name} for {duration}. Reason: {reason or 'None Provided'}", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"Failed to mute {user.name}. I lack the permission to do so.", ephemeral=True)
    except Exception as e:
        logging.exception(e)
        if not interaction.response.is_done():
            await interaction.response.send_message("Some error has occured while processing the command.", ephemeral=True)

# =============================
# UNMUTE COMMAND
# =============================
@bot.tree.command(name="unmute", description="Removes the timeout/mute from a user.")
@app_commands.default_permissions(moderate_members=True)
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.describe(
    user="The user to unmute",
    reason="Reason for unmuting (optional)"
)
async def unmute(
    interaction: discord.Interaction, 
    user: discord.Member, 
    reason: str | None=None
):
    try:
        # Removes timeout
        await user.timeout(None, reason=reason)

        # Unmute in voice channel
        if user.voice and user.voice.channel:
            try:
                await user.edit(mute=False, reason=reason)
            except discord.HTTPException:
                pass

        logging.info(f"{interaction.user} ({interaction.user.id}) unmuted {user.name} ({user.id}). Reason: {reason}")
        await interaction.response.send_message(f"Unmuted {user.name}. Reason: {reason or 'None Provided'}", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"Failed to unmute {user.name}. I lack the permissions needed to do so.", ephemeral=True)
    except Exception as e:
        logging.exception(e)
        if not interaction.response.is_done():
            await interaction.response.send_message("Some error has occured while processing the command.", ephemeral=True)

# Command that warns a user in the server.

# Command that shows the warnings of a user in the server.

# Command that clears the warnings of a user in the server.

# --------------------------------
# Club Purpose Commands WITH Permission Checks
# --------------------------------

# =============================
# ANNOUNCE COMMAND
# Command that announces certain messages in the server similar to embed but with more parameters
# =============================
@bot.tree.command(name="announce", description="Announces a message in the server.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(
    channel="The channel to post the announcement in",
    title="Main title of the announcement",
    description="Main body/text of the anouncement",
    meeting="Meeting details/link/info (optional)",
    section1="Additional information section (optional)",
    section2="Additional information section (optional)",
    color="Hex color code (e.g., #0000FF or 0000FF)",
    ping="Role or mention to include with the announcement (optional)"
)
async def announce(
    interaction: discord.Interaction, 
    channel: discord.TextChannel,
    title: str, 
    description: str, 
    meeting: str | None=None, 
    section1: str | None=None, 
    section2: str | None=None, 
    color: str="#327634",
    ping: discord.Role | None=None
):
    # Safe parsing of hex color
    clean_hex = color.lstrip('#')
    try:
        color_int = int(clean_hex, 16) # convert hex color to int
        # Check if the color input is a valid hex color code (between 0x000000 and 0xFFFFFF)
        if (0 <= color_int >= 0xFFFFFF):
            raise ValueError("Hex Not In Range")
    except ValueError:
        logging.info(f"{interaction.user} provided wrong color format for using /announce command.")
        await interaction.response.send_message("Wrong color format. Please provide the correct 6-digit hex code.",ephemeral=True)

    # Create embed
    embed = discord.Embed(
        title=title,
        description=description,
        color=color_int
    )

    # -------------------------------------------
    # Add additional sections if they are provided
    # -------------------------------------------
    if meeting:
        embed.add_field(name="📅 Meeting Information", value=meeting, inline=False)
    if section1:
        embed.add_field(name="ℹ️ Additional Info", value=section1, inline=False)
    if section2:
        embed.add_field(name="📌 Notes", value=section2, inline=False)

    # Add Footer for author attribution
    embed.set_footer(
        text=f"Announced by {interaction.user.display_name}", 
        icon_url=interaction.user.display_avatar.url
    )

    try:
        # Send the message to the targeted channel
        content = ping.mention if ping else None
        
        await channel.send(content=content, embed=embed)
        logging.info(f"{interaction.user} ({interaction.user.id}) with role {interaction.user.top_role.name} used /announce in #{channel.name}")
        await interaction.response.send_message(f"Announcement sent to {channel.mention}.", ephemeral=True)

    except discord.Forbidden:
        logging.info(f"The bot does not have the permissions to run /announce.")
        await interaction.response.send_message(f"I do not have permission to send messages or embeds in {channel.mention}.", ephemeral=True)
    except Exception as e:
        logging.exception(e)
        if not interaction.response.is_done():
            await interaction.response.send_message("Some error has occurred while sending the announcement.", ephemeral=True)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        # Log the failed attempt 
        logging.info(f"{interaction.user} ({interaction.user.id}) with the role {interaction.user.top_role.name} tried to use /{interaction.command.name} but lacked permissions.")
        msg="You don not have permission to use that command."
    elif isinstance(error, app_commands.BotMissingPermissions):
        logging.warning(f"Bot lacked permissions for /{interaction.command.name} in {interaction.guild.name}")
        msg="I do not have the required permissions to run this command."
    else:
        logging.error(f"Unhandled command error in /{interaction.command.name}: {error}")
        msg="Some error has occured while running the command."

    # Send response
    if interaction.response.is_done():
        await interaction.followup.send(msg, ephemeral=True)
    else:
        await interaction.response.send_message(msg, ephemeral=True)

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
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
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