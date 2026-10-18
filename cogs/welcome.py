import discord
from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):

        role= discord.utils.get(
            member.guild.roles,
            name="member"
        )
        if role:
            await member.add_roles(role)

        channel = discord.utils.get(
            member.guild.text_channels,
            name="welcome"
        )

        if not channel:
            return

        embed = discord.Embed(
            title="🤖 Welcome to 404Bit Studios",
            description=f"Welcome {member.mention} to **{member.guild.name}**!",
            colour=0x00BFFF
        )

        embed.add_field(
            name="Get Started",
            value="Read the rules and enjoy your stay!",
            inline=False
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.set_footer(
            text="Powered by BitBot"
        )

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        channel = discord.utils.get(
            member.guild.text_channels,
            name="serverlogs"
        )

        if not channel:
            return

        embed = discord.Embed(
            title=" Farewell",
            description=f"**{member.name}** has left **{member.guild.name}**.",
            colour=discord.Colour.red()
        )

        embed.add_field(
            name="Members Remaining",
            value=str(member.guild.member_count),
            inline=False
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.set_footer(
            text="Powered by BitBot"
        )

        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Welcome(bot))