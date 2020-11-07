import requests
import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt




#API key proporcionada por la AEMET
apikey_aemet = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJybWFydGEuY0BnbWFpbC5jb20iLCJqdGkiOiJhNzYwMTAzYy02MjI5LTRlZWYtOGM3OS1hZjU1ODEyZDVhOWYiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTYwMzAxNjczNSwidXNlcklkIjoiYTc2MDEwM2MtNjIyOS00ZWVmLThjNzktYWY1NTgxMmQ1YTlmIiwicm9sZSI6IiJ9.ONiaCS7xlCkaLBIFMTAorHq_yEl9H9jya8W8Db-wg0g"
querystring = {"api_key":apikey_aemet}

# Funcion que construye un objeto con el nombre de la ciudad, la provincia y el código
# de la estacion meteorológica.
# Los datos se encuentran en 2 inputs seleccionables, el primero ya viene relleno con los datos de provincia
# y el segundo se rellena según la opción escogida en el primero mediante javascript
# este segundo selector es el que tiene el nombre de la provincia y el codigo de estacion
# para recoger estos datos se ha utilizado selenium, beautifulSoup y requests
def createEstacionesPorProvincia():

    # URL donde se encuentran el codigo de las estaciones junto con el nombre de provincia y ciudad
    url = "https://datosclima.es/Aemethistorico/Estaciones.php"

    # inicializacion del buscador usando selenium, el motor elegido es Firefox
    binary = FirefoxBinary('D:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe')
    b = webdriver.Firefox(firefox_binary=binary)

    # peticion a Firefox (selenium)
    b.get(url)

    # petición usando requests
    page = requests.get("https://datosclima.es/Aemethistorico/Estaciones.php")

    # formateo de datos para recoger el nombre de provincia
    soup = BeautifulSoup(page.content, "lxml")

    listado = list()

    # recorrido de las provincias recogidas por BeautifulSoup
    # este primer bucle solo ejecuta 1 vuelta ya que findAll devuelve un objeto con todas las provincias
    # se podria poner como una asignacion (provincia =  soup.findAll(...) )
    # en vez de bucle pero por comodidad y comprension del codigo lo hemos dejado asi
    for provincia in soup.findAll('select', attrs={'name':"Provincia"}):
        # recorrido de las provincias al hacer un split
        for i in range(3,len(provincia.text.splitlines())):
            # nombre de la provincia
            print(provincia.text.splitlines()[i])
            # ejecución del click en el selector para desplegar las ciudades asociadas a la provincia
            b.find_element_by_xpath("//option[@value='{0}']".format(provincia.text.splitlines()[i])).click()
            # captura del objeto select con las ciudades
            id_hijaSelect = b.find_element_by_name("id_hija")
            # lista de las ciudades
            options = [x for x in id_hijaSelect.find_elements_by_tag_name("option")]
            
            # formateo del resultado recogiendo la provincia, la ciudad y el codigo de estación
            for element in options:
                infoprov = {
                    "provincia": provincia.text.splitlines()[i],
                    "ciudad": element.text,
                    "codigo": element.get_attribute("value")
                }
                listado.append(infoprov)
    return listado

# ejemplo de un objeto de la lista:
# {'provincia': 'BARCELONA', 'ciudad': 'ARENYS DE MAR', 'codigo': '08186'}
estaciones_por_provincia = createEstacionesPorProvincia() 

# inicialización del año desde el cual se empiezan a capturar datos
anio = 2015

# columnas del dataset
infoMes = {
    "temperaturaMediaMensual": list(),
    "temperaturaMediaMensual_maximas": list(),
    "temperaturaMediaMensual_minimas": list(),
    "numDiasLLuvia": list(),
    "precipitacionTotalMensual": list(),
    "anio": list(),
    "ciudad": list()
}

