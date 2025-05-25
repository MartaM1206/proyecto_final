# Para tratamiento de datos
import polars as pl
import math
# Para visualizaciones
import seaborn as sns 
import matplotlib.pyplot as plt
# Para gestión de fechas
from datetime import datetime
# Para conectar a la base de datos
import psycopg2
# Cargar variables de entorno
import os
from dotenv import load_dotenv
# Configuracion de Polars para mostrar todas las columnas y hasta 25 filas
pl.Config.set_tbl_rows(25)  # Asegura que se muestren hasta 1000 filas
pl.Config.set_tbl_width_chars(500)  # Aumenta el ancho para evitar cortes
# importamos funciones de soporte
from src import funciones_load as fl

def obtener_datos(conexion, anio_inicio, anio_fin, zona):
    """
    Conecta a la base de datos PostgreSQL y ejecuta una consulta SQL para obtener datos 
    de contaminación en la zona especificada dentro del rango de años indicado. Devuelve 
    los resultados en un DataFrame de Polars.

    Args:
        conexion (str): 
            Cadena de conexión a la base de datos PostgreSQL.
        anio_inicio (int): 
            Año inicial del rango de consulta.
        anio_fin (int): 
            Año final del rango de consulta.
        zona (str): 
            Nombre de la zona geográfica para la consulta (ej. "Madrid").

    Returns:
        pl.DataFrame: 
            DataFrame de Polars con las siguientes columnas:
            ['estacion', 'contaminante', 'hora_medida', 'valor', 'unidad', 'id_medida', 'tipo_estacion'].
            Si la conexión falla o hay un error en la consulta, retorna `None`.
    """
    conn, cur = None, None
    
    try:
        conn, cur = fl.conectar_postgres(conexion)
        
        # Verificar que la conexión es válida antes de continuar
        if conn is None or cur is None:
            print("Error: No se pudo conectar a la base de datos.")
            return None

        
        query = """SELECT estaciones.nombre_estacion AS estacion,
                        contaminantes.descripcion_magnitud AS contaminante,
                        fecha_hora_f AS hora_medida, 
                        valor,
                        contaminantes.unidad AS unidad,
                        id_medida,
                        estaciones.tipo_estacion
                FROM medidas
                JOIN contaminantes ON medidas.magnitud = contaminantes.codigo_magnitud
                JOIN estaciones ON medidas.codigo_estacion = estaciones.codigo_estacion
                JOIN zonas ON estaciones.codigo_zona = zonas.codigo_zona
                WHERE EXTRACT(YEAR FROM fecha_hora_f) BETWEEN %s AND %s
                AND zonas.descripcion = %s"""

        cur.execute(query, (anio_inicio, anio_fin, zona))
        datos = cur.fetchall()
        
        # Definir nombres de columnas
        column_names = ["estacion", "contaminante", "hora_medida", "valor", "unidad", "id_medida", "tipo_estacion"]
        
        # Convertir resultados en un DataFrame de Polars
        df = pl.DataFrame(datos, schema=column_names, orient="row")
        
        return df

    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return None

    finally:
        # Cerrar cursor y conexión
        cur.close()
        conn.close()


