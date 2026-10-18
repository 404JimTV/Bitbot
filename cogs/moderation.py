import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime

MOD_PATH = os.path.join("data", "moderation.json")

def load_data():
    if not os.path.exists(MOD_PATH):
        with open(MOD_PATH, "w") as f:
            json.dump({"users": {}, "settings": {"log_channel": None, "case_id": 0}}, f)

    with open(MOD_PATH, "r") as f:
        data = json.load(f)

    # Auto-repair missing keys
    if "users" not in data:
        data["users"] = {}
    if "settings" not in data:
        data["settings"] = {"log_channel": None, "case_id": 0}
    if "case_id" not in data["settings"]:
        data["settings"]["case_id"] = 0

    save_data(data)
    return data

def save_data(data):
    with open(MOD_PATH, "w") as f:
        json.dump(data, f, indent=2)


class Mod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data = load_data()

    group = app_commands.Group(name="mod", description="Moderation commands")

    # Ensure user exists
    def ensure_user(self, uid):
        if uid not in self.data["users"]:
            self.data["users"][uid] = {
                "warnings": [],
                "kicks": [],
                "bans": [],
                "unbans": [],
                "purges": []
            }

    # Case ID generator
    def next_case_id(self):
        self.data["settings"]["case_id"] += 1
        save_data(self.data)
        return self.data["settings"]["case_id"]

    # Logging helper
    async def send_log(self, interaction: discord.Interaction, title: str, fields: dict, color: discord.Color):
        log_channel_id = self.data["settings"].get("log_channel")
        if not log_channel_id:
            return

        channel = interaction.guild.get_channel(log_channel_id)
        if not channel:
            return

        case_id = self.next_case_id()

        embed = discord.Embed(
            title=f"{title} — Case #{case_id}",
            color=color,
            timestamp=datetime.utcnow()
        )

        for name, value in fields.items():
            embed.add_field(name=name, value=value, inline=False)

        embed.set_footer(text=f"Moderator: {interaction.user}")

        await channel.send(embed=embed)

    # -------------------------
    # SET LOG CHANNEL
    # -------------------------
    @group.command(name="setlogchannel", description="Set the moderation log channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def setlogchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.data["settings"]["log_channel"] = channel.id
        save_data(self.data)

        await interaction.response.send_message(
            f" Log channel set to {channel.mention}",
            ephemeral=True
        )

    # -------------------------
    # WARN
    # -------------------------
    @group.command(name="warn", description="Warn a user")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        uid = str(user.id)
        self.ensure_user(uid)

        case_id = self.next_case_id()

        self.data["users"][uid]["warnings"].append({
            "moderator": str(interaction.user),
            "reason": reason,
            "date": datetime.utcnow().isoformat(),
            "case": case_id
        })
        save_data(self.data)

        await interaction.response.send_message(
            f" **{user}** has been warned.\nReason: {reason}",
            ephemeral=True
        )

        await self.send_log(
            interaction,
            " User Warned",
            {"User": str(user), "Reason": reason},
            discord.Color.yellow()
        )

    # -------------------------
    # WARNINGS LIST
    # -------------------------
    @group.command(name="warnings", description="View warnings for a user")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings_cmd(self, interaction: discord.Interaction, user: discord.Member):
        uid = str(user.id)
        self.ensure_user(uid)

        warnings = self.data["users"][uid]["warnings"]

        if not warnings:
            return await interaction.response.send_message(
                f" **{user}** has no warnings.",
                ephemeral=True
            )

        lines = [
            f"**Case #{w['case']}** — {w['reason']} *(by {w['moderator']})*"
            for w in warnings
        ]

        await interaction.response.send_message(
            f" **Warnings for {user}:**\n" + "\n".join(lines),
            ephemeral=True
        )

    # -------------------------
    # CLEAR WARNINGS
    # -------------------------
    @group.command(name="clearwarnings", description="Clear all warnings for a user")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def clearwarnings(self, interaction: discord.Interaction, user: discord.Member):
        uid = str(user.id)
        self.ensure_user(uid)

        self.data["users"][uid]["warnings"] = []
        save_data(self.data)

        await interaction.response.send_message(
            f" Cleared all warnings for **{user}**.",
            ephemeral=True
        )

        await self.send_log(
            interaction,
            " Warnings Cleared",
            {"User": str(user)},
            discord.Color.light_gray()
        )

    # -------------------------
    # KICK
    # -------------------------
    @group.command(name="kick", description="Kick a user")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str | None = None):
        reason = reason or "No reason provided"
        bot_member = interaction.guild.me

        # Bot permission check
        if not bot_member.guild_permissions.kick_members:
            return await interaction.response.send_message(
                " I do not have permission to kick members.",
                ephemeral=True
            )

        # Role hierarchy check
        if user.top_role >= bot_member.top_role:
            return await interaction.response.send_message(
                " I cannot kick this user due to role hierarchy.",
                ephemeral=True
            )

        await user.kick(reason=reason)

        uid = str(user.id)
        self.ensure_user(uid)

        case_id = self.next_case_id()

        self.data["users"][uid]["kicks"].append({
            "moderator": str(interaction.user),
            "reason": reason,
            "date": datetime.utcnow().isoformat(),
            "case": case_id
        })
        save_data(self.data)

        await interaction.response.send_message(
            f" **{user}** has been kicked.\nReason: {reason}",
            ephemeral=True
        )

        await self.send_log(
            interaction,
            " User Kicked",
            {"User": str(user), "Reason": reason},
            discord.Color.orange()
        )

    # -------------------------
    # BAN
    # -------------------------
    @group.command(name="ban", description="Ban a user")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str | None = None):
        reason = reason or "No reason provided"
        bot_member = interaction.guild.me

        if not bot_member.guild_permissions.ban_members:
            return await interaction.response.send_message(
                " I do not have permission to ban members.",
                ephemeral=True
            )

        if user.top_role >= bot_member.top_role:
            return await interaction.response.send_message(
                " I cannot ban this user due to role hierarchy.",
                ephemeral=True
            )

        await interaction.guild.ban(user, reason=reason)

        uid = str(user.id)
        self.ensure_user(uid)

        case_id = self.next_case_id()

        self.data["users"][uid]["bans"].append({
            "moderator": str(interaction.user),
            "reason": reason,
            "date": datetime.utcnow().isoformat(),
            "case": case_id
        })
        save_data(self.data)

        await interaction.response.send_message(
            f" **{user}** has been banned.\nReason: {reason}",
            ephemeral=True
        )

        await self.send_log(
            interaction,
            " User Banned",
            {"User": str(user), "Reason": reason},
            discord.Color.red()
        )

    # -------------------------
    # UNBAN
    # -------------------------
    @group.command(name="unban", description="Unban a user by ID")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, userid: str):
        try:
            user_id_int = int(userid)
        except ValueError:
            return await interaction.response.send_message("? Invalid user ID.", ephemeral=True)

        try:
            await interaction.guild.unban(discord.Object(id=user_id_int))

            uid = str(user_id_int)
            self.ensure_user(uid)

            case_id = self.next_case_id()

            self.data["users"][uid]["unbans"].append({
                "moderator": str(interaction.user),
                "date": datetime.utcnow().isoformat(),
                "case": case_id
            })
            save_data(self.data)

            await interaction.response.send_message(
                f" Unbanned user with ID: **{userid}**",
                ephemeral=True
            )

            await self.send_log(
                interaction,
                " User Unbanned",
                {"User ID": userid},
                discord.Color.green()
            )

        except Exception:
            await interaction.response.send_message(
                " Could not unban that user. They may not be banned.",
                ephemeral=True
            )

    # -------------------------
    # PURGE
    # -------------------------
    @group.command(name="purge", description="Delete messages in this channel")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            return await interaction.response.send_message(
                "Amount must be between **1** and **100**.",
                ephemeral=True
            )

        await interaction.channel.purge(limit=amount)

        uid = str(interaction.user.id)
        self.ensure_user(uid)

        case_id = self.next_case_id()

        self.data["users"][uid]["purges"].append({
            "moderator": str(interaction.user),
            "amount": amount,
            "date": datetime.utcnow().isoformat(),
            "case": case_id
        })
        save_data(self.data)

        await interaction.response.send_message(
            f" Deleted **{amount}** messages.",
            ephemeral=True
        )

        await self.send_log(
            interaction,
            " Messages Purged",
            {"Amount": str(amount), "Channel": interaction.channel.mention},
            discord.Color.blue()
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Mod(bot))
