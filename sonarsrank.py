import asyncio
import json
import websockets
from dotenv import load_dotenv
from discord import Webhook, SyncWebhook
import discord
import requests
import os
import time
import sqlite3
import aiohttp
import traceback
# Load environment variables
load_dotenv()
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL")
filter_types = ["Hunt"]
huntDict_url = os.getenv("HUNT_DICT_URL")
huntDic = requests.get(huntDict_url).json()
lightUrl = os.getenv("WEBHOOK_URL")
chaosUrl = os.getenv("CWEBHOOK_URL")
shadowUrl = os.getenv("SWEBHOOK_URL")
materiaUrl = os.getenv("MWEBHOOK_URL")
light_role_id = os.getenv("SRANK_ROLE_ID")
chaos_role_id = os.getenv("CSRANK_ROLE_ID")
shadow_role_id = os.getenv("SSRANK_ROLE_ID")
materia_role_id = os.getenv("MSRANK_ROLE_ID")
arr_srank = os.getenv("ARR_SRANK")
hw_srank = os.getenv("HW_SRANK")
sb_srank = os.getenv("SB_SRANK")
shb_srank = os.getenv("SHB_SRANK")
ew_srank = os.getenv("EW_SRANK")
dt_srank = os.getenv("DT_SRANK")
c_arr_srank = os.getenv("C_ARR_SRANK")
c_hw_srank = os.getenv("C_HW_SRANK")
c_sb_srank = os.getenv("C_SB_SRANK")
c_shb_srank = os.getenv("C_SHB_SRANK")
c_ew_srank = os.getenv("C_EW_SRANK")
c_dt_srank = os.getenv("C_DT_SRANK")
m_arr_srank = os.getenv("M_ARR_SRANK")
m_hw_srank = os.getenv("M_HW_SRANK")
m_sb_srank = os.getenv("M_SB_SRANK")
m_shb_srank = os.getenv("M_SHB_SRANK")
m_ew_srank = os.getenv("M_EW_SRANK")
m_dt_srank = os.getenv("M_DT_SRANK")
s_arr_srank = os.getenv("S_ARR_SRANK")
s_hw_srank = os.getenv("S_HW_SRANK")
s_sb_srank = os.getenv("S_SB_SRANK")
s_shb_srank = os.getenv("S_SHB_SRANK")
s_ew_srank = os.getenv("S_EW_SRANK")
s_dt_srank = os.getenv("S_DT_SRANK")




#dictionaries from json url
worlds = huntDic['WorldDictionary']
cworlds = huntDic['CWorldDictionary']
sworlds = huntDic['SWorldDictionary']
mworlds = huntDic['MWorldDictionary']
EUworlds = huntDic['EUWorldDictionary']
zones = huntDic['zoneDictionary']
mobs = huntDic['MobDictionary']
#zone_ids for each expansion
arr = [134, 135, 137, 138, 139, 140, 141, 145, 146, 147, 148, 152, 153, 154, 155, 156, 180]
hw = [397, 398, 399, 400, 401, 402]
sb = [612, 613, 614, 620, 621, 622]
shb = [813, 814, 815, 816, 817, 818]
ew = [956, 957, 958, 959, 960, 961]
dt = [1187, 1188, 1189, 1190, 1191, 1192]

#SS autismo
ss = [8915, 10615, 13406]
ss_minion = [8916, 10616, 13407]
SS_ids = {} #storing minion spawns so I can check if already posted
message_ids = {}  # Dictionary to store message IDs so I can edit posts with new information
#Debug webhook, send errors to discord channel
debug_url = os.getenv("DEBUG_URL")
webhookDebug = SyncWebhook.from_url(debug_url)

