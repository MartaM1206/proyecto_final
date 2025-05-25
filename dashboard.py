# Importamos librerías necesarias
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import math
import os
from dotenv import load_dotenv
from datetime import datetime
import psycopg2

# Configuración de Polars
pl.Config.set_tbl_rows(1000)  # Mostrar hasta 1000 filas
pl.Config.set_tbl_width_chars(500)  # Ajustar ancho para mejor visualización

# Importamos funciones de soporte
from src import funciones_load as fl
from src import funciones_dashboard as fdb

# Cargar variables de entorno
load_dotenv()
st.set_page_config(layout="wide")  # Esto hace que la página ocupe todo el ancho disponible
# Datos de conexión a la base de datos
conexion = os.getenv("conexion_bbdd")  
# Guardamos los datos en cache para no tener que volver a cargar los datos cada página
@st.cache_data
def obtener_datos():
    # Llamar a la función sin pasar la conexión directamente
    madrid = fdb.obtener_datos(conexion, 2018, 2024, "Madrid")
    return madrid

# Obtener los datos sin cachear la conexión
madrid = obtener_datos()

# Procesar los datos
df_mensual, df_diario, df_anual, estaciones, contaminantes, anios = fdb.separar_datos(madrid)
num_estaciones = len(estaciones)
num_contaminantes = len(contaminantes)
num_anios = len(anios)  
estaciones_trafico = madrid.filter(pl.col("tipo_estacion") =="Tráfico")["estacion"].unique().to_list()
estaciones_fondo = madrid.filter(pl.col("tipo_estacion") =="Fondo")["estacion"].unique().to_list()


# Sidebar para navegación
st.sidebar.title("Menú de navegación")
opcion = st.sidebar.radio("Selecciona una página", ["Inicio", "Gráficos por año", "Comparación de estaciones", "Comparación de años", "Filtros avanzados", "Conclusiones"])
# Página principal
if opcion == "Inicio":
    st.title("Análisis de la contaminación en Madrid")
    # Configuramos la pagina de inicio en 3 secciones
    # Primera sección: Introduccióm
    with st.container():
        st.subheader("🌍 ¿Por qué la contaminación es un problema?")
        st.write("La exposición a contaminantes como contaminantes como PM$_{2.5}$, PM$_{10}$, NO$_{2}$ y ozono " \
                "contribuye a problemas respiratorios, cardiovasculares y otras enfermedades crónicas.")
        st.write("Además del impacto directo en la salud, la calidad del aire influye en la economía, al aumentar los costes de "\
                "tratamientos médicos y las pérdidas de productividad laboral. Además de ocasionar gastos de mantenimiento y "\
                "restauración de edificios y monumentos")
        st.write("Este fenómeno es particularmente crítico en áreas urbanas densamente pobladas, como Madrid, que en 2021"
                "encabezaba la lista de ciudades europeas con mayor mortalidad atribuible a la contaminación.")

    # Segunda sección: Origen de los datos
    with st.container():
        st.subheader("📊 Los datos")
        st.write("Datos horarios de estaciones de calidad del aire desde 2001")
        st.write("API del Ayuntamiento de Madrid.")

    # Tercera sección: Extensión del análisis
    with st.container():
        st.subheader("🔎 Extensión del análisis")
        st.write(f"{num_estaciones} estaciones de medida")
        st.write(f"{num_contaminantes} contaminantes medidos")
        st.write(f"{num_anios} años analizados")
 
# Página de gráficos filtrados por año con Polars y Matplotlib
# Función para actualizar el estado
def actualizar_seleccion():
    st.session_state.estacion_seleccionada = st.session_state.estacion_key

