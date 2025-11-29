import asyncio
import json
import websockets
from discord import Webhook, SyncWebhook
import discord
import time
import sqlite3
import aiohttp
import aiosqlite
import traceback

import config
import utils
import db_utils
from utils import MessageState

# Local dictionaries for tracking state
SS_ids = {} #storing minion spawns so I can check if already posted
message_ids = {}  # Dictionary to store message IDs so I can edit posts with new information

# Debug webhook
webhookDebug = SyncWebhook.from_url(config.DEBUG_URL)

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
            flagXcoord, flagYcoord = utils.get_flag_coordinates(rawX, rawY)
            worldName = config.EU_WORLDS[str(world_id)]
            mobName = config.MOBS[str(hunt_id)]
            zoneName = config.ZONES[str(zone_id)]
            HPpercent = (currenthp / maxHP) * 100
            trueTime = str(int(time.time()))
            
            
            #assign urls and role ping IDs
            webhook_url = None
            srank_role_id = None
            srank_exp = None

            if str(world_id) in config.WORLDS:
                webhook_url = config.LIGHT_WEBHOOK_URL
                srank_role_id = config.LIGHT_ROLE_ID
                if zone_id in config.ARR_ZONES: srank_exp = config.ARR_SRANK
                elif zone_id in config.HW_ZONES: srank_exp = config.HW_SRANK
                elif zone_id in config.SB_ZONES: srank_exp = config.SB_SRANK
                elif zone_id in config.SHB_ZONES: srank_exp = config.SHB_SRANK
                elif zone_id in config.EW_ZONES: srank_exp = config.EW_SRANK
                elif zone_id in config.DT_ZONES: srank_exp = config.DT_SRANK
            elif str(world_id) in config.C_WORLDS:
                webhook_url = config.CHAOS_WEBHOOK_URL
                srank_role_id = config.CHAOS_ROLE_ID
                if zone_id in config.ARR_ZONES: srank_exp = config.C_ARR_SRANK
                elif zone_id in config.HW_ZONES: srank_exp = config.C_HW_SRANK
                elif zone_id in config.SB_ZONES: srank_exp = config.C_SB_SRANK
                elif zone_id in config.SHB_ZONES: srank_exp = config.C_SHB_SRANK
                elif zone_id in config.EW_ZONES: srank_exp = config.C_EW_SRANK
                elif zone_id in config.DT_ZONES: srank_exp = config.C_DT_SRANK
            elif str(world_id) in config.S_WORLDS:
                webhook_url = config.SHADOW_WEBHOOK_URL
                srank_role_id = config.SHADOW_ROLE_ID
                if zone_id in config.ARR_ZONES: srank_exp = config.S_ARR_SRANK
                elif zone_id in config.HW_ZONES: srank_exp = config.S_HW_SRANK
                elif zone_id in config.SB_ZONES: srank_exp = config.S_SB_SRANK
                elif zone_id in config.SHB_ZONES: srank_exp = config.S_SHB_SRANK
                elif zone_id in config.EW_ZONES: srank_exp = config.S_EW_SRANK
                elif zone_id in config.DT_ZONES: srank_exp = config.S_DT_SRANK
            elif str(world_id) in config.M_WORLDS:
                webhook_url = config.MATERIA_WEBHOOK_URL
                srank_role_id = config.MATERIA_ROLE_ID
                if zone_id in config.ARR_ZONES: srank_exp = config.M_ARR_SRANK
                elif zone_id in config.HW_ZONES: srank_exp = config.M_HW_SRANK
                elif zone_id in config.SB_ZONES: srank_exp = config.M_SB_SRANK
                elif zone_id in config.SHB_ZONES: srank_exp = config.M_SHB_SRANK
                elif zone_id in config.EW_ZONES: srank_exp = config.M_EW_SRANK
                elif zone_id in config.DT_ZONES: srank_exp = config.M_DT_SRANK
            
            
            if hunt_id and zoneName and webhook_url:    
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
                        if hunt_id in config.SS_IDS: #if its a ss, delete from ss_ids.
                            del SS_ids[(world_id, zone_id, instance)]
                            del message_ids[(hunt_id, world_id, actorID)]
                            return 'SS event over'
                        else:#delete from message ids and save to database; deathtimer, yeet old mapping, save srank spot to new mapping
                            #del message_ids[(hunt_id, world_id, actorID)]
                            await db_utils.save_s_rank_death(hunt_id, world_id, message_state.message_id, deathtimer, actorID, instance)
                            await db_utils.delete_mapping(world_id, zone_id, instance)
                            await db_utils.save_mapping_to_db(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, int(rawX), int(rawY), actorID, timestamp)
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
                        if hunt_id in config.SS_IDS: #if its a ss, delete from ss_ids
                            del SS_ids[(world_id, zone_id, instance)]
                            del message_ids[(hunt_id, world_id, actorID)]
                            return 'SS event over'
                        else:#delete from message ids and save to database; deathtimer, yeet old mapping, save srank spot to new mapping
                            #del message_ids[(hunt_id, world_id, actorID)]
                            await db_utils.save_s_rank_death(hunt_id, world_id, message_state.message_id, deathtimer, actorID, instance)
                            await db_utils.delete_mapping(world_id, zone_id, instance)
                            await db_utils.save_mapping_to_db(hunt_id, world_id, instance, zone_id, flagXcoord, flagYcoord, int(rawX), int(rawY), actorID, timestamp)
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
            
        except aiosqlite.Error as e:
            print(f"Database error {e}")
            webhookDebug.send("PLG: Unexpected error in process_hunts() with database, if you get no further error, restart script")
            webhookDebug.send(traceback.format_exc(chain=False))
            return f"failed to process data due to DB error: {e}"

        
        except Exception as e:
            print(f"Uexpected error: {e}")
            webhookDebug.send("PLG: Unexpected error in process_hunts(), if you get no further error, restart script")
            webhookDebug.send(traceback.format_exc(chain=False))
            return f"failed to process data due to unexpected error: {e}"
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
            flagXcoord, flagYcoord = utils.get_flag_coordinates(rawX, rawY)
            trueTime = str(int(time.time()))
            zoneName = config.ZONES[str(zone_id)]
            worldName = config.EU_WORLDS[str(world_id)]
            mapurl = f"https://assets.ffxivsonar.com/ssminions/{zone_id}.jpg"
            ssRankDead = f"SS Minion on **[{worldName[0]}]** - **{zoneName[0]}** - **x** **{flagXcoord}** **y** **{flagYcoord}** -  has died at <t:{trueTime}:f>"
            ssRankDeadInstance = f"SS Minion on **[{worldName[0]}]** - **{zoneName[0]}** - **x** **{flagXcoord}** **y** **{flagYcoord}** in Instance: {instance} has died at <t:{trueTime}:f>"
            embed=discord.Embed(title=f" SS MINIONS - **[{worldName[0]}]**  - **{zoneName[0]}**", color=0xe1e100)
            embed.set_image(url=mapurl)
            #Determine which webhook url to use
            webhook_url = None
            if str(world_id) in config.WORLDS:
                webhook_url = config.LIGHT_WEBHOOK_URL
            elif str(world_id) in config.C_WORLDS:
                webhook_url =  config.CHAOS_WEBHOOK_URL
            elif str(world_id) in config.S_WORLDS:
                webhook_url = config.SHADOW_WEBHOOK_URL
            elif str(world_id) in config.M_WORLDS:
                webhook_url = config.MATERIA_WEBHOOK_URL 
            
            if webhook_url:
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
        
async def connect_websocket():
    while True:  # This loop will keep trying to connect
        try:
            async with websockets.connect(config.WEBSOCKET_URL) as websocket:
                while True:
                    data = await websocket.recv()
                    event = json.loads(data)
                    event_type = event.get("Type")
                    world_id = event.get("WorldId")
                    hunt_id = event.get("Id")
                    
                    #if event is SS minion, then send to process_ss>
                    if event_type in config.FILTER_TYPES_HUNT and hunt_id in config.SS_MINION_IDS and str(world_id) in config.EU_WORLDS:
                        await process_ss(event)
                    #if event is normal S-rank, then send to process_hunts
                    elif event_type in config.FILTER_TYPES_HUNT and str(world_id) in config.EU_WORLDS and str(hunt_id) in config.MOBS:
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

asyncio.run(main())

