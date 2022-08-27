
from time import sleep
from tqdm import trange
from bs4 import BeautifulSoup
import requests
import json
from transmission_rpc import Client
import os

rpc_password = os.environ['NEWPCT']


def ConnectTransmission(torrent_url, rpc_password=rpc_password):
    try:
        c = Client(host='192.168.1.69', port=9091, username='transmission',
                   password=rpc_password)
        c.add_torrent(torrent_url)
    except:
        print("ERROR: Error al conectar con el servidor.")


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


def GetVideo_Spanish():
    try:
        peli = {}
        lista = {}
        identificator = 0

        print("\n Espere mientras cargamos las peliculas")

        for page in trange(1, 103):

            request_spanish = requests.get(
                f"https://www1.newpct.net/idioma/castellano/page/{page}/", headers={"Content-Type": "text/html"})
            bs = BeautifulSoup(request_spanish.text, 'html.parser')

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

        search_sol = input(f"{search_get} \n Elige la posición 0-x: ")

        for diccionario in lista:
            if search_get[int(search_sol)] in diccionario:
                enlace = diccionario[search_get[int(search_sol)]]

        return GetTorrent(enlace)

    except request_spanish.status_code == 404:
        print("ERROR: El servidor no pudo encontrar el contenido solicitado.")


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
        s = json.dumps(lista, sort_keys=False, indent=4, ensure_ascii=False)

        ident = input(f"{s} \n Introduce la opción a descargar: ")

        enlace = [x for x in lista[int(ident)].values()][0]

        return GetTorrent(enlace)

    except request.status_code == 404:
        print("ERROR: El servidor no pudo encontrar el contenido solicitado.")


option = input(
    "\n 1-Busqueda \n 2-Busqueda Español \n 3-Buscada Only 1080p \n Introduce la opción: ")
while True:
    if option == "1":
        busqueda = str(input("Escriba lo que busque: "))
        r_busqueda = requests.get(f'https://www1.newpct.net/?s={busqueda}',
                                  headers={"Content-Type": "text/html"})
        GetVideo(r_busqueda)
        break
    elif option == "2":
        GetVideo_Spanish()
        break
    else:
        print("Valor incorrecto")
    option = input(
        "\n 1-Busqueda \n 2-Busqueda Español \n 3-Buscada Only 1080p \n Introduce la opción: ")