if opcion == "Gráficos por año":
    st.title("Gráficos de estaciones por año")
    st.write("Aquí puedes ver las medias mensuales de los contaminantes medidos en cada estación "
             "de Madrid. Selecciona el año y la estación que quieras analizar")

    # Inicializar valores en session_state si no existen
    if "anio_seleccionado" not in st.session_state:
        st.session_state.anio_seleccionado = anios[0]
    
    if "estacion_seleccionada" not in st.session_state:
        st.session_state.estacion_seleccionada = estaciones[0]

    # Selectbox con claves y función de actualización
    anio_seleccionado = st.selectbox("Selecciona un año", anios, index=anios.index(st.session_state.anio_seleccionado), key="anio_key")
    estacion_seleccionada = st.selectbox("Selecciona una estación", estaciones, index=estaciones.index(st.session_state.estacion_seleccionada), key="estacion_key", on_change=actualizar_seleccion)

    # Actualizar año en session_state directamente
    st.session_state.anio_seleccionado = anio_seleccionado

    # Mostrar valores de session_state para depuración
    st.write("Año en session_state:", st.session_state.anio_seleccionado)
    st.write("Estación en session_state:", st.session_state.estacion_seleccionada)

    # Mostrar gráficos con valores correctos
    st.pyplot(fdb.estacion_anio(df_mensual, contaminantes, st.session_state.anio_seleccionado, st.session_state.estacion_seleccionada))

if opcion == "Comparación de estaciones":
    st.title("Comparación de estaciones de tráfico y fondo")
    st.write("Selecciona un año y una estación de cada tipo para comparar sus valores de contaminación.")

    # Inicializar valores en session_state si no existen
    if "anio_seleccionado" not in st.session_state:
        st.session_state.anio_seleccionado = anios[0]

    if "estacion_trafico" not in st.session_state:
        st.session_state.estacion_trafico = estaciones_trafico[0]

    if "estacion_fondo" not in st.session_state:
        st.session_state.estacion_fondo = estaciones_fondo[0]

    # Funciones para actualizar session_state
    def actualizar_trafico():
        st.session_state.estacion_trafico = st.session_state.trafico_key

    def actualizar_fondo():
        st.session_state.estacion_fondo = st.session_state.fondo_key

    # Selector de año único
    anio_seleccionado = st.selectbox("Selecciona un año", anios, index=anios.index(st.session_state.anio_seleccionado), key="anio_key")
    st.session_state.anio_seleccionado = anio_seleccionado  # Mantener año seleccionado

    # Crear dos columnas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Estaciones de tráfico")
        estacion_trafico = st.selectbox("Selecciona una estación de tráfico", estaciones_trafico, 
                                        index=estaciones_trafico.index(st.session_state.estacion_trafico), key="trafico_key", on_change=actualizar_trafico)
        st.pyplot(fdb.estacion_anio(df_mensual, contaminantes, anio_seleccionado, st.session_state.estacion_trafico))

    with col2:
        st.subheader("Estaciones de fondo")
        estacion_fondo = st.selectbox("Selecciona una estación de fondo", estaciones_fondo, 
                                      index=estaciones_fondo.index(st.session_state.estacion_fondo), key="fondo_key", on_change=actualizar_fondo)
        st.pyplot(fdb.estacion_anio(df_mensual, contaminantes, anio_seleccionado, st.session_state.estacion_fondo))

if opcion == "Comparación de años":
    st.title("Comparación de una estación en distintos años")
    st.write("Selecciona una estación y los 3 años que quieras analizar.")

    # Inicializar valores en session_state si no existen
    if "estacion_seleccionada" not in st.session_state:
        st.session_state.estacion_seleccionada = estaciones[0]

    if "anio1" not in st.session_state:
        st.session_state.anio1 = anios[0]

    if "anio2" not in st.session_state:
        st.session_state.anio2 = anios[0]

    if "anio3" not in st.session_state:
        st.session_state.anio3 = anios[0]

    # Funciones para actualizar session_state
    def actualizar_estacion():
        st.session_state.estacion_seleccionada = st.session_state.estacion_key

    def actualizar_anio1():
        st.session_state.anio1 = st.session_state.anio1_key

    def actualizar_anio2():
        st.session_state.anio2 = st.session_state.anio2_key

    def actualizar_anio3():
        st.session_state.anio3 = st.session_state.anio3_key

    # Selector de estación
    estacion_seleccionada = st.selectbox("Selecciona una estación", estaciones, 
                                         index=estaciones.index(st.session_state.estacion_seleccionada), 
                                         key="estacion_key", on_change=actualizar_estacion)


    # Crear tres columnas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Año 1")
        anio1 = st.selectbox("Selecciona un año", anios, index=anios.index(st.session_state.anio1), key="anio1_key", on_change=actualizar_anio1)
        st.pyplot(fdb.estacion_anio(df_mensual, contaminantes, st.session_state.anio1, st.session_state.estacion_seleccionada))

    with col2:
        st.subheader("Año 2")
        anio2 = st.selectbox("Selecciona un año", anios, index=anios.index(st.session_state.anio2), key="anio2_key", on_change=actualizar_anio2)
        st.pyplot(fdb.estacion_anio(df_mensual, contaminantes, st.session_state.anio2, st.session_state.estacion_seleccionada))

    with col3:
        st.subheader("Año 3")
        anio3 = st.selectbox("Selecciona un año", anios, index=anios.index(st.session_state.anio3), key="anio3_key", on_change=actualizar_anio3)
        st.pyplot(fdb.estacion_anio(df_mensual, contaminantes, st.session_state.anio3, st.session_state.estacion_seleccionada))

