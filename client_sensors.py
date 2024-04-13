from requests import get, post
import time
#request usato da codice di sensore

#base_url = 'http://localhost:80'
base_url="http://34.154.27.7:80"

sensor = 's1'
#client che simula sensore leggendo dati e inviandoli al server
with open('CleanData_PM10.csv') as f:
    for l in f.readlines()[1:]:
        data,val = l.strip().split(',')
        print(data,val)
        #dati e valori inviati con funzione di libreria request
        #passo url richiesta
        #data è dizionario che riceve i dati
        r = post(f'{base_url}/sensors/{sensor}',
                 data={'data':data,'val':val})
        #sleep per mandare i dati poco per volta
        time.sleep(5)



print('done')
#NON SERVE MANDARE CLIENT SERVER NEL CLOUD PUò RIMANERE SUL NOSTRO PC