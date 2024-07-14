import asyncio
import json
import websockets
from dotenv import load_dotenv
import requests
import os
import sqlite3
from PIL import Image, ImageDraw
import discord
from discord.ext import commands
import time
import math
from kmeans import get_adjusted_spawn_locations
from maintmode import maintmode_set_db
import traceback
hw = [397, 398, 399, 400, 401, 402]
mob_zone_map = {
		"134": "Croque-mitaine",
		"135": "Croakadile",
		"137": "the Garlok",
		"138": "Bonnacon",
		"139": "Nandi",
		"140": "Zona Seeker",
		"141": "Brontes",
		"145": "Lampalagua",
		"146": "Nunyunuwi",
		"147": "Minhocao",
		"148": "Laideronnette",
		"152": "Wulgaru",
		"153": "mindflayer",
		"154": "Thousand-cast Theda",
		"155": "Safat",
		"156": "Agrippa the Mighty",
		"180": "Chernobog",
		"397": "kaiser behemoth",
		"398": "Senmurv",
		"399": "the Pale Rider",
		"400": "Gandarewa",
		"401": "Bird of Paradise",
		"402": "Leucrotta",
		"612": "Udumbara",
		"613": "Okina",
		"614": "Gamma",
		"620": "Bone Crawler",
		"621": "Salt and Light",
		"622": "Orghana",
		"813": "Tyger",
		"814": "forgiven pedantry",
		"815": "Tarchia",
		"816": "Aglaope",
		"817": "Ixtab",
		"818": "Gunitt",
		"956": "Burfurlur the Canny",
		"957": "sphatika",
		"958": "Armstrong",
		"959": "Ruminator",
		"960": "Narrow-rift",
		"961": "Ophioneus",
        "1187": "Kirlirger the Abhorrent",
        "1188": "Ihnuxokiy",
        "1189": "Neyoozoteel",
        "1190": "Sansheya",
        "1191": "Atticus the Primogenitor",
        "1192": "The Forecaster"
	}
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
load_dotenv()
huntDict_url = os.getenv("HUNT_DICT_URL")
WEBSOCKET_URL = os.getenv('WEBSOCKET_URL')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
huntDic = requests.get(huntDict_url).json()
filter_types = ["Hunt"]
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)
zone_mob_map = {v.lower(): k for k, v in mob_zone_map.items()}
EUworlds = huntDic['EUWorldDictionary']


async def mapping(event):  # sourcery skip: move-assign
    try:
        #Get Raw data
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

        zones = huntDic['zoneDictionary']
        zoneName = zones[str(zone_id)]
        worlds = huntDic['EUWorldDictionary']
        worldName = worlds[str(world_id)]
        flagXcoord = str((41 * ((rawX + 1024) / 2048)) + 1)[:4]
        flagYcoord = str((41 * ((rawY + 1024) / 2048)) + 1)[:4]

        if currentHP == maxHP:
            #process raw data
            await saveMappingToDB(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, int(rawX), int(rawY), actorID, timestamp)


    except sqlite3.Error as e:
        print(f"Database error {e}")
        print(event)
        return f"failed to process data due to DB error: {e}"

    except Exception as e:
        print(f"Uexpected error: {e}")
        traceback.print_exc()
        return f"failed to process data due to error {e}"

async def connect_websocket():
    while True:  # This loop will keep trying to connect
        try:
            async with websockets.connect(WEBSOCKET_URL) as websocket:
                while True:
                    data = await websocket.recv()
                    event = json.loads(data)
                    event_type = event.get("Type")
                    world_id = event.get("WorldId")
                    hunt_id = event.get("Id")
                    mobs = huntDic['ABDictionary']
                    worlds = huntDic['EUWorldDictionary']
                    currentHP = event.get('CurrentHp')
                    maxHP = event.get('MaxHp')
                    
                    
                    if event_type in filter_types and str(world_id) in worlds and str(hunt_id) in mobs and currentHP == maxHP:
                        await mapping(event)
                    
                    
        except websockets.exceptions.ConnectionClosedError as e:
            print(e)
            print("WebSocket connection closed unexpectedly. Reconnecting...")
            await asyncio.sleep(5)  
            continue

        except websockets.exceptions.ConnectionClosed as e:
            print(e)
            await websocket.close()
            await asyncio.sleep(5)
            continue

        except Exception as e:
            print(f"Unexpected error with WebSocket: {e}")
            await asyncio.sleep(5)  
            continue

async def saveMappingToDB(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, rawX, rawY, actorID, timestamp):
    conn = sqlite3.connect('hunts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO mapping (hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, rawX, rawY, actorID, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, rawX, rawY, actorID, timestamp))
    
    conn.commit()
    conn.close()
    
def setup_database():
    with sqlite3.connect('hunts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mapping (
            hunt_id INTEGER,
            world_id INTEGER,
            instance INTEGER,
            zone_id INTEGER,
            flagXcoord TEXT,
            flagYcoord TEXT,
            actorID INTEGER,
            timestamp INTEGER,
            rawX TEXT,
            rawY TEXT,            
            PRIMARY KEY (actorID)
        )
        ''')
    conn.commit()
    conn.close()

setup_database()

    
async def fixMapping(world_id, zone_id, instance, timestamp: int):
    with sqlite3.connect('hunts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        DELETE FROM mapping
        WHERE world_id = ? AND zone_id = ? AND instance = ? AND timestamp < ?
        ''', (world_id, zone_id, instance, timestamp))
        print("deleted")
        conn.commit()
    

