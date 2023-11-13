import requests
privatekey = ""
apiEndpoint = "https://xivapi.com"

###########################################
# Queries XIVAPI for hunt names and ID's  #
# 1 = b rank, 2 = A rank, 3 = S rank      #
###########################################


response = requests.get(apiEndpoint + f"/NotoriousMonster?private_key={privatekey}")
if response.status_code == 200:
    results = response.json()["Results"]
    pagination = response.json()["Pagination"]
else:
    raise Exception("Territory Type Page not Available")

urls = list()
for result in results:
    urls.append(result["Url"])

for page in range(1,pagination["PageTotal"]):
    response = requests.get(apiEndpoint + f"/NotoriousMonster?page={page+1}&private_key={privatekey}")
    if response.status_code == 200:
        results = response.json()["Results"]
        for result in results:
            urls.append(result["Url"])
    else:
        raise Exception(f"NotoriousMonster Page {page} not Available")

NotoriousMonsters = list()
for url in urls:
    response = requests.get(apiEndpoint + url + f"?private_key={privatekey}")
    if response.status_code == 200:
        result = response.json()
        if "BNpcName" in result.keys():
            if not result["BNpcName"] == None:
                Monster = {"Name": result["BNpcName"]["Name"], 
                           "Name_en": result["BNpcName"]["Name_en"], 
                           "Rank": result["Rank"],
                           "ID": result["BNpcName"]["ID"],
                           "Rank": result["Rank"]}
                if not Monster in NotoriousMonsters:
                     print(f"'{Monster['ID']}': '{Monster['Name_en']}' : {Monster['Rank']}")
                     NotoriousMonsters.append(Monster)
        else:
            break
