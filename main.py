from flask import Flask,request,redirect,url_for, render_template
import json
from joblib import dump, load
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from secret import secret_key
from google.cloud import firestore

#definita classe che rappresenta utenti del sistema a cui sono passate id univoco per un certo username
class User(UserMixin):
    def __init__(self, username):
        super().__init__()
        self.id = username
        self.username = username
        self.par={}#altri dati se mi servono per un certo username
#in questo modo non devo usare in modo esplicito il concetto di session!!
#libreria flaask per realizzare applicazioni web
app = Flask(__name__)#funzione che crea applicazione
app.config['SECRET_KEY'] = secret_key

# The login manager contains the code that lets your application and Flask-Login work together,
# such as how to load a user from an ID, where to send users when they need to log in, and the like.
#login manager gestisce login applicazione
login = LoginManager(app)
#se serve fare il login rimanda a questa pagina
login.login_view = '/static/login.html'

#salvo autenticati
usersdb = {'marco':'mamei'}

@login.user_loader
def load_user(username):
    if username in usersdb:
        return User(username)
    return None

@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('/sensors'))
    username = request.values['u']
    password = request.values['p']
    #next_page = request.values['next']
    if username in usersdb and password == usersdb[username]:
        #serve a flask per tener traccia che utente attuale ha fatto login
        login_user(User(username))
        return redirect('/sensors')
        #next page per portare alla pagina selezionata in precedenza dopo aver fatto il login

    return redirect('/static/login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')




coll="data"
db = firestore.Client.from_service_account_json('credentials.json', database='sensors')
#non metto credentials su guthub ma da inserire a parte

#endpoint: annotazione e funzione sottostante
@app.route('/graph',methods=["GET"])
@login_required
def graph():
    print("ciao")
    #funzione che ridirige verso altra pagina che è un file che sitrova nella cartella static

    #così programazione lato client-->è client che recupera dati dal server e li elabora
    #ALTERBATIVA: QUANDO CLIENT CHIAMA GRAPH 2 è SERVER CHE RENDE TEMPLATE DOVE METTE DENTRO I DATI IN PANCIA E MANDA A
    #BROWSER PAGINA HTML GIà PRONTA CON DENTRO I DATI(SENZA DOVER USARE JS)-->SOSTITUISCO PROGRAMMAZIONE JS SU CLIENT CON
    #PROGRAMMAZIONE PYTHON SUL SERVER
    return redirect(url_for('static', filename='graph.html'))

@app.route('/graph2',methods=["GET"])
#in questo caso è server che deve prendere dati dal sensore
def graph2():
    d2=json.loads(get_data("s1")[0])
    print(d2)
    ds=""
    for x in d2[:-10]:
        ds+=f"['{x[0]}', {x[1]}, null],\n"
    for x in d2[-10:]:
        ds += f"['{x[0]}', null, {x[1]}],\n"
    print("ciao2")
    #funzione che ridirige verso altra pagina che è un file che sitrova nella cartella static

    #così programazione lato client-->è client che recupera dati dal server e li elabora
    #ALTERBATIVA: QUANDO CLIENT CHIAMA GRAPH 2 è SERVER CHE RENDE TEMPLATE DOVE METTE DENTRO I DATI IN PANCIA E MANDA A
    #BROWSER PAGINA HTML GIà PRONTA CON DENTRO I DATI(SENZA DOVER USARE JS)-->SOSTITUISCO PROGRAMMAZIONE JS SU CLIENT CON
    #PROGRAMMAZIONE PYTHON SUL SERVER
    #return redirect(url_for('static', filename='graph.html'))
    return render_template("graph.html",data=ds)


@app.route('/sensors',methods=['GET'])
def sensors():
    sensors=[]
    # stream genera lista con tutte entità resenti nella tabella
    for entity in db.collection(coll).stream():
        sensors.append(entity.id)
    #dizionario per rappresentare dati sensori: prese tutte chievi dizionario e trasfromate in stringa json e restituita
    #a client per vedere tutti sensori disponibili e sulla base di questo anche generare gli url giusti
    #return json.dumps(list(db.keys())), 200
    return json.dumps(sensors), 200

#CLIENT ASSOICATO A SENSORE S1
#post per scrivere dei dati
#url parametrico (<s>) per inserire dei parametri che possono essere dentro l'url
@app.route('/sensors/<s>',methods=['POST'])
def add_data(s):
    #request.values rappresenta il dizionario che è stato passato come parametro a una richiesta post
    data = request.values['data']#valori ricevuti
    val = float(request.values['val'])

    # sesnosre potrebbe creare diversi documenti nella tabella associata a quel sensore
    doc_ref = db.collection(coll).document(s)  # id can be omitted-->ottengo riferimento
    if doc_ref.get().exists:
        diz= doc_ref.get().to_dict()['values']
        diz[data]=val
        doc_ref.update({'values': diz})
    else:
        doc_ref.set({ 'values': {data:val}})
    print(doc_ref.get().id)

    '''if s in db:
        db[s].append([data,val])
    else:#se è prima rilevazione inizializzo sensore e salvo data rilevazione e valore
        db[s] = [[data,val]]#meglio tupla'''
    return 'ok',200#200: codice di ritono standard di una richiesta fatta correttamente
#200 per valutare se salvataggio fatto correttamente


#GET per prendere informazioni
@app.route('/sensors/<s>',methods=['GET'])
def get_data(s):
    doc_ref = db.collection(coll).document(s)
    if doc_ref.get().exists:
        r=[]
        diz = doc_ref.get().to_dict()['values']
        #dizionario da ordinar ein base a chiavi
        #diz=sorted(diz)
        i=0
        for k,v in diz.items():
            r.append([i,v])
            i+=1




        '''if s in db:
        #return json.dumps(db[s])#restituisco a client versione scritta in json per informazioni
        r = []
        for i in range(len(db[s])):
            r.append([i,db[s][i][1]])'''

        model = load('model.joblib')
        for i in range(10):
            yp = model.predict([[r[-1][1], r[-2][1], r[-3][1], 0]])
            r.append([len(r), yp[0]])

        return json.dumps(r), 200
    else:
        return 'sensor not found', 404



if __name__ == '__main__':
    #funzione run per far partire server su pc su cui sto eseguendo
    #host0000 per fare accedere applicazioen anche dall'esterno
    #porta 80 è quella classica del http
    ##debug a true per stampare info di debug sulla console
    app.run(host='0.0.0.0', port=80, debug=True)

    #NECESSARIO DEFINIRE ENDPOINT SAPPLICAZIONE: URL A CUI APPLICAZIONE RISPONDE