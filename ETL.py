# importamos librerías
import pandas as pd
import numpy as np
import requests
import os
import camelot
from datetime import datetime
import zipfile
import unidecode
from src import funciones_extract as fe
from src import funciones_transform as ft

from dotenv import load_dotenv

# Cargamos variables de entorno
load_dotenv()


url_cmadrid_anual = os.getenv("url_cmadrid_anual")
url_cmadrid_mes_curso = os.getenv("url_cmadrid_mes_curso")
url_cmadrid_dia_curso = os.getenv("url_cmadrid_dia_curso")
url_cmadrid_estaciones = os.getenv("url_cmadrid_estaciones")
url_madrid = os.getenv("url_madrid")
carpeta_descargas = os.getenv("carpeta_descargas")

# Extraemos datos anuales incluyendo el año en curso de la Comunidad de Madrid
fe.descargar_datos_cmadrid(url_cmadrid_anual, carpeta_descargas)
# Extraemos datos del mes en curso de la Comunidad de Madrid, necesitamos los datos en csv y especificamos que tenga en cuenta el mes para el nombre
fe.descargar_datos_cmadrid(url_cmadrid_mes_curso, carpeta_descargas, formato = "csv", mes=True)
# Extraemos datos del día en curso de la Comunidad de Madrid, especificando mes y día y que estén en formato csv
fe.descargar_datos_cmadrid(url_cmadrid_dia_curso, carpeta_descargas, formato = "csv", mes=True, dia=True)
# Extraemos datos de las estaciones de medición de la Comunidad de Madrid, indicando el formato csv
fe.descargar_datos_cmadrid(url_cmadrid_estaciones, carpeta_descargas, formato = "csv")
# Extraemos los datos de Madrid y obtenemos las lista de archivos descargados
archivos_dh = fe.descargar_datos_madrid(url_madrid, carpeta_descargas)
# Usar la lista de archivos en la función procesar_archivos_zip para extraer y concatenar los csv de cada zip anual de Madrid
fe.procesar_zips(carpeta_descargas, archivos_dh, carpeta_descargas)
# Extraemos una tabla con datos de contaminantes del pdf "Descripcion datos de contaminantes" de la Comunidad de Madrid
fe.extraer_tabla_pdf("data/raw/cmadrid_Descripción datos de contaminantes.pdf", "3", carpeta_descargas)

carpeta_procesados = os.getenv("carpeta_procesados")
# Generamos df uniendo todos los csv de datos de medidas de la Comunidad de Madrid
df_cmadrid = ft.unir_archivos(carpeta_descargas, "cmadrid_20", carpeta_procesados, "cmadrid")
# Generamos df uniendo todos los csv de datos de medidas de Madrid
df_madrid = ft.unir_archivos(carpeta_descargas, "madrid_20", carpeta_procesados, "madrid")
# Usamos df_cmadrid y df_madrid para generar un df_medidas
df_medidas = ft.crear_df_medidas(df_cmadrid, df_madrid)
# Procesamos la tabla extraida del pdf para generar df_tecnicas y df_contaminantes
df_datos_contaminantes = pd.read_csv(f"{carpeta_descargas}/tabla_contaminantes.csv")
df_tecnicas = ft.tablas_contaminantes(df_datos_contaminantes)[0]
df_contaminantes = ft.tablas_contaminantes(df_datos_contaminantes)[1]
# cargamos los csv con informacion de las estaciones de medida
estaciones_cmadrid = pd.read_csv("../data/raw/cmadrid_Red de Calidad del Aire. Estaciones.csv", sep=";", encoding="latin1")
estaciones_madrid = pd.read_csv("../data/raw/madrid_Calidad del aire. Estaciones de control.csv", sep=";")
# A partir de estaciones_cmadrid obtenemos una tabla de zonas de calidad del aire
df_zonas = ft.obtener_zonas(estaciones_cmadrid)
# Procesamos todos los datos de estaciones para obtener informacion de las estaciones y los municipios
df_estaciones = ft.obtener_estaciones_y_municipios(estaciones_cmadrid, estaciones_madrid)[0]
df_municipios = ft.obtener_estaciones_y_municipios(estaciones_cmadrid, estaciones_madrid)[1]
