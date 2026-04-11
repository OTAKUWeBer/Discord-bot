import discord
from discord.ext import commands
from discord import app_commands, Interaction
from datetime import datetime
import os
import csv

def write_to_log_csv(action: str, user: str, user_id: int, moderator: str, moderator_id: int, reason: str = ""):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    file_path = os.path.join(logs_dir, "moderation_logs.csv")
    write_header = not os.path.exists(file_path)
    with open(file_path, "a", encoding="utf-8", newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(["timestamp", "action", "user", "user_id", "moderator", "moderator_id", "reason"])
        writer.writerow([timestamp, action, user, user_id, moderator, moderator_id, reason])


class Moderation(commands.Cog):
    """Unified Moderation module: Ban, Kick, Roles, and Logs."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Support fallback if ENV variables are missing or misconfigured
        try:
            self.log_channel_id = int(os.getenv("MOD_LOG_CHANNEL_ID", "0"))
        except ValueError:
            self.log_channel_id = 0

    async def _send_log_embed(self, guild: discord.Guild, title: str, color: discord.Color, user: discord.abc.User, moderator: discord.abc.User, reason: str = None):
        if not self.log_channel_id:
            return
        log_channel = guild.get_channel(self.log_channel_id)
        if log_channel:
            embed = discord.Embed(title=title, color=color, timestamp=datetime.utcnow())
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
            embed.add_field(name="Moderator", value=f"{moderator} ({moderator.id})", inline=False)
            if reason is not None:
                embed.add_field(name="Reason", value=reason, inline=False)
            await log_channel.send(embed=embed)

    def _can_execute_ban_kick(self, issuer: discord.Member, target: discord.Member) -> bool:
        return (
            issuer != target and
            issuer.top_role > target.top_role
        )

    # ==========================
    # BAN & UNBAN
    # ==========================

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        if not self._can_execute_ban_kick(ctx.author, member):
            return await ctx.send("❌ You cannot ban that user.")
        try:
            await member.ban(reason=reason)
            await ctx.send(f"✅ {member.mention} has been banned.")
            write_to_log_csv("BAN", str(member), member.id, str(ctx.author), ctx.author.id, reason or "")
            await self._send_log_embed(ctx.guild, "🔨 Ban Log", discord.Color.red(), member, ctx.author, reason or "No reason provided.")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban that user.")

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_slash(self, interaction: Interaction, member: discord.Member, reason: str = None):
        if not self._can_execute_ban_kick(interaction.user, member):
            return await interaction.response.send_message("❌ You cannot ban that user.", ephemeral=True)
        try:
            await interaction.guild.ban(member, reason=reason)
            await interaction.response.send_message(f"✅ {member.mention} has been banned.")
            write_to_log_csv("BAN", str(member), member.id, str(interaction.user), interaction.user.id, reason or "")
            await self._send_log_embed(interaction.guild, "🔨 Ban Log", discord.Color.red(), member, interaction.user, reason or "No reason provided.")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to ban that user.", ephemeral=True)

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"✅ {user.mention} has been unbanned.")
            write_to_log_csv("UNBAN", str(user), user.id, str(ctx.author), ctx.author.id)
            await self._send_log_embed(ctx.guild, "🟢 Unban Log", discord.Color.green(), user, ctx.author)
        except discord.NotFound:
            await ctx.send("❌ User not found or not banned.")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban users.")

    @app_commands.command(name="unban", description="Unban a member from the server by ID")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban_slash(self, interaction: Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"✅ {user.mention} has been unbanned.")
            write_to_log_csv("UNBAN", str(user), user.id, str(interaction.user), interaction.user.id)
            await self._send_log_embed(interaction.guild, "🟢 Unban Log", discord.Color.green(), user, interaction.user)
        except discord.NotFound:
            await interaction.response.send_message("❌ User not found or not banned.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to unban users.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Invalid user ID.", ephemeral=True)

    # ==========================
    # KICK
    # ==========================

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, user: discord.Member, *, reason: str = None):
        if user == ctx.author:
            return await ctx.send("❌ You cannot kick yourself.")
        if not self._can_execute_ban_kick(ctx.author, user):
            return await ctx.send("❌ You cannot kick that user.")
        try:
            await user.kick(reason=reason)
            await ctx.send(f"✅ {user.mention} has been kicked.")
            write_to_log_csv("KICK", str(user), user.id, str(ctx.author), ctx.author.id, reason or "")
            await self._send_log_embed(ctx.guild, "🚪 Kick Log", discord.Color.orange(), user, ctx.author, reason or "No reason provided.")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick that user.")

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_kick(self, interaction: Interaction, user: discord.Member, reason: str = None):
        if user == interaction.user:
            return await interaction.response.send_message("❌ You cannot kick yourself.", ephemeral=True)
        if not self._can_execute_ban_kick(interaction.user, user):
            return await interaction.response.send_message("❌ You cannot kick that user.", ephemeral=True)
        try:
            await interaction.guild.kick(user, reason=reason)
            await interaction.response.send_message(f"✅ {user.mention} has been kicked.")
            write_to_log_csv("KICK", str(user), user.id, str(interaction.user), interaction.user.id, reason or "")
            await self._send_log_embed(interaction.guild, "🚪 Kick Log", discord.Color.orange(), user, interaction.user, reason or "No reason provided.")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to kick that user.", ephemeral=True)

    # ==========================
    # MOD LOGS HISTORY
    # ==========================

    @commands.command(name="modlogs")
    @commands.has_permissions(kick_members=True)
    async def modlogs(self, ctx: commands.Context, user_id: int):
        """Check moderation history of a user by ID."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(base_dir, "logs", "moderation_logs.csv")

        if not os.path.exists(file_path):
            return await ctx.send("❌ No log file found.")

        logs = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row["user_id"]) == user_id:
                        logs.append(row)
        except Exception as e:
            return await ctx.send(f"⚠️ Error reading logs: {e}")

        if not logs:
            return await ctx.send("📭 No moderation logs found for that user.")

        embed = discord.Embed(title=f"📜 Mod History for {user_id}", color=discord.Color.blue())
        for entry in logs[-10:]:
            embed.add_field(
                name=f"{entry['action']} at {entry['timestamp']}",
                value=f"By: {entry['moderator']}\nReason: {entry['reason'] or 'N/A'}",
                inline=False
            )
        await ctx.send(embed=embed)

    # ==========================
    # ROLES
    # ==========================

    def _find_role(self, guild: discord.Guild, name: str) -> discord.Role | None:
        return discord.utils.get(guild.roles, name=name)

    @commands.command(name="giverole")
    @commands.has_permissions(manage_roles=True)
    async def giverole(self, ctx: commands.Context, user: discord.Member, *, role_name: str):
        role = self._find_role(ctx.guild, role_name)
        if not role:
            return await ctx.send(f"❌ Role `{role_name}` not found.")
        if role >= ctx.guild.me.top_role:
            return await ctx.send(f"❌ I can't assign `{role_name}`; it's higher than my role.")
        if role >= ctx.author.top_role:
            return await ctx.send(f"❌ You need a higher role to assign `{role_name}`.")
        await user.add_roles(role)
        await ctx.send(f"✅ Assigned `{role_name}` to {user.mention}.")

    @app_commands.command(name="giverole", description="Assign a role to a member")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def slash_giverole(self, interaction: Interaction, user: discord.Member, role_name: str):
        role = self._find_role(interaction.guild, role_name)
        if not role:
            return await interaction.response.send_message(f"❌ Role `{role_name}` not found.", ephemeral=True)
        if role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(f"❌ I can't assign `{role_name}`; it's higher than my role.", ephemeral=True)
        if role >= interaction.user.top_role:
            return await interaction.response.send_message(f"❌ You need a higher role to assign `{role_name}`.", ephemeral=True)
        await user.add_roles(role)
        await interaction.response.send_message(f"✅ Assigned `{role_name}` to {user.mention}.")

    @commands.command(name="removerole")
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx: commands.Context, user: discord.Member, *, role_name: str):
        role = self._find_role(ctx.guild, role_name)
        if not role:
            return await ctx.send(f"❌ Role `{role_name}` not found.")
        if role >= ctx.guild.me.top_role:
            return await ctx.send(f"❌ I can't remove `{role_name}`; it's higher than my role.")
        if role >= ctx.author.top_role:
            return await ctx.send(f"❌ You need a higher role to remove `{role_name}`.")
        await user.remove_roles(role)
        await ctx.send(f"✅ Removed `{role_name}` from {user.mention}.")

    @app_commands.command(name="removerole", description="Remove a role from a member")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def slash_removerole(self, interaction: Interaction, user: discord.Member, role_name: str):
        role = self._find_role(interaction.guild, role_name)
        if not role:
            return await interaction.response.send_message(f"❌ Role `{role_name}` not found.", ephemeral=True)
        if role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(f"❌ I can't remove `{role_name}`; it's higher than my role.", ephemeral=True)
        if role >= interaction.user.top_role:
            return await interaction.response.send_message(f"❌ You need a higher role to remove `{role_name}`.", ephemeral=True)
        await user.remove_roles(role)
        await interaction.response.send_message(f"✅ Removed `{role_name}` from {user.mention}.")

    @commands.hybrid_command(name="purge", aliases=["clear"], description="Delete a specified number of messages instantly.")
    @app_commands.describe(amount="The number of messages to delete (max 100)")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, amount: int = 10):
        if amount < 1 or amount > 100:
            msg = "❌ Please provide a valid amount between 1 and 100."
            if ctx.interaction:
                return await ctx.send(msg, ephemeral=True)
            return await ctx.send(msg)
            
        # Handle interaction and prefix independently for cleanest UI
        if ctx.interaction:
            await ctx.defer(ephemeral=False)
            deleted = await ctx.channel.purge(limit=amount)
            await ctx.send(f"✅ Purged {len(deleted)} messages.", delete_after=5)
        else:
            await ctx.message.delete()
            deleted = await ctx.channel.purge(limit=amount)
            msg = await ctx.send(f"✅ Purged {len(deleted)} messages.")
            await msg.delete(delay=5)
            
    @commands.hybrid_command(name="lock", description="Lock a channel to prevent standard users from messaging.")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx: commands.Context, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"🔒 {channel.mention} has been locked.")

    @commands.hybrid_command(name="unlock", description="Unlock a channel to allow standard users to message.")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx: commands.Context, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=None)
        await ctx.send(f"🔓 {channel.mention} has been unlocked.")

    @commands.hybrid_command(name="slowmode", description="Set the slowmode delay of a channel.")
    @app_commands.describe(seconds="Slowmode delay in seconds (0 to disable)")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx: commands.Context, seconds: int, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        if seconds < 0 or seconds > 21600:
            return await ctx.send("❌ Slowmode delay must be between 0 and 21600 seconds.")
        await channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await ctx.send(f"✅ Slowmode disabled in {channel.mention}.")
        else:
            await ctx.send(f"🐌 Slowmode set to {seconds} seconds in {channel.mention}.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