#make less ugly?
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
            worldName = EUworlds[str(world_id)]
            mobName = mobs[str(hunt_id)]
            zoneName = zones[str(zone_id)]
            HPpercent = (currenthp / maxHP) * 100
            trueTime = str(int(time.time()))
            
            
            #assign urls and role ping IDs
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
                elif zone_id in dt:
                    srank_exp = dt_srank
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
                elif zone_id in dt:
                    srank_exp = c_dt_srank
            if str(world_id) in sworlds:
                webhook_url = shadowUrl
                srank_role_id = shadow_role_id
                if zone_id in arr:
                    srank_exp = s_arr_srank
                elif zone_id in hw:
                    srank_exp = s_hw_srank
                elif zone_id in sb:
                    srank_exp = s_sb_srank
                elif zone_id in shb:
                    srank_exp = s_shb_srank
                elif zone_id in ew:
                    srank_exp = s_ew_srank
                elif zone_id in dt:
                    srank_exp = s_dt_srank
            if str(world_id) in mworlds:
                webhook_url = materiaUrl
                srank_role_id = materia_role_id
                if zone_id in arr:
                    srank_exp = m_arr_srank
                elif zone_id in hw:
                    srank_exp = m_hw_srank
                elif zone_id in sb:
                    srank_exp = m_sb_srank
                elif zone_id in shb:
                    srank_exp = m_shb_srank
                elif zone_id in ew:
                    srank_exp = m_ew_srank
                elif zone_id in dt:
                    srank_exp = m_dt_srank
            
            
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
                embeddead=discord.Embed(title=f"~~{worldName[0]}  - {mobName[0]} - x {flagXcoord} y {flagYcoord}~~", color=0xF04C5C)
                embeddead.add_field(name="~~Players:~~", value=f"{players}", inline=True)
                embeddead.add_field(name="~~HP %~~", value="~~0 %~~", inline=True)
                webhookSrank = Webhook.from_url(webhook_url, session=session)
                
                
                #if not in instance
                if instance == 0:
                    #check if dead
                    if currenthp == 0:
                        await webhookSrank.send(sRankDead)
                        deathtimer = str(int(time.time()))
                        timestamp = str(int(time.time()))
                        message_state = message_ids[(hunt_id, world_id, actorID)]
                        editcontentstring = f"<@&{srank_role_id}> <@&{srank_exp}> on **[{worldName[0]}]** - **{mobName[0]}** spawned <t:{message_state.firsttime}:R>"
                        message = await webhookSrank.edit_message(message_state.message_id, embed=embeddead, content=editcontentstring)
                        if hunt_id in ss: #if its a ss, delete from ss_ids.
                            del SS_ids[(world_id, zone_id, instance)]
                            del message_ids[(hunt_id, world_id, actorID)]
                            return 'SS event over'
                        else:#delete from message ids and save to database; deathtimer, yeet old mapping, save srank spot to new mapping
                            #del message_ids[(hunt_id, world_id, actorID)]
                            await save_to_database(hunt_id, world_id, message_state.message_id, deathtimer, actorID, instance)
                            await deleteMapping(world_id, zone_id, instance)
                            await saveMappingToDB(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, int(rawX), int(rawY), actorID, timestamp)
                    else: #if alive check if already posted, if not then post.
                        #check if mob already in message_ids, if it is then update the post
                        if (hunt_id, world_id, actorID) in message_ids:
                            message_state = message_ids[(hunt_id, world_id, actorID)]
                            if message_state.needs_update(currenthp, players):
                                editcontentstring = f"<@&{srank_role_id}> <@&{srank_exp}> on **[{worldName[0]}]** - **{mobName[0]}** spawned <t:{message_state.firsttime}:R>"
                                embed.set_image(url=message_state.map_url)
                                message = await webhookSrank.edit_message(message_state.message_id, embed=embed, content=editcontentstring)
                                message_state.update(currenthp, players)
                        else: #initial post
                            firsttime = str(int(time.time()))
                            contentstring = f"<@&{srank_role_id}> <@&{srank_exp}> on **[{worldName[0]}]** - **{mobName[0]}** spawned <t:{firsttime}:R>"
                            message = await webhookSrank.send(embed=embed, wait=True, content=contentstring)
                            message_state = MessageState(message.id, firsttime, mapurl, currenthp, players)
                            message_ids[(hunt_id, world_id, actorID)] = message_state
                else:#if in instance
                    #check if dead
                    if currenthp == 0:
                        await webhookSrank.send(sRankDeadInstance)
                        deathtimer = str(int(time.time()))
                        timestamp = str(int(time.time()))
                        message_state = message_ids[(hunt_id, world_id, actorID)]
                        editcontentstring = f"<@&{srank_role_id}> <@&{srank_exp}> on **[{worldName[0]}]** - **{mobName[0]}** in **Instance: {instance}** spawned <t:{message_state.firsttime}:R>"
                        message = await webhookSrank.edit_message(message_state.message_id, embed=embeddead, content=editcontentstring)
                        if hunt_id in ss: #if its a ss, delete from ss_ids
                            del SS_ids[(world_id, zone_id, instance)]
                            del message_ids[(hunt_id, world_id, actorID)]
                            return 'SS event over'
                        else:#delete from message ids and save to database; deathtimer, yeet old mapping, save srank spot to new mapping
                            #del message_ids[(hunt_id, world_id, actorID)]
                            await save_to_database(hunt_id, world_id, message_state.message_id, deathtimer, actorID, instance)
                            await deleteMapping(world_id, zone_id, instance)
                            await saveMappingToDB(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, int(rawX), int(rawY), actorID, timestamp)
                    else: #if alive check if already posted, if not then post.
                        #check if mob already in message_ids, if it is then update the post
                        if (hunt_id, world_id, actorID) in message_ids:
                            message_state = message_ids[(hunt_id, world_id, actorID)]
                            if message_state.needs_update(currenthp, players):
                                editcontentstring = f"<@&{srank_role_id}> <@&{srank_exp}> on **[{worldName[0]}]** - **{mobName[0]}** in **Instance: {instance}** spawned <t:{message_state.firsttime}:R>"
                                embed.set_image(url=message_state.map_url)
                                embed.add_field(name="Instance: ", value=f"{instance}", inline=True)
                                message = await webhookSrank.edit_message(message_state.message_id, embed=embed, content=editcontentstring)
                                message_state.update(currenthp, players)
                        else: #if not in message_ids, make a new post and save to message_ids/message_state
                            firsttime = str(int(time.time()))
                            contentstring = f"<@&{srank_role_id}> <@&{srank_exp}> on **[{worldName[0]}]** - **{mobName[0]}** in **Instance: {instance}** spawned <t:{firsttime}:R>"
                            embed.add_field(name="Instance: ", value=f"{instance}", inline=True)
                            message = await webhookSrank.send(embed=embed, wait=True, content=contentstring)
                            message_state = MessageState(message.id, firsttime, mapurl, currenthp, players)
                            message_ids[(hunt_id, world_id, actorID)] = message_state


            return 'Data processed and sent to webhook'
            
        except sqlite3.Error as e:
            print(f"Database error {e}")
            webhookDebug.send("Unexpected error in process_hunts() with database, if you get no further error, restart script")
            webhookDebug.send(traceback.format_exc(chain=False))
            return f"failed to process data due to DB error: {e}"

        
        except Exception as e:
            print(f"Uexpected error: {e}")
            webhookDebug.send("Unexpected error in process_hunts(), if you get no further error, restart script")
            webhookDebug.send(traceback.format_exc(chain=False))
            return f"failed to process data due to unexpected error: {e}"



