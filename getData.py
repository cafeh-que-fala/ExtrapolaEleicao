import requests , json

    
def url_generator(role,uf,city_code,election_number):
    return  f"https://resultados.tse.jus.br/oficial/ele2022/{election_number}/dados/{uf}/{uf}{city_code}-c{role.zfill(4)}-e{election_number.zfill(6)}-v.json"

def get_city_data(role,uf,city_code,election_number,previous_election_number,url_generator): 
   
    bool_current_values = True
    current_response = requests.get(url_generator(role,uf,city_code,election_number)).json()
    previous_response = requests.get(url_generator(role,uf,city_code,previous_election_number)).json()
    pct_city_ballots_counted = float(current_response['abr'][0]['pst'].replace(',','.'))/100
    if pct_city_ballots_counted == 0:
        current_response  = None
        bool_current_values = False
    
    return (current_response,previous_response,bool_current_values)

def extrapolate_by_zone(current_response,previous_response,bool_current_values,valid_voting_number_tuple,votes,ballots_status):
    response = current_response or previous_response
    for vote_dict in response['abr']:
        if vote_dict['tpabr'] == "ZONA":
            bool_current_value_zone = bool_current_values
            pct_zone_ballots_counted = float(vote_dict['pst'].replace(',','.'))/100
            if pct_zone_ballots_counted == 0:
                bool_current_value_zone = False
                for dict in previous_response['abr']:
                    if dict['cdabr'] == vote_dict['cdabr']:
                        final_vote_dict = dict
                        pct_zone_ballots_counted = float(final_vote_dict['pst'].replace(',','.'))/100 
            else:
                final_vote_dict = vote_dict

            for cand in final_vote_dict['cand']:
                    n = cand['n']
                    if n in valid_voting_number_tuple:
                        #print(cand)
                        zone_votes_cand = int(cand['vap'])
                        if bool_current_value_zone:
                            votes['current'][n] += zone_votes_cand[n]
                        votes['extrapolated'][n] += zone_votes_cand/pct_zone_ballots_counted

            if not bool_current_value_zone:
                ballots_status['not started'] += 1
            elif pct_zone_ballots_counted < 1:
                ballots_status['partial'] += 1
            else:
                ballots_status['completed'] += 1

            
    # with open('tmp.json','w') as f:
    #     f.write(json.dumps(c or p,indent=4))