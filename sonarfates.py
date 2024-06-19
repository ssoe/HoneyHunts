import asyncio
import json
import websockets
from dotenv import load_dotenv
from discord import Webhook
import discord
import requests
import os
import time
from datetime import datetime
import sqlite3
import aiohttp
import traceback

load_dotenv()

# Configuration variables
filter_types = ["Fate"]
huntDict_url = os.getenv("HUNT_DICT_URL")
lightwebhook = os.getenv("WEBHOOK_FATE_URL")
chaoswebhook = os.getenv("C_WEBHOOK_FATE_URL")
srankfate_role_id = os.getenv("SRANKFATE_ROLE_ID")
l_sid = os.getenv("SENMURV_ROLE")
l_oid = os.getenv("ORGHANA_ROLE")
l_mid = os.getenv("MINHOCAO_ROLE")
c_oid = os.getenv("C_ORGHANA_ROLE")
c_sid = os.getenv("C_SENMURV_ROLE")
c_mid = os.getenv("C_MINHOCAO_ROLE")
WEBSOCKET_URL = os.getenv('WEBSOCKET_URL')
MAX_MESSAGE_AGE = 900  # 15 minutes

# Initialize hunt dictionaries
huntDic = requests.get(huntDict_url).json()
EU = [33, 36, 42, 56, 66, 67, 402, 403, 39, 71, 80, 83, 85, 97, 400, 401]
EUworlds = huntDic['WorldDictionary']
lworlds = huntDic['WorldDictionary']
cworlds = huntDic['CWorldDictionary']
fates = huntDic['FateDictionary']
zones = huntDic['zoneDictionary']
status = huntDic['FateStatus']

# Fate and hunt mappings
fate_to_hunt_map = {
    1259: 5986,  # Orghana
    831: 4375,  # Senmurv
    556: 2961   # Minhocao
}
hunt_to_cooldown_map = {
    5986: 84 * 3600,  # Orghana
    4375: 84 * 3600,  # Senmurv
    2961: 57 * 3600   # Minhocao
}

# Dictionary to store message IDs
message_ids = {}

def get_flag_coordinates(raw_x, raw_y):
    flag_x = str((41 * ((raw_x + 1024) / 2048)) + 1)[:4]
    flag_y = str((41 * ((raw_y + 1024) / 2048)) + 1)[:4]
    return flag_x, flag_y

