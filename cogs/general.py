import discord
from discord.ext import commands
from discord import app_commands
import logging

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Replies with Pong!")
    async def ping(self, interaction: discord.Interaction):
        logging.info(f"{interaction.user} used /ping")
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="greet", description="Replies with Hello!")
    async def greet(self, interaction: discord.Interaction):
        logging.info(f"{interaction.user} used /greet")
        await interaction.response.send_message(f"Hello {interaction.user.mention}")

    @app_commands.command(name="userinfo", description="Gives info about the user who used the command.")
    async def userinfo(self, interaction: discord.Interaction):
        logging.info(f"{interaction.user} used /userinfo")
        user = interaction.user
        embed = discord.Embed(title=f"User Info for {user.name}", color=discord.Color.blue())
        embed.add_field(name="Username", value=user.name, inline=True)
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)

        roles = [role.name for role in user.roles if role.name != "@everyone"]
        embed.add_field(name="Roles", value=", ".join(roles) if roles else "No Roles", inline=False)

        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=f"Display Name: {user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Gives info about the server.")
    async def serverinfo(self, interaction: discord.Interaction):
        logging.info(f"{interaction.user} used /serverinfo")
        guild = interaction.guild
        embed = discord.Embed(title=f"Server Info for {guild.name}", color=discord.Color.blue())
        if guild.icon:
            embed.add_field(name="Server Icon", value=guild.icon.url, inline=True)
        embed.add_field(name="Server Name", value=guild.name, inline=True)
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Server Owner", value=guild.owner, inline=True)
        embed.add_field(name="Server Created At", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
