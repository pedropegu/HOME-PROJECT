from web_scraper import *

def main():
    option = input("\n1-NEWPCT \n2-DONTORRENT \n\nElige tu opción: ")
    if option == "1":
        newpct = input("\n 1-Busqueda \n 2-Busqueda Español \n 3-Buscada Only 1080p \n Introduce la opción: ")
        while True:
            if newpct == "1":
                busqueda = str(input("\nEscriba lo que busque: "))
                r_busqueda = requests.get(f'https://www1.newpct.net/?s={busqueda}',
                                        headers={"Content-Type": "text/html"})
                GetVideo(r_busqueda)
                break
            elif newpct == "2":
                GetVideo_Spanish()
                break
            elif newpct == "3":
                GetVideo_1080()
                break
            else:
                print("Valor incorrecto")
            newpct = input(
                "\n1-Busqueda \n2-Busqueda Español \n3-Buscada Only 1080p \n\nIntroduce la opción: ")

    elif option == "2":
        busqueda = str(input("\nEscriba lo que busque: "))
        request = requests.get(f'https://dontorrent.in/buscar/{busqueda}',
                                        headers={"Content-Type": "text/html"})
        DonTorrent_Search(request)                              
    else:
        print("ERROR: El valor introducido no es correcto.")


if __name__ == "__main__":
    main()
