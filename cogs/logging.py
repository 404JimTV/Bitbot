import discord
from discord.ext import commands


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_log_channel(self, guild):
        return discord.utils.get(
            guild.text_channels,
            name="serverlogs"
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):

        channel = self.get_log_channel(member.guild)

        if not channel:
            return

        embed = discord.Embed(
            title="✅ Member Joined",
            colour=discord.Colour.green()
        )

        embed.add_field(
            name="User",
            value=f"{member} ({member.id})",
            inline=False
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        channel = self.get_log_channel(member.guild)

        if not channel:
            return

        embed = discord.Embed(
            title="❌ Member Left",
            colour=discord.Colour.red()
        )

        embed.add_field(
            name="User",
            value=f"{member} ({member.id})",
            inline=False
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        if message.author.bot:
            return

        channel = self.get_log_channel(message.guild)

        if not channel:
            return

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            colour=discord.Colour.orange()
        )

        embed.add_field(
            name="Author",
            value=message.author.mention,
            inline=False
        )

        embed.add_field(
            name="Channel",
            value=message.channel.mention,
            inline=False
        )

        embed.add_field(
            name="Content",
            value=message.content or "No text content",
            inline=False
        )

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        if before.author.bot:
            return

        if before.content == after.content:
            return

        channel = self.get_log_channel(before.guild)

        if not channel:
            return

        embed = discord.Embed(
            title="✏️ Message Edited",
            colour=discord.Colour.blue()
        )

        embed.add_field(
            name="Author",
            value=before.author.mention,
            inline=False
        )

        embed.add_field(
            name="Before",
            value=before.content[:1024] or "Empty",
            inline=False
        )

        embed.add_field(
            name="After",
            value=after.content[:1024] or "Empty",
            inline=False
        )

        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Logging(bot))