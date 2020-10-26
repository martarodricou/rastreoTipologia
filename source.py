import requests
import json
import pandas as pd


#listado de todas las estaciones en españa
url_estaciones = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones/"

#ejecucion peticion
apikey_aemet = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJybWFydGEuY0BnbWFpbC5jb20iLCJqdGkiOiJhNzYwMTAzYy02MjI5LTRlZWYtOGM3OS1hZjU1ODEyZDVhOWYiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTYwMzAxNjczNSwidXNlcklkIjoiYTc2MDEwM2MtNjIyOS00ZWVmLThjNzktYWY1NTgxMmQ1YTlmIiwicm9sZSI6IiJ9.ONiaCS7xlCkaLBIFMTAorHq_yEl9H9jya8W8Db-wg0g"
querystring = {"api_key":apikey_aemet}

#consulta listado de estaciones aemet
response = requests.request("GET", url_estaciones, params=querystring, verify=False)
data_estaciones = json.loads(response.text) 
#print(data_estaciones['datos'])

req_estaciones = requests.get(data_estaciones['datos'])

#parseo de los datos para poder realizar de nuevo la consulta
data_estaciones = json.loads(req_estaciones.text) 

#listado de estaciones meteorologicas
#print(data_estaciones)

def createEstacionesPorProvincia(listado):
    lista = list()
    for provincia in listado:
        infoprov = {
            "provincia": provincia["provincia"],
            "ciudad": provincia["nombre"],
            "codigo" : provincia["indicativo"]
        }
        lista.append(infoprov)
        
    #print(lista)


    return lista



estaciones_por_provincia = createEstacionesPorProvincia(data_estaciones) #{'provincia': 'BARCELONA', 'ciudad': 'ARENYS DE MAR', 'codigo': '08186'}

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
            else:
                print("status: " + status)
        else:
            anio += 1
        print("-------------------------------------------------------")

    anio = 2015

df = pd.DataFrame(infoMes)
df.to_csv('dataset-climatologia.csv') 