def separar_datos(df):
    """
    Realiza el preprocesamiento de los datos de contaminación en un DataFrame de Polars.
    Convierte la columna "valor" a float, agrega columnas "mes", "año" y "fecha",
    y calcula la media mensual, diaria y anual de los valores.

    Args:
        df : pl.DataFrame
            DataFrame de Polars con datos de contaminación, incluyendo las columnas
            ["estacion", "contaminante", "hora_medida", "valor"].

    Returns:
        tuple (pl.DataFrame, pl.DataFrame, pl.DataFrame, list, list)
            - `df_mensual` (pl.DataFrame): Media mensual por estación y contaminante.
            - `df_diario` (pl.DataFrame): Media diaria por estación y contaminante.
            - `df_anual` (pl.DataFrame): Media anual por estación y contaminante.
            - `estaciones` (list): Lista de estaciones únicas en los datos.
            - `contaminantes` (list): Lista de contaminantes únicos en los datos.
    """

    # Convertimos la columna "valor" a float64
    df = df.with_columns(pl.col("valor").cast(pl.Float64))

    # Extraemos "mes", "año" y "fecha"
    df = df.with_columns([
        pl.col("hora_medida").dt.month().alias("mes"),
        pl.col("hora_medida").dt.year().alias("año"),
        pl.col("hora_medida").dt.date().alias("fecha")
    ])

    # Media mensual
    df_mensual = (
        df.group_by(["estacion", "contaminante", "mes", "año"])
        .agg(pl.col("valor").mean().round(2).alias("media_mensual"))
        .sort(["estacion", "contaminante", "año", "mes"])
    )

    # Media diaria
    df_diario = (
        df.group_by(["estacion", "contaminante", "fecha"])
        .agg(pl.col("valor").mean().round(2).alias("media_diaria"))
        .sort(["estacion", "contaminante", "fecha"])
    )

    # Media anual
    df_anual = (
        df.group_by(["estacion", "contaminante", "año"])
        .agg(pl.col("valor").mean().round(2).alias("media_anual"))
        .sort(["estacion", "contaminante", "año"])
    )

    # Extraer listas únicas para visualizaciones
    estaciones = df["estacion"].unique().to_list()
    contaminantes = df["contaminante"].unique().to_list()
    anios = df["año"].unique().to_list()
    return df_mensual, df_diario, df_anual, estaciones, contaminantes, anios




def estaciones_anio(df_mensual, contaminantes, año_seleccionado, estaciones_seleccionadas):
    """
    Genera un gráfico de medias mensuales de contaminantes para una estación específica y un año seleccionado.

    Args:
        df_mensual: DataFrame con los datos mensuales.
        contaminantes: Lista de contaminantes a graficar.
        estacion_seleccionada: Estación seleccionada para el análisis.
        año_seleccionado: Año a filtrar.
    Returns: 
        Figura de Matplotlib lista para visualizar en Streamlit.
    """
    # Crear diccionarios de colores y marcadores
    cmap = plt.get_cmap("tab20", len(contaminantes))
    colores_dict = {cont: cmap(i) for i, cont in enumerate(contaminantes)}

    marcadores_unicos = ['o', '^', 's', 'D', 'x', 'p', '*', 'h', '+', 'X', '|', '_', 'v', '<', '4']
    marcadores_dict = {cont: marcadores_unicos[i % len(marcadores_unicos)] for i, cont in enumerate(contaminantes)}

    # Filtrar por año y estación seleccionada
    df_año = df_mensual.filter(pl.col("año") == año_seleccionado)
    

    # Definir la cantidad de columnas y filas
    num_cols =  1
    num_rows = math.ceil(len(estaciones_seleccionadas)/num_cols)

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(12, 5), sharex=True, sharey=True)
    axes = axes.flatten().tolist()

    for j, estacion in enumerate(estaciones_seleccionadas):  
        df_estacion = df_año.filter(pl.col("estacion") == estacion).sort("mes")
        ax = axes[j]  

        for contaminante in contaminantes:
            df_contaminante = df_estacion.filter(pl.col("contaminante") == contaminante)
            if df_contaminante.height > 0:
                ax.plot(df_contaminante["mes"], df_contaminante["media_mensual"], 
                        marker=marcadores_dict[contaminante], color=colores_dict[contaminante], label=contaminante)

        ax.set_title(f"Estación {estacion} - Año {año_seleccionado}")
        ax.set_ylabel("Media Mensual")
        ax.set_xticks(df_contaminante["mes"].to_list())
        ax.set_xticklabels(df_contaminante["mes"], rotation=45, ha="right")
        ax.grid(True)
        plt.tight_layout()
    return fig
    

