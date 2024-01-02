import asyncio
import json
import websockets
from dotenv import load_dotenv
from discord import Webhook
import discord
import requests
import os
import time
import sqlite3
import aiohttp

# Load environment variables
load_dotenv()
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL")
filter_types = ["Hunt"]
huntDict_url = os.getenv("HUNT_DICT_URL")
huntDic = requests.get(huntDict_url).json()
lightUrl = os.getenv("WEBHOOK_URL")
chaosUrl = os.getenv("CWEBHOOK_URL")
light_role_id = os.getenv("SRANK_ROLE_ID")
chaos_role_id = os.getenv("CSRANK_ROLE_ID")
arr_srank = os.getenv("ARR_SRANK")
hw_srank = os.getenv("HW_SRANK")
sb_srank = os.getenv("SB_SRANK")
shb_srank = os.getenv("SHB_SRANK")
ew_srank = os.getenv("EW_SRANK")
c_arr_srank = os.getenv("C_ARR_SRANK")
c_hw_srank = os.getenv("C_HW_SRANK")
c_sb_srank = os.getenv("C_SB_SRANK")
c_shb_srank = os.getenv("C_SHB_SRANK")
c_ew_srank = os.getenv("C_EW_SRANK")
#zone_ids for each expansion
arr = [134, 135, 137, 138, 139, 140, 141, 145, 146, 147, 148, 152, 153, 154, 155, 156, 180]
hw = [397, 198, 399, 400, 401, 402]
sb = [612, 613, 614, 620, 621, 622]
shb = [813, 814, 815, 816, 817, 818]
ew = [956, 957, 958, 959, 960, 961]

message_ids = {}  # Dictionary to store message IDs


async def process_hunts(event):
    async with aiohttp.ClientSession() as session:
        try:
            #Get Raw data
            hunt_id = event.get("Id")
            world_id = event.get("WorldId")
            zone_id = event.get("ZoneId")
            coords = event.get('Coords')
            rawX = coords.get('X')
            rawY = coords.get('Y')
            instance = event.get('InstanceId')
            players = event.get('Players')
            currenthp = event.get('CurrentHp')
            maxHP = event.get('MaxHp')
            actorID = event.get('ActorId')
            

            #process raw data
            flagXcoord = str((41 * ((rawX + 1024) / 2048)) + 1)[:4]
            flagYcoord = str((41 * ((rawY + 1024) / 2048)) + 1)[:4]
            worlds = huntDic['WorldDictionary']
            cworlds = huntDic['CWorldDictionary']
            EUworlds = huntDic['EUWorldDictionary']
            worldName = EUworlds[str(world_id)]
            mobs = huntDic['MobDictionary']
            mobName = mobs[str(hunt_id)]
            zones = huntDic['zoneDictionary']
            zoneName = zones[str(zone_id)]
            HPpercent = (currenthp / maxHP) * 100
            trueTime = str(int(time.time()))
            
            
            
            if str(world_id) in worlds:
                webhook_url = lightUrl
                srank_role_id = light_role_id
                if zone_id in arr:
                    srank_exp = arr_srank
                elif zone_id in hw:
                    srank_exp = hw_srank
                elif zone_id in sb:
                    srank_exp = sb_srank
                elif zone_id in shb:
                    srank_exp = shb_srank
                elif zone_id in ew:
                    srank_exp = ew_srank
            if str(world_id) in cworlds:
                webhook_url = chaosUrl
                srank_role_id = chaos_role_id
                if zone_id in arr:
                    srank_exp = c_arr_srank
                elif zone_id in hw:
                    srank_exp = c_hw_srank
                elif zone_id in sb:
                    srank_exp = c_sb_srank
                elif zone_id in shb:
                    srank_exp = c_shb_srank
                elif zone_id in ew:
                    srank_exp = c_ew_srank            
            
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
                embeddead=discord.Embed(title=f"~~{worldName[0]}  - {mobName[0]} - x {flagXcoord} y {flagYcoord}~~", color=0xe1e100)
                embeddead.add_field(name="~~Players:~~", value=f"{players}", inline=True)
                embeddead.add_field(name="~~HP %~~", value="~~0 %~~", inline=True)
                webhookSrank = Webhook.from_url(webhook_url, session=session)
                

                # Logic for sending, instance, and death checking
                if instance != 0:
                    if currenthp == 0:
                        await webhookSrank.send(sRankDeadInstance)
                        deathtimer = str(int(time.time()))
                        timestamp = str(int(time.time()))
                        message_state = message_ids[(hunt_id, world_id, actorID)]
                        editcontentstring = f"<@&{srank_role_id}> <@&{srank_exp}> on **[{worldName[0]}]** - **{mobName[0]}** in **Instance: {instance}** spawned <t:{firsttime}:R>"
                        message = await webhookSrank.edit_message(message_state.message_id, embed=embeddead, content=editcontentstring)
                        del message_ids[(hunt_id, world_id, actorID)]
                        await save_to_database(hunt_id, world_id, message_state.message_id, deathtimer, actorID)
                        await deleteMapping(world_id, zone_id, instance)
                        await saveMappingToDB(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, int(rawX), int(rawY), actorID, timestamp)
                    else:
                        if (hunt_id, world_id, actorID) in message_ids:
                            message_state = message_ids[(hunt_id, world_id, actorID)]
                            if message_state.needs_update(currenthp, players):
                                editcontentstring = f"<@&{srank_role_id}> <@&{srank_exp}> on **[{worldName[0]}]** - **{mobName[0]}** spawned <t:{message_state.firsttime}:R>"
                                embed.set_image(url=message_state.map_url)
                                message = await webhookSrank.edit_message(message_state.message_id, embed=embed, content=editcontentstring)
                                message_state.update(currenthp, players)
                        else:
                            firsttime = str(int(time.time()))
                            contentstring = f"<@&{srank_role_id}> <@&{srank_exp}> on **[{worldName[0]}]** - **{mobName[0]}** in **Instance: {instance}** spawned <t:{firsttime}:R>"
                            message = await webhookSrank.send(embed=embed, wait=True, content=contentstring)
                            message_state = MessageState(message.id, firsttime, mapurl, currenthp, players)
                            message_ids[(hunt_id, world_id, actorID)] = message_state
                else:
                    if currenthp == 0:
                        await webhookSrank.send(sRankDead)
                        deathtimer = str(int(time.time()))
                        timestamp = str(int(time.time()))
                        message_state = message_ids[(hunt_id, world_id, actorID)]
                        editcontentstring = f"<@&{srank_role_id}> <@&{srank_exp}> on **[{worldName[0]}]** - **{mobName[0]}** spawned <t:{message_state.first_time}:R>"
                        message = await webhookSrank.edit_message(message_state.message_id, embed=embeddead, content=editcontentstring)
                        #print(message_ids)
                        del message_ids[(hunt_id, world_id, actorID)]
                        await save_to_database(hunt_id, world_id, message_state.message_id, deathtimer, actorID)
                        await deleteMapping(world_id, zone_id, instance)
                        await saveMappingToDB(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, int(rawX), int(rawY), actorID, timestamp)
                    else:
                        if (hunt_id, world_id, actorID) in message_ids:
                            message_state = message_ids[(hunt_id, world_id, actorID)]
                            if message_state.needs_update(currenthp, players):
                                editcontentstring = f"<@&{srank_role_id}> <@&{srank_exp}> on **[{worldName[0]}]** - **{mobName[0]}** in spawned <t:{message_state.first_time}:R>"
                                embed.set_image(url=message_state.map_url)
                                message = await webhookSrank.edit_message(message_state.message_id, embed=embed, content=editcontentstring)
                                message_state.update(currenthp, players)

                                #print(message_ids)

                        else:
                            firsttime = str(int(time.time()))
                            contentstring = f"<@&{srank_role_id}> <@&{srank_exp}> on **[{worldName[0]}]** - **{mobName[0]}** spawned <t:{firsttime}:R>"
                            message = await webhookSrank.send(embed=embed, wait=True, content=contentstring)
                            message_state = MessageState(message.id, firsttime, mapurl, currenthp, players)
                            message_ids[(hunt_id, world_id, actorID)] = message_state
                            #print(message_ids)

                return 'Data processed and sent to webhook'
            
        except sqlite3.Error as e:
            print(f"Database error {e}")
            return f"failed to process data due to DB error: {e}"
        
        except Exception as e:
            print(f"Uexpected error: {e}")
            return f"failed to process data due to error {e}"

