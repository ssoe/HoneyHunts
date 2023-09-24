import asyncio
import json
import websockets
from dotenv import load_dotenv
import requests
import os
import sqlite3
#39, 71, 80, 83, 85, 97, 400, 401 Chaos world IDs
#33, 36, 42, 56, 66, 67, 402, 403 Light world IDs
filter_worlds = [33, 36, 42, 56, 66, 67, 402, 403, 39, 71, 80, 83, 85, 97, 400, 401]
load_dotenv()
huntDict_url = os.getenv("HUNT_DICT_URL")
WEBSOCKET_URL = os.getenv('WEBSOCKET_URL')
huntDic = requests.get(huntDict_url).json()
filter_types = ["Hunt"]


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
        flagXcoord = str((41 * ((rawxcoord + 1024) / 2048)) + 1)[:4]
        flagYcoord = str((41 * ((rawycoord + 1024) / 2048)) + 1)[:4]
        zones = huntDic['zoneDictionary']
        zoneName = zones[str(zone_id)]
        
        if hunt_id and zoneName:
            saveMappingToDB(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, actorID)
            
            
    except sqlite3.Error as e:
        print(f"Database error {e}")
        print(event)
        #print(type(hunt_id))
        #print(type(mobName))
        #print(type(world_id))
        #print(type(worldName))
        #print(type(instance))
        #print(type(zone_id))
        #print(type(zoneName))
        #print(type(flagXcoord))
        #print(type(flagYcoord))
        #print(type(actorID))
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

async def main():
    await connect_websocket()
    
asyncio.run(main())
