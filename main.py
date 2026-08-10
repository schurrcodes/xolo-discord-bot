import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import sys

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Setup logging
file_handler = logging.FileHandler(filename="bot.log", encoding="utf-8", mode="w")
console_handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name}")
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} commands.")
    except Exception as e:
        logging.exception(f"Failed to sync commands: {e}")

@bot.tree.error
async def on_app_command_error(interation: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        msg = "You do not have permission to use that command."
    elif isinstance(error, app_commands.BotMissingPermissions):
        msg = "I do not have the required permissions to run this command."
    else:
        logging.error(f"Unhandled command error in /{interaction.command.name}: {error}")
        msg = "An error occurred while running this command."

    if interaction.response.is_done():
        await interaction.followup.send(msg, ephemeral=True)
    else:
        await interaction.response.send_message(msg, ephemeral=True)

@bot.tree.command(name="sync", description="Syncs commands. Bot Owner Only.")
@app_commands.default_permissions(administrator=True)
async def sync(interaction: discord.Interaction):
    if await bot.is_owner(interaction.user):
        synced = await bot.tree.sync()
        await interaction.response.send_message(f"Synced {len(synced)} commands.", ephemeral=True)
    else:
        await interaction.response.send_message("Only the bot owner can use this.", ephemeral=True)

async def main():
    async with bot:
        # Load Cogs automatically
        initial_extensions = ['cogs.general', 'cogs.moderation', 'cogs.club', 'cogs.cs']
        for extension in initial_extensions:
            await bot.load_extension(extension)
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