#make less ugly?
async def process_ss(event):
    async with aiohttp.ClientSession() as session2:
        try:
            #get raw data from event
            zone_id = event.get("ZoneId")
            world_id = event.get("WorldId")
            coords = event.get('Coords')
            rawX = coords.get('X')
            rawY = coords.get('Y')
            instance = event.get('InstanceId')
            currenthp = event.get('CurrentHp')
            hunt_id = event.get("Id")
            #process raw data 
            flagXcoord = str((41 * ((rawX + 1024) / 2048)) + 1)[:4]
            flagYcoord = str((41 * ((rawY + 1024) / 2048)) + 1)[:4]
            trueTime = str(int(time.time()))
            zoneName = zones[str(zone_id)]
            worldName = EUworlds[str(world_id)]
            mapurl = f"https://assets.ffxivsonar.com/ssminions/{zone_id}.jpg"
            ssRankDead = f"SS Minion on **[{worldName[0]}]** - **{zoneName[0]}** - **x** **{flagXcoord}** **y** **{flagYcoord}** -  has died at <t:{trueTime}:f>"
            ssRankDeadInstance = f"SS Minion on **[{worldName[0]}]** - **{zoneName[0]}** - **x** **{flagXcoord}** **y** **{flagYcoord}** in Instance: {instance} has died at <t:{trueTime}:f>"
            embed=discord.Embed(title=f" SS MINIONS - **[{worldName[0]}]**  - **{zoneName[0]}**", color=0xe1e100)
            embed.set_image(url=mapurl)
            #Determine which webhook url to use
            if str(world_id) in worlds:
                webhook_url = lightUrl
            elif str(world_id) in cworlds:
                webhook_url =  chaosUrl
            elif str(world_id) in sworlds:
                webhook_url = shadowUrl
            elif str(world_id) in mworlds:
                webhook_url = materiaUrl 
            webhookSrank = Webhook.from_url(webhook_url, session=session2)            

            #if not in instance
            if instance == 0:
                #check if dead
                if currenthp == 0:
                    await webhookSrank.send(ssRankDead)
                #check if already posted, if not then post
                else:
                    if (world_id, zone_id, instance) in SS_ids:
                        return 'ss already posted'
                    firsttime = str(int(time.time()))
                    contentstring = f"SS Minion on **[{worldName[0]}]** - **{zoneName[0]}** - spawned <t:{firsttime}:R>"
                    message = await webhookSrank.send(embed=embed, wait=True, content=contentstring)
                    SS_ids[(world_id, zone_id, instance)] = (hunt_id, message.id, firsttime, mapurl)
            #else in instance and dead
            elif currenthp == 0:
                await webhookSrank.send(ssRankDeadInstance)
            #else in instance, check if already posted, if not then post
            else:
                if (world_id, zone_id, instance) in SS_ids:
                    return 'ss already posted'
                firsttime = str(int(time.time()))
                contentstring = f"SS Minion on **{worldName[0]}** - **{zoneName[0]}** - in **Instance: {instance}** spawned <t:{firsttime}:R>"
                message = await webhookSrank.send(embed=embed, wait=True, content=contentstring)
                SS_ids[(world_id, zone_id, instance)] = (hunt_id, message.id, firsttime, mapurl)
            return 'Data processed and sent to webhook'
        
        except Exception as e:
            webhookDebug.send("Unexpected in process_ss(), if you get no further error, restart script")
            webhookDebug.send(traceback.format_exc(chain=False))
            return f"failed to process data due to error {e}"
        
