import discord
from discord.ext import commands
import sqlite3
import time
from PIL import Image, ImageDraw, ImageFont
import io
import traceback
import asyncio
import requests
from dotenv import load_dotenv
import config
import utils
import db_utils
from kmeans import get_adjusted_spawn_locations
import os
import json
import websockets
from maintmode import maintmode_set_db

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Pre-computed lists for optimization
WORLD_NAMES = list(config.WORLD_DICT.values())
MOB_NAMES = list(config.MOB_ZONE_MAP.values())

async def matchWorlds(worldName):
    worldName = worldName.lower()
    matches = [(name, name.lower().find(worldName)) for name in WORLD_NAMES if worldName in name.lower()]
    matches = [match for match in matches if match[1] == 0]  # Ensure it matches from the beginning of the name
    matches.sort(key=lambda x: (x[1], len(x[0])))  # Sort by position and length
    return matches[0][0] if matches else None

async def matchHunts(mobName):
    mobName = mobName.lower()
    matches = [(name, name.lower().find(mobName)) for name in MOB_NAMES if mobName in name.lower()]
    matches = [match for match in matches if match[1] == 0]  # Ensure it matches from the beginning of the name
    matches.sort(key=lambda x: (x[1], len(x[0])))  # Sort by position and length
    return matches[0][0] if matches else None

async def draw(world_id, zone_id, instance=0):
    # Use get_adjusted_spawn_locations to fetch adjusted coordinates
    adjusted_locations = await get_adjusted_spawn_locations(world_id, zone_id, instance)

    filtered_locations = adjusted_locations # Placeholder until I verify Location.type

    mapped_image_path = f'maps/{zone_id}_mapped.jpg'
    base_image_path = f'maps/{zone_id}.jpg'

    # Open the image
    try:
        with Image.open(base_image_path) as im:
            draw = ImageDraw.Draw(im)
            
            # Iterate through the adjusted coordinates and draw circles
            for location in filtered_locations:

                x_pixel = 1024 + location.raw_x  # Adjust this if necessary
                y_pixel = 1024 + location.raw_y  # Adjust this if necessary
                
                draw.ellipse([(x_pixel-20, y_pixel-20), (x_pixel+20, y_pixel+20)], outline='red', fill='red')
            
            # Save the new image
            im.save(mapped_image_path)
            return len(filtered_locations), mapped_image_path
    except FileNotFoundError:
        return 0, None

@bot.command(name='map')
async def mapping(ctx, mobName: str, worldName: str, instance: int = 0):
    try:
        # Convert mobName and worldName to lowercase to make the search case insensitive
        mobName = mobName.lower()
        worldName = worldName.lower()

        # Look up zone_id using the mob name (even with partial matches)
        # config.ZONE_MOB_MAP is {mob_name_lower: zone_id}
        zone_id = next((v for k, v in config.ZONE_MOB_MAP.items() if mobName in k), None)

        # If no matching zone, send error
        if not zone_id:
            await ctx.send(f"No zone matches the mob '{mobName}'.")
            return

        # Look up world_id
        matched_worldName = await matchWorlds(worldName)
        matched_hunts = await matchHunts(mobName)
        
        if not matched_worldName:
            await ctx.send(f"Invalid world name '{worldName}'.")
            return

        # Find world_id from config.WORLD_DICT
        world_id = next((k for k, v in config.WORLD_DICT.items() if v == matched_worldName), None)
        
        if not world_id:
             await ctx.send(f"Could not resolve world ID for '{matched_worldName}'.")
             return

        # Generate the map image
        data_count, mapped_image_path = await draw(int(world_id), int(zone_id), instance)
        
        if not mapped_image_path:
             await ctx.send(f"Could not find base map for zone {zone_id}.")
             return

        # Send the image
        with open(mapped_image_path, 'rb') as img:
            await ctx.send(f"mapping for {matched_hunts} on {matched_worldName}")
            await ctx.send(file=discord.File(img, f"maps/{zone_id}_mapped.jpg"))
        
        # Delete the image after sending it
        os.remove(mapped_image_path)

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        traceback.print_exc()

