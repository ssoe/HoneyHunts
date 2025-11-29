import discord
from discord.ext import commands
import sqlite3
import time
import traceback
import os
import asyncio
from dotenv import load_dotenv
import config
import utils
import db_utils

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command(name='fates')
async def get_fates(ctx, fate_name: str, world_name: str = None):
    try:
        # Map common names to Fate IDs
        fate_map = {
            "senmurv": 831,
            "orghana": 1259,
            "sansheya": 1862,
            "minhocao": 556
        }
        
        fate_id = fate_map.get(fate_name.lower())
        if not fate_id:
            await ctx.send(f"Unknown fate: {fate_name}. Available: senmurv, orghana, sansheya, minhocao")
            return

        query = 'SELECT * FROM fate_statuses WHERE fate_id = ?'
        params = [fate_id]
        
        if world_name:
            world_id = utils.find_best_match(world_name, config.EU_WORLDS)
            if world_id:
                query += ' AND world_id = ?'
                params.append(world_id)
            else:
                await ctx.send(f"Unknown world: {world_name}")
                return
                
        query += ' ORDER BY time DESC LIMIT 5'
        
        async with db_utils.get_async_db_connection('fates.db') as conn:
            cursor = await conn.execute(query, tuple(params))
            rows = await cursor.fetchall()
        
        if not rows:
            await ctx.send("No fate history found.")
            return
            
        message = f"**Fate History for {fate_name.capitalize()}**\n"
        for row in rows:
            # row: fate_id, world_id, status, time, starttime, instance
            w_id = str(row[1])
            status_id = str(row[2])
            timestamp = row[3]
            
            w_name = config.EU_WORLDS.get(w_id, ["Unknown"])[0]
            s_name = config.FATE_STATUS.get(status_id, ["Unknown"])[0]
            
            message += f"**{w_name}**: {s_name} <t:{timestamp}:R>\n"
            
        await ctx.send(message)

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        traceback.print_exc()

# Run the bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
