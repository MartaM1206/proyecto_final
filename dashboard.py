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

# Obtener el dataframe de la base de datos
conexion = os.getenv("conexion_bbdd")
madrid = fdb.obtener_datos(conexion, 2018, 2024, "Madrid")
df_mensual, df_diario, df_anual, estaciones, contaminantes = fdb.separar_datos(madrid)

# Configurar la página
st.title("Contaminación en Madrid")
st.markdown("Análisis de la contaminación en Madrid entre 2018 y 2024")

# Sección 1: Big Numbers
st.header("Estaciones de medición y contaminantes")
col1, col2 = st.columns(2)


# Mostrar Big Numbers
num_estaciones = len(estaciones)
num_contaminantes = len(contaminantes)


col1.metric("Estaciones disponibles", num_estaciones)
col2.metric("Contaminantes analizados", num_contaminantes)


# Sección 2: Gráficos 
st.title("Comparación de Presupuesto y Recaudación por Película")

# Crear el gráfico de barras horizontales agrupadas
fig, ax = plt.subplots()

# Posición de las barras
y = np.arange(len(datos_pelis["Película"])) 
height = 0.35  # Ancho de las barras

# Barras de presupuesto y recaudación
bars1 = ax.barh(y - height/2, datos_pelis["Presupuesto (en USD)"], height, label="Presupuesto")
bars2 = ax.barh(y + height/2, datos_pelis["Recaudación mundial (USD)"], height, label="Recaudación")

ax.set_ylabel("Película")
ax.set_xlabel("Monto en millones de dólares")
ax.set_yticks(y)
ax.set_yticklabels(datos_pelis["Película"])
ax.legend()

st.pyplot(fig)

st.title("Comparación de Recaudación en mercados por Película")
# Crear el gráfico de barras horizontales agrupadas
fig, ax = plt.subplots()

# Posición de las barras
y = np.arange(len(datos_pelis["Película"])) 
height = 0.35  # Ancho de las barras

# Barras de presupuesto y recaudación
bars1 = ax.barh(y - height/2, datos_pelis["Recaudación USA (USD)"], height, label="Recaudación USA")
bars2 = ax.barh(y + height/2, datos_pelis["Recaudación internacional (USD)"], height, label="Recaudación internacional")

ax.set_ylabel("Película")
ax.set_xlabel("Monto en millones de dólares")
ax.set_yticks(y)
ax.set_yticklabels(datos_pelis["Película"])
ax.legend()

st.pyplot(fig)