import discord
from discord.ext import commands
from discord import app_commands

class CS(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Slash command group: /cs
    cs_group = app_commands.Group(name="cs", description="Computer Science subgroup commands")

    @cs_group.command(name="resources", description="Get useful CS learning resources.")
    async def resources(self, interaction: discord.Interaction):
        embed = discord.Embed(title="💻 Computer Science Resources", color=discord.Color.green())
        embed.add_field(name="Python Docs", value="[docs.python.org](https://docs.python.org/3/)", inline=False)
        embed.add_field(name="LeetCode", value="[leetcode.com](https://leetcode.com/)", inline=False)
        await interaction.response.send_message(embed=embed)

    @cs_group.command(name="info", description="Get info on the Computer Science track/club.")
    async def info(self, interaction: discord.Interaction):
        await interaction.response.send_message("Welcome to the CS division! Check our channels for workshops and coding competitions.")

async def setup(bot: commands.Bot):
    await bot.add_cog(CS(bot))
