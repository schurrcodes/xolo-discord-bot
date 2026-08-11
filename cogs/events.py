import discord
from discord.ext import commands
import logging
from utils.db import (
    get_welcome_channel,
    upsert_member,
    remove_member,
    increment_message_count
)

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        logging.info(f"{member.name} joined {member.guild.name}")

        # Push to DB
        await upsert_member(
            guild_id=member.guild.id,
            user_id=member.id,
            username=str(member),
            display_name=member.display_name,
            joined_at=member.joined_at.isoformat() if member.joined_at else None,
            is_bot=member.bot
        )

        channel_id = await get_welcome_channel(member.guild.id)

        if not channel_id:
            return  # No welcome channel configured yet

        # Try to get channel from cache first otherwise fetch via API
        channel = member.guild.get_channel(channel_id) or await member.guild.fetch_channel(channel_id)
        if channel is None:
            try:
                channel = await member.guild.fetch_channel(channel_id)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                logging.error(f"Could not fetch welcome channel with ID {channel_id}")
                return

        if channel:
            embed = discord.Embed(
                title="👋 New Member Joined!",
                description=f"Welcome to the server, {member.mention}!",
                color=discord.Color.brand_green()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(
                name="Account Created", 
                value=member.created_at.strftime("%Y-%m-%d"), 
                inline=True
            )
            
            try:
                await channel.send(embed=embed)
            except discord.Forbidden:
                logging.warning(f"Lacking permissions to send welcome message in channel {channel.id}")

    # Clean up DB when somone leaves the server
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        logging.info(f"{member.name} left {member.guild.name}")

        # Remove from DB
        await remove_member(
            member.guild.id, member.id
        )

    # Track member activity on every message sent
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bot messages and direct messages
        if message.author.bot or not message.guild:
            return

        await increment_message_count(
            message.guild.id, message.author.id
        )
        

async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))