class MessageState:
    def __init__(self, message_id, first_time, map_url, current_hp, players):
        self.message_id = message_id
        self.first_time = first_time
        self.map_url = map_url
        self.current_hp = current_hp
        self.players = players

    def needs_update(self, new_hp, new_players):
        return self.current_hp != new_hp or self.players != new_players

    def update(self, new_hp, new_players):
        self.current_hp = new_hp
        self.players = new_players
    

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
                    EUworlds = huntDic['EUWorldDictionary']

                    
                    if event_type in filter_types and str(world_id) in EUworlds and str(hunt_id) in mobs:
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
    with sqlite3.connect('hunts.db') as conn:
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

async def deleteMapping(world_id, zone_id, instance):
    try:
        with sqlite3.connect('hunts.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            DELETE FROM mapping
            WHERE world_id = ? AND zone_id = ? AND instance = ?
            ''', (world_id, zone_id, instance))
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return f"Failed to delete entries due to DB error: {e}"

async def save_to_database(hunt_id, world_id, message_id, deathtimer, actorID):
    conn = sqlite3.connect('hunts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO hunts (hunt_id, world_id, message_id, deathtimer, actorID)
    VALUES (?, ?, ?, ?, ?)
    ''', (hunt_id, world_id, message_id, deathtimer, actorID))
    
    conn.commit()
    conn.close()
    
async def saveMappingToDB(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, rawX, rawY, actorID, timestamp):
    conn = sqlite3.connect('hunts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO mapping (hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, rawX, rawY, actorID, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, rawX, rawY, actorID, timestamp))
    
    conn.commit()
    conn.close()
    
async def get_from_database(hunt_id, world_id):
    conn = sqlite3.connect('hunts.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT message_id, deathtimer FROM hunts WHERE hunt_id = ? AND world_id = ?', (hunt_id, world_id))
    result = cursor.fetchone()
    
    conn.close()
    return result

asyncio.run(main())
