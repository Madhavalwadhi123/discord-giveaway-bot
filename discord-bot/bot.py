import discord
from discord.ext import commands
import asyncio

# === CONFIG ===
GIVEAWAY_CHANNEL_IDS = [
    665860505029836820,       # 🎁 Daily Giveaway channel
    1346118769935777863        # 🗓️ Weekly Giveaway channel
]
VERIFICATION_CHANNEL_ID = 1021530129433903134   # ✅ Verification reminder channel
VERIFIED_ROLE_ID = 648172461455573013           # 🛡️ Verified role
DELAY_SECONDS = 30                               # ⏱️ Wait before first ping check

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

        # Send up to 5 DMs every 3 hours if still unverified
        max_reminders = 5
        interval = 3 * 60 * 60  # 3 hours in seconds

        for i in range(max_reminders):
            await asyncio.sleep(interval)
            if verified_role in member.roles or member.id in pinged_users:
                print(f'✅ {member} verified. Stopping DM reminders.')
                break
            try:
                await member.send(
                    f"⏰ Reminder #{i+1}!\n"
                    "We’ve got **daily and weekly giveaways** happening right now in **BloxEarn** 🎁\n"
                    "Make sure you **verify in our server** so you don’t miss out!\n"
                    "👉 https://discord.com/channels/611680363106009101/1021530129433903134"
                )
                print(f'📬 Sent DM reminder #{i+1} to {member}')
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
bot.run('MTM4NjkxMDU5OTE4NzAwOTYwNg.GNyJqS.OGgpixNZv_LtvgB4e22ltdY87BRgxch_eBduQ0')  # ⚠️ Make sure your repo is private
