# honeyhunts S-rank and s-rank fates bot.

Join the discord: https://discord.gg/ACePrQAmtH

Send ffxiv s ranks to discord through webhooks. This project is connecting to a websocket from an external service providing S rank spawn and death notifications, reformats them and sends them to discord.
includes:


sonarsrank.py - Sends S rank notifications using embed with map link. Edits post on new websocket events containing new info, such as player numbers and HP%. Hardcoded for Light, change this if needed.

Csonarsrank.py - the same but for Chaos DC. I use 2 scripts right now because i havent merged them yet, will probably just do that later. Hardcoded for Chaos, change this if needed.

sonarfates.py - Sends fate notifications related to S-rank spawning, currently only relevant for Minhocao, Orghana and Senmurv S ranks. Hardcoded for Light, change this if needed.
It checks in database made by sonarsrank.py for relevant S rank death timers and will only post if spawn window is open.

getFates.py - Simple fetch from database made by sonarfates.py. Will fetch last 5 known fate states on a world and return it. Hardcoded for Light, change this if needed.

See "HuntDictionary.json" in repo for example of dictionary expected, this is built for Light datacenter and will reflect that.


HUNT_DICT_URL="foo.bar/HuntDictionary.json"

WEBHOOK_URL="https://discord.com/api/webhooks/0000000000000000000000"

SRANK_ROLE_ID="00000000000000"

WEBSOCKET_URL="wss://somewebsocket.somewhere"

SENMURV_ROLE="00000000000000"

ORGHANA_ROLE="00000000000000"

MINHOCAO_ROLE="00000000000000"

WEBHOOK_FATE_URL="https://discord.com/api/webhooks/0000000000000000000000"

Ressources folder has scripts to pull world ID's and mob ID's, edit these to include your API key and run.
Note that xivApi does not have complete data for world ID's as of writing. If you need any world IDs that are missing, feel free to contact.


Feel free to make PRs if relevant. Can be new features or optimization. Im not a software developer, this is my first "real" project while im learning for hobby projects, code is ugly.
