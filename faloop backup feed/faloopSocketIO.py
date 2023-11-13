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

username = os.getenv('FALOOP_USERNAME')
password = os.getenv('FALOOP_PASSWORD')
huntDict_url = os.getenv("HUNT_DICT_URL")
webhook_url = os.getenv('FALOOP_WEBHOOK')
huntDic = requests.get(huntDict_url).json()
srank_role_id = os.getenv("SRANK_ROLE_ID")

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
    discordPost(webhook_url, data)
    
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


def discordPost(webhook_url, data):
    # Ensure the data meets your criteria before sending
    if (data.get('type') == 'mob' and 
        data.get('subType') == 'report' and 
        data.get('data', {}).get('action') == 'spawn'):
        
        # Extract the relevant information
        mob_id = data['data']['mobId']
        world_id = data['data']['worldId']
        timestamp = data['data']['data']['timestamp']
        zone_id = data['data']['data']['zoneId']
        pos_id = int(data['data']['data']['zonePoiIds'][0])
        #ids to names
        worlds = huntDic['WorldDictionary']
        worldName = worlds[str(world_id)]
        mobs = huntDic['MobDictionary']
        mobName = mobs[str(mob_id)]
        zones = huntDic['zoneDictionary']
        zoneName = zones[str(zone_id)]
        coords = getCoords(pos_id, zone_id)
        print(coords)
        print(type(coords))
        timer = int(time.time())
        
        if coords:
            x, y = [value.strip() for value in coords.split(',')]
            mapurl = f"https://api.ffxivsonar.com/render/map?zoneid={zone_id}&flagx={x}&flagy={y}"
            message = f"<@&{srank_role_id}> {mobName[0]}, on world: {worldName[0]}, coords: {coords}, zone: {zoneName[0]}, Timestamp: <t:{timer}:R>, {mapurl}"
        
            # Create webhook instance and send the message
            faloopWebhook = SyncWebhook.from_url(webhook_url)
            faloopWebhook.send(message)
            print("Message sent to Discord successfully.")

def getCoords(pos_id, zone_id):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('faloopdb.db')
        cursor = conn.cursor()

        # Query to select the coordinates
        query = "SELECT coords FROM zone_positions WHERE posId = ? AND zoneId = ?"
        cursor.execute(query, (pos_id, zone_id))
        
        # Fetch the result
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        # Return the coordinates if found, otherwise return None
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None


try:
    
    responseJWTsessionID = getJWTsessionID()
    session_id = responseJWTsessionID.get("sessionId")
    jwt_token = responseJWTsessionID.get("token")

    
    login_response = login(session_id, jwt_token, username, password)
    

    
    connectFaloopSocketio(session_id, jwt_token)
except Exception as e:
    print(e)
