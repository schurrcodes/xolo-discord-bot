import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime, timedelta
from utils.json_storage import load_saved_messages, save_user_message, load_warnings, save_warnings
from utils.helpers import parse_duration, calculate_timeout

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    mod_group = app_commands.Group(name="mod", description="Moderation commands")

    @mod_group.command(name="giverole", description="Gives a role to a user.")
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    async def giverole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        if role in user.roles:
            await interaction.response.send_message(f"{user.name} already has the role {role.name}", ephemeral=True)
            return
        try:
            await user.add_roles(role)
            logging.info(f"{interaction.user} gave {role.name} to {user.name}")
            await interaction.response.send_message(f"Gave {role.name} to {user.name}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(f"Failed to give {role.name} to {user.name}. Insufficient permissions.", ephemeral=True)

    @mod_group.command(name="removerole", description="Removes a role from a user.")
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    async def removerole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        if role not in user.roles:
            await interaction.response.send_message(f"{user.name} does not have the role {role.name}.", ephemeral=True)
            return
        try:
            await user.remove_roles(role)
            logging.info(f"{interaction.user} removed {role.name} from {user.name}")
            await interaction.response.send_message(f"Removed {role.name} from {user.name}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(f"Failed to remove {role.name} from {user.name}. Insufficient permissions.", ephemeral=True)

    @mod_group.command(name="embed", description="Embeds a message in the server.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def embed(self, interaction: discord.Interaction, title: str, description: str):
        embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @mod_group.command(name="say", description="Repeats a message or sends your saved default message.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def say(self, interaction: discord.Interaction, message: str | None = None):
        user_id_str = str(interaction.user.id)
        saved_data = load_saved_messages()
        if message:
            save_user_message(interaction.user.id, message)
            text_to_send = message
        elif user_id_str in saved_data:
            text_to_send = saved_data[user_id_str]
        else:
            await interaction.response.send_message("You do not have a saved message yet.", ephemeral=True)
            return
        await interaction.channel.send(text_to_send)
        await interaction.response.send_message("Message has been sent.", ephemeral=True)

    @mod_group.command(name="clear", description="Deletes a specified number of messages from the channel.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            await interaction.response.send_message("Please provide a number between 1 and 100.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)

    @mod_group.command(name="kick", description="Kicks a user from the server.")
    @app_commands.default_permissions(kick_members=True)
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        if user == interaction.user:
            await interaction.response.send_message("You cannot kick yourself.", ephemeral=True)
            return
        await user.kick(reason=reason)
        await interaction.response.send_message(f"Kicked {user.name} for: {reason}", ephemeral=True)

    @mod_group.command(name="ban", description="Bans a user from the server.")
    @app_commands.default_permissions(ban_members=True)
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        if user == interaction.user:
            await interaction.response.send_message("You cannot ban yourself.", ephemeral=True)
            return
        await user.ban(reason=reason)
        await interaction.response.send_message(f"Banned {user.name} for: {reason}", ephemeral=True)

    @mod_group.command(name="unban", description="Unbans a user from the server.")
    @app_commands.default_permissions(ban_members=True)
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user: discord.User):
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"Unbanned {user.name}.", ephemeral=True)

    @mod_group.command(name="mute", description="Mutes a user.")
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str | None = None):
        seconds = parse_duration(duration)
        if seconds is None:
            await interaction.response.send_message("Wrong duration format.", ephemeral=True)
            return
        timeout_until = calculate_timeout(seconds)
        await user.timeout(timeout_until, reason=reason)
        await interaction.response.send_message(f"Muted {user.name} for {duration}.", ephemeral=True)

    @mod_group.command(name="unmute", description="Unmutes a user.")
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, user: discord.Member, reason: str | None = None):
        await user.timeout(None, reason=reason)
        await interaction.response.send_message(f"Unmuted {user.name}.", ephemeral=True)

    @mod_group.command(name="warn", description="Issues a warning to a member.")
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        data = load_warnings()
        guild_id, user_id = str(interaction.guild_id), str(user.id)
        if guild_id not in data:
            data[guild_id] = {}
        if user_id not in data[guild_id]:
            data[guild_id][user_id] = []

        warn_id = len(data[guild_id][user_id]) + 1
        data[guild_id][user_id].append({
            "warn_id": warn_id,
            "reason": reason,
            "moderator_id": interaction.user.id,
            "timestamp": datetime.now().isoformat()
        })
        save_warnings(data)
        await interaction.response.send_message(f"Warned {user.name} (ID: #{warn_id}).", ephemeral=True)

    @mod_group.command(name="warnings", description="Views active warnings for a member.")
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):
        data = load_warnings()
        user_warns = data.get(str(interaction.guild_id), {}).get(str(user.id), [])
        if not user_warns:
            await interaction.response.send_message(f"{user.name} has no warnings.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Warnings for {user.display_name}", color=discord.Color.yellow())
        for item in user_warns:
            embed.add_field(name=f"Warning ID: #{item['warn_id']}", value=f"Reason: {item['reason']}\nModerator: <@{item['moderator_id']}>", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @mod_group.command(name="clearwarnings", description="Clears warnings for a user.")
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    async def clearwarnings(self, interaction: discord.Interaction, user: discord.Member, warn_id: int | None = None):
        data = load_warnings()
        guild_id, user_id = str(interaction.guild_id), str(user.id)
        if warn_id:
            data[guild_id][user_id] = [w for w in data.get(guild_id, {}).get(user_id, []) if w["warn_id"] != warn_id]
        else:
            data.get(guild_id, {})[user_id] = []
        save_warnings(data)
        await interaction.response.send_message(f"Warnings updated for {user.name}.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