def graficar_contaminantes(df_mensual, contaminantes, estaciones, año_seleccionado):
    """
    Genera gráficos de medias mensuales de contaminantes por estación y año.

    :param df_mensual: DataFrame con los datos mensuales.
    :param contaminantes: Lista de contaminantes a graficar.
    :param estaciones: Lista de estaciones.
    :param año_seleccionado: Año a filtrar.
    """
    # Crear diccionarios de colores y marcadores
    cmap = plt.get_cmap("tab20", len(contaminantes))
    colores_dict = {cont: cmap(i) for i, cont in enumerate(contaminantes)}

    marcadores_unicos = ['o', '^', 's', 'D', 'x', 'p', '*', 'h', '+', 'X', '|', '_', 'v', '<', '4']
    marcadores_dict = {cont: marcadores_unicos[i % len(marcadores_unicos)] for i, cont in enumerate(contaminantes)}

    # Filtrar por año seleccionado
    df_año = df_mensual.filter(pl.col("año") == año_seleccionado)

    # Definir la cantidad de columnas y filas
    num_cols = 3  
    num_rows = math.ceil(len(estaciones)/num_cols)# Solo una fila para el año seleccionado

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(12, 5), sharex=True, sharey=True)
    axes = axes.flatten().tolist()

    for j, estacion in enumerate(estaciones):  
        df_estacion = df_año.filter(pl.col("estacion") == estacion).sort("mes")
        ax = axes[j]  

        for contaminante in contaminantes:
            df_contaminante = df_estacion.filter(pl.col("contaminante") == contaminante)
            if df_contaminante.height > 0:
                ax.plot(df_contaminante["mes"], df_contaminante["media_mensual"], 
                        marker=marcadores_dict[contaminante], color=colores_dict[contaminante], label=contaminante)

        ax.set_title(f"Estación {estacion} - Año {año_seleccionado}")
        ax.set_ylabel("Media Mensual")
        ax.set_xticks(df_contaminante["mes"].to_list())
        ax.set_xticklabels(df_contaminante["mes"], rotation=45, ha="right")
        ax.grid(True)
        plt.tight_layout()
    return fig

def estacion_anio(df_mensual, contaminantes, año_seleccionado, estacion_seleccionada):
    """
    Genera un gráfico de medias mensuales de contaminantes para una estación específica y un año seleccionado.

    Args:
        df_mensual: DataFrame con los datos mensuales.
        contaminantes: Lista de contaminantes a graficar.
        estacion_seleccionada: Estación seleccionada para el análisis.
        año_seleccionado: Año a filtrar.
    Returns: 
        Figura de Matplotlib lista para visualizar en Streamlit.
    """
    # Crear diccionarios de colores y marcadores
    cmap = plt.get_cmap("tab20", len(contaminantes))
    colores_dict = {cont: cmap(i) for i, cont in enumerate(contaminantes)}

    marcadores_unicos = ['o', '^', 's', 'D', 'x', 'p', '*', 'h', '+', 'X', '|', '_', 'v', '<', '4']
    marcadores_dict = {cont: marcadores_unicos[i % len(marcadores_unicos)] for i, cont in enumerate(contaminantes)}

    # Filtrar por año y estación seleccionada
    df_año = df_mensual.filter(pl.col("año") == año_seleccionado)
    df_estacion = df_año.filter(pl.col("estacion") == estacion_seleccionada)

    # Crear la figura
    fig, ax = plt.subplots(figsize=(10, 6))

    # Iterar sobre contaminantes y graficar cada uno
    for contaminante in contaminantes:
        df_contaminante = df_estacion.filter(pl.col("contaminante") == contaminante)
        if df_contaminante.height > 0:
            ax.plot(df_contaminante["mes"], df_contaminante["media_mensual"], 
                    marker=marcadores_dict[contaminante], color=colores_dict[contaminante], label=contaminante)

    # Configuración del gráfico
    ax.set_title(f"Estación {estacion_seleccionada} - Año {año_seleccionado}")
    ax.set_ylabel("Media Mensual")
    ax.set_xticks(df_estacion["mes"].to_list())
    ax.set_xticklabels(df_estacion["mes"], rotation=45, ha="right")
    ax.grid(True)
    
    # Leyenda
    handles = [plt.Line2D([0], [0], marker=marcadores_dict[c], color=colores_dict[c], linestyle='None', markersize=8)
               for c in contaminantes]
    fig.legend(handles, contaminantes, loc="upper center", bbox_to_anchor=(0.5, -0.15), title="Contaminantes", frameon=True, ncol=4, fontsize=10)

    fig.suptitle(f"Comparación de Medias Mensuales - Estación {estacion_seleccionada} - Año {año_seleccionado}", fontsize=16, y=1.02)
    plt.tight_layout()
    
    return fig  # Devuelve la figura para su uso en Streamlit