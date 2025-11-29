import asyncio
import json
import websockets
from discord import Webhook
import discord
import time
from datetime import datetime
import aiosqlite
import aiohttp
import traceback

import config
import utils
import db_utils

# Dictionary to store message IDs
message_ids = {}

async def process_fate(session, event, fate_id, role_id, webhook_url, title):
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

        flag_x, flag_y = utils.get_flag_coordinates(raw_x, raw_y)
        world_name = config.EU_WORLDS[str(world_id)]
        zone_name = config.ZONES[str(zone_id)]
        status_name = config.FATE_STATUS[str(status_id)]

        # Calculate remaining time
        current_time = datetime.now().timestamp()
        elapsed_time = current_time - start_time
        remaining_time = max(0, duration - elapsed_time)

        # Create and send the embed
        embed = utils.create_embed(
            title=f"**[{world_name[0]}] {title}**",
            progress=progress,
            zone=zone_name[0],
            status_name=status_name[0],
            timer=utils.create_timer_string(duration, remaining_time),
            image_url=f"https://api.ffxivsonar.com/render/map?zoneid={zone_id}&flagx={flag_x}&flagy={flag_y}&fate=true"
        )
        if instance != 0:
            content = f"<@&{role_id}> {title} on **{world_name[0]}** in **Instance: {instance}**"
        else:
            content = f"<@&{role_id}> {title} on **{world_name[0]}**"
        
        webhook = Webhook.from_url(webhook_url, session=session)
                    
        if (fate_id, world_id, instance) in message_ids:
            message_id, _ = message_ids[(fate_id, world_id, instance)]
            await db_utils.insert_status_to_fates_db(fate_id, world_id, status_id, start_time, instance)
            message = await webhook.edit_message(message_id, embed=embed, content=content)
        else:
            message = await webhook.send(embed=embed, wait=True, content=content)
            await db_utils.insert_status_to_fates_db(fate_id, world_id, status_id, start_time, instance)
            message_ids[(fate_id, world_id, instance)] = (message.id, time.time())
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(traceback.format_exc(chain=False))
        return f"Failed to process data due to unexpected error: {e}"
        
async def filter_events(session):
    while True:
        print("Attempting to connect to WebSocket...")
        try:
            async with websockets.connect(config.WEBSOCKET_URL) as websocket:
                print("Successfully connected to WebSocket!")
                while True:
                    data = await websocket.recv()
                    event = json.loads(data)
                    event_type = event.get("Type")
                    fate_id = event.get("Id")
                    world_id = event.get("WorldId")
                    status_id = event.get("Status")
                    instance = event.get('InstanceId')
                    
                    if event_type in config.FILTER_TYPES_FATE and fate_id in config.FATE_TO_HUNT_MAP and world_id in config.EU_IDS:
                        
                        # Special case for FATE IDs 1922 and 1871
                        if fate_id == 1922 and str(world_id) in config.WORLDS:
                            await process_fate(session, event, fate_id, config.L_MASCOT_ROLE, config.FATE_WEBHOOK_URL, "Mica the Magical Mu Fate - Mascot Murder")
                            continue
                        elif fate_id == 1871 and str(world_id) in config.WORLDS:
                            await process_fate(session, event, fate_id, config.L_SERPENT_ROLE, config.FATE_WEBHOOK_URL, "Ttokrrone Fate - The Serpentlord Seethes")
                            continue

                        # For other FATEs, check the deathtimer and cooldown
                        hunt_id = config.FATE_TO_HUNT_MAP.get(fate_id)
                        db_result = await get_from_database(hunt_id, world_id, instance)
                        if db_result:
                            deathtimer = db_result[0]

                            if deathtimer is None:
                                print(f"Deathtimer is None for hunt_id {hunt_id}, world_id {world_id}, instance {instance}")
                                continue

                            current_time = int(time.time())
                            cooldown_time = config.HUNT_TO_COOLDOWN_MAP.get(hunt_id)

                            if current_time - deathtimer > cooldown_time:
                                print(f"CD {cooldown_time}, CT {current_time}, DT {deathtimer}, CT - DT {current_time - deathtimer}")
                                await delete_from_database(hunt_id, world_id, instance)
                                print(f"Checking if window open... It is! Deleted {hunt_id}, {world_id}, {instance} from database")

                                if fate_id == 1259:
                                    await process_fate(session, event, fate_id, config.C_ORGHANA_ROLE if str(world_id) in config.C_WORLDS else config.L_ORGHANA_ROLE, config.CHAOS_FATE_WEBHOOK_URL if str(world_id) in config.C_WORLDS else config.LIGHT_FATE_WEBHOOK_URL, "Orghana Fate - Not Just a Tribute")
                                elif fate_id == 831:
                                    await process_fate(session, event, fate_id, config.C_SENMURV_ROLE if str(world_id) in config.C_WORLDS else config.L_SENMURV_ROLE, config.CHAOS_FATE_WEBHOOK_URL if str(world_id) in config.C_WORLDS else config.LIGHT_FATE_WEBHOOK_URL, "Senmurv Fate - Cerf's Up")
                                elif fate_id == 556:
                                    await process_fate(session, event, fate_id, config.C_MINHOCAO_ROLE if str(world_id) in config.C_WORLDS else config.L_MINHOCAO_ROLE, config.CHAOS_FATE_WEBHOOK_URL if str(world_id) in config.C_WORLDS else config.LIGHT_FATE_WEBHOOK_URL, "Minhocao Fate - Core Blimey")
                                elif fate_id == 1862:
                                    await process_fate(session, event, fate_id, config.C_SANSHEYA_ROLE if str(world_id) in config.C_WORLDS else config.L_SANSHEYA_ROLE, config.CHAOS_FATE_WEBHOOK_URL if str(world_id) in config.C_WORLDS else config.LIGHT_FATE_WEBHOOK_URL, "Sansheya Fate - You Are What You Drink")
                            else:
                                print("The window is closed! Ignoring event")

                        # Cleanup old message IDs
                        if status_id in [3, 4] or (fate_id, world_id) in message_ids and time.time() - message_ids[(fate_id, world_id)][1] > config.MAX_MESSAGE_AGE:
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
    async with db_utils.get_async_db_connection('hunts.db') as conn:
        cursor = await conn.execute('SELECT deathtimer FROM hunts WHERE hunt_id = ? AND world_id = ? AND instance = ?', (hunt_id, world_id, instance))
        return await cursor.fetchone()

async def delete_from_database(hunt_id, world_id, instance):
    async with db_utils.get_async_db_connection('hunts.db') as conn:
        await conn.execute('DELETE FROM hunts WHERE hunt_id = ? AND world_id = ? AND instance = ?', (hunt_id, world_id, instance))
        await conn.commit()

async def main():
    async with aiohttp.ClientSession() as session:
        await filter_events(session)

asyncio.run(main())