#class for storing and checking variables for changes. I implemented this to avoid needless edits to avoid rate limiting.
class MessageState:
    def __init__(self, message_id, firsttime, map_url, current_hp, players):
        self.message_id = message_id
        self.firsttime = firsttime
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
                    #if event is SS minion, then send to process_ss>
                    if event_type in filter_types and hunt_id in ss_minion and str(world_id) in EUworlds:
                        await process_ss(event)
                    #if event is normal S-rank, then send to process_hunts
                    elif event_type in filter_types and str(world_id) in EUworlds and str(hunt_id) in mobs:
                        await process_hunts(event)
                    
                    
        except websockets.exceptions.ConnectionClosedError as e:
            await asyncio.sleep(5)  
            continue
                    
        except websockets.exceptions.ConnectionClosed as e:
            print(e)
            webhookDebug.send("Connection error with websocket in connect_websocket(), if you get no further error, restart script")
            webhookDebug.send(traceback.format_exc(chain=False))
            websocket.close()
            await asyncio.sleep(5)
            continue

        except Exception as e:
            print(f"Unexpected error with WebSocket: {e}")
            print("exc print")
            traceback.print_exc()
            webhookDebug.send("Unexpected error with websocket in connect_websocket(), if you get no further error, restart script")
            webhookDebug.send(traceback.format_exc(chain=False))
            print("stack print")
            traceback.print_stack()
            await asyncio.sleep(5)  
            continue


async def main():
    await connect_websocket()
    
#database for storing S rank deaths    
# def setup_database():
#     with sqlite3.connect('hunts.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS hunts (
#             hunt_id INTEGER,
#             world_id INTEGER,
#             message_id INTEGER,
#             deathtimer TIMESTAMP,
#             actorID TEXT,
#             PRIMARY KEY (actorID),
#             instance INTEGER
#         )
#         ''')
#     conn.commit()
#     conn.close()

#setup_database()

#Delete old mapping when S rank dies
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
#save S rank death to database
async def save_to_database(hunt_id, world_id, message_id, deathtimer, actorID, instance):
    conn = sqlite3.connect('hunts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO hunts (hunt_id, world_id, message_id, deathtimer, actorID, instance)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (hunt_id, world_id, message_id, deathtimer, actorID, instance))
    
    conn.commit()
    conn.close()
#S ranks will never spawn in the same place twice, so using the S rank death location as mapping is a free map point.    
async def saveMappingToDB(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, rawX, rawY, actorID, timestamp):
    conn = sqlite3.connect('hunts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO mapping (hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, rawX, rawY, actorID, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, rawX, rawY, actorID, timestamp))
    
    conn.commit()
    conn.close()

asyncio.run(main())
