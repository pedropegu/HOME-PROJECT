
from bs4 import BeautifulSoup
import requests
import json
from transmission_rpc import Client

busqueda = str(input("Escriba lo que busque: "))
r = requests.get(f'https://www1.newpct.net/?s={busqueda}',
                 headers={"Content-Type": "text/html"})

bs = BeautifulSoup(r.text, 'html.parser')

peli = {}
lista = {}
identificator = 0

# BUSCAMOS TODAS LAS PELICULAS CON SUS ENLACES Y LAS AÑADIMOS A UN DICCIONARIO DONDE LAS ENUMERAMOS.
for link in bs.find_all('a'):
    if link.get('href') != "#" and link.get('href') != None and "page" not in link.get('href'):
        peli[link.get('title')] = link.get('href')
        if peli not in lista.values():
            lista[identificator] = peli
            peli = {}
            identificator += 1
s = json.dumps(lista, sort_keys=False, indent=4, ensure_ascii=False)

# A TRAVÉS DE LA ENUMERACIÓN PEDIMOS UNA OPCIÓN PARA PODER ELEGIR CUAL DESCARGAR
ident = input(f"{s} \n Introduce la opción a descargar: ")

# GUARDAMOS LA OPCIÓN Y COJEMOS EL ENLACE
save = [x for x in lista[int(ident)].values()][0]
peli = requests.get(save,
                    headers={"Content-Type": "text/html"})

# PARSEAMOS EL NUEVO HTML EN BUSCA DEL TORRENT DE DESCARGA
peli.bs = BeautifulSoup(peli.text, 'html.parser')
# SACAMOS LOS ENLACES Y FILTRAMOS POR ENLACE_TORRENT Y AÑADIMOS LAS OPCIONES A UNA LISTA DONDE ENCONTRAREMOS LA OPCIÓN DEL TORRENT O QUE ABRA AUTOMATICAMENTE EL GESTOR DE DESCARGAS
descarga = []
for link in peli.bs.find_all("a"):
    if link.get("class") == ['enlace_torrent', 'degradado1']:
        descarga.append(link.get("href"))

# GUARDAMOS EL ENLACE DEL TORRENT
enlace = "https://www1.newpct.net"+descarga[0].replace(' ', '%20')

# MANDAMOS EL ENLACE DEL TORRENT AL GESTOR DE DESCARGAS DE NUESTRO SERVER
torrent_url = enlace
c = Client(host='192.168.1.69', port=9091, username='transmission',
           password='{6b45855dad4d0cf61a684b247b87a19b476ec6c02tUwZ8rs')  # CAMBIAR LA CONTRASEÑA, EN PLANO ESTA FEO XD
c.add_torrent(torrent_url)
