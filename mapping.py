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
#39, 71, 80, 83, 85, 97, 400, 401 Chaos world IDs
#33, 36, 42, 56, 66, 67, 402, 403 Light world IDs
filter_worlds = [33, 36, 42, 56, 66, 67, 402, 403, 39, 71, 80, 83, 85, 97, 400, 401]
load_dotenv()
huntDict_url = os.getenv("HUNT_DICT_URL")
WEBSOCKET_URL = os.getenv('WEBSOCKET_URL')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
huntDic = requests.get(huntDict_url).json()
filter_types = ["Hunt"]
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)

async def mapping(event):
    try:
        #Get Raw data
        hunt_id = event.get("Id")
        world_id = event.get("WorldId")
        zone_id = event.get("ZoneId")
        coords = event.get('Coords')
        rawxcoord = coords.get('X')
        rawycoord = coords.get('Y')
        instance = event.get('InstanceId')
        actorID = event.get('ActorId')

        #process raw data
        flagXcoord = int(rawxcoord)
        flagYcoord = int(rawycoord)
        zones = huntDic['zoneDictionary']
        zoneName = zones[str(zone_id)]
        worlds = huntDic['EUWorldDictionary']
        worldName = worlds[str(world_id)]
        
        if hunt_id and zoneName:
            saveMappingToDB(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, actorID)
            
            
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

def saveMappingToDB(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, actorID):
    conn = sqlite3.connect('hunts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO mapping (hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, actorID)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, actorID))
    
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
        SELECT flagXcoord, flagYcoord FROM mapping 
        WHERE world_id = ? AND zone_id = ? AND instance = ?
        ''', (world_id, zone_id, instance))
        
        return cursor.fetchall()

async def draw(world_id, zone_id, instance=0):
    coords = fetch_coordinates(world_id, zone_id, instance)
    image_path = f'maps/{zone_id}.jpg'
    
    # Open the image
    with Image.open(image_path) as im:
        draw = ImageDraw.Draw(im)
        
        # Iterate through the coordinates and draw circles
        for coord in coords:
            x, y = coord
            # Convert string coordinates to float
            x_pixel = 1024 + int(x)
            y_pixel = 1024 + int(y)
            #draw 24x24 red circles on map
            draw.ellipse([(x_pixel-15, y_pixel-15), (x_pixel+15, y_pixel+15)], outline='red', fill='red')
        
        # Save the new image
        im.save(f'maps/{zone_id}_mapped.jpg')
        
@bot.command()
async def map(ctx, zoneName: str, worldName: str):
    # Find closest matching zone and world
    zone_id = next((k for k, v in huntDic['zoneDictionary'].items() if zoneName.lower() in v[0].lower()), None)
    world_id = next((k for k, v in huntDic['EUWorldDictionary'].items() if worldName.lower() in v[0].lower()), None)
    
    # If no matching zone or world is found, send an error message
    if not zone_id or not world_id:
        await    ctx.send("Invalid zone or world name.")
        return

    # Generate the map image
    await draw(int(world_id), int(zone_id))
    image_path = f'maps/{zone_id}_mapped.jpg'
    
    # Send the image
    with open(image_path, 'rb') as img:
        await ctx.send(file=discord.File(img, f"maps/{zone_id}_mapped.jpg"))

@bot.event
async def on_ready():
    print(f'logged in as {bot.user}')
    bot.loop.create_task(main())
    print("started websocket")

async def main():
    await connect_websocket()

bot.run(DISCORD_TOKEN)
