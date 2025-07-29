import discord
from discord.ext import commands
import asyncio


from flask import Flask
import threading

# Health check server
server = Flask(__name__)
@server.route('/')
def ping():
    return "pong"

# Start in background
threading.Thread(
    target=server.run,
    kwargs={'host':'0.0.0.0','port':8080},
    daemon=True
).start()


# === CONFIG ===
GIVEAWAY_CHANNEL_IDS = [
    665860505029836820,       # 🎁 Daily Giveaway channel
    1346118769935777863        # 🗓️ Weekly Giveaway channel
]
VERIFICATION_CHANNEL_ID = 1021530129433903134   # ✅ Verification reminder channel
VERIFIED_ROLE_ID = 648172461455573013           # 🛡️ Verified role
DELAY_SECONDS = 30                               # ⏱️ Wait before first ping check
FIRST_DM_DELAY = 3600                            # 1 hour for first DM
FOLLOWUP_DM_COUNT = 5
FOLLOWUP_DM_INTERVAL = 3 * 60 * 60               # 3 hours between follow-up DMs

# === INTENTS ===
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Track users we've already pinged to avoid duplicate pings
pinged_users = set()

@bot.event
async def on_ready():
    print(f'✅ Bot is ready! Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    print(f'👋 {member} joined. Waiting {DELAY_SECONDS}s to check verification...')

    await asyncio.sleep(DELAY_SECONDS)

    if member.id in pinged_users:
        return

    verified_role = discord.utils.get(member.guild.roles, id=VERIFIED_ROLE_ID)
    verification_channel = member.guild.get_channel(VERIFICATION_CHANNEL_ID)

    if verified_role in member.roles:
        for channel_id in GIVEAWAY_CHANNEL_IDS:
            channel = member.guild.get_channel(channel_id)
            if channel:
                await channel.send(
                    f'🎉 Welcome {member.mention}! Check out our giveaways!',
                    delete_after=5
                )
        pinged_users.add(member.id)
        print(f'✅ Pinged {member} in giveaway channels.')
    else:
        if verification_channel:
            await verification_channel.send(
                f'👋 {member.mention}, please complete verification to access giveaways!',
                delete_after=5
            )
        print(f'❌ {member} not verified. Sent reminder in verification channel.')

        # 🕐 Wait 1 hour for first DM
        await asyncio.sleep(FIRST_DM_DELAY)

        if verified_role not in member.roles and member.id not in pinged_users:
            try:
                await member.send(
                    "Hey! We’ve got **daily and weekly giveaways** happening right now in **BloxEarn** 🎁\n"
                    "Make sure you **verify in our server** so you don’t miss out!\n"
                    "👉 https://discord.com/channels/611680363106009101/1021530129433903134"
                )
                print(f'📬 Sent initial DM to {member}')
            except discord.Forbidden:
                print(f'❌ Could not DM {member} (DMs likely closed)')
                return

        # 🔁 Send 5 more follow-up DMs every 3 hours if still unverified
        for _ in range(FOLLOWUP_DM_COUNT):
            await asyncio.sleep(FOLLOWUP_DM_INTERVAL)
            if verified_role in member.roles or member.id in pinged_users:
                print(f'✅ {member} verified. Stopping DM reminders.')
                break
            try:
                await member.send(
                    "Hey! Just a reminder — don’t miss out on our **daily and weekly giveaways** in **BloxEarn** 🎁\n"
                    "Verify in the server now to access them!\n"
                    "👉 https://discord.com/channels/611680363106009101/1021530129433903134"
                )
                print(f'📬 Sent follow-up DM to {member}')
            except discord.Forbidden:
                print(f'❌ Could not DM {member} (DMs likely closed)')
                break

@bot.event
async def on_member_update(before, after):
    verified_role = discord.utils.get(after.guild.roles, id=VERIFIED_ROLE_ID)

    if (
        verified_role not in before.roles and
        verified_role in after.roles and
        after.id not in pinged_users
    ):
        for channel_id in GIVEAWAY_CHANNEL_IDS:
            channel = after.guild.get_channel(channel_id)
            if channel:
                await channel.send(
                    f'🎉 Welcome {after.mention}! Check out our giveaways!',
                    delete_after=5
                )
        pinged_users.add(after.id)
        print(f'⚡ Instant ping for {after} on verify.')

# === RUN BOT ===
import os
bot.run(os.getenv("DISCORD_TOKEN"))
