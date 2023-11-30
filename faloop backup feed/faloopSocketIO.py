import socketio
from faloopApiLogin import getJWTsessionID, login
from dotenv import load_dotenv
import os
load_dotenv()
from discord import SyncWebhook
import requests
import sqlite3
import time

sio = socketio.Client(logger=True, reconnection=True, reconnection_delay=5, reconnection_attempts=0)
1144937436498116728
username = os.getenv('FALOOP_USERNAME')
password = os.getenv('FALOOP_PASSWORD')
huntDict_url = os.getenv("HUNT_DICT_URL")
webhook_url = os.getenv('FALOOP_WEBHOOK')
faloopWebhook = SyncWebhook.from_url(webhook_url)
huntDic = requests.get(huntDict_url).json()
srank_role_id = os.getenv("SRANK_ROLE_ID")
csrank_role_id = os.getenv("CSRANK_ROLE_ID")
mobs = huntDic['MobDictionary']
worlds = huntDic['EUWorldDictionary']
lightWorlds = huntDic['WorldDictionary']
chaosWorlds = huntDic['CWorldDictionary']
zones = huntDic['zoneDictionary']
ss = [8815, 8916, 10615, 10616] #to filter out SS ranks and minions
zoneIds = {} #dictionary for storing zone_id on spawn to use again on death because floop doesnt send zone_id on death?????????

@sio.event
def connect():
    print("I'm connected!")

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

@sio.on('*', namespace='/mobStatus')
def catch_all(event, data):
    #print("Message received:", data)
    #print("event received: ", event)
    filter_data(data)
    
    with open('received_events.txt', 'a') as file:
        file.write(f"{data}\n")

def connectFaloopSocketio(session_id, jwt_token):
    
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en",
        "Referer": "https://faloop.app/",
        "Origin": "https://faloop.app",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }
    
    
    sio.connect(
        'https://comms.faloop.app/mobStatus',
        headers=headers,
        transports='websocket',
        namespaces='/mobStatus',
        wait=True,
        auth={'sessionid': session_id}
    )    
    
    sio.wait()

#spawned S rank
#{'type': 'mob', 'subType': 'report', 'data': {'action': 'spawn', 'mobId': 2962, 'worldId': 42, 'zoneInstance': 0, 'data': {'zoneId': 134, 'zonePoiIds': [27], 'timestamp': '2023-11-28T19:53:54.648Z', 'window': 1}}}
#dead srank
#{'type': 'mob', 'subType': 'report', 'data': {'action': 'death', 'mobId': 10618, 'worldId': 33, 'zoneInstance': 3, 'data': {'num': 1, 'startedAt': '2023-11-29T19:27:23.322Z', 'prevStartedAt': '2023-11-23T19:48:46.901Z'}}}
def filter_data(data):
    # Ensure the data meets your criteria before sending
    mobs = huntDic['MobDictionary']
    if (data.get('type') == 'mob' and 
        data.get('subType') == 'report' and 
        data.get('data', {}).get('action') == 'spawn' and
        str(data['data']['mobId']) in mobs and
        data['data']['mobId'] not in ss):
            hunt_id = data['data']['mobId']
            world_id = data['data']['worldId']
            zone_id = data['data']['data']['zoneId']
            pos_id = int(data['data']['data']['zonePoiIds'][0])
            instance = data['data']['zoneInstance']
            sendSpawn(data, hunt_id, world_id, zone_id, pos_id, instance)
            
    if (data.get('type') == 'mob' and 
        data.get('subType') == 'report' and 
        data.get('data', {}).get('action') == 'death' and
        str(data['data']['mobId']) in mobs and
        data['data']['mobId'] not in ss):
        
            hunt_id = data['data']['mobId']
            world_id = data['data']['worldId']
            instance = data['data']['zoneInstance']
            sendDeath(data, hunt_id, world_id, instance)
    
def sendSpawn(faloopWebhook, data, hunt_id, world_id, zone_id, pos_id, instance):
    worldName = worlds[str(world_id)]
    mobName = mobs[str(hunt_id)]
    zoneName = zones[str(zone_id)]
    coords = getCoords(pos_id, zone_id)
    timer = int(time.time())
    
    if coords:
        x, y = [value.strip() for value in coords.split(',')]
        mapurl = f"https://api.ffxivsonar.com/render/map?zoneid={zone_id}&flagx={x}&flagy={y}"
        if world_id in lightWorlds:
            srank_role = srank_role_id
        if world_id in chaosWorlds:
            srank_role = csrank_role_id  
        
        message = f"<@&{srank_role}> {mobName[0]}, on world: {worldName[0]}, coords: {coords}, zone: {zoneName[0]}, in instance: {instance}, Timestamp: <t:{timer}:R>, {mapurl}"
        zoneIds[(hunt_id, world_id, instance)] = (zone_id)
        faloopWebhook.send(message)
        faloopWebhook.send(data)
        print("Message sent to Discord successfully.")

def sendDeath(faloopWebhook, data, hunt_id, world_id, instance):
    worldName = worlds[str(world_id)]
    mobName = mobs[str(hunt_id)]
    zone_id = zoneIds[(hunt_id, world_id, instance)]
    
    message = f"Srank {mobName[0]} on {worldName[0]} in instance: {instance} died"
    faloopWebhook.send(message)
    faloopWebhook.send(data)
    print("death sent to Discord successfully.")
    deleteMapping(world_id, zone_id, instance)
    print("mapping yeeted")
    del zoneIds[(hunt_id, world_id, instance)]    
    
def getCoords(pos_id, zone_id):
    try:
        with sqlite3.connect('faloopdb.db') as conn:
            cursor = conn.cursor()
            query = "SELECT coords FROM zone_positions WHERE posId = ? AND zoneId = ?"
            cursor.execute(query, (pos_id, zone_id))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] if result else None
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None

def deleteMapping(world_id, zone_id, instance):
    try:
        with sqlite3.connect('hunts.db') as conn:
            cursor = conn.cursor()
            query = "DELETE FROM mapping WHERE world_id = ? AND zone_id = ? AND instance = ?"
            cursor.execute(query, (world_id, zone_id, instance))
            cursor.close()
            conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return f"Failed to delete entries due to DB error: {e}"

try:
    
    responseJWTsessionID = getJWTsessionID()
    session_id = responseJWTsessionID.get("sessionId")
    jwt_token = responseJWTsessionID.get("token")
    login_response = login(session_id, jwt_token, username, password)
    
    connectFaloopSocketio(session_id, jwt_token)
except Exception as e:
    print(e)
