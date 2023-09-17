import asyncio
import json
import websockets
from dotenv import load_dotenv
from discord import SyncWebhook
import discord
import requests
import os
import time
import sqlite3

# Load environment variables
load_dotenv()
WEBSOCKET_URL = os.getenv('WEBSOCKET_URL')
filter_types = ["Hunt"]
cfilter_worlds = [39, 71, 80, 83, 85, 97, 400, 401]
huntDict_url = os.getenv("HUNT_DICT_URL")
cwebhook_url = os.getenv("CWEBHOOK_URL")
csrank_role_id = os.getenv("CSRANK_ROLE_ID")
huntDic = requests.get(huntDict_url).json()
cwebhookSrank = SyncWebhook.from_url(cwebhook_url)
message_ids = {}  # Dictionary to store message IDs


async def process_hunts(event):
    try:
        #Get Raw data
        hunt_id = event.get("Id")
        world_id = event.get("WorldId")
        zone_id = event.get("ZoneId")
        coords = event.get('Coords')
        rawxcoord = coords.get('X')
        rawycoord = coords.get('Y')
        instance = event.get('InstanceId')
        players = event.get('Players')
        currenthp = event.get('CurrentHp')
        maxHP = event.get('MaxHp')
        actorID = event.get('ActorId')

        #process raw data
        flagXcoord = str((41 * ((rawxcoord + 1024) / 2048)) + 1)[:4]
        flagYcoord = str((41 * ((rawycoord + 1024) / 2048)) + 1)[:4]
        worlds = huntDic['CWorldDictionary']
        worldName = worlds[str(world_id)]
        mobs = huntDic['MobDictionary']
        mobName = mobs[str(hunt_id)]
        zones = huntDic['zoneDictionary']
        zoneName = zones[str(zone_id)]
        HPpercent = (currenthp / maxHP) * 100
        trueTime = str(int(time.time()))
        
        if hunt_id and zoneName:    
            #make webhook embeds, pain
            mapurl = f"https://api.ffxivsonar.com/render/map?zoneid={zone_id}&flagx={flagXcoord}&flagy={flagYcoord}"
            sRankDead = f"Srank on **[{worldName[0]}]** - **{mobName[0]}** - has died at <t:{trueTime}:f>"
            sRankDeadInstance = f"Srank on **[{worldName[0]}]** - **{mobName[0]}** - Instance: {instance} has died at <t:{trueTime}:f>"
            embed=discord.Embed(title=f"{worldName[0]}  - {mobName[0]} - x {flagXcoord} y {flagYcoord}", color=0xe1e100)
            embed.add_field(name="Zone: ", value=f"{zoneName[0]}", inline=False)
            embed.add_field(name="Players:", value=f"{players}", inline=True)
            embed.add_field(name="HP %", value=f"{round(HPpercent, 1)}", inline=True)
            embed.add_field(name="Teleporter: ", value=f"/ctp {flagXcoord} {flagYcoord} : {zoneName[0]}", inline=False)
            embed.set_image(url=mapurl)
            instancecontent = f"<@&{csrank_role_id}> on **[{worldName[0]}]** - **{mobName[0]}** in **Instance: {instance}** spawned <t:{trueTime}:R>"
            embeddead=discord.Embed(title=f"~~{worldName[0]}  - {mobName[0]} - x {flagXcoord} y {flagYcoord}~~", color=0xe1e100)
            embeddead.add_field(name="~~Players:~~", value=f"{players}", inline=True)
            embeddead.add_field(name="~~HP %~~", value="~~0 %~~", inline=True)
            

            # Logic for sending, instance, and death checking
            if instance != 0:
                if currenthp == 0:
                    cwebhookSrank.send(sRankDeadInstance)
                    deathtimer = str(int(time.time()))
                    message_id, firsttime, mapurl = message_ids[(hunt_id, world_id, actorID)]
                    editcontentstring = f"<@&{csrank_role_id}> on **[{worldName[0]}]** - **{mobName[0]}** in **Instance: {instance}** spawned <t:{firsttime}:R>"
                    message = cwebhookSrank.edit_message(message_id, embed=embeddead, content=editcontentstring)
                    del message_ids[(hunt_id, world_id, actorID)]
                    save_to_database(hunt_id, world_id, message_id, deathtimer, actorID)
                else:
                    if (hunt_id, world_id, actorID) in message_ids:
                        message_id, firsttime, mapurl = message_ids[(hunt_id, world_id, actorID)]
                        editcontentstring = f"<@&{csrank_role_id}> on **[{worldName[0]}]** - **{mobName[0]}** in **Instance: {instance}** spawned <t:{firsttime}:R>"
                        embed.set_image(url=mapurl)
                        message = cwebhookSrank.edit_message(message_id, embed=embed, content=editcontentstring)
                    else:
                        firsttime = str(int(time.time()))
                        contentstring = f"<@&{csrank_role_id}> on **[{worldName[0]}]** - **{mobName[0]}** in **Instance: {instance}** spawned <t:{firsttime}:R>"
                        message = cwebhookSrank.send(embed=embed, wait=True, content=contentstring)
                        message_ids[(hunt_id, world_id, actorID)] = (message.id, firsttime, mapurl)
            else:
                if currenthp == 0:
                    cwebhookSrank.send(sRankDead)
                    deathtimer = str(int(time.time()))
                    message_id, firsttime, mapurl = message_ids[(hunt_id, world_id, actorID)]
                    editcontentstring = f"<@&{csrank_role_id}> on **[{worldName[0]}]** - **{mobName[0]}** spawned <t:{firsttime}:R>"
                    message = cwebhookSrank.edit_message(message_id, embed=embeddead, content=editcontentstring)
                    del message_ids[(hunt_id, world_id, actorID)]
                    save_to_database(hunt_id, world_id, message_id, deathtimer, actorID)
                else:
                    if (hunt_id, world_id, actorID) in message_ids:
                        message_id, firsttime, mapurl = message_ids[(hunt_id, world_id, actorID)]
                        editcontentstring = f"<@&{csrank_role_id}> on **[{worldName[0]}]** - **{mobName[0]}** spawned <t:{firsttime}:R>"
                        embed.set_image(url=mapurl)
                        message = cwebhookSrank.edit_message(message_id, embed=embed, content=editcontentstring)
                    else:
                        firsttime = str(int(time.time()))
                        contentstring = f"<@&{csrank_role_id}> on **[{worldName[0]}]** - **{mobName[0]}** spawned <t:{firsttime}:R>"
                        message = cwebhookSrank.send(embed=embed, wait=True, content=contentstring)
                        message_ids[(hunt_id, world_id, actorID)] = (message.id, firsttime, mapurl)
            return 'Data processed and sent to webhook'
        
    except sqlite3.Error as e:
        print(f"Database error {e}")
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
                    mobs = huntDic['MobDictionary']
                    
                    
                    if event_type in filter_types and world_id in cfilter_worlds and str(hunt_id) in mobs:
                        await process_hunts(event)
                    
                    
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


async def main():
    await connect_websocket()
    
def setup_database():
    with sqlite3.connect('chunts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS hunts (
            hunt_id INTEGER,
            world_id INTEGER,
            message_id INTEGER,
            deathtimer TIMESTAMP,
            actorID TEXT,
            PRIMARY KEY (actorID)
        )
        ''')
    conn.commit()
    conn.close()

setup_database()

def save_to_database(hunt_id, world_id, message_id, deathtimer, actorID):
    conn = sqlite3.connect('chunts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO hunts (hunt_id, world_id, message_id, deathtimer, actorID)
    VALUES (?, ?, ?, ?, ?)
    ''', (hunt_id, world_id, message_id, deathtimer, actorID))
    
    conn.commit()
    conn.close()
    
def get_from_database(hunt_id, world_id):
    conn = sqlite3.connect('chunts.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT message_id, deathtimer FROM hunts WHERE hunt_id = ? AND world_id = ?', (hunt_id, world_id))
    result = cursor.fetchone()
    
    conn.close()
    return result

asyncio.run(main())
