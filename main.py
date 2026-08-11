import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import sys
import asyncio
from cogs.roles import RoleButtonView
from utils.db import (
    init_db,
    upsert_member
)

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Setup logging
file_handler = logging.FileHandler(filename="bot.log", encoding="utf-8", mode="w")
console_handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

# Setup intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Setup bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def setup_hook():
    # Initialize the database and tables
    await init_db()
    logging.info("Databased initialized in setup_hook.")
    # Setup Role button view
    bot.add_view(RoleButtonView())
    
@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name}")

    #Sync all current existing members into database
    for guild in bot.guilds:
        for member in guild.members:
            await upsert_member(
                guild_id=guild.id,
                user_id=member.id,
                username=str(member),
                display_name=member.display_name,
                joined_at=member.joined_at.isoformat() if member.joined_at else None,
                is_bot=member.bot
            )
    logging.info("Server all guild members synced to database.")
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
        logging.info(f"User {interaction.user} lacks permissions for /{interaction.command.name}: {error}")
        msg = "You do not have permission to use that command."
    elif isinstance(error, app_commands.BotMissingPermissions):
        logging.info(f"Bot lacks permissions for /{interaction.command.name}: {error}")
        msg = "I do not have the required permissions to run this command."
    else:
        logging.error(f"Unhandled command error in /{interaction.command.name}: {error}")
        msg = "An error occurred while running this command."

    try:
        if interaction.response.is_done():
            logging.warning(f"Interaction response already was sent for /{interaction.command.name}, sending followup instead.")
            await interaction.followup.send(msg, ephemeral=True)
        else:
            logging.info(f"Sending error message for /{interaction.command.name}: {msg}")
            await interaction.response.send_message(msg, ephemeral=True)
    except discord.HTTPException:
        #Prevent crashes if the interaction expired completely
        logging.error(f"Failed to send error message for /{interaction.command.name}: {error}")
        pass

@bot.tree.command(name="sync", description="Syncs commands. Bot Owner Only.")
@app_commands.default_permissions(administrator=True)
async def sync(interaction: discord.Interaction):
    if await bot.is_owner(interaction.user):
        # Defer immediately to buy time (up to 15 minutes instead of 3 seconds)
        logging.info(f"Bot owner {interaction.user} initiated a command sync.")
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
        logging.warning(f"Unauthorized sync attempt by {interaction.user}.")
        await interaction.response.send_message("Only the bot owner can use this.", ephemeral=True)

async def main():
    async with bot:
        # Load Cogs automatically
        initial_extensions = [
                'cogs.general',
                'cogs.moderation',
                'cogs.club',
                'cogs.cs',
                'cogs.events',
                'cogs.roles'
        ]
        for extension in initial_extensions:
            logging.info(f"Loading extension: {extension}")
            await bot.load_extension(extension)
        await bot.start(TOKEN)

if __name__ == "__main__":
    logging.info("Starting bot...")
    asyncio.run(main())
