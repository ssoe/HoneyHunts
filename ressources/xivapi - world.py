from requests_ratelimiter import LimiterSession
from time import time
privatekey = ""
apiEndpoint = "https://xivapi.com"

session = LimiterSession(per_second=5)
start = time()

###########################################
# Queries XIVAPI for world names and ID's #
###########################################

response = session.get(apiEndpoint + f"/world?private_key={privatekey}")
if response.status_code == 200:
    results = response.json()["Results"]
    pagination = response.json()["Pagination"]
else:
    raise Exception("Territory Type Page not Available")

urls = list()
for result in results:
    urls.append(result["Url"])

for page in range(1,pagination["PageTotal"]):
    response = session.get(apiEndpoint + f"/world?page={page+1}&private_key={privatekey}")
    if response.status_code == 200:
        results = response.json()["Results"]
        for result in results:
            urls.append(result["Url"])
    else:
        raise Exception(f"world Page {page} not Available")

NotoriousMonsters = list()
for url in urls:
    response = session.get(apiEndpoint + url + f"?private_key={privatekey}")
    if response.status_code == 200:
        result = response.json()
        if "GamePatch" in result.keys():
            if not result["GamePatch"] == None:
                Monster = {"InternalName_en": result["InternalName_en"],
                           "ID": result["ID"]}
                if not Monster in NotoriousMonsters:
                    print(f"{Monster['InternalName_en']} {Monster['ID']}")
                    NotoriousMonsters.append(Monster)
        else:
            break
