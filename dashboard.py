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
contaminantes_nitro = madrid.filter(pl.col("contaminante").str.contains("nitrógeno"))["contaminante"].unique().to_list()
contaminantes_filtrados =["Ozono"] + contaminantes_nitro
estaciones_verdes = ["Parque del Retiro", "Juan Carlos I", "Casa de Campo", "El Pardo"]
estaciones_fondo_urbanas = [estacion for estacion in estaciones_fondo if estacion not in estaciones_verdes]

# Sidebar para navegación
st.sidebar.title("Menú de navegación")
opcion = st.sidebar.radio("Selecciona una página", ["Sobre el Proyecto", "Análisis Anual por Estación", "Tráfico vs. Fondo", "Evolución por Estación", "Análisis Detallado", "Evolución Anual"])
# Página principal
if opcion == "Sobre el Proyecto":
    st.title("Análisis de la contaminación en Madrid")
    st.write("Introducción al análisis de la contaminación ambiental, incluyendo fuentes de datos y alcance del estudio.")
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

if opcion == "Análisis Anual por Estación":
    st.title("Tendencias Anuales por Estación")
    st.write("Visualización de las medias mensuales de contaminantes para una estación específica en un año determinado, con opciones de filtrado personalizadas.")

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
    st.plotly_chart(fdb.estacion_anio_interactivo(df_mensual, contaminantes, st.session_state.anio_seleccionado, st.session_state.estacion_seleccionada))

if opcion == "Tráfico vs. Fondo":
    st.title("Doble Perspectiva: Comparando Estaciones")
    st.write("Análisis comparativo de los niveles de contaminación entre una estación de tráfico y una estación de fondo en un año seleccionado.")

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
        st.plotly_chart(fdb.estacion_anio_interactivo(df_mensual, contaminantes, anio_seleccionado, st.session_state.estacion_trafico))

    with col2:
        st.subheader("Estaciones de fondo")
        estacion_fondo = st.selectbox("Selecciona una estación de fondo", estaciones_fondo, 
                                      index=estaciones_fondo.index(st.session_state.estacion_fondo), key="fondo_key", on_change=actualizar_fondo)
        st.plotly_chart(fdb.estacion_anio_interactivo(df_mensual, contaminantes, anio_seleccionado, st.session_state.estacion_fondo))

if opcion == "Evolución por Estación":
    st.title("Tres Años, Una Estación")
    st.write("Evolución temporal de los contaminantes en una única estación, con datos de tres años seleccionados por el usuario para identificar tendencias.")

    # Inicializar valores en session_state si no existen
    if "estacion_seleccionada" not in st.session_state:
        st.session_state.estacion_seleccionada = estaciones[0]

    if "anio1" not in st.session_state:
        st.session_state.anio1 = anios[0]

    if "anio2" not in st.session_state:
        st.session_state.anio2 = anios[1]

    if "anio3" not in st.session_state:
        st.session_state.anio3 = anios[2]

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
        st.plotly_chart(fdb.estacion_anio_interactivo(df_mensual, contaminantes, st.session_state.anio1, st.session_state.estacion_seleccionada))

    with col2:
        st.subheader("Año 2")
        anio2 = st.selectbox("Selecciona un año", anios, index=anios.index(st.session_state.anio2), key="anio2_key", on_change=actualizar_anio2)
        st.plotly_chart(fdb.estacion_anio_interactivo(df_mensual, contaminantes, st.session_state.anio2, st.session_state.estacion_seleccionada))

    with col3:
        st.subheader("Año 3")
        anio3 = st.selectbox("Selecciona un año", anios, index=anios.index(st.session_state.anio3), key="anio3_key", on_change=actualizar_anio3)
        st.plotly_chart(fdb.estacion_anio_interactivo(df_mensual, contaminantes, st.session_state.anio3, st.session_state.estacion_seleccionada))

if opcion == "Análisis Detallado":
    st.title("Análisis Personalizado de Contaminantes")
    st.write("Análisis detallado de los contaminantes comunes en una estación específica, con opción de filtro por fecha y visualización de medias diarias.")
    # Filtramos solo los contaminantes de nitrógeno porque son los que aparecen en todas las estaciones


    # Inicializar valores en session_state si no existen
   
    #if "contaminante_seleccionado" not in st.session_state:
        #st.session_state.contaminante_seleccionado = contaminantes[0]

    if "estacion_seleccionada" not in st.session_state:
        st.session_state.estacion_seleccionada = estaciones[0]    

    if "fecha_inicio" not in st.session_state:
        st.session_state.fecha_inicio = pd.to_datetime("2018-01-01").date()

    if "fecha_fin" not in st.session_state:
        st.session_state.fecha_fin = pd.to_datetime("2024-01-31").date()

    # Funciones para actualizar session_state
    #def actualizar_contaminante():
        #st.session_state.contaminante_seleccionado = st.session_state.contaminante_key
    def actualizar_estacion():
        st.session_state.estacion_seleccionada = st.session_state.estacion_key
    def actualizar_fecha_inicio():
        st.session_state.fecha_inicio = st.session_state.fecha_inicio_key
    def actualizar_fecha_fin():
        st.session_state.fecha_fin = st.session_state.fecha_fin_key
    # Selectores de filtros
    #contaminante_seleccionado = st.selectbox("Selecciona un contaminante", contaminantes, 
                                            #index = contaminantes.index(st.session_state.contaminante_seleccionado),
                                            #key="contaminante_key", on_change = actualizar_contaminante)
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
                            (pl.col("fecha").is_between(st.session_state.fecha_inicio, st.session_state.fecha_fin, closed="both")))


    fig = fdb.graficar_medias_diarias_interactivo(df_filtrado, contaminantes, estacion_seleccionada, fecha_inicio, fecha_fin)
    st.plotly_chart(fig)


