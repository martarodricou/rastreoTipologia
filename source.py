import requests
import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt




#ejecucion peticion
apikey_aemet = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJybWFydGEuY0BnbWFpbC5jb20iLCJqdGkiOiJhNzYwMTAzYy02MjI5LTRlZWYtOGM3OS1hZjU1ODEyZDVhOWYiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTYwMzAxNjczNSwidXNlcklkIjoiYTc2MDEwM2MtNjIyOS00ZWVmLThjNzktYWY1NTgxMmQ1YTlmIiwicm9sZSI6IiJ9.ONiaCS7xlCkaLBIFMTAorHq_yEl9H9jya8W8Db-wg0g"
querystring = {"api_key":apikey_aemet}


def createEstacionesPorProvincia():


    url = "https://datosclima.es/Aemethistorico/Estaciones.php"

    binary = FirefoxBinary('D:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe')
    b = webdriver.Firefox(firefox_binary=binary)

    b.get(url)

    page = requests.get("https://datosclima.es/Aemethistorico/Estaciones.php")
    soup = BeautifulSoup(page.content, "lxml")



    listado = list()

    for provincia in soup.findAll('select', attrs={'name':"Provincia"}):
        for i in range(3,len(provincia.text.splitlines())):
                print(provincia.text.splitlines()[i])
                b.find_element_by_xpath("//option[@value='{0}']".format(provincia.text.splitlines()[i])).click()
                id_hijaSelect = b.find_element_by_name("id_hija")
                options = [x for x in id_hijaSelect.find_elements_by_tag_name("option")]
                
                for element in options:
                    infoprov = {
                        "provincia": provincia.text.splitlines()[i],
                        "ciudad": element.text,
                        "codigo": element.get_attribute("value")
                    }
                    listado.append(infoprov)
    return listado


estaciones_por_provincia = createEstacionesPorProvincia() #{'provincia': 'BARCELONA', 'ciudad': 'ARENYS DE MAR', 'codigo': '08186'}

codEstacion = 0
anio = 2015

valoresTotales = list()

infoMes = {
    "temperaturaMediaMensual": list(),
    "temperaturaMediaMensual_maximas": list(),
    "temperaturaMediaMensual_minimas": list(),
    "numDiasLLuvia": list(),
    "precipitacionTotalMensual": list(),
    "anio": list(),
    "ciudad": list()
}

for ciudades in estaciones_por_provincia:
    print(ciudades)
    
    #valoresCiudad = list()
    
    while anio <= 2020:
        url_anios = "https://opendata.aemet.es/opendata/api/valores/climatologicos/mensualesanuales/datos/anioini/" + str(anio) + "/aniofin/"+ str(anio) +"/estacion/"
       
        #print(anio)
        if ciudades['codigo'] != '':
            codEstacion = ciudades['codigo'] #str(1387)
            url_anios += codEstacion
            infoCiudad = requests.get(url_anios, params=querystring)
            status = infoCiudad.status_code
            print("infoCiudad: " + str(status))
            if status != 500:
                jsonCiudad = json.loads(infoCiudad.text)
                if jsonCiudad['estado'] != 404 and jsonCiudad['estado'] != 429:
                    valoresAnuales = list()
                    #print("entra en el if de estado correcto")
                    jsonValoresCiudad = requests.request("GET", jsonCiudad['datos'], params=querystring, timeout=300)
                    statusValoresCiudad = jsonValoresCiudad.status_code
                    print("jsonValoresCiudad: " + str(statusValoresCiudad))
                    if statusValoresCiudad != 500:
                        parseJsonValoresCiudad = json.loads(jsonValoresCiudad.text)
                        for meses in parseJsonValoresCiudad:
                        
                            tempMedia = '-'
                            tempMediaMax ='-'
                            tempMediaMin ='-'
                            numDiasLLuvia ='-'
                            precipitacionTotal ='-'

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

                            infoMes["temperaturaMediaMensual"].append(tempMedia)
                            infoMes["temperaturaMediaMensual_maximas"].append(tempMediaMax)
                            infoMes["temperaturaMediaMensual_minimas"].append(tempMediaMin)
                            infoMes["numDiasLLuvia"].append(numDiasLLuvia)
                            infoMes["precipitacionTotalMensual"].append(precipitacionTotal)
                            infoMes["anio"].append(meses['fecha'])
                            infoMes["ciudad"].append(ciudades['ciudad'])
                            #valoresAnuales.append(infoMes)
                            print(tempMedia + " - " + tempMediaMax + " - " + tempMediaMin + " - " + numDiasLLuvia + " - " + precipitacionTotal + " - " + meses['fecha'] + " - " + ciudades['ciudad'])
                        anio += 1
                elif jsonCiudad['estado'] == 404:
                    anio += 1
                elif jsonCiudad['estado'] == 429:
                    time.sleep(10)
            else:
                print("status: " + status)
        else:
            anio += 1
        print("-------------------------------------------------------")

    anio = 2015

df = pd.DataFrame(infoMes)
df.to_csv('dataset-climatologia.csv') 


# VISUALIZACION DE DATOS

#SE ESCOGE UNA CIUDAD -> TERUEL
#AÑO 2019 - 2020

tiempo = pd.read_csv('datos.csv')
def logic(index):
    if index < 495 or index > 572:
       return True
    return False

tiempo = pd.read_csv('dataset-climatología1.csv', 
    header=0,
    usecols=['temperaturaMediaMensual', 'anio', 'ciudad'])

teruel = tiempo[tiempo['ciudad'] == 'TERUEL']

teruel.loc[teruel['temperaturaMediaMensual'] == '-', 'temperaturaMediaMensual'] = '0'
teruel['temperaturaMediaMensual'] = pd.to_numeric(teruel['temperaturaMediaMensual'])

teruel2020 = teruel[teruel['anio'].str.contains("2020")]
teruel2019 = teruel[teruel['anio'].str.contains("2019")]


plt.plot(teruel2020.anio.str[5:7], teruel2020.temperaturaMediaMensual.astype(int), label = "Teruel 2020")
plt.plot(teruel2020.anio.str[5:7], teruel2019.temperaturaMediaMensual.astype(int), label = "Teruel 2019")

plt.legend(loc='upper left')
plt.xlabel('Meses')
plt.ylabel('Temperatura media mensual')

plt.show()
