# honeyhunts S-rank and s-rank fates bot.

Join the discord: https://discord.gg/ACePrQAmtH

Send ffxiv s ranks to discord through webhooks. This project is connecting to a websocket from an external service providing S rank spawn and death notifications, reformats them and sends them to discord.
includes:


sonarsrank.py - Sends S rank notifications using embed with map link. Edits post on new websocket events containing new info, such as player numbers and HP%. Hardcoded for Light, chaos, shadow and materia, change this if needed.

sonarfates.py - Sends fate notifications related to S-rank spawning, currently only relevant for Minhocao, Orghana and Senmurv S ranks. Hardcoded for Light and chaos, change this if needed.
It checks in database made by sonarsrank.py for relevant S rank death timers and will only post if spawn window is open.

getFates.py - Simple fetch from database made by sonarfates.py. Will fetch last 5 known fate states on a world and return it. Hardcoded for Light and chaos, change this if needed.

mapping.py - Records A/B rank locations to database. Upon S rank death, sonarsrank.py will delete entries based on world_id, zone_id and instance number. Will probably be merged into other script later
Uses kmeans.py to more correctly draw dots on pre-made images due to spawn area variance. 
Uses maintmode.py to insert some hardcoded deaths into huntsDB for sonarfates to check against, after a maintenance.

See "HuntDictionary.json" in repo for example of dictionary expected, this is built for Light datacenter and will reflect that.


Example relays from websocket

Hunt:

{"ActorId":1073828849,"CurrentHp":914137,"MaxHp":992341,"Players":37,"Type":"Hunt","Key":"407_13145_1","Id":13145,"Coords":{"X":-680.0,"Y":188.0,"Z":59.0},"WorldId":407,"ZoneId":1187,"InstanceId":1}

Fate:

{"Progress":0,"Status":2,"StartTime":1721918545000.0,"Duration":1800000.0,"Type":"Fate","Key":"39_838_0","Id":838,"Coords":{"X":-453.0,"Y":701.0,"Z":-84.0},"WorldId":39,"ZoneId":398,"InstanceId":0}


Ressources folder has scripts to pull world ID's and mob ID's, edit these to include your API key and run.
Note that xivApi does not have complete data for world ID's as of writing. If you need any world IDs that are missing, feel free to contact.


Feel free to make PRs if relevant. Can be new features or optimization. Im not a software developer, this is my first "real" project while im learning for hobby projects, code is ugly.