if opcion == "Filtros avanzados":
    st.title("Filtros avanzados")
    st.write("Aquí puedes ver las medias diarias por contaminante en la estación y el rango de fechas elegidas")
    # Filtramos solo los contaminantes de nitrógeno porque son los que aparecen en todas las estaciones
    contaminantes_filtrados = df_diario.filter(pl.col("contaminante").str.contains("nitrógeno"))["contaminante"].unique().to_list()

    # Inicializar valores en session_state si no existen
   
    if "contaminante_seleccionado" not in st.session_state:
        st.session_state.contaminante_seleccionado = contaminantes_filtrados[0]

    if "estacion_seleccionada" not in st.session_state:
        st.session_state.estacion_seleccionada = estaciones[0]    

    if "fecha_inicio" not in st.session_state:
        st.session_state.fecha_inicio = pd.to_datetime("2018-01-01").date()

    if "fecha_fin" not in st.session_state:
        st.session_state.fecha_fin = pd.to_datetime("2024-01-31").date()

    # Funciones para actualizar session_state
    def actualizar_contaminante():
        st.session_state.contaminante_seleccionado = st.session_state.contaminante_key
    def actualizar_estacion():
        st.session_state.estacion_seleccionada = st.session_state.estacion_key
    def actualizar_fecha_inicio():
        st.session_state.fecha_inicio = st.session_state.fecha_inicio_key
    def actualizar_fecha_fin():
        st.session_state.fecha_fin = st.session_state.fecha_fin_key
    # Selectores de filtros
    contaminante_seleccionado = st.selectbox("Selecciona un contaminante", contaminantes_filtrados, 
                                            index = contaminantes_filtrados.index(st.session_state.contaminante_seleccionado),
                                            key="contaminante_key", on_change = actualizar_contaminante)
    estacion_seleccionada = st.selectbox("Selecciona una estación", estaciones, 
                                            index = estaciones.index(st.session_state.estacion_seleccionada),
                                            key="estacion_key", on_change = actualizar_estacion)
    fecha_minima = df_diario["fecha"].min()
    fecha_maxima = df_diario["fecha"].max()

    fecha_inicio = st.date_input("Selecciona fecha de inicio", value=st.session_state.fecha_inicio,
                                 min_value = fecha_minima, max_value = fecha_maxima,
                                 key="fecha_inicio_key", on_change = actualizar_fecha_inicio)
    fecha_fin = st.date_input("Selecciona fecha de fin", value=st.session_state.fecha_fin,
                              min_value = fecha_minima, max_value = fecha_maxima,
                                 key="fecha_fin_key", on_change = actualizar_fecha_fin)

    # Filtrar datos por estación, contaminante y rango de fechas
    df_filtrado = df_diario.filter((pl.col("estacion") == st.session_state.estacion_seleccionada) & 
                            (pl.col("contaminante") == st.session_state.contaminante_seleccionado) & 
                            (pl.col("fecha").is_between(st.session_state.fecha_inicio, st.session_state.fecha_fin, closed="both")))


    # Graficar las medias diarias
    fig, ax = plt.subplots()
    ax.plot(df_filtrado["fecha"], df_filtrado["media_diaria"], marker="o", linestyle="-")
    ax.set_title(f"Medias diarias de {contaminante_seleccionado} en {estacion_seleccionada} entre {fecha_inicio} y {fecha_fin}")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Media diaria")
    ax.grid(True)
    plt.xticks(rotation=45)

    # Mostrar gráfico en Streamlit
    st.pyplot(fig)




  
    
    



