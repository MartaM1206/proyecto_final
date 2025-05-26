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
# Extraemos información adicional
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
opcion = st.sidebar.radio("Selecciona una página", ["Sobre el Proyecto", "Tráfico vs. Fondo", "Análisis Detallado", "Evolución Anual"])
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
        st.write("Este fenómeno es particularmente crítico en áreas urbanas densamente pobladas, como Madrid, que en 2021 "\
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
 


# Página de comparación entre estaciones de tráfico y fondo
if opcion == "Tráfico vs. Fondo":
    st.title("Doble Perspectiva: Comparando Estaciones")
    st.write("Análisis comparativo de los niveles de contaminación entre una estación de tráfico y una estación de fondo en un año seleccionado.")
    # Usamos session_state para evitar que los valores seleccionados se pierdan al recargar la página
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

    # Creamos dos columnas para mostrar los gráficos en paralelo
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


# Configuramos la página de análisis detallado
if opcion == "Análisis Detallado":
    st.title("Análisis Personalizado de Contaminantes")
    st.write("Análisis detallado de los contaminantes en una estación específica, con opción de filtro por fecha y visualización de medias mensuales y diarias.")
    # organizamos la pagina en contenedores para poner filtros distintos
    # Evolución mensual
    with st.container():
        st.subheader("Valores mensuales por estación")
    # Usamos session_state para evitar que los valores seleccionados se pierdan al recargar la página
    # Inicializar valores en session_state si no existen
    if "estacion_seleccionada_mes" not in st.session_state:
        st.session_state.estacion_seleccionada_mes = estaciones[0]

    if "año_inicio" not in st.session_state:
        st.session_state.año_inicio = df_mensual["año"].min()

    if "año_fin" not in st.session_state:
        st.session_state.año_fin = df_mensual["año"].max()

    # Selector de estación
    estacion_seleccionada_mes = st.selectbox("Selecciona una estación", estaciones,
                                            index=estaciones.index(st.session_state.estacion_seleccionada_mes),
                                            key="estacion_mes_key")

    # Selector de rango de años
    año_inicio, año_fin = st.slider(
        "Selecciona un rango de años",
        min_value=df_mensual["año"].min(), max_value=df_mensual["año"].max(),
        value=(st.session_state.año_inicio, st.session_state.año_fin),
        key="rango_años_key"
    )

    # Guardar selección en session_state
    st.session_state.año_inicio = año_inicio
    st.session_state.año_fin = año_fin

    # Filtrar datos por estación y rango de años
    df_filtrado = df_mensual.filter(
        (pl.col("año").is_in(range(año_inicio, año_fin + 1))) &
        (pl.col("estacion") == estacion_seleccionada_mes) &
        (pl.col("contaminante").is_in(contaminantes))
    ).with_columns(
        (pl.col("año").cast(pl.Utf8) + "-" + pl.col("mes").cast(pl.Utf8)).alias("fecha_completa")
    ).sort(["año", "mes"])

    # Verificar si hay datos antes de graficar
    if df_filtrado.is_empty():
        st.warning("No hay datos disponibles para el rango de años y estación seleccionados.")
    else:
        fig = px.line(
            df_filtrado, x="fecha_completa", y="media_mensual", color="contaminante", markers=True,
            title=f"Medias Mensuales en {estacion_seleccionada_mes} ({año_inicio}-{año_fin})",
            labels={"media_mensual": "Media Mensual", "fecha_completa": "Fecha"},
            hover_data={"media_mensual": ":.2f", "fecha_completa": True})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig)

    # Evolución diaria
    with st.container():
        st.subheader("Valores diarios por estación")
        # Usamos session_state para evitar que los valores seleccionados se pierdan al recargar la página
        # Inicializar valores en session_state si no existen
    
        if "estacion_seleccionada" not in st.session_state:
            st.session_state.estacion_seleccionada = estaciones[0]    

        if "fecha_inicio" not in st.session_state:
            st.session_state.fecha_inicio = pd.to_datetime("2018-01-01").date()

        if "fecha_fin" not in st.session_state:
            st.session_state.fecha_fin = pd.to_datetime("2024-01-31").date()

        # Funciones para actualizar session_state
        def actualizar_estacion():
            st.session_state.estacion_seleccionada = st.session_state.estacion_key
        def actualizar_fecha_inicio():
            st.session_state.fecha_inicio = st.session_state.fecha_inicio_key
        def actualizar_fecha_fin():
            st.session_state.fecha_fin = st.session_state.fecha_fin_key
        # Selectores de filtros
       
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

        if df_filtrado.is_empty():
                st.warning("No hay datos disponibles para el rango de años y estación seleccionados.")
        else:
            fig = fdb.graficar_medias_diarias_interactivo(df_filtrado, contaminantes, estacion_seleccionada, fecha_inicio, fecha_fin)
            st.plotly_chart(fig)

  


# Configuramos la página de evolución anual
if opcion == "Evolución anual":
    st.title("Tendencias en el tiempo")
    st.write("Evaluación de la variabilidad anual de los niveles de contaminación, incluyendo análisis de tendencias y máximos registrados en diferentes períodos.")

    # Organizamos la página en contendores para que no se solapen los filtros
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
    



