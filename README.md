
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

Sobre el script, no hace falta tenerlo en el servidor, se puede ejecutar desde otro dispositivo si este esta registrado en settings.json > "rpc-whitelist" de la configuración de Transmision.

```python3

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
           password='{6b45855dad4d0cf61a684b247b87a19b476ec6c02tUwZ8rs')  # CAMBIAR LA CONTRASEÑA, EN PLANO ESTA FEO
c.add_torrent(torrent_url)

```
