import requests
import time
import threading
UFs = [
 'ac',
 'al',
 'am',
 'ap',
 'ba',
 'ce',
 'df',
 'es',
 'go',
 'ma',
 'mg',
 'ms',
 'mt',
 'pa',
 'pb',
 'pe',
 'pi',
 'pr',
 'rj',
 'rn',
 'ro',
 'rr',
 'rs',
 'sc',
 'se',
 'sp',
 'to',
 'zz' # exterior
 ]
votos_atuais       =  {'13':0,'22':0}
votos_extrapolados =  {'13':0,'22':0}



def get_data(uf,votos_atuais,votos_extrapolados): 
   
    try: # Obtem dados do segundo turno
        bool_valoresAtuais = True
        response = requests.get(f"https://resultados.tse.jus.br/oficial/ele2022/545/dados/{uf}/{uf}-c0001-e000545-v.json").json()
        pct_urnas_apuradas_uf = float(response['abr'][0]['pst'].replace(',','.'))/100
        if pct_urnas_apuradas_uf == 0:
            raise ZeroDivisionError()
    except: # Caso não consiga obter OU essa UF não tenha nenhum voto no segundo turno até o momento, pegue os dados do 1o turno
        bool_valoresAtuais = False
        response = requests.get(f"https://resultados.tse.jus.br/oficial/ele2022/544/dados/{uf}/{uf}-c0001-e000544-v.json").json()
        pct_urnas_apuradas_uf = float(response['abr'][0]['pst'].replace(',','.'))/100
    
    votos_uf = {'13':0,'22':0}
    for dicionario_votos in response['abr'][0]['cand']:
        n = dicionario_votos['n']
        if n in ['13','22']:
            votos_uf[n] = int(dicionario_votos['vap'])
            if bool_valoresAtuais:
                votos_atuais[n]       += votos_uf[n]
            votos_extrapolados[n] += votos_uf[n]/pct_urnas_apuradas_uf

    print(uf)
            
threads = [threading.Thread(target=get_data, args=(uf,votos_atuais,votos_extrapolados)) for uf in UFs]

t0 = time.time()
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
t1 = time.time()


print("-------votos atuais---------")
print(f'Lula: {votos_atuais["13"]}')
print(f'Bolsonaro: {votos_atuais["22"]}')
print()
print("-------votos extrapolados---------")
print(f'Lula: {votos_extrapolados["13"]}')
print(f'Bolsonaro: {votos_extrapolados["22"]}')
print()
print(f"tempo gasto: {t1-t0}s")


#Gov : 
#Gov : https://resultados.tse.jus.br/oficial/ele2022/546/dados/sp/sp64033-c0003-e000546-v.json