import discord
from discord.ext import commands
from discord import app_commands, Interaction
from datetime import datetime

class Info(commands.Cog):
    """Server and User information panels."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="userinfo", aliases=["whois"], description="Get information about a specific user.")
    @app_commands.describe(member="The user you want to get information on")
    async def userinfo(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        
        # Calculate times securely avoiding purely timezone naive conflicts
        created_at = discord.utils.format_dt(member.created_at, style="R")
        joined_at = discord.utils.format_dt(member.joined_at, style="R") if member.joined_at else "Unknown"

        roles = [role.mention for role in reversed(member.roles) if role.id != ctx.guild.id]
        role_string = " ".join(roles) if roles else "No extra roles"

        if len(role_string) > 1024:
            role_string = role_string[:1020] + "..."

        embed = discord.Embed(title=f"User Info - {member.display_name}", color=member.color or discord.Color.blurple())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Account Name", value=f"{member.name}#{member.discriminator}" if member.discriminator != "0" else member.name, inline=True)
        embed.add_field(name="User ID", value=str(member.id), inline=True)
        embed.add_field(name="Bot?", value="Yes" if member.bot else "No", inline=True)
        embed.add_field(name="Created Account", value=created_at, inline=True)
        embed.add_field(name="Joined Server", value=joined_at, inline=True)
        embed.add_field(name="Top Role", value=member.top_role.mention if member.top_role else "None", inline=True)
        embed.add_field(name=f"Roles [{len(roles)}]", value=role_string, inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverinfo", description="Get information about the current server.")
    async def serverinfo(self, ctx: commands.Context):
        guild = ctx.guild
        owner = guild.owner
        
        created_at = discord.utils.format_dt(guild.created_at, style="R")
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        total_members = guild.member_count
        bot_count = sum(1 for m in guild.members if m.bot)
        
        embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.teal())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            
        embed.add_field(name="Owner", value=owner.mention if owner else "Unknown", inline=True)
        embed.add_field(name="Server ID", value=str(guild.id), inline=True)
        embed.add_field(name="Created", value=created_at, inline=True)
        embed.add_field(name="Members", value=f"Total: {total_members}\nBots: {bot_count}", inline=True)
        embed.add_field(name="Channels", value=f"Text: {text_channels}\nVoice: {voice_channels}", inline=True)
        embed.add_field(name="Boosts", value=f"Level {guild.premium_tier} ({guild.premium_subscription_count} boosts)", inline=True)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="avatar", aliases=["av", "pfp"], description="Fetch a user's avatar.")
    @app_commands.describe(member="The user whose avatar you want to fetch")
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"{member.display_name}'s Avatar", color=discord.Color.default())
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
