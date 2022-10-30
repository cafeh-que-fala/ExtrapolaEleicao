from concurrent.futures import thread
import time ,json, threading
from getData import extrapolate_by_zone,get_city_data,url_generator


def wrapper(role,uf,city_code,election_number,previous_election_number,url_generator,valid_voting_number_tuple,votes,ballots_status,counter):
    current_response,previous_response,bool_current_values = get_city_data(role,uf, city_code, election_number, previous_election_number, url_generator)
    extrapolate_by_zone(current_response,previous_response,bool_current_values,valid_voting_number_tuple,votes,ballots_status)
    counter[0] += 1
def state_wrapper(role,state_dict,election_number,previous_election_number,url_generator,valid_voting_number_tuple,votes,ballots_status,counter):
    uf = state_dict["cd"].lower()
    for city in state_dict["mu"]:
        city_code = city["cd"]
        wrapper(role,uf,city_code,election_number,previous_election_number, url_generator,valid_voting_number_tuple,votes,ballots_status,counter)

def printETA(counter,t0,len_cities):
    while counter[0] == 0:
        time.sleep(0.1)
    while counter[0] < len_cities:
        remaining = len_cities - counter[0] + 1
        eta = (time.time() - t0)/counter[0] *remaining
        print(f"\r{str(counter[0]).zfill(5)} / {len_cities} -- ETA: {eta:.1f}s    ",end="")
        time.sleep(0.5)

votes = {
    "current":{
        "13": 0,
        "22": 0
    },
    "extrapolated":{
        "13": 0,
        "22": 0
    },
    "extrapolated_pct":{
        "13":0,
        "22":0
    }
}
ballots_status = {
    "not started": 0,
    "partial":0,
    "completed":0
}



with open("municipios.json") as f:
    brazilian_cities_dictionary = json.loads(f.read())




cities = []
for state in brazilian_cities_dictionary['abr']:
    for city in state["mu"]:
        cities.append(city["cd"])
len_cities = len(cities)

t0 = time.time()
counter = [0]

threads = [threading.Thread(
    target=state_wrapper,
    args = ("1",state_dict,"545", "544",url_generator,("13","22"),votes,ballots_status,counter)
    ) for state_dict  in brazilian_cities_dictionary['abr']]
threads.append(threading.Thread(target=printETA, args = (counter,t0,len_cities)))

for my_thread in threads:
    my_thread.start()
for my_thread in threads:
    my_thread.join()
t1 = time.time()

votes["extrapolated_pct"]["13"] = votes["extrapolated"]["13"] / (votes["extrapolated"]["13"] + votes["extrapolated"]["22"])
votes["extrapolated_pct"]["22"] = votes["extrapolated"]["22"] / (votes["extrapolated"]["13"] + votes["extrapolated"]["22"])

print()
print(votes)
print(ballots_status)
print()
print(f"tempo gasto: {t1-t0}s")


#Gov : 
#Gov : https://resultados.tse.jus.br/oficial/ele2022/546/dados/sp/sp64033-c0003-e000546-v.json

