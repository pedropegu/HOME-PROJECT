
# LOCAL MOVIES STREAMING
Se trata de un proyecto básico en el cual tendremos un servidor de Jellyfin
para la reproducción de peliculas, para añadir estas tendremos un Script de python
en el cual solo tendremos que introducir el nombre de la película que estemos buscando y seleccionar la que más nos convenga. 

El Script se encargará de mandar el torrent al servidor para que empiece la descarga de forma automática.
Vamos a usar la web: https://www1.newpct.net/




## REQUISITOS

Para llevar a cabo este proyecto vamos a necesitar lo siguiente:

    Transmission-daemon
    JellyFin
    Python3:
        Transmission_rpc
        Requests
        BeautifulSoup
        Json

Aclarar que todo esto se ha montado sobre un Ubuntu Server.

## Instalación | Configuración

#### Transmision

```bash
  sudo apt-get install transmission-daemon
  sudo systemctl stop transmission-daemon.service
  sudo nano /etc/transmission-daemon/settings.json
```
```json
{
    "alt-speed-down": 50,
    "alt-speed-enabled": false,
    "alt-speed-time-begin": 540,
    "alt-speed-time-day": 127,
    "alt-speed-time-enabled": false,
    "alt-speed-time-end": 1020,
    "alt-speed-up": 50,
    "bind-address-ipv4": "0.0.0.0",
    "bind-address-ipv6": "::",
    "blocklist-enabled": false,
    "blocklist-url": "http://www.example.com/blocklist",
    "cache-size-mb": 4,
    "dht-enabled": true,
    "download-dir": "<RUTA DONDE DESCARGAR LOS TORRENTS>",
    "download-limit": 100,
    "download-limit-enabled": 0,
    "download-queue-enabled": true,
    "download-queue-size": 5,
    "encryption": 1,
    "idle-seeding-limit": 30,
    "idle-seeding-limit-enabled": false,
    "incomplete-dir": "/var/lib/transmission-daemon/Downloads",
    "incomplete-dir-enabled": false,
    "lpd-enabled": false,
    "max-peers-global": 200,
    "message-level": 1,
    "peer-congestion-algorithm": "",
    "peer-id-ttl-hours": 6,
    "peer-limit-global": 200,
    "peer-limit-per-torrent": 50,
    "peer-port": 51413,
    "peer-port-random-high": 65535,
    "peer-port-random-low": 49152,
    "peer-port-random-on-start": false,
    "peer-socket-tos": "default",
    "pex-enabled": true,
    "port-forwarding-enabled": false,
    "preallocation": 1,
    "prefetch-enabled": true,
    "queue-stalled-enabled": true,
    "queue-stalled-minutes": 30,
    "ratio-limit": 2,
    "ratio-limit-enabled": false,
    "rename-partial-files": true,
    "rpc-authentication-required": false,
    "rpc-bind-address": "0.0.0.0",
    "rpc-enabled": true,
    "rpc-host-whitelist": "",
    "rpc-host-whitelist-enabled": false,
    "rpc-password": "{6b45855dad4d0cf61a684b247b87a19b476ec6c02tUwZ8rs",
    "rpc-port": 9091,
    "rpc-url": "/transmission/",
    "rpc-username": "transmission",
    "rpc-whitelist": "127.0.0.1, <LISTAS DE IP QUE TENDRÁN ACCESO>",
    "rpc-whitelist-enabled": true,
    "scrape-paused-torrents-enabled": true,
    "script-torrent-done-enabled": false,
    "script-torrent-done-filename": "",
    "seed-queue-enabled": false,
    "seed-queue-size": 10,
    "speed-limit-down": 100,
    "speed-limit-down-enabled": false,
    "speed-limit-up": 100,
    "speed-limit-up-enabled": false,
    "start-added-torrents": true,
    "trash-original-torrent-files": false,
    "umask": 18,
    "upload-limit": 100,
    "upload-limit-enabled": 0,
    "upload-slots-per-torrent": 14,
    "utp-enabled": true
}
```

```bash
sudo systemctl start transmission-daemon.service
```

Para acceder a la interfaz web de transmission: http://localhost:9091

#### Jellyfin

Página oficial: https://jellyfin.org/

```bash
docker pull jellyfin/jellyfin:latest
mkdir -p /srv/jellyfin/{config,cache}
docker run -d -v /srv/jellyfin/config:/config -v /srv/jellyfin/cache:/cache -v <ruta de las películas>:/media --net=host jellyfin/jellyfin:latest
```
Asegurarse que se tienen todos los permisos sobre la ruta de las peliculas, tanto para transmission como Jellyfin


Para acceder a Jellyfin: http://localhost:8096

Cuando se entre en la interfaz web y realice la configuración, a la hora elegir la biblioteca para las peliculas debe elegir la ruta /media

#### Python

```bash
pip3 install transmission-rpc
pip3 install requests
pip3 install beautifulsoup4
```

Sobre el script, no hace falta tenerlo en el servidor, haremos uso de trasmission_rpc y de la identificacón mediante usuario y contraseña

```python3

from time import sleep
from tqdm import trange
from bs4 import BeautifulSoup
import requests
import json
from transmission_rpc import Client
import os

rpc_password = os.environ['NEWPCT']
servidor = "192.168.1.69"


def ConnectTransmission(torrent_url, rpc_password=rpc_password):
    try:
        c = Client(host=servidor, port=9091, username='transmission',
                   password=rpc_password)
        c.add_torrent(torrent_url)

        print(
            f"\nTorrent añadido correctamente, para ver la descarga visita: http://{servidor}:9091")
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

```
