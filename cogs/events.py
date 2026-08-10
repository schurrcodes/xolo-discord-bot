import discord
from discord.ext import commands
import logging

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

# Lisenter executes automatically whenever a new member joins the server
@commands.Cog.listener()
async def on_member_join(self, member: discord.Member):
    logging.info(f"{member.name} has joined {member.guild.name}.")

    WELCOME_CHANNEL_ID=
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)

    if channel:
        embed = discord.Embed(
            title="New Member Joined!",
            description=f"Welcome to the server, {member.mention}!",
            color=discord.Color.brand_green()
        )

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        await channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
