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
from src import funciones_update as fu
from src import funciones_transform as ft
from src import funciones_load as fl
import psycopg2

from dotenv import load_dotenv

# Cargamos variables de entorno
load_dotenv()


url_cmadrid_anual = os.getenv("url_cmadrid_anual")
url_cmadrid_mes_curso = os.getenv("url_cmadrid_mes_curso")
url_cmadrid_dia_curso = os.getenv("url_cmadrid_dia_curso")
url_cmadrid_estaciones = os.getenv("url_cmadrid_estaciones")
url_madrid = os.getenv("url_madrid")
carpeta_descargas = os.getenv("carpeta_actus")

# Extraemos datos anuales incluyendo el año en curso de la Comunidad de Madrid
fu.actualizar_datos_cmadrid(url_cmadrid_anual, carpeta_descargas, ano = True)
# Extraemos datos del mes en curso de la Comunidad de Madrid, necesitamos los datos en csv y especificamos que tenga en cuenta el mes para el nombre
fe.descargar_datos_cmadrid(url_cmadrid_mes_curso, carpeta_descargas, formato = "csv", mes=True)
# Extraemos datos del día en curso de la Comunidad de Madrid, especificando mes y día y que estén en formato csv
fe.descargar_datos_cmadrid(url_cmadrid_dia_curso, carpeta_descargas, formato = "csv", mes=True, dia=True)
# Extraemos datos de las estaciones de medición de la Comunidad de Madrid, indicando el formato csv
fe.descargar_datos_cmadrid(url_cmadrid_estaciones, carpeta_descargas, formato = "csv")
# Extraemos los datos de Madrid y obtenemos las lista de archivos descargados
archivos_dh = fu.actualizar_datos_madrid(url_madrid, carpeta_descargas, actualizar=True)
# Usar la lista de archivos en la función procesar_archivos_zip para extraer y concatenar los csv de cada zip anual de Madrid
fe.procesar_zips(carpeta_descargas, archivos_dh, carpeta_descargas)
# Extraemos una tabla con datos de contaminantes del pdf "Descripcion datos de contaminantes" de la Comunidad de Madrid
fe.extraer_tabla_pdf("data/raw/cmadrid_Descripción datos de contaminantes.pdf", "3", "datos_contaminantes_cmadrid",carpeta_descargas)
# Extraemos una tabla con datos de contaminantes del pdf "Interprete_ficheros_ calidad_ del_ aire_global" de Madrid
fe.extraer_tabla_pdf("data/raw/Interprete_ficheros_ calidad_ del_ aire_global.pdf", "7", "datos_contaminantes_madrid", carpeta_descargas)

carpeta_procesados = os.getenv("carpeta_procesados")
# Generamos df uniendo todos los csv de datos de medidas de la Comunidad de Madrid
df_cmadrid_actual = ft.unir_archivos(carpeta_descargas, "cmadrid_20", carpeta_procesados, "cmadrid_actual")
# Generamos df uniendo todos los csv de datos de medidas de Madrid
df_madrid_actual = ft.unir_archivos(carpeta_descargas, "madrid_20", carpeta_procesados, "madrid_actual")
# Usamos df_cmadrid y df_madrid para generar un df_medidas
df_medidas_actual = ft.crear_df_medidas(df_cmadrid_actual, df_madrid_actual)
# Cargamos las tablas extraidas de los pdf para generar df_tecnicas y df_contaminantes
df_datos_contaminantes_cmadrid = pd.read_csv(f"{carpeta_descargas}/datos_contaminantes_cmadrid.csv")
df_datos_contaminantes_madrid = pd.read_csv("../data/raw/datos_contaminantes_madrid.csv")
# Primero obtenemos un diccionario con las unidades de medida
dict_unidades = ft.obtener_unidades(df_datos_contaminantes_cmadrid)
# Procesamos ambos df para obtener un df_tecnicas y un df_contaminantes
df_tecnicas, df_contaminantes = ft.tablas_contaminantes(df_datos_contaminantes_cmadrid, df_datos_contaminantes_madrid, dict_unidades)
# cargamos los csv con informacion de las estaciones de medida
estaciones_cmadrid = pd.read_csv(f"{carpeta_descargas}/cmadrid_Red de Calidad del Aire. Estaciones.csv", sep=";", encoding="latin1")
estaciones_madrid = pd.read_csv(f"{carpeta_descargas}/madrid_Calidad del aire. Estaciones de control.csv", sep=";")
# A partir de estaciones_cmadrid obtenemos una tabla de zonas de calidad del aire
df_zonas = ft.obtener_zonas(estaciones_cmadrid)
# Procesamos todos los datos de estaciones para obtener informacion de las estaciones y los municipios
df_estaciones, df_municipios = ft.obtener_estaciones_y_municipios(estaciones_cmadrid, estaciones_madrid)[0]


conexion = os.getenv("conexion_bbdd")
# Conectamos a la base de datos y creamos un cursor
conn, cur= fl.conectar_postgres(conexion)
# generamos un df de provincias con el único valor "Madrid"
df_provincias = pd.DataFrame({"codigo_provincia":["28"], "nombre_provincia":["Madrid"]})
# Creamos unas listas con los nombres de las tablas de las bbdd y los df que se corresponden
lista_df = [df_provincias, df_municipios, df_contaminantes, df_tecnicas, df_zonas, df_estaciones, df_medidas_actual]
lista_tablas = ["provincias", "municipios", "contaminantes", "tecnicas_medida", "zonas", "estaciones", "medidas"]
# Generamos un diccionario con las claves primarias de cada tabla, que nos servirá para evitar duplicados
dict_pk = {"provincias": "codigo_provincia",
           "municipios": "codigo_municipio",
           "contaminantes": "codigo_magnitud",
           "tecnicas_medida": "codigo_tecnica_de_medida",
           "zonas": "codigo_zona",
           "estaciones":"codigo_estacion",
           "medidas": "id_medida"}
# Cargamos estos df en la base de datos
fl.cargar_datos(conn, cur, lista_df, lista_tablas, dict_pk)
fl.cerrar_conexion(conn,cur)