def create_timer_string(duration, remaining_time):
    remaining_minutes = int(remaining_time // 60)
    remaining_seconds = int(remaining_time % 60)
    duration_minutes = int(duration // 60)
    duration_seconds = int(duration % 60)
    return f"{remaining_minutes:02d}:{remaining_seconds:02d} / {duration_minutes:02d}:{duration_seconds:02d}"

def create_embed(title, progress, zone, status_name, timer, image_url):
    embed = discord.Embed(title=title, color=0x633ada)
    embed.add_field(name="Progress:", value=f"{progress} %", inline=True)
    embed.add_field(name="Zone:", value=zone, inline=True)
    embed.add_field(name="Status", value=status_name, inline=False)
    embed.add_field(name="Timer", value=timer, inline=False)
    embed.set_image(url=image_url)
    return embed

async def process_fate(event, fate_id, role_id, webhook_url, title):
    async with aiohttp.ClientSession() as session:
        try:
            # Extract and process raw data
            world_id = event.get("WorldId")
            zone_id = event.get("ZoneId")
            coords = event.get('Coords')
            raw_x = coords.get('X')
            raw_y = coords.get('Y')
            progress = event.get('Progress')
            status_id = event.get('Status')
            start_time = event.get("StartTime") / 1000  # Convert milliseconds to seconds
            duration = event.get("Duration") / 1000  # Convert milliseconds to seconds

            flag_x, flag_y = get_flag_coordinates(raw_x, raw_y)
            world_name = EUworlds[str(world_id)]
            fate_name = fates[str(fate_id)]
            zone_name = zones[str(zone_id)]
            status_name = status[str(status_id)]

            # Calculate remaining time
            current_time = datetime.now().timestamp()
            elapsed_time = current_time - start_time
            remaining_time = max(0, duration - elapsed_time)

            # Create and send the embed
            embed = create_embed(
                title=f"**[{world_name[0]}] {title}**",
                progress=progress,
                zone=zone_name[0],
                status_name=status_name[0],
                timer=create_timer_string(duration, remaining_time),
                image_url=f"https://api.ffxivsonar.com/render/map?zoneid={zone_id}&flagx={flag_x}&flagy={flag_y}&fate=true"
            )
            content = f"<@&{role_id}> {title} on {world_name[0]}"
            webhook = Webhook.from_url(webhook_url, session=session)
                        
            if (fate_id, world_id) in message_ids:
                message_id, _ = message_ids[(fate_id, world_id)]
                await insert_status_to_fates_db(fate_id, world_id, status_id, start_time)
                message = await webhook.edit_message(message_id, embed=embed, content=content)
            else:
                message = await webhook.send(embed=embed, wait=True, content=content)
                await insert_status_to_fates_db(fate_id, world_id, status_id, start_time)
                message_ids[(fate_id, world_id)] = (message.id, time.time())
            print(message.id)
        except Exception as e:
            print(f"Uexpected error: {e}")
            print(traceback.format_exc(chain=False))
            return f"failed to process data due to unexpected error: {e}"
        
async def filter_events():
    while True:
        print("Attempting to connect to WebSocket...")
        try:
            async with websockets.connect(WEBSOCKET_URL) as websocket:
                print("Successfully connected to WebSocket!")
                while True:
                    data = await websocket.recv()
                    event = json.loads(data)
                    event_type = event.get("Type")
                    fate_id = event.get("Id")
                    world_id = event.get("WorldId")
                    status_id = event.get("Status")

                    if event_type in filter_types and fate_id in fate_to_hunt_map and world_id in EU:
                        print(f"Received event: {event}")
                        print("Now checking database for dead hunts...")

                        hunt_id = fate_to_hunt_map.get(fate_id)
                        if db_result := await get_from_database(hunt_id, world_id):
                            deathtimer = db_result[0]
                            current_time = int(time.time())
                            cooldown_time = hunt_to_cooldown_map.get(hunt_id)
                            if current_time - deathtimer > cooldown_time:
                                await delete_from_database(hunt_id, world_id)
                                #print(f"Checking if window open... It is! deleted {hunt_id}, {world_id} from database")
                            else:
                                #print("The swanky window is closed! Ignoring event")
                                continue

                        if fate_id == 1259:
                            await process_fate(event, fate_id, c_oid if str(world_id) in cworlds else l_oid, chaoswebhook if str(world_id) in cworlds else lightwebhook, "Orghana Fate - Not Just a Tribute")
                        elif fate_id == 831:
                            await process_fate(event, fate_id, c_sid if str(world_id) in cworlds else l_sid, chaoswebhook if str(world_id) in cworlds else lightwebhook, "Senmurv Fate - Cerf's Up")
                        elif fate_id == 556:
                            await process_fate(event, fate_id, c_mid if str(world_id) in cworlds else l_mid, chaoswebhook if str(world_id) in cworlds else lightwebhook, "Minhocao Fate - Core Blimey")

                        if status_id in [3, 4] or (fate_id, world_id) in message_ids and time.time() - message_ids[(fate_id, world_id)][1] > MAX_MESSAGE_AGE:
                            del message_ids[(fate_id, world_id)]

        except sqlite3.Error as e:
            print(f"Database error {e}")
            await asyncio.sleep(5)
            continue

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


async def get_from_database(hunt_id, world_id):
    conn = sqlite3.connect('hunts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT deathtimer FROM hunts WHERE hunt_id = ? AND world_id = ?', (hunt_id, world_id))
    result = cursor.fetchone()
    print(f"Retrieved entry for hunt_id {hunt_id}, world_id {world_id} from the database: {result}")
    conn.close()
    return result

async def delete_from_database(hunt_id, world_id):
    conn = sqlite3.connect('hunts.db')
    cursor = conn.cursor()
    print(f"Deleted entry for hunt_id {hunt_id}, world_id {world_id} from the database.")
    cursor.execute('DELETE FROM hunts WHERE hunt_id = ? AND world_id = ?', (hunt_id, world_id))
    conn.commit()
    conn.close()

async def insert_status_to_fates_db(fate_id, world_id, status_id, start_time):
    try:
        conn = sqlite3.connect('fates.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM fate_statuses WHERE fate_id = ? AND world_id = ? AND starttime = ?', (fate_id, world_id, start_time))
        existing_record = cursor.fetchone()

        current_time = int(time.time())

        if existing_record:
            cursor.execute('UPDATE fate_statuses SET status = ?, time = ? WHERE fate_id = ? AND world_id = ? AND starttime = ?', (status_id, current_time, fate_id, world_id, start_time))
        else:
            cursor.execute('INSERT INTO fate_statuses (fate_id, world_id, status, time, starttime) VALUES (?, ?, ?, ?, ?)', (fate_id, world_id, status_id, current_time, start_time))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


async def main():
    await filter_events()

asyncio.run(main())
