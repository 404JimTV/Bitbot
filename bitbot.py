import discord
from discord.ext import commands
import os

TOKEN="MTU2MDQwNjk2NTQ3NjI2MTk4MQ.GvaLGG.76IAscaQ4QOsOaw0-gT0Cs9cw3UG4g1lJaTGlE"
APPLICATION_ID=1560406965476261981
GUILD_ID=1555474747477725234

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    application_id=APPLICATION_ID
)

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print (f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load {filename}: {e}") 

@bot.event
async def setup_hook():
    await load_cogs()

    bot.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))

    synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Synced {len(synced)} commands to guild.")


@bot.event
async def on_ready():
    print (f"Bitbot is online as {bot.user}!")
    print("Bitbot is fully ready")

@bot.event 
async def on_disconnect():
    print("BitBot Disconnected.")
@bot.event
async def on_resumed():
    print("BitBot resumed")
bot.run(TOKEN)