if opcion == "Evolución Anual":
    st.title("Máximos, Mínimos y Tendencias en el Tiempo")
    st.write("Evaluación de la variabilidad anual de los niveles de contaminación, incluyendo análisis de tendencias, máximos y mínimos registrados en diferentes períodos.")


    # Evaluación anual
    with st.container():
        st.subheader("Evolución anual por estación")
        
        # Funciones para actualizar session_state
        def actualizar_trafico():
            st.session_state.estacion_trafico = st.session_state.trafico_key

        def actualizar_fondo():
            st.session_state.estacion_fondo = st.session_state.fondo_key
        
        def actualizar_verde():
            st.session_state.estacion_verde = st.session_state.verde_key
       # Inicializar valores en session_state si no existen
        if "estacion_verde" not in st.session_state:
            st.session_state.estacion_verde = estaciones_verdes[0]

        if "estacion_trafico" not in st.session_state:
            st.session_state.estacion_trafico = estaciones_trafico[0]

        if "estacion_fondo" not in st.session_state:
            st.session_state.estacion_fondo = estaciones_fondo_urbanas[0]
        # Crear tres columnas
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Estaciones de tráfico")
            estacion_trafico = st.selectbox("Selecciona una estación de tráfico", estaciones_trafico, 
                                            index=estaciones_trafico.index(st.session_state.estacion_trafico), key="trafico_key", on_change=actualizar_trafico)
            st.plotly_chart(fdb.evolucion_anual_interactivo(df_anual, contaminantes_filtrados, st.session_state.estacion_trafico))

        with col2:
            st.subheader("Estaciones de fondo")
            estacion_fondo = st.selectbox("Selecciona una estación de fondo", estaciones_fondo_urbanas, 
                                        index=estaciones_fondo_urbanas.index(st.session_state.estacion_fondo), key="fondo_key", on_change=actualizar_fondo)
            st.plotly_chart(fdb.evolucion_anual_interactivo(df_anual, contaminantes_filtrados, st.session_state.estacion_fondo))

        with col3:
            st.subheader("Estaciones de zonas verdes")
            estacion_verde = st.selectbox("Selecciona una estación de zona verde", estaciones_verdes, 
                                        index=estaciones_verdes.index(st.session_state.estacion_verde), key="verde_key", on_change=actualizar_verde)
            st.plotly_chart(fdb.evolucion_anual_interactivo(df_anual, contaminantes_filtrados, st.session_state.estacion_verde))

     # Evaluación máximos
    with st.container():
        st.subheader("Evolución de máximos anuales por estación")
        # Funciones para actualizar session_state
        def actualizar_trafico_max():
            st.session_state.estacion_trafico_max = st.session_state.trafico_max_key

        def actualizar_fondo_max():
            st.session_state.estacion_fondo_max = st.session_state.fondo_max_key
        
        def actualizar_verde_max():
            st.session_state.estacion_verde_max = st.session_state.verde_max_key
       # Inicializar valores en session_state si no existen
        if "estacion_verde_max" not in st.session_state:
            st.session_state.estacion_verde_max = estaciones_verdes[0]

        if "estacion_trafico_max" not in st.session_state:
            st.session_state.estacion_trafico_max = estaciones_trafico[0]

        if "estacion_fondo_max" not in st.session_state:
            st.session_state.estacion_fondo_max = estaciones_fondo_urbanas[0]
        # Crear tres columnas
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Estaciones de tráfico")
            estacion_trafico_max = st.selectbox("Selecciona una estación de tráfico", estaciones_trafico, 
                                            index=estaciones_trafico.index(st.session_state.estacion_trafico_max), key="trafico_max_key", on_change=actualizar_trafico_max)
            st.plotly_chart(fdb.evolucion_maximos_interactivo(df_diario, contaminantes_filtrados, st.session_state.estacion_trafico_max))

        with col2:
            st.subheader("Estaciones de fondo")
            estacion_fondo_max = st.selectbox("Selecciona una estación de fondo", estaciones_fondo_urbanas, 
                                        index=estaciones_fondo_urbanas.index(st.session_state.estacion_fondo_max), key="fondo_max_key", on_change=actualizar_fondo_max)
            st.plotly_chart(fdb.evolucion_maximos_interactivo(df_diario, contaminantes_filtrados, st.session_state.estacion_fondo_max))

        with col3:
            st.subheader("Estaciones de zonas verdes")
            estacion_verde = st.selectbox("Selecciona una estación de zona verde", estaciones_verdes, 
                                        index=estaciones_verdes.index(st.session_state.estacion_verde_max), key="verde_max_key", on_change=actualizar_verde_max)
            st.plotly_chart(fdb.evolucion_maximos_interactivo(df_diario, contaminantes_filtrados, st.session_state.estacion_verde_max))   
    