# recorrido de las estaciones recogidas con la funcion createEstacionesPorProvincia()
for ciudades in estaciones_por_provincia:
    print(ciudades)
    while anio <= 2020:
        # url para recopilar datos asociados a un código de estacion y un año en concreto
        url_anios = "https://opendata.aemet.es/opendata/api/valores/climatologicos/mensualesanuales/datos/anioini/" + str(anio) + "/aniofin/"+ str(anio) +"/estacion/"

        # si el codigo no es vacio vacio
        if ciudades['codigo'] != '':
            # asignacion del codigo de estacion
            codEstacion = ciudades['codigo']
            # concatenar a la url el codigo de estación
            url_anios += codEstacion
            # peticion a la url con el parametro api key
            # devuelve los datos climatologicos asociados a esa estacion en el año seleccionado
            infoCiudad = requests.get(url_anios, params=querystring)
            # guardado del estado de peticion
            status = infoCiudad.status_code
            print("infoCiudad: " + str(status))
            # si no ha habido error de servidor
            if status != 500:
                # parseo de la respuesta en formato json
                jsonCiudad = json.loads(infoCiudad.text)
                # si ha habido datos en ese año y no se ha saturado el servidor con demasiadas peticiones
                if jsonCiudad['estado'] != 404 and jsonCiudad['estado'] != 429:
                    valoresAnuales = list()
                    # se hace una nueva petición usando la informacion de la respuesta recogida por jsonCiudad
                    # esto es porque la primera peticion solo devuelve el estado, la url donde se se encuentra la peticion
                    # y otra url donde se explica en detalle los metadatos
                    jsonValoresCiudad = requests.request("GET", jsonCiudad['datos'], params=querystring, timeout=300)
                    statusValoresCiudad = jsonValoresCiudad.status_code
                    print("jsonValoresCiudad: " + str(statusValoresCiudad))
                    # comprobacion del estado de la peticion por si el seridor ha dado fallo
                    if statusValoresCiudad != 500:
                        # parseo de la peticion en formato json
                        parseJsonValoresCiudad = json.loads(jsonValoresCiudad.text)
                        # recopilacion de datos de interes para formar el dataset
                        for meses in parseJsonValoresCiudad:
                        
                            # inicializacion de variables a "vacio"
                            tempMedia = '-'
                            tempMediaMax ='-'
                            tempMediaMin ='-'
                            numDiasLLuvia ='-'
                            precipitacionTotal ='-'

                            # en caso de que se encuentren los valores solicitados, se asignan
                            if {'tm_mes'}.issubset(meses.keys()):
                                tempMedia = meses['tm_mes']
                            if {'tm_max'}.issubset(meses.keys()):
                                tempMediaMax = meses['tm_max']
                            if {'tm_min'}.issubset(meses.keys()):
                                tempMediaMin = meses['tm_min']
                            if {'n_llu'}.issubset(meses.keys()):
                                numDiasLLuvia = meses['n_llu']
                            if {'p_mes'}.issubset(meses.keys()):
                                precipitacionTotal = meses['p_mes']

                            # asignacion de datos al dataset

                            infoMes["temperaturaMediaMensual"].append(tempMedia)
                            infoMes["temperaturaMediaMensual_maximas"].append(tempMediaMax)
                            infoMes["temperaturaMediaMensual_minimas"].append(tempMediaMin)
                            infoMes["numDiasLLuvia"].append(numDiasLLuvia)
                            infoMes["precipitacionTotalMensual"].append(precipitacionTotal)
                            infoMes["anio"].append(meses['fecha'])
                            infoMes["ciudad"].append(ciudades['ciudad'])
                            
                            print(tempMedia + " - " + tempMediaMax + " - " + tempMediaMin + " - " + numDiasLLuvia + " - " + precipitacionTotal + " - " + meses['fecha'] + " - " + ciudades['ciudad'])
                        anio += 1
                elif jsonCiudad['estado'] == 404:
                    anio += 1
                elif jsonCiudad['estado'] == 429:
                    # en caso de haber saturado el servidor se hace una espera de 10 segundos
                    time.sleep(10)
            else:
                print("status: " + status)
        else:
            anio += 1
        print("-------------------------------------------------------")
    # una vez recopilados los datos de una ciudad desde el 2015 al 2020 se inicializa de nuevo a 2015 para empezar con la
    # siguiente ciudad
    anio = 2015

# creacion del dataset a traves del objeto infoMes
df = pd.DataFrame(infoMes)
df.to_csv('dataset-climatologia.csv') 


# VISUALIZACION DE DATOS

# se escoge una ciudad, por ejemplo Teruel
# comparación de la temperatura media mensual entre el 2019 y el 2020

# lectura del csv dejando las columnas de interes, temperatura, anio y ciudad
tiempo = pd.read_csv('dataset-climatologia.csv', 
    header=0,
    usecols=['temperaturaMediaMensual', 'anio', 'ciudad'])

# seleccion de la ciudad -> Teruel
teruel = tiempo[tiempo['ciudad'] == 'TERUEL']

# para mostrar los datos de temperatura hay que convertirlos a numero
# Los meses sin valores (ultimo trimestre de este año) se ha decidido poner un 0
teruel.loc[teruel['temperaturaMediaMensual'] == '-', 'temperaturaMediaMensual'] = '0'
teruel['temperaturaMediaMensual'] = pd.to_numeric(teruel['temperaturaMediaMensual'])

# se dividen los datos por años
teruel2020 = teruel[teruel['anio'].str.contains("2020")]
teruel2019 = teruel[teruel['anio'].str.contains("2019")]

# generacion del plot para la comparacion de la temperatura entre el 2019 y el 2020
plt.plot(teruel2020.anio.str[5:7], teruel2020.temperaturaMediaMensual.astype(int), label = "Teruel 2020")
plt.plot(teruel2020.anio.str[5:7], teruel2019.temperaturaMediaMensual.astype(int), label = "Teruel 2019")

# se añade una leyenda para identificar a qué línea pertenece cada año
plt.legend(loc='upper left')

# se asigna un título para los datos de la "x" y de la "y"
plt.xlabel('Meses')
plt.ylabel('Temperatura media mensual')

# se muestra el plot
plt.show()
