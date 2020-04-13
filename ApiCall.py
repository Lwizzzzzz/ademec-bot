import requests
import json
import random
import math

class Api_Call():

    def __init__(self):
        with open ('deja_vu.json') as f:
            self.deja_vu = json.load(f)
        self.resultats_par_page = 50
        self.adresse_api = "https://api.isidore.science/resource/search"
        self.sujet = "http://data.bnf.fr/ark:/12148/cb16620091k" 
        self.output = "json"
        self.parameter = {"subject": self.sujet, "output": self.output}
        self.total_pages = self.get_total_pages()
        self.excluded_pages = []
        self.today_special = False
        self.get_today_special()


    def get_total_pages(self):
        parameters = self.parameter
        parameters["replies"]= 0
        response = requests.get(self.adresse_api, parameters)
        resultat = response.json()
        return math.ceil(int(resultat['response']['replies']['meta']['@items'])/self.resultats_par_page)

    
    def get_random_page(self):
        # get un page number random mais pas dans les pages exlues. 
        page = False
        while page == False:
            random_page = random.randrange(1, self.total_pages)
            if random_page not in self.excluded_pages: 
                page = random_page

        self.selected_page = page

        
        # set up parameters
        parameters = self.parameter
        parameters['replies'] = self.resultats_par_page
        parameters['page'] = self.selected_page

        # execute le call

        return requests.get(self.adresse_api, parameters).json()['response']['replies']['content']['reply']

    def get_today_special(self):
        while not self.today_special: # tant que nous n'avons pas d'heureux élus, nous le cherchons dans plusieurs page random si besoin !
            liste_de_ressources = self.get_random_page()
            #on choisit la première ressource de la page qui n'a pas encore été citée
            self.today_special = next((r for r in liste_de_ressources if r['@uri'] not in self.deja_vu), False)
            self.deja_vu.append(self.today_special['@uri'])
            print(self.deja_vu)
            with open('deja_vu.json', "w") as f:
                json.dump(self.deja_vu, f)

            self.excluded_pages.append(self.selected_page) # on rajoute la page en cours aux pages exlues. Si l'opération précédente avait réussi, cette valeur ne sera jamais pris en compte. 

    def get_tweet(self):
        subject =  self.today_special
        #author = ' '.join(subject['isidore']['enrichedCreators']['creator']['firstname'])+subject['isidore']['enrichedCreators']['creator']['lastname']
        last_author = subject['isidore']['enrichedCreators']['creator']
        if isinstance(last_author, list) and last_author:
            last_author_string = "de "+', '.join([a['@normalizedAuthor'].title() for index, a in enumerate(last_author) if index <2])
            if len(last_author) >=3:
                last_author_string+=" et alii"
        elif last_author: 
            last_author_string = "de "+last_author['@normalizedAuthor']
        else: 
            last_author_string =""
        #first_author = subject['isidore']['enrichedCreators']['creator']
        print("author", last_author_string)
        #print("firs", first_author)
        try: 
            date = subject['isidore']['date']['normalizedDate']
            if date:
                date_str = f"le {date} "
        except KeyError:
            date_str: ""
        print("date", date)
        title = subject['isidore']['title']
        if isinstance(title, list):
            title_string = title[0]['$']
        elif isinstance(title, str):
            title_string = title
        else:
            title_string = title['$']
        print("title", title_string)
        url = subject['isidore']['url']
        print(url)
        print("========================================")
        print(f'Aujourd\'hui, nous présentons {title_string}  {last_author_string}. Il a été originellement publié {date_str} ici: {url}. Merci @isidore! ' )



""" 


    # step 1:
    # On sait qu'il existe beaucoup de ressources sur le thème "humanités numériques" de l'API d'isidore.
    # On ne veut pas toujours se contenter des ressources présentent sur la première page.
    # Notre premier travail : savoir combien il y a de pages, sachant qu'on requête x par x

    resultats_par_page = 50

    nombre_de_page = 0 # nous allons devoir récupérer cette information grâce à l'appel de l'API

    adresse_api = "https://api.isidore.science/resource/search"

    sujet = "http://data.bnf.fr/ark:/12148/cb16620091k" # l'entrée humanités numériques de gallica, utilisé dans le référentiel d'isidore.

    output = "json"

    parameters = {
        "subject": sujet,
        "output": output,
        "replies": 0  #pour la première requète, nous ne voulons pas de résultats, mais simplement connaître le nombre de résultats au total
    }


    nombre_total = int(response['response']['replies']['meta']['@items'])
    #il y a actuellement un bug sur l'API d'Isidore. Les résultats sont limités à 1000 toutes pages confondues. 
    # Nous allons hard-coder le nombre de page maximum pour éviter que la page 20 soit statistiquement sur-représentée. 
    #nombre_page = math.ceil(nombre_total/resultats_par_page)
    nombre_page = 20
    numero_page = random.randrange(1, nombre_page)
    print(numero_page)

    parameters["replies"] = resultats_par_page
    parameters["page"] = numero_page

    liste_de_ressources = requests.get(adresse_api, parameters).json()['response']['replies']['content']['reply']

    today_special = next((r['@uri'] for r in liste_de_ressources if r['@uri'] in deja_vu), False)
    print(today_special)

    if not today_special: #si tous les éléments de la page ont déjà fait l'objet d'une publication 









    response = requests.get("https://api.isidore.science/resource/search?subject=http://data.bnf.fr/ark:/12148/cb16620091k&output=json&replies=3")
    #dict_response = json.loads(response)
    print(type(response.json()))
    dict_response = response.json()
    first_resource = dict_response['response']['replies']['content']['reply'][0]
    author = ' '.join(first_resource['isidore']['enrichedCreators']['creator']['firstname'])+first_resource['isidore']['enrichedCreators']['creator']['lastname']
    date = first_resource['isidore']['date']['normalizedDate']
    title = first_resource['isidore']['title']
    url = first_resource['isidore']['url']
    print(f'Aujourd\'hui, nous présentons {title} de {author}. Il a été originellement publié le {date} à l\'adresse suivante: {url}. Merci @isidore! ' )
    #print(dict_response)

 """