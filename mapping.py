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
#39, 71, 80, 83, 85, 97, 400, 401 Chaos world IDs
#33, 36, 42, 56, 66, 67, 402, 403 Light world IDs
hw = [397, 398, 399, 400, 401, 402]
filter_worlds = [33, 36, 42, 56, 66, 67, 402, 403, 39, 71, 80, 83, 85, 97, 400, 401]
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
		"961": "Ophioneus"
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

        zones = huntDic['zoneDictionary']
        zoneName = zones[str(zone_id)]
        worlds = huntDic['EUWorldDictionary']
        worldName = worlds[str(world_id)]
        flagXcoord = str((41 * ((rawX + 1024) / 2048)) + 1)[:4]
        flagYcoord = str((41 * ((rawY + 1024) / 2048)) + 1)[:4]

        if hunt_id and zoneName:
            #process raw data
            saveMappingToDB(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, int(rawX), int(rawY), actorID, timestamp)


    except sqlite3.Error as e:
        print(f"Database error {e}")
        print(event)
        return f"failed to process data due to DB error: {e}"

    except Exception as e:
        print(f"Uexpected error: {e}")
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
                    
                    
                    if event_type in filter_types and world_id in filter_worlds and str(hunt_id) in mobs:
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

def saveMappingToDB(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, rawX, rawY, actorID, timestamp):
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

def fetch_coordinates(world_id, zone_id, instance):
    with sqlite3.connect('hunts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT rawX, rawY FROM mapping 
        WHERE world_id = ? AND zone_id = ? AND instance = ?
        ''', (world_id, zone_id, instance))
        
        return cursor.fetchall()

    
def fixMapping(world_id, zone_id, instance, timestamp):
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
    
    mapped_image_path = f'maps/{zone_id}_mapped.jpg'
    base_image_path = f'maps/{zone_id}.jpg'

    # Open the image
    with Image.open(base_image_path) as im:
        draw = ImageDraw.Draw(im)
        
        # Iterate through the adjusted coordinates and draw circles
        for location in adjusted_locations:
            x_pixel = 1024 + location.raw_x  # Adjust this if necessary
            y_pixel = 1024 + location.raw_y  # Adjust this if necessary
            
            draw.ellipse([(x_pixel-20, y_pixel-20), (x_pixel+20, y_pixel+20)], outline='red', fill='red')
        
        # Save the new image
        im.save(mapped_image_path)

    return len(adjusted_locations), mapped_image_path

        
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
    world_id = next((k for k, v in huntDic['EUWorldDictionary'].items() if worldName in v[0].lower()), None)
    
    # If no matching world, send error
    if not world_id:
        await ctx.send(f"Invalid world name '{worldName}'.")
        return


    # Generate the map image
    data_count, mapped_image_path = await draw(int(world_id), int(zone_id), instance)
    
    # Send the image
    with open(mapped_image_path, 'rb') as img:
        await ctx.send(file=discord.File(img, f"maps/{zone_id}_mapped.jpg"))
        await ctx.send(f"Map generated using {data_count} data points.")
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
    fixMapping(world_id, zone_id, instance, timestamp)
    await ctx.send("mapping deleted good luck kiddo")
    return
    

@bot.event
async def on_ready():
    print(f'logged in as {bot.user}')
    bot.loop.create_task(main())
    print("started websocket")

async def main():
    await connect_websocket()

bot.run(DISCORD_TOKEN)
