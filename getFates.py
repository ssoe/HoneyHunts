import discord
from discord.ext import commands
import sqlite3
import os
from dotenv import load_dotenv
import difflib

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

def find_best_match(world_name):
    world_names = list(world_dict.values())
    world_name = world_name.lower()
    matches = [(name, name.lower().find(world_name)) for name in world_names if world_name in name.lower()]
    matches = [match for match in matches if match[1] == 0]  # Ensure it matches from the beginning of the name
    matches.sort(key=lambda x: (x[1], len(x[0])))  # Sort by position and length
    return matches[0][0] if matches else None

# Command to get the last 5 statuses for Senmurv
@bot.command()
async def senmurv(ctx, world_name):
    # Find the world_id corresponding to the best matching world_name
    matched_world_name = find_best_match(world_name)
    if not matched_world_name:
        await ctx.send("Invalid world name.")
        return
    world_id = [k for k, v in world_dict.items() if v == matched_world_name][0]

    # Fetch the last 5 statuses
    fate_id = 831  
    statuses = get_last_5_statuses(fate_id, world_id)

    # Prepare the message
    message = f"Last 5 known states for Senmurv fate on {matched_world_name}:\n"
    for status, time in statuses:
        message += f"- {status_dict[str(status)]} at <t:{time}> <t:{time}:R>\n"

    # Send the message
    await ctx.send(message)

# Command to get the last 5 statuses for Orghana
@bot.command()
async def orghana(ctx, world_name):
    # Find the world_id corresponding to the best matching world_name
    matched_world_name = find_best_match(world_name)
    if not matched_world_name:
        await ctx.send("Invalid world name.")
        return
    world_id = [k for k, v in world_dict.items() if v == matched_world_name][0]

    # Fetch the last 5 statuses
    fate_id = 1259  
    statuses = get_last_5_statuses(fate_id, world_id)

    # Prepare the message
    message = f"Last 5 known states for Orghana fate on {matched_world_name}:\n"
    for status, time in statuses:
        message += f"- {status_dict[str(status)]} at <t:{time}> <t:{time}:R>\n"

    # Send the message
    await ctx.send(message)

# Run the bot
bot.run(DISCORD_TOKEN)
