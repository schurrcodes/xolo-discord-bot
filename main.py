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

intents = discord.Intents.default()
intents.message_content=True
intents.members=True # Text and Poll Payloads

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")

    try:
        synced=await bot.tree.sync()
        logging.info(f"Synced {len(synced)} commands.")
    except Exception as e:
        logging.exception(e)

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
 

bot.run(token)