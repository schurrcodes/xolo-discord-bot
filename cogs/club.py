import discord
from discord.ext import commands
from discord import app_commands
import logging
import datetime
import json
from utils.db import (
    get_club_info, 
    set_club_info, 
    save_welcome_channel
)

class Club(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Slash command group: /club
    club_group = app_commands.Group(
        name="club", 
        description="General club administrative commands"
    )

    # Slash command group: /set
    set_group = app_commands.Group(
        name="set",
        description="Officer settings commands",
        default_permissions=discord.Permissions(manage_messages=True)
    )

    # =======================================
    # /club GROUP COMMANDS
    # =======================================
    @club_group.command(name="announce", description="Announces a message in the server.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def announce(
        self,
        interaction: discord.Interaction, 
        channel: discord.TextChannel,
        title: str, 
        description: str, 
        meeting: str | None = None, 
        section1: str | None = None, 
        section2: str | None = None, 
        color: str = "#327634",
        ping: discord.Role | None = None
    ):
        try:
            color_int = int(color.lstrip('#'), 16)
        except ValueError:
            logging.info(f"User {interaction.user} provided a wrong color format for /club announce: {color}")
            await interaction.response.send_message("Wrong color format. Use a 6-digit hex code.", ephemeral=True)
            return

        embed = discord.Embed(title=title, description=description, color=color_int)
        if meeting:
            embed.add_field(name="📅 Meeting Information", value=meeting, inline=False)
        if section1:
            embed.add_field(name="ℹ️ Additional Info", value=section1, inline=False)
        if section2:
            embed.add_field(name="📌 Notes", value=section2, inline=False)

        embed.set_footer(text=f"Announced by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        content = ping.mention if ping else None
        logging.info(f"User {interaction.user} is sending an announcement to channel {channel.id} with title '{title}'")
        await channel.send(content=content, embed=embed)
        await interaction.response.send_message(f"Announcement sent to {channel.mention}.", ephemeral=True)

    @club_group.command(name="poll", description="Creates a Discord poll.")
    @app_commands.default_permissions(create_polls=True)
    @app_commands.checks.has_permissions(create_polls=True)
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        option1: str,
        option2: str,
        option3: str | None = None,
        option4: str | None = None,
        duration: int | None = 24,
        multiple: bool | None = False
    ):
        options = [opt for opt in [option1, option2, option3, option4] if opt is not None]
        poll_obj = discord.Poll(question=question, duration=datetime.timedelta(hours=duration), multiple=multiple)
        for opt in options:
            poll_obj.add_answer(text=opt)

        logging.info(f"User {interaction.user} created a poll in channel {interaction.channel.id} with question '{question}' and options {options}")
        await interaction.response.send_message("Poll has been created.", ephemeral=True)
        await interaction.channel.send(poll=poll_obj)

    # =====================================
    # STANDALONE MEMBER COMMANDS
    # =====================================
    @app_commands.command(name="links", description="Shows important club links.")
    async def links(self, interaction: discord.Interaction):
        key = f"links:{interaction.guild_id}"
        raw_data = await get_club_info(key)
        
        data = json.loads(raw_data) if raw_data else {}

        if not data:
            logging.info(f"{interaction.user.id} requested links, but none are set.")
            await interaction.response.send_message("No links have been set yet!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🔗 Important Club Links",
            description="Click the buttons below to open the official club resources:",
            color=discord.Color.blue()
        )

        view = discord.ui.View()

        if data.get("site"):
            view.add_item(discord.ui.Button(
                label="Google Site", 
                url=data["site"], 
                style=discord.ButtonStyle.link,
                emoji="🌐"
            ))

        if data.get("portal"):
            view.add_item(discord.ui.Button(
                label="School Portal", 
                url=data["portal"], 
                style=discord.ButtonStyle.link,
                emoji="🏫"
            ))

        if data.get("instagram"):
            view.add_item(discord.ui.Button(
                label="Instagram",
                url=data["instagram"],
                style=discord.ButtonStyle.link,
                emoji="📸"
            ))

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="meeting", description="Displays details for the next meeting.")
    async def meeting(self, interaction: discord.Interaction):
        key = f"meeting:{interaction.guild_id}"
        raw_data = await get_club_info(key)
        
        data = json.loads(raw_data) if raw_data else {}

        if not data:
            await interaction.response.send_message("No upcoming meeting details found.", ephemeral=True)
            return

        embed = discord.Embed(title="📅 Next Club Meeting", color=discord.Color.gold())
        embed.add_field(name="Date & Time", value=data.get("datetime", "TBD"), inline=False)
        embed.add_field(name="Location / Channel", value=data.get("location", "TBD"), inline=False)
        if "details" in data:
            embed.add_field(name="Topic / Details", value=data["details"], inline=False)

        await interaction.response.send_message(embed=embed) 

    # ====================================
    # /set GROUP COMMANDS
    # ====================================
    @set_group.command(name="links", description="Set important links for the club.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def set_links(
        self, 
        interaction: discord.Interaction, 
        site: str | None = None,
        portal: str | None = None,
        instagram: str | None = None
    ):
        key = f"links:{interaction.guild_id}"
        raw_data = await get_club_info(key)
        data = json.loads(raw_data) if raw_data else {}

        if site:
            data["site"] = site
        if portal:
            data["portal"] = portal
        if instagram:
            data["instagram"] = instagram

        await set_club_info(key, json.dumps(data))
        await interaction.response.send_message("Updated club links!", ephemeral=True)

    @set_group.command(name="meeting", description="Update the next meeting details.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def set_meeting(self, 
        interaction: discord.Interaction, 
        date_and_time: str, 
        location: str,
        details: str | None = None
    ):
        key = f"meeting:{interaction.guild_id}"
        data = {
            "datetime": date_and_time,
            "location": location,
            "details": details or "No additional details were provided."
        }

        await set_club_info(key, json.dumps(data))
        await interaction.response.send_message(f"Next meeting set for {date_and_time} at {location}!", ephemeral=True)

    @set_group.command(name="welcome", description="Set the welcome channel for new members.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def set_welcome(self, 
        interaction: discord.Interaction, 
        channel: discord.TextChannel
    ):
        await save_welcome_channel(interaction.guild_id, channel.id)
        await interaction.response.send_message(f"Welcome channel set to {channel.mention}!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Club(bot))