async def draw(world_id, zone_id, instance=0):
    # Use get_adjusted_spawn_locations to fetch adjusted coordinates
    adjusted_locations = get_adjusted_spawn_locations(world_id, zone_id, instance)
    
    # Filter locations with type 1
    filtered_locations = [loc for loc in adjusted_locations if loc.type == 1]
    
    mapped_image_path = f'maps/{zone_id}_mapped.jpg'
    base_image_path = f'maps/{zone_id}.jpg'

    # Open the image
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


async def matchWorlds(worldName):
    worldNames = list(world_dict.values())
    worldName = worldName.lower()
    matches = [(name, name.lower().find(worldName)) for name in worldNames if worldName in name.lower()]
    matches = [match for match in matches if match[1] == 0]  # Ensure it matches from the beginning of the name
    matches.sort(key=lambda x: (x[1], len(x[0])))  # Sort by position and length
    return matches[0][0] if matches else None

async def matchHunts(mobName):
    mobNames = list(mob_zone_map.values())
    mobName = mobName.lower()
    matches = [(name, name.lower().find(mobName)) for name in mobNames if mobName in name.lower()]
    matches = [match for match in matches if match[1] == 0]  # Ensure it matches from the beginning of the name
    matches.sort(key=lambda x: (x[1], len(x[0])))  # Sort by position and length
    return matches[0][0] if matches else None

@bot.command()
async def map(ctx, mobName: str, worldName: str, instance: int = 0):
    # Convert mobName and worldName to lowercase to make the search case insensitive
    mobName = mobName.lower()
    worldName = worldName.lower()

    # Look up zone_id using the mob name (even with partial matches)
    zone_id = next((v for k, v in zone_mob_map.items() if mobName in k), None)

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

    world_id = [k for k, v in world_dict.items() if v == matched_worldName][0]
    # Generate the map image
    data_count, mapped_image_path = await draw(int(world_id), int(zone_id), instance)
    
    # Send the image
    with open(mapped_image_path, 'rb') as img:
        await ctx.send(f"mapping for {matched_hunts} on {matched_worldName}")
        await ctx.send(file=discord.File(img, f"maps/{zone_id}_mapped.jpg"))
    # Delete the image after sending it
    os.remove(mapped_image_path)

@bot.command()
async def fixmap(ctx, mobName: str, worldName: str, instance: int = 0, timestamp: int = 0):
# Convert mobName and worldName to lowercase to make the search case insensitive
    mobName = mobName.lower()
    worldName = worldName.lower()

    # Look up zone_id using the mob name (even with partial matches)
    zone_id = next((v for k, v in zone_mob_map.items() if mobName in k), None)

    # If no matching zone, send error
    if not zone_id:
        await ctx.send(f"No zone matches the mob '{mobName}'.")
        return

    # Look up world_id
    world_id = next((k for k, v in huntDic['EUWorldDictionary'].items() if worldName in v[0].lower()), None)
    
    # If no matching world, send error
    if not world_id:
        await ctx.send(f"Invalid world name '{worldName}'.")
        return    
    
    #delete the old mapping points
    await fixMapping(world_id, zone_id, instance, timestamp)
    await ctx.send("mapping deleted good luck kiddo")
    return

@bot.command(name='maintmode')
async def maintmode(ctx, epoch_time: int):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('hunts.db')
        cursor = conn.cursor()

        # Delete rows with timestamp older than the given epoch time
        cursor.execute('DELETE FROM mapping WHERE timestamp < ?', (epoch_time,))
        conn.commit()
        # Get the number of deleted rows
        deleted_rows = cursor.rowcount
        # Delete old hunt timers
        cursor.execute('DELETE FROM hunts WHERE hunt_id = 13399')
        cursor.execute('DELETE FROM hunts WHERE hunt_id = 2961')
        cursor.execute('DELETE FROM hunts WHERE hunt_id = 4375')
        cursor.execute('DELETE FROM hunts WHERE hunt_id = 5986')
        conn.commit()

        # Close the database connection
        conn.close()
        await maintmode_set_db(epoch_time)

        # Send a confirmation message to the Discord channel
        await ctx.send(f'Maintenance mode activated. {deleted_rows} old mapping entries removed from DB. Deleted old hunt death timers and inserted new death timers from maint time.')

    except Exception as e:
        # Send an error message if something goes wrong
        await ctx.send(f'An error occurred: {e}')

@bot.event
async def on_ready():
    print(f'logged in as {bot.user}')
    bot.loop.create_task(main())
    print("started websocket")

async def main():
    await connect_websocket()

bot.run(DISCORD_TOKEN)
