import discord
from discord.ext import commands
from discord import app_commands
import logging

# Global Listener for Dynamic Role Buttons
class RoleButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        # Check if the interaction is a button click from our role panel
        if interaction.type != discord.InteractionType.component:
            return
        
        custom_id = interaction.data.get("custom_id", "")
        if not custom_id.startswith("rolepanel:"):
            return

        # Extract the role ID from the button's custom_id
        try:
            role_id = int(custom_id.split(":")[1])
        except (IndexError, ValueError):
            logging.error(f"Invalid custom_id format: {custom_id}")
            await interaction.response.send_message("Invalid role button configuration.", ephemeral=True)
            return

        guild = interaction.guild
        role = guild.get_role(role_id) if guild else None

        if not role:
            logging.error(f"Role not found for ID: {role_id}")
            await interaction.response.send_message("Role no longer exists on this server.", ephemeral=True)
            return

        user = interaction.user
        if isinstance(user, discord.Member):
            if role in user.roles:
                await user.remove_roles(role)
                await interaction.response.send_message(f"Removed the {role.name} role.", ephemeral=True)
            else:
                await user.add_roles(role)
                await interaction.response.send_message(f"Added the {role.name} role.", ephemeral=True)


# Main Cog Class
class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Register the global listener when the cog loads
        self.bot.add_listener(RoleButtonView().on_interaction)

    role_group = app_commands.Group(
        name="role", 
        description="Role config commands",
        default_permissions=discord.Permissions(manage_roles=True, manage_messages=True)
    )

    @role_group.command(name="rolepanel", description="Creates a custom button role panel.")
    @app_commands.default_permissions(manage_roles=True, manage_messages=True)
    @app_commands.checks.has_permissions(manage_roles=True, manage_messages=True)
    async def set_rolepanel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        title: str,
        description: str,
        role1: discord.Role,
        label1: str,
        emoji1: str | None = None,
        role2: discord.Role | None = None,
        label2: str | None = None,
        emoji2: str | None = None,
        role3: discord.Role | None = None,
        label3: str | None = None,
        emoji3: str | None = None,
        role4: discord.Role | None = None,
        label4: str | None = None,
        emoji4: str | None = None,
    ):
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Click a button to toggle your role!")

        # Create a view to hold the dynamic buttons
        view = discord.ui.View(timeout=None)

        # Collect roles, labels, and emojis into a list for clean processing
        roles_data = [
            (role1, label1, emoji1),
            (role2, label2, emoji2),
            (role3, label3, emoji3),
            (role4, label4, emoji4),
        ]

        # Button styles to rotate through visually
        button_styles = [
            discord.ButtonStyle.primary,
            discord.ButtonStyle.success,
            discord.ButtonStyle.secondary,
            discord.ButtonStyle.danger
        ]

        added_roles = 0
        for idx, (role, label, emoji) in enumerate(roles_data):
            if role and label:
                btn = discord.ui.Button(
                    label=label,
                    style=button_styles[idx % len(button_styles)],
                    emoji=emoji if emoji else None,
                    custom_id=f"rolepanel:{role.id}"  # Embeds the role ID into the button!
                )
                view.add_item(btn)
                added_roles += 1

        if added_roles == 0:
            await interaction.response.send_message("❌ You must provide at least one role and label!", ephemeral=True)
            return

        # Send the created panel to the requested channel
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"✅ Role panel successfully created in {channel.mention}!", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Roles(bot))