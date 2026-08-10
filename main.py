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
        logging.info(f"Synced {len(synced)} commands on startup.")
        for cmd in synced:
            logging.info(f"Registered: /{cmd.name}")
    except Exception as e:
        logging.exception(f"Failed to sync commands: {e}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        msg = "You do not have permission to use that command."
    elif isinstance(error, app_commands.BotMissingPermissions):
        msg = "I do not have the required permissions to run this command."
    else:
        logging.error(f"Unhandled command error in /{interaction.command.name}: {error}")
        msg = "An error occurred while running this command."

    try:
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except discord.HTTPException:
        #Prevent crashes if the interaction expired completely
        pass

@bot.tree.command(name="sync", description="Syncs commands. Bot Owner Only.")
@app_commands.default_permissions(administrator=True)
async def sync(interaction: discord.Interaction):
    if await bot.is_owner(interaction.user):
        # Defer immediately to buy time (up to 15 minutes instead of 3 seconds)
        await interaction.response.defer(ephemeral=True)
        synced = await bot.tree.sync()

        # Log each synced command specifically
        for cmd in synced:
            #Check if the command has subcommands or options 
            if hasattr(cmd, 'options') and cmd.options:
                sub_names = [opt.name for opt in cmd.options if opt.type.value == 1]
                if sub_names:
                    logging.info(f"Synced group commands: /{cmd.name} [Subcommands: {', '.join(sub_names)}]")
                else:
                    logging.info(f"Synced slash commands: /{cmd.name}")
            else:
                logging.info(f"Synced slash command: /{cmd.name}")

        logging.info(f"Sync complete: {len(synced)} commands.")
        await interaction.followup.send(f"Synced {len(synced)} commands.", ephemeral=True)
    else:
        await interaction.response.send_message("Only the bot owner can use this.", ephemeral=True)

async def main():
    async with bot:
        # Load Cogs automatically
        initial_extensions = [
                'cogs.general',
                'cogs.moderation',
                'cogs.club',
                'cogs.cs',
                'cogs.events'
        ]
        for extension in initial_extensions:
            await bot.load_extension(extension)
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
