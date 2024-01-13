import discord
from discord.ext import commands
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
# Your dictionaries
world_dict = {
    "33": "Twintania",
    "36": "Lich",
    "42": "Zodiark",
    "56": "Phoenix",
    "66": "Odin",
    "67": "Shiva",
    "402": "Alpha",
    "403": "Raiden",
    "39": "Omega",
    "71": "Moogle",
    "80": "Cerberus",
    "83": "Louisoix",
    "85": "Spriggan",
    "97": "Ragnarok",
    "400": "Sagittarius",
    "401": "Phantom"
}

status_dict = {
    "1": "Preparation: Talk to NPC to start",
    "2": "Running",
    "3": "Completed",
    "4": "FATE FAILED"
}

# Function to get the last 5 statuses from fates.db
def get_last_5_statuses(fate_id, world_id):
    conn = sqlite3.connect('fates.db')
    cursor = conn.cursor()
    cursor.execute('SELECT status, time FROM fate_statuses WHERE fate_id = ? AND world_id = ? ORDER BY time DESC LIMIT 5', (fate_id, world_id))
    results = cursor.fetchall()
    conn.close()
    return results

# Command to get the last 5 statuses for Senmurv
@bot.command()
async def senmurv(ctx, world_name):
    # Find the world_id corresponding to the world_name
    world_id = [k for k, v in world_dict.items() if v[0].lower() == world_name[0].lower()]
    if not world_id:
        await ctx.send("Invalid world name.")
        return
    world_id = world_id[0]  # Take the first match

    # Fetch the last 5 statuses
    fate_id = 831  # Replace with the actual fate_id for Senmurv
    statuses = get_last_5_statuses(fate_id, world_id)

    # Prepare the message
    message = f"Last 5 known states for Senmurv fate on {world_name}:\n"
    for status, time in statuses:
        message += f"- {status_dict[str(status)]} at <t:{time}> <t:{time}:R>\n"

    # Send the message
    await ctx.send(message)
    
    # Command to get the last 5 statuses for orghana
@bot.command()
async def orghana(ctx, world_name):
    # Find the world_id corresponding to the world_name
    world_id = [k for k, v in world_dict.items() if v[0].lower() == world_name[0].lower()]
    if not world_id:
        await ctx.send("Invalid world name.")
        return
    world_id = world_id[0]  # Take the first match

    # Fetch the last 5 statuses
    fate_id = 1259  # Replace with the actual fate_id for orghana
    statuses = get_last_5_statuses(fate_id, world_id)

    # Prepare the message
    message = f"Last 5 known states for orghana fate on {world_name}:\n"
    for status, time in statuses:
        message += f"- {status_dict[str(status)]} at <t:{time}> <t:{time}:R>\n"

    # Send the message
    await ctx.send(message)


# Run the bot
bot.run(DISCORD_TOKEN)
