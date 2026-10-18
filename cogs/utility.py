import discord
from discord.ext import commands
from discord import app_commands
import time
import platform


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    def get_uptime(self):
        current_time = time.time()
        total_seconds = int(current_time - self.start_time)

        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{days}d {hours}h {minutes}m {seconds}s"

    # -------------------- PING --------------------

    @app_commands.command(
        name="ping",
        description="Check BitBot's latency."
    )
    async def ping(self, interaction: discord.Interaction):

        latency = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: **{latency}ms**",
            colour=discord.Colour.blue()
        )

        await interaction.response.send_message(embed=embed)

    # -------------------- UPTIME --------------------

    @app_commands.command(
        name="uptime",
        description="See how long BitBot has been running."
    )
    async def uptime(self, interaction: discord.Interaction):

        current_time = time.time()
        total_seconds = int(current_time - self.start_time)

        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        embed = discord.Embed(
            title="⏱ BitBot Uptime",
            description=f"Running for:\n**{days}d {hours}h {minutes}m {seconds}s**",
            colour=discord.Colour.green()
        )

        await interaction.response.send_message(embed=embed)
 
    # -------------------- USERINFO --------------------

    @app_commands.command(
        name="userinfo",
        description="Show information about a user."
    )
    async def userinfo(
        self,
        interaction: discord.Interaction,
        user: discord.Member = None
    ):

        user = user or interaction.user

        embed = discord.Embed(
            title=f"User Info: {user.name}",
            colour=discord.Colour.orange()
        )

        embed.add_field(
            name="ID",
            value=user.id,
            inline=False
        )

        embed.add_field(
            name="Joined Server",
            value=user.joined_at.strftime("%d %b %Y"),
            inline=False
        )

        embed.add_field(
            name="Account Created",
            value=user.created_at.strftime("%d %b %Y"),
            inline=False
        )

        embed.set_thumbnail(
            url=user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    # -------------------- SERVERINFO --------------------

    @app_commands.command(
        name="serverinfo",
        description="Information about this server."
    )
    async def serverinfo(self, interaction: discord.Interaction):

        guild = interaction.guild

        embed = discord.Embed(
            title=f"Server Info: {guild.name}",
            colour=discord.Colour.teal()
        )

        embed.add_field(
            name="Server ID",
            value=guild.id,
            inline=False
        )

        embed.add_field(
            name="Members",
            value=guild.member_count,
            inline=False
        )

        embed.add_field(
            name="Created",
            value=guild.created_at.strftime("%d %b %Y"),
            inline=False
        )

        if guild.icon:
            embed.set_thumbnail(
                url=guild.icon.url
            )

        await interaction.response.send_message(embed=embed)

    # -------------------- INFO --------------------

    @app_commands.command(
        name="info",
        description="Information about BitBot."
    )
    async def info(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🤖 BitBot",
            description="The official community, moderation and utility bot for 404Bit Studios.",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Version",
            value="0.3.0",
            inline=True
        )

        embed.add_field(
            name="Python",
            value=platform.python_version(),
            inline=True
        )

        embed.add_field(
            name="Discord.py",
            value=discord.__version__,
            inline=True
        )

        embed.add_field(
            name="Uptime",
            value=self.get_uptime(),
            inline=False
        )

        await interaction.response.send_message(embed=embed)



    # -------------------- HELP --------------------

    @app_commands.command(
        name="help",
        description="Show BitBot's command list."
    )
    async def help(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="📘 BitBot Help Menu",
            description="Here are BitBot's available commands:",
            colour=discord.Colour.blurple()
        )

        embed.add_field(
            name="Utility Commands",
            value=(
                "/ping\n"
                "/uptime\n"
                "/userinfo\n"
                "/serverinfo\n"
                "/info\n"
            ),
            inline=False
        )

        embed.set_footer(
            text="More commands coming soon!"
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))