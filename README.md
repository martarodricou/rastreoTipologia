# rastreoTipologia
Practica1 Tipologia

En esta práctica, se pretende realizar un estudio de como ha afectado el periodo de confinamiento domiciliario al clima. De forma, que se aprecie la manera en que el ser humano afecta con su actividad diaria en el cambio climático y de que forma se puede corregir en un periodo corto de tiempo.

Para ello, se ha obtenido la información de precipitación y temperaturas medias en las distintas estaciones meteorológicas de Aemet de España desde 2015 a 2020. Con el objetivo, de posteriormente comparar esta información y sacar conclusiones.

Los campos almacenados en el dataset generado son los siguientes:

•	ciudad: Ciudad en la que se han recogido los datos de meteorología.

•	anio: Variable con el formato YYYY-MM que indica el mes al que corresponde la información. Donde los meses del 1 al 12 corresponden con la información mensual, mientras que el mes 13 corresponde con la información anual.

•	temperaturaMediaMensual: La temperatura media que hizo en la ciudad en el mes correspondiente.

•	temperaturaMediaMensual_maximas: La temperatura media de las máximas del mes.

•	temperaturaMediaMensual_minimas: Temperatura media de las mínimas del mes.

•	numDiasLLuvia: Número de días que ha llovido en el mes correspondiente.

•	PrecipitaciónTotalMensual: Precipitación total en el mes correspondiente, medida en mm.

Para la recopilación de datos se han utilizado las siguientes librerias:

requests

selenium

json

time

Para el tratamiento y visualización de los mismos se han utilizado:

pandas

numpy

matplotlib.pyplot