@bot.command(name='fixmap')
async def fix_mapping(ctx, mobName: str, worldName: str, instance: int = 0, timestamp: int = 0):
    try:
        # Convert mobName and worldName to lowercase to make the search case insensitive
        mobName = mobName.lower()
        worldName = worldName.lower()

        # Look up zone_id using the mob name (even with partial matches)
        zone_id = next((v for k, v in config.ZONE_MOB_MAP.items() if mobName in k), None)

        # If no matching zone, send error
        if not zone_id:
            await ctx.send(f"No zone matches the mob '{mobName}'.")
            return
        
        matched_worldName = await matchWorlds(worldName)
        if not matched_worldName:
            await ctx.send(f"Invalid world name '{worldName}'.")
            return
            
        world_id = next((k for k, v in config.WORLD_DICT.items() if v == matched_worldName), None)

        if not world_id:
            await ctx.send(f"Invalid world name '{worldName}'.")
            return    
        
        # delete the old mapping points
        async with db_utils.get_async_db_connection('hunts.db') as conn:
            await conn.execute('''
            DELETE FROM mapping
            WHERE world_id = ? AND zone_id = ? AND instance = ? AND timestamp < ?
            ''', (world_id, zone_id, instance, timestamp))
            await conn.commit()
            
        await ctx.send("mapping deleted good luck kiddo")
        
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        traceback.print_exc()

@bot.command(name='maintmode')
async def maintmode(ctx, epoch_time: int):
    try:
        async with db_utils.get_async_db_connection('hunts.db') as conn:
            # Delete rows with timestamp older than the given epoch time
            cursor = await conn.execute('DELETE FROM mapping WHERE timestamp < ?', (epoch_time,))
            await conn.commit()
            # Get the number of deleted rows
            deleted_rows = cursor.rowcount
            
            # Delete old hunt timers
            # 13399, 2961, 4375, 5986
            for hunt_id in [13399, 2961, 4375, 5986]:
                await conn.execute('DELETE FROM hunts WHERE hunt_id = ?', (hunt_id,))
            await conn.commit()
        
        await maintmode_set_db(epoch_time)
        await ctx.send(f'Maintenance mode activated. {deleted_rows} old mapping entries removed from DB. Deleted old hunt death timers and inserted new death timers from maint time.')

    except Exception as e:
        await ctx.send(f'An error occurred: {e}')
        traceback.print_exc()

async def process_socket_data(event):
    try:
        # Get Raw data
        hunt_id = event.get("Id")
        world_id = event.get("WorldId")
        zone_id = event.get("ZoneId")
        coords = event.get('Coords')
        rawX = coords.get('X')
        rawY = coords.get('Y')
        instance = event.get('InstanceId')
        actorID = event.get('ActorId')
        timestamp = int(time.time())
        currentHP = event.get('CurrentHp')
        maxHP = event.get('MaxHp')

        # Calculate flag coordinates 
        flagXcoord = str((41 * ((rawX + 1024) / 2048)) + 1)[:4]
        flagYcoord = str((41 * ((rawY + 1024) / 2048)) + 1)[:4]

        if currentHP == maxHP:
            # Save to DB using db_utils
            await db_utils.save_mapping_to_db(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, int(rawX), int(rawY), actorID, timestamp)
            #print(f"Saved mapping for hunt {hunt_id} on world {world_id}")

    except Exception as e:
        print(f"Error processing socket data: {e}")
        traceback.print_exc()

async def connect_websocket():
    while True:
        try:
            async with websockets.connect(config.WEBSOCKET_URL) as websocket:
                print("Connected to websocket")
                while True:
                    data = await websocket.recv()
                    event = json.loads(data)
                    event_type = event.get("Type")
                    world_id = event.get("WorldId")
                    hunt_id = event.get("Id")
                    currentHP = event.get('CurrentHp')
                    maxHP = event.get('MaxHp')
                    
                   
                    # if event_type in filter_types and str(world_id) in worlds and str(hunt_id) in mobs and currentHP == maxHP:
                    
                    if (event_type == "Hunt" and 
                        str(world_id) in config.EU_WORLDS and 
                        str(hunt_id) in config.AB_MOBS and 
                        currentHP == maxHP):
                        
                        await process_socket_data(event)

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"WebSocket connection closed unexpectedly: {e}. Reconnecting...")
            await asyncio.sleep(5)
            continue
        except websockets.exceptions.ConnectionClosed as e:
            print(f"WebSocket connection closed: {e}")
            await asyncio.sleep(5)
            continue
        except Exception as e:
            print(f"Unexpected error with WebSocket: {e}")
            await asyncio.sleep(5)
            continue

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    bot.loop.create_task(connect_websocket())
    print("Started websocket listener")






# Run the bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
