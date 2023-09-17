# honeyhunts S-rank and s-rank fates bot.

Join the discord: https://discord.gg/ACePrQAmtH

Send ffxiv s ranks to discord through webhooks. This project is connecting to a websocket from an external service providing S rank spawn and death notifications, reformats them and sends them to discord.
includes:

Custom role mentions, edit these to reflect your servers role ID's.


Customizable notification texts and embeds

Instance detecting when relevant.
 

See "HuntDictionary.json" in repo for example, this is built for Light datacenter and will reflect that.


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



