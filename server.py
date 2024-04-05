from flask import Flask,request,redirect,url_for
import json

#libreria flaask per realizzare applicazioni web
app = Flask(__name__)#funzione che crea applicazione

db = {}
#endpoint: annotazione e funzione sottostante
@app.route('/graph',methods=["GET"])
def graph():
    #funzione che ridirige verso altra pagina che è un file che sitrova nella cartella static
    return redirect(url_for('static', filename='graph.html'))



@app.route('/sensors',methods=['GET'])
def sensors():
    #dizionario per rappresentare dati sensori: prese tutte chievi dizionario e trasfromate in stringa json e restituita
    #a client per vedere tutti sensori disponibili e sulla base di questo anche generare gli url giusti
    return json.dumps(list(db.keys())), 200

#CLIENT ASSOICATO A SENSORE S1
#post per scrivere dei dati
#url parametrico (<s>) per inserire dei parametri che possono essere dentro l'url
@app.route('/sensors/<s>',methods=['POST'])
def add_data(s):
    #request.values rappresenta il dizionario che è stato passato come parametro a una richiesta post
    data = request.values['data']#valori ricevuti
    val = float(request.values['val'])
    if s in db:
        db[s].append([data,val])
    else:#se è prima rilevazione inizializzo sensore e salvo data rilevazione e valore
        db[s] = [[data,val]]#meglio tupla
    return 'ok',200#200: codice di ritono standard di una richiesta fatta correttamente
#200 per valutare se salvataggio fatto correttamente


#GET per prendere informazioni
@app.route('/sensors/<s>',methods=['GET'])
def get_data(s):
    if s in db:
        #return json.dumps(db[s])#restituisco a client versione scritta in json per informazioni
        r = []
        for i in range(len(db[s])):
            r.append([i,db[s][i][1]])
        return json.dumps(r),200
    else:
        return 'sensor not found',404#codice standard http



if __name__ == '__main__':
    #funzione run per far partire server su pc su cui sto eseguendo
    #host0000 per fare accedere applicazioen anche dall'esterno
    #porta 80 è quella classica del http
    ##debug a true per stampare info di debug sulla console
    app.run(host='0.0.0.0', port=80, debug=True)

    #NECESSARIO DEFINIRE ENDPOINT SAPPLICAZIONE: URL A CUI APPLICAZIONE RISPONDE