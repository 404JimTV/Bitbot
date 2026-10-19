import asyncio
import discord
import yt_dlp

from discord.ext import commands
from discord import app_commands


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = []

        return self.queues[guild_id]

    async def play_next(self, guild):

        queue = self.get_queue(guild.id)

        if not queue:
            vc = guild.voice_client

            if vc:
                await asyncio.sleep(300)

                if vc.is_connected() and not vc.is_playing():
                    await vc.disconnect()

            return

        vc = guild.voice_client

        song = queue.pop(0)

        source = discord.FFmpegPCMAudio(
            song["url"],
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        )

        def after(error):
            if error:
                print(error)

            future = asyncio.run_coroutine_threadsafe(
                self.play_next(guild),
                self.bot.loop
            )

            try:
                future.result()
            except Exception as e:
                print(e)

        vc.play(source, after=after)

    @app_commands.command(
        name="play",
        description="Play a song from YouTube"
    )
    async def play(
        self,
        interaction: discord.Interaction,
        query: str
    ):

        if not interaction.user.voice:
            return await interaction.response.send_message(
                "❌ Join a voice channel first.",
                ephemeral=True
            )

        await interaction.response.defer()

        voice_channel = interaction.user.voice.channel

        vc = interaction.guild.voice_client

        if vc is None:

            vc = await voice_channel.connect()

        elif vc.channel != voice_channel:

            await vc.move_to(voice_channel)

        ydl_opts = {
            "format": "bestaudio/best",
            "default_search": "ytsearch",
            "noplaylist": True,
            "quiet": True
        }

        try:

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                info = ydl.extract_info(
                    query,
                    download=False
                )

                if "entries" in info:
                    info = info["entries"][0]

                song = {
                    "title": info["title"],
                    "url": info["url"],
                    "webpage_url": info["webpage_url"]
                }

        except Exception as e:

            return await interaction.followup.send(
                f"❌ Error: {e}"
            )

        queue = self.get_queue(interaction.guild.id)

        queue.append(song)

        embed = discord.Embed(
            title="🎵 Added to Queue",
            description=f"**{song['title']}**",
            colour=discord.Colour.blue()
        )

        await interaction.followup.send(
            embed=embed
        )

        if not vc.is_playing() and not vc.is_paused():
            await self.play_next(interaction.guild)

    @app_commands.command(
        name="skip",
        description="Skip the current song"
    )
    async def skip(self, interaction: discord.Interaction):

        vc = interaction.guild.voice_client

        if not vc or not vc.is_playing():

            return await interaction.response.send_message(
                "❌ Nothing is playing."
            )

        vc.stop()

        await interaction.response.send_message(
            "⏭️ Song skipped."
        )

    @app_commands.command(
        name="queue",
        description="View the music queue"
    )
    async def queue(self, interaction: discord.Interaction):

        queue = self.get_queue(interaction.guild.id)

        if not queue:

            return await interaction.response.send_message(
                "📭 Queue is empty."
            )

        description = []

        for index, song in enumerate(queue, start=1):
            description.append(
                f"`{index}` {song['title']}"
            )

        embed = discord.Embed(
            title="🎵 Music Queue",
            description="\n".join(description),
            colour=discord.Colour.green()
        )

        await interaction.response.send_message(
            embed=embed
        )

    @app_commands.command(
        name="stop",
        description="Stop playback and clear the queue"
    )
    async def stop(self, interaction: discord.Interaction):

        self.queues[interaction.guild.id] = []

        vc = interaction.guild.voice_client

        if vc:

            vc.stop()

            await vc.disconnect()

        await interaction.response.send_message(
            "🛑 Music stopped and queue cleared."
        )

    @app_commands.command(
        name="nowplaying",
        description="Show the current song"
    )
    async def nowplaying(self, interaction: discord.Interaction):

        vc = interaction.guild.voice_client

        if not vc or not vc.is_playing():

            return await interaction.response.send_message(
                "📭 Nothing is currently playing."
            )

        await interaction.response.send_message(
            "🎵 Music is currently playing."
        )


async def setup(bot):
    await bot.add_cog(Music(bot))