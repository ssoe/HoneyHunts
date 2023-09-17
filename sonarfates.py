import asyncio
import json
import websockets
from dotenv import load_dotenv
from discord import SyncWebhook
import discord
import requests
import os
import time
from datetime import datetime


filter_types = ["Fate"]
filter_worlds = [33, 36, 42, 56, 66, 67, 402, 403]
load_dotenv()
huntDict_url = os.getenv("HUNT_DICT_URL")
webhook_url = os.getenv("WEBHOOK_URL")
srankfate_role_id = os.getenv("SRANKFATE_ROLE_ID")
senmurv_role_id = os.getenv("SENMURV_ROLE")
orghana_role_id = os.getenv("ORGHANA_ROLE")
minhocao_role_id = os.getenv("MINHOCAO_ROLE")
huntDic = requests.get(huntDict_url).json()
webhookFateSrank = SyncWebhook.from_url(webhook_url)
message_ids = {}  # Dictionary to store message IDs

# Define a maximum age (in seconds) for a message ID to be considered valid
MAX_MESSAGE_AGE = 900  # 15 minutes

async def process_fate_orghana(event):
    #Get Raw data
    fate_id = event.get("Id")
    world_id = event.get("WorldId")
    zone_id = event.get("ZoneId")
    coords = event.get('Coords')
    rawxcoord = coords.get('X')
    rawycoord = coords.get('Y')
    progress = event.get('Progress')
    statusid = event.get('Status')

    #process raw data
    flagXcoord = str((41 * ((rawxcoord + 1024) / 2048)) + 1)[:4]
    flagYcoord = str((41 * ((rawycoord + 1024) / 2048)) + 1)[:4]
    worlds = huntDic['WorldDictionary']
    worldName = worlds[str(world_id)]
    fates = huntDic['FateDictionary']
    fateName = fates[str(fate_id)]
    zones = huntDic['zoneDictionary']
    zoneName = zones[str(zone_id)]
    status = huntDic['FateStatus']
    statusName = status[str(statusid)]

    start_time = event.get("StartTime") / 1000  # Convert milliseconds to seconds
    duration = event.get("Duration") / 1000  # Convert milliseconds to seconds

    # Calculate the elapsed time since the fate started
    current_time = datetime.now().timestamp()
    elapsed_time = current_time - start_time

    # Calculate the remaining time in seconds
    remaining_time = max(0, duration - elapsed_time)

    # Format the remaining time and duration as minutes and seconds
    remaining_minutes = int(remaining_time // 60)
    remaining_seconds = int(remaining_time % 60)
    duration_minutes = int(duration // 60)
    duration_seconds = int(duration % 60)

    # Create the timer string in the format "01:00 / 15:00"
    timer_string = f"{remaining_minutes:02d}:{remaining_seconds:02d} / {duration_minutes:02d}:{duration_seconds:02d}"
    #make discord embed        
    if fate_id and zoneName:
        print('')
        print(f"Filtered event: {fateName} {worldName} Fate posted to Discord")
        print('')
        print(event)
        embed=discord.Embed(title=f"**[{worldName[0]}] Orghana Fate - Not Just a Tribute**", color=0x633ada)
        embed.add_field(name="Progress:", value=f"{progress} %", inline=True)
        embed.add_field(name="Zone: ", value=f"{zoneName[0]}", inline=True)
        embed.add_field(name=f"Status {statusid}", value=f"{statusName[0]}", inline=False)
        embed.add_field(name="Timer", value=timer_string, inline=False)
        embed.set_image(url=f"https://api.ffxivsonar.com/render/map?zoneid={zone_id}&flagx={flagXcoord}&flagy={flagYcoord}&fate=true")
        contentstring = f"<@&{orghana_role_id}> Orghana Fate on {worldName[0]}"
        #message = webhookFateSrank.send(embed=embed, wait=True, content=contentstring)
        if (fate_id, world_id) in message_ids:
            message_id, _ = message_ids[(fate_id, world_id)]
            message = webhookFateSrank.edit_message(message_id, embed=embed, content=contentstring)
        else:
            message = webhookFateSrank.send(embed=embed, wait=True, content=contentstring)
            message_ids[(fate_id, world_id)] = (message.id, time.time())
        print(message.id)
        
        #previous_message_id = message.id
        #print("message ID: " + previous_message_id)
    else:
        print(f"Filtered event: ID={fate_id}, WorldID={world_id}, ZoneID={zone_id}")


async def process_fate_senmurv(event):
        #Get Raw data
    fate_id = event.get("Id")
    world_id = event.get("WorldId")
    zone_id = event.get("ZoneId")
    coords = event.get('Coords')
    rawxcoord = coords.get('X')
    rawycoord = coords.get('Y')
    progress = event.get('Progress')
    statusid = event.get('Status')
    start_time = event.get("StartTime") / 1000  # Convert milliseconds to seconds
    duration = event.get("Duration") / 1000  # Convert milliseconds to seconds
    
    #process raw data
    flagXcoord = str((41 * ((rawxcoord + 1024) / 2048)) + 1)[:4]
    flagYcoord = str((41 * ((rawycoord + 1024) / 2048)) + 1)[:4]
    worlds = huntDic['WorldDictionary']
    worldName = worlds[str(world_id)]
    fates = huntDic['FateDictionary']
    fateName = fates[str(fate_id)]
    zones = huntDic['zoneDictionary']
    zoneName = zones[str(zone_id)]
    status = huntDic['FateStatus']
    statusName = status[str(statusid)]

    # Calculate the elapsed time since the fate started
    current_time = datetime.now().timestamp()
    elapsed_time = current_time - start_time
    remaining_time = max(0, duration - elapsed_time)
    remaining_minutes = int(remaining_time // 60)
    remaining_seconds = int(remaining_time % 60)
    duration_minutes = int(duration // 60)
    duration_seconds = int(duration % 60)

    # Create the timer string in the format "01:00 / 15:00"
    timer_string = f"{remaining_minutes:02d}:{remaining_seconds:02d} / {duration_minutes:02d}:{duration_seconds:02d}"
  
    if fate_id and zoneName:
        print('')
        print(f"Filtered event: {fateName} {worldName} Fate posted to Discord")
        print('')
        print(event)
        embed=discord.Embed(title=f"**[{worldName[0]}] Senmurv Fate - Cerf's Up**", color=0x633ada)
        embed.add_field(name="Progress:", value=f"{progress} %", inline=True)
        embed.add_field(name="Zone: ", value=f"{zoneName[0]}", inline=True)
        embed.add_field(name=f"Status {statusid}", value=f"{statusName[0]}", inline=False)
        embed.add_field(name="Timer", value=timer_string, inline=False)
        embed.set_image(url=f"https://api.ffxivsonar.com/render/map?zoneid={zone_id}&flagx={flagXcoord}&flagy={flagYcoord}&fate=true")
        contentstring = f"<@&{senmurv_role_id}> Senmurv Fate on {worldName[0]}"
        #message = webhookFateSrank.send(embed=embed, wait=True, content=contentstring)
        if (fate_id, world_id) in message_ids:
            message_id, _ = message_ids[(fate_id, world_id)]
            message = webhookFateSrank.edit_message(message_id, embed=embed, content=contentstring)
        else:
            message = webhookFateSrank.send(embed=embed, wait=True, content=contentstring)
            message_ids[(fate_id, world_id)] = (message.id, time.time())
        print(message.id)
        #previous_message_id = message.id
        #print("message ID: " + previous_message_id)
    else:
        print(f"Filtered event: ID={fate_id}, WorldID={world_id}, {fateName}, {worldName}")
    pass


async def process_fate_minhocao(event):
        #Get Raw data
    fate_id = event.get("Id")
    world_id = event.get("WorldId")
    zone_id = event.get("ZoneId")
    coords = event.get('Coords')
    rawxcoord = coords.get('X')
    rawycoord = coords.get('Y')
    progress = event.get('Progress')
    statusid = event.get('Status')
    start_time = event.get("StartTime") / 1000  # Convert milliseconds to seconds
    duration = event.get("Duration") / 1000  # Convert milliseconds to seconds
    
    #process raw data
    flagXcoord = str((41 * ((rawxcoord + 1024) / 2048)) + 1)[:4]
    flagYcoord = str((41 * ((rawycoord + 1024) / 2048)) + 1)[:4]
    worlds = huntDic['WorldDictionary']
    worldName = worlds[str(world_id)]
    fates = huntDic['FateDictionary']
    fateName = fates[str(fate_id)]
    zones = huntDic['zoneDictionary']
    zoneName = zones[str(zone_id)]
    status = huntDic['FateStatus']
    statusName = status[str(statusid)]

    # Calculate the elapsed time since the fate started
    current_time = datetime.now().timestamp()
    elapsed_time = current_time - start_time
    remaining_time = max(0, duration - elapsed_time)
    remaining_minutes = int(remaining_time // 60)
    remaining_seconds = int(remaining_time % 60)
    duration_minutes = int(duration // 60)
    duration_seconds = int(duration % 60)

    # Create the timer string in the format "01:00 / 15:00"
    timer_string = f"{remaining_minutes:02d}:{remaining_seconds:02d} / {duration_minutes:02d}:{duration_seconds:02d}"
   
    if fate_id and zoneName:
        print('')
        print(f"Filtered event: {fateName} {worldName} Fate posted to Discord")
        print('')
        print(event)
        embed=discord.Embed(title=f"**[{worldName[0]}] Minhocao Fate - Core Blimey**", color=0x633ada)
        embed.add_field(name="Progress:", value=f"{progress} %", inline=True)
        embed.add_field(name="Zone: ", value=f"{zoneName[0]}", inline=True)
        embed.add_field(name=f"Status {statusid}", value=f"{statusName[0]}", inline=False)
        embed.add_field(name="Timer", value=timer_string, inline=False)
        embed.set_image(url=f"https://api.ffxivsonar.com/render/map?zoneid={zone_id}&flagx={flagXcoord}&flagy={flagYcoord}&fate=true")
        contentstring = f"<@&{minhocao_role_id}> Minhocao Fate on {worldName[0]}"
        #message = webhookFateSrank.send(embed=embed, wait=True, content=contentstring)
        if (fate_id, world_id) in message_ids:
            message_id, _ = message_ids[(fate_id, world_id)]
            message = webhookFateSrank.edit_message(message_id, embed=embed, content=contentstring)
        else:
            message = webhookFateSrank.send(embed=embed, wait=True, content=contentstring)
            message_ids[(fate_id, world_id)] = (message.id, time.time())
        print(message.id)
##        previous_message_id = message.id
##        print("message ID: " + previous_message_id)
    else:
        print(f"Filtered event: ID={fate_id}, WorldID={world_id}, {fateName}, {worldName}")
    pass


async def filter_events():
    try:
        async with websockets.connect("wss://api.ffxivsonar.com/feed/relay") as websocket:
            while True:
                data = await websocket.recv()
                event = json.loads(data)
                event_type = event.get("Type")
                fate_id = event.get("Id")
                world_id = event.get("WorldId")
                status_id = event.get("Status")

                if event_type in filter_types and fate_id in [1259, 831, 556] and world_id in filter_worlds:
                    if fate_id == 1259:
                        await process_fate_orghana(event)
                    elif fate_id == 831:
                        await process_fate_senmurv(event)
                    elif fate_id == 556:
                        await process_fate_minhocao(event)

                    # Check if the status is 3 (completed) or 4 (failed)
                    # or if the message ID is older than the maximum age
                    if status_id in [3, 4] or (fate_id, world_id) in message_ids and time.time() - message_ids[(fate_id, world_id)][1] > MAX_MESSAGE_AGE:
                        del message_ids[(fate_id, world_id)]

    except websockets.exceptions.ConnectionClosedError:
        print("WebSocket connection closed unexpectedly. Reconnecting...")
        await websocket.close()
        await asyncio.sleep(5)  # Wait for a few seconds before reconnecting
        
        # Re-establish the WebSocket connection
        await establish_connection()
        
        # Retry the filter_events() function
        await filter_events()



async def establish_connection():
    await filter_events()
    pass

async def main():
    await establish_connection()
    await filter_events()

asyncio.run(main())
