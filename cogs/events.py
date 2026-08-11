import discord
from discord.ext import commands
import logging
from utils.db import get_welcome_channel

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        logging.info(f"{member.name} joined {member.guild.name}")

        channel_id = await get_welcome_channel(member.guild.id)

        if not channel_id:
            return  # No welcome channel configured yet

        # Try to get channel from cache first otherwise fetch via API
        channel = member.guild.get_channel(channel_id)
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

async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))