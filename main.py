import discord
from discord.ext import commands
import json
import os
import asyncio
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()  # reads .env (WALLET_MNEMONIC, GAS_WALLET_KEY)

with open("config.json", "r") as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Secure Middleman Service"
        )
    )

@bot.event
async def on_command_error(ctx, error):
    """Give users feedback when a prefix command fails instead of silently failing."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply("I don't know that dot command. Try `.help`.", mention_author=False)
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("You don't have permission to use that command.", mention_author=False)
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"You're missing `{error.param.name}`. Try `.help` for command examples.", mention_author=False)
        return

    print(f"❌ Prefix command error in {ctx.command}: {type(error).__name__}: {error}")
    await ctx.reply("That command hit an error. The bot owner can check the Render logs.", mention_author=False)

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded cog: {filename}")
            except Exception as e:
                print(f"❌ Failed to load cog {filename}: {e}")

async def main():
    token = os.getenv("DISCORD_TOKEN") or config.get("token")
    if not token:
        raise SystemExit("❌ No bot token. Set the DISCORD_TOKEN environment variable.")
    async with bot:
        await load_cogs()
        await bot.start(token)

if __name__ == "__main__":
    keep_alive()  # tiny web server so Render + UptimeRobot keep the service awake
    asyncio.run(main())
