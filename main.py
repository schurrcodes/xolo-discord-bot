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

# Greeting command that replies with Hello and mentions the user who invoked the command.
@bot.tree.command(name="greet", description="Replies with Hello!")
async def greet(interaction: discord.Interaction):
    try:
        logging.info(f"{interaction.user} used /greet")
        await interaction.response.send_message(f"Hello {interaction.user.mention}")
    except Exception as e:
        logging.exception(e)
bot.run(token)