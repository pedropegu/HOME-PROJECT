
from time import sleep
from tqdm import trange
from bs4 import BeautifulSoup
import requests
import json
from transmission_rpc import Client
import os

rpc_password = os.environ['NEWPCT']

servidor = '192.168.1.43'

#ConnectTransmission LIMPIO
def ConnectTransmission(torrent_url, rpc_password=rpc_password, servidor=servidor):
    try:
        c = Client(host=servidor, port=9091, username='transmission',
                    password=rpc_password)
        c.add_torrent(torrent_url) 

        print(
            f"\nTorrent añadido correctamente, para ver la descarga visita: http://{servidor}:9091")
    except Exception as Error:
        print(Error.message)

#NEWPCT

def GetVideo_Spanish_or_1080p(option):

    try:
        peli = {}
        lista = {}
        identificator = 0

        print("\n Espere mientras cargamos las peliculas")
        max_range = 103 if option == "spanish" else 33
        opt = "idioma/castellano" if option == "spanish" else "calidad/1080p/"
        for page in trange(1, max_range):

            request = requests.get(
                f"https://www1.newpct.net/{opt}/page/{page}/", headers={"Content-Type": "text/html"})
            bs = BeautifulSoup(request.text, 'html.parser')

            for link in bs.find_all('a'):
                if link.get('href') != "#" and link.get('href') != None and "page" not in link.get('href'):
                    peli[link.get('title')] = link.get('href')
                    if peli not in lista.values():
                        lista[identificator] = peli
                        peli = {}
                        identificator += 1

        s = json.loads(json.dumps(lista, sort_keys=False, indent=4,
                                    ensure_ascii=False))

        lista = [x for x in s.values()]
        nombres = []
        for x in lista:
            nombres.append(list(x.keys())[0])

        search = input("Qué buscas: ")
        search_get = []

        for x in nombres:
            if search in x:
                search_get.append(x)

        if search_get:
            search_sol = input(f"{search_get} \n Elige la posición 0-x: ")

        for diccionario in lista:
            if search_get[int(search_sol)] in diccionario:
                enlace = diccionario[search_get[int(search_sol)]]

        return GetTorrent(enlace)
    except Exception as Error:
        print(Error.message)

def GetVideo(request):
    try:
        bs = BeautifulSoup(request.text, 'html.parser')

        peli = {}
        lista = {}
        identificator = 0

        for link in bs.find_all('a'):
            if link.get('href') != "#" and link.get('href') != None and "page" not in link.get('href'):
                peli[link.get('title')] = link.get('href')
                if peli not in lista.values():
                    lista[identificator] = peli
                    peli = {}
                    identificator += 1
        s = json.dumps(lista, sort_keys=False,
                        indent=4, ensure_ascii=False)

        ident = input(f"{s} \n Introduce la opción a descargar: ")

        enlace = [x for x in lista[int(ident)].values()][0]

        return GetTorrent(enlace)

    except Exception as Error:
        print(Error.message)
#DONTORRENT - LIMPIO
def DonTorrent_Search(request):
    try:
        bs = BeautifulSoup(request.text, 'html.parser')
        peli = {}
        lista = {}
        identificator = 0

        for link in bs.find_all('a'):
            if link.get('href') != "#" and link.get('href') != None and "page" not in link.get('href'):
                peli[link.get_text()] = link.get('href')
                if peli not in lista.values():
                    lista[identificator] = peli
                    peli = {}
                    identificator += 1
        s = json.dumps(lista, sort_keys=False,
                        indent=4, ensure_ascii=False)
        ident = input(f"{s} \n Introduce la opción a descargar: ")

        enlace = [x for x in lista[int(ident)].values()][0]
        
        return GetTorrent_DonTorrent(f"https://dontorrent.in/{enlace}")

    except Exception as Error:
        print(Error.message)

#GETTORRENT MEDIO-LIMPIOS (ERROR AL COMBINARLOS - MIRAR MÁS TARDE)
def GetTorrent_DonTorrent(enlace):

    peli = requests.get(enlace,
                        headers={"Content-Type": "text/html"})

    peli.bs = BeautifulSoup(peli.text, 'html.parser')

    for link in peli.bs.find_all("a"):
        if link.get_text("a") == "Descargar":
            enlace = link.get("href")

    torrent = f"https:{enlace}"

    return ConnectTransmission(torrent)

def GetTorrent(enlace):

    peli = requests.get(enlace,
                        headers={"Content-Type": "text/html"})

    peli.bs = BeautifulSoup(peli.text, 'html.parser')
    descarga = []
    for link in peli.bs.find_all("a"):
        if link.get("class") == ['enlace_torrent', 'degradado1']:
            descarga.append(link.get("href"))

    torrent = "https://www1.newpct.net"+descarga[0].replace(' ', '%20')
    return ConnectTransmission(torrent)
