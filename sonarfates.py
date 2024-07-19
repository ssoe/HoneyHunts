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
import aiosqlite
import aiohttp
import traceback

load_dotenv()

# Configuration variables
filter_types = ["Fate"]
huntDict_url = os.getenv("HUNT_DICT_URL")
lightwebhook = os.getenv("WEBHOOK_FATE_URL")
chaoswebhook = os.getenv("C_WEBHOOK_FATE_URL")
srankfate_role_id = os.getenv("SRANKFATE_ROLE_ID")
fatewebhook = os.getenv("FATE_WEBHOOK_URL")

l_serpent = os.getenv("SERPENT_ROLE")
l_mascot = os.getenv("MASCOT_ROLE")
l_sid = os.getenv("SENMURV_ROLE")
l_oid = os.getenv("ORGHANA_ROLE")
l_mid = os.getenv("MINHOCAO_ROLE")
c_oid = os.getenv("C_ORGHANA_ROLE")
c_sid = os.getenv("C_SENMURV_ROLE")
c_mid = os.getenv("C_MINHOCAO_ROLE")
l_DTid = os.getenv("L_Sansheya_ROLE")
c_DTid = os.getenv("C_Sansheya_ROLE")

WEBSOCKET_URL = os.getenv('WEBSOCKET_URL')
MAX_MESSAGE_AGE = 1800  # 15 minutes

# Initialize hunt dictionaries
huntDic = requests.get(huntDict_url).json()
EU = [33, 36, 42, 56, 66, 67, 402, 403, 39, 71, 80, 83, 85, 97, 400, 401]
EUworlds = huntDic['EUWorldDictionary']
lworlds = huntDic['WorldDictionary']
cworlds = huntDic['CWorldDictionary']
fates = huntDic['FateDictionary']
zones = huntDic['zoneDictionary']
status = huntDic['FateStatus']

# Fate and hunt mappings
fate_to_hunt_map = {
    1259: 5986,  # Orghana
    831: 4375,  # Senmurv
    556: 2961,  # Minhocao
    1862: 13399,  # Sansheya
    1871: 1,
    1922: 1
}
hunt_to_cooldown_map = {
    5986: 108 * 3600,  # Orghana
    4375: 108 * 3600,  # Senmurv
    2961: 57 * 3600,  # Minhocao
    13399: 84 * 3600,  # Sansheya
    1: 2 * 2
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
            instance = event.get('InstanceId')

            flag_x, flag_y = get_flag_coordinates(raw_x, raw_y)
            world_name = EUworlds[str(world_id)]
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
            if instance != 0:
                content = f"<@&{role_id}> {title} on **{world_name[0]}** in **Instance: {instance}**"
            else:
                content = f"<@&{role_id}> {title} on **{world_name[0]}**"
            
            webhook = Webhook.from_url(webhook_url, session=session)
                        
            if (fate_id, world_id, instance) in message_ids:
                message_id, _ = message_ids[(fate_id, world_id, instance)]
                await insert_status_to_fates_db(fate_id, world_id, status_id, start_time, instance)
                message = await webhook.edit_message(message_id, embed=embed, content=content)
            else:
                message = await webhook.send(embed=embed, wait=True, content=content)
                await insert_status_to_fates_db(fate_id, world_id, status_id, start_time, instance)
                message_ids[(fate_id, world_id, instance)] = (message.id, time.time())
        except Exception as e:
            print(f"Unexpected error: {e}")
            print(traceback.format_exc(chain=False))
            return f"Failed to process data due to unexpected error: {e}"
        
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
                    instance = event.get('InstanceId')
                    
                    if event_type in filter_types and fate_id in fate_to_hunt_map and world_id in EU:
                        
                        # Special case for FATE IDs 1922 and 1871
                        if fate_id == 1922 and str(world_id) in lworlds:
                            await process_fate(event, fate_id, l_mascot, fatewebhook, "Mica the Magical Mu Fate - Mascot Murder")
                            continue
                        elif fate_id == 1871 and str(world_id) in lworlds:
                            await process_fate(event, fate_id, l_serpent, fatewebhook, "Ttokrrone Fate - The Serpentlord Seethes")
                            continue

                        # For other FATEs, check the deathtimer and cooldown
                        hunt_id = fate_to_hunt_map.get(fate_id)
                        db_result = await get_from_database(hunt_id, world_id, instance)
                        if db_result:
                            deathtimer = db_result[0]

                            if deathtimer is None:
                                print(f"Deathtimer is None for hunt_id {hunt_id}, world_id {world_id}, instance {instance}")
                                continue

                            current_time = int(time.time())
                            cooldown_time = hunt_to_cooldown_map.get(hunt_id)

                            if current_time - deathtimer > cooldown_time:
                                print(f"CD {cooldown_time}, CT {current_time}, DT {deathtimer}, CT - DT {current_time - deathtimer}")
                                await delete_from_database(hunt_id, world_id, instance)
                                print(f"Checking if window open... It is! Deleted {hunt_id}, {world_id}, {instance} from database")

                                if fate_id == 1259:
                                    await process_fate(event, fate_id, c_oid if str(world_id) in cworlds else l_oid, chaoswebhook if str(world_id) in cworlds else lightwebhook, "Orghana Fate - Not Just a Tribute")
                                elif fate_id == 831:
                                    await process_fate(event, fate_id, c_sid if str(world_id) in cworlds else l_sid, chaoswebhook if str(world_id) in cworlds else lightwebhook, "Senmurv Fate - Cerf's Up")
                                elif fate_id == 556:
                                    await process_fate(event, fate_id, c_mid if str(world_id) in cworlds else l_mid, chaoswebhook if str(world_id) in cworlds else lightwebhook, "Minhocao Fate - Core Blimey")
                                elif fate_id == 1862:
                                    await process_fate(event, fate_id, c_DTid if str(world_id) in cworlds else l_DTid, chaoswebhook if str(world_id) in cworlds else lightwebhook, "Sansheya Fate - You Are What You Drink")
                            else:
                                print("The window is closed! Ignoring event")

                        # Cleanup old message IDs
                        if status_id in [3, 4] or (fate_id, world_id) in message_ids and time.time() - message_ids[(fate_id, world_id)][1] > MAX_MESSAGE_AGE:
                            del message_ids[(fate_id, world_id)]

        except aiosqlite.Error as e:
            print(f"Database error {e}")
            traceback.print_stack()
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

async def get_from_database(hunt_id, world_id, instance):
    async with aiosqlite.connect('hunts.db') as conn:
        cursor = await conn.execute('SELECT deathtimer FROM hunts WHERE hunt_id = ? AND world_id = ? AND instance = ?', (hunt_id, world_id, instance))
        return await cursor.fetchone()

async def delete_from_database(hunt_id, world_id, instance):
    async with aiosqlite.connect('hunts.db') as conn:
        await conn.execute('DELETE FROM hunts WHERE hunt_id = ? AND world_id = ? AND instance = ?', (hunt_id, world_id, instance))
        await conn.commit()

async def insert_status_to_fates_db(fate_id, world_id, status_id, start_time, instance):
    try:
        async with aiosqlite.connect('fates.db') as conn:
            cursor = await conn.execute('SELECT * FROM fate_statuses WHERE fate_id = ? AND world_id = ? AND starttime = ? AND instance = ?', (fate_id, world_id, start_time, instance))
            existing_record = await cursor.fetchone()

            current_time = int(time.time())

            if existing_record:
                await conn.execute('UPDATE fate_statuses SET status = ?, time = ? WHERE fate_id = ? AND world_id = ? AND starttime = ? AND instance = ?', (status_id, current_time, fate_id, world_id, start_time, instance))
            else:
                await conn.execute('INSERT INTO fate_statuses (fate_id, world_id, status, time, starttime, instance) VALUES (?, ?, ?, ?, ?, ?)', (fate_id, world_id, status_id, current_time, start_time, instance))

            await conn.commit()
    except aiosqlite.Error as e:
        print(f"Database error: {e}")

async def main():
    await filter_events()

asyncio.run(main())
