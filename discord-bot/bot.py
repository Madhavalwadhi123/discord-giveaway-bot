import discord
from discord.ext import commands
import asyncio

# === CONFIG ===
GIVEAWAY_CHANNEL_ID = 1384413995532025938       # 🎁 Giveaway channel
VERIFICATION_CHANNEL_ID = 1384413988997042177   # ✅ Verification reminder channel
VERIFIED_ROLE_ID = 1386914375813562479          # 🛡️ Verified role
DELAY_SECONDS = 30                               # ⏱️ Wait before first ping check
DM_REMINDER_DELAY = 3600                         # ⏱️ DM after 1 hour

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

    # Safety check — don't double ping
    if member.id in pinged_users:
        return

    verified_role = discord.utils.get(member.guild.roles, id=VERIFIED_ROLE_ID)
    giveaway_channel = member.guild.get_channel(GIVEAWAY_CHANNEL_ID)
    verification_channel = member.guild.get_channel(VERIFICATION_CHANNEL_ID)

    if verified_role in member.roles:
        if giveaway_channel:
            await giveaway_channel.send(
                f'🎉 Welcome {member.mention}! Check out our giveaways!',
                delete_after=5
            )
            pinged_users.add(member.id)
            print(f'✅ Pinged {member} in giveaway channel.')
    else:
        if verification_channel:
            await verification_channel.send(
                f'👋 {member.mention}, please complete verification to access giveaways!',
                delete_after=5
            )
            print(f'❌ {member} not verified. Sent reminder in verification channel.')

        # After 1 hour, send DM if still not verified
        await asyncio.sleep(DM_REMINDER_DELAY)
        if verified_role not in member.roles and member.id not in pinged_users:
            try:
                await member.send(
                    "Hey! We got a **daily and weekly giveaway** going on right now in **BloxEarn** 🎁\nMake sure you **verify in our server** so you don't miss out! https://discord.com/channels/611680363106009101/1021530129433903134"
                )
                print(f'📬 Sent DM reminder to {member}')
            except discord.Forbidden:
                print(f'❌ Could not DM {member} (DMs likely closed)')

@bot.event
async def on_member_update(before, after):
    # Only act if user wasn't verified before, and is now verified
    verified_role = discord.utils.get(after.guild.roles, id=VERIFIED_ROLE_ID)

    if (
        verified_role not in before.roles and
        verified_role in after.roles and
        after.id not in pinged_users
    ):
        giveaway_channel = after.guild.get_channel(GIVEAWAY_CHANNEL_ID)
        if giveaway_channel:
            await giveaway_channel.send(
                f'🎉 Welcome {after.mention}! Check out our giveaways!',
                delete_after=5
            )
            pinged_users.add(after.id)
            print(f'⚡ Instant ping for {after} on verify.')

# === RUN BOT ===
bot.run('MTM4NjkxMDU5OTE4NzAwOTYwNg.GNyJqS.OGgpixNZv_LtvgB4e22ltdY87BRgxch_eBduQ0')  # Replace with your regenerated token