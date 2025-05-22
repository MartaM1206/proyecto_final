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

def obtener_datos_madrid(conexion, anio_inicio, anio_fin, zona):
    """
    Conecta a la base de datos PostgreSQL, ejecuta una consulta SQL para obtener datos de contaminación
    en la zona especificada dentro del rango de años indicado y devuelve los resultados en un DataFrame de Polars.

    Args:
        conexion : str
            Cadena de conexión a la base de datos PostgreSQL.
        anio_inicio : int
            Año inicial del rango de consulta.
        anio_fin : int
            Año final del rango de consulta.
        zona : str
            Nombre de la zona geográfica para la consulta (ej. "Madrid").

    Returns:
        pl.DataFrame
            DataFrame de Polars con las columnas ['estacion', 'contaminante', 'hora_medida', 'valor', 'unidad', 'id_medida'].
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
                        id_medida
                FROM medidas
                JOIN contaminantes ON medidas.magnitud = contaminantes.codigo_magnitud
                JOIN estaciones ON medidas.codigo_estacion = estaciones.codigo_estacion
                JOIN zonas ON estaciones.codigo_zona = zonas.codigo_zona
                WHERE EXTRACT(YEAR FROM fecha_hora_f) BETWEEN %s AND %s
                AND zonas.descripcion = %s"""

        cur.execute(query, (anio_inicio, anio_fin, zona))
        datos = cur.fetchall()
        
        # Definir nombres de columnas
        column_names = ["estacion", "contaminante", "hora_medida", "valor", "unidad", "id_medida"]
        
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


def preproceso_datos(df):
    """
    Realiza el preprocesamiento de los datos de contaminación en un DataFrame de Polars.
    Convierte la columna "valor" a float, agrega una columna "mes_año" para agrupamiento 
    y calcula la media mensual de los valores. Además, extrae listas únicas de estaciones 
    y contaminantes presentes en el conjunto de datos.

    Args:
        df : pl.DataFrame
            DataFrame de Polars con datos de contaminación, incluyendo las columnas 
            ["estacion", "contaminante", "hora_medida", "valor"].

    Returns:
        tuple (pl.DataFrame, list, list)
            - `df_mensual` (pl.DataFrame): DataFrame con la media mensual por estación y contaminante.
            - `estaciones` (list): Lista de estaciones únicas en los datos.
            - `contaminantes` (list): Lista de contaminantes únicos en los datos.

    """
    # Convertimos la columna "valor" a float64
    df = df.with_columns(pl.col("valor").cast(pl.Float64))
    # Calculamos la media mensual de cada contaminante por estación
    # Primero creamos un df con una columna "mes_año" a partir de la columna "hora medida"
    # Después agrupamos por estación, contaminante y mes y calculamos la media de los balores
    df_mensual =(
    df.with_columns(
        pl.col("hora_medida").dt.month().alias("mes"))
            .group_by(["estacion", "contaminante", "mes"])  
            .agg(pl.col("valor").mean().round(2).alias("media_mensual"))  
            .sort(["estacion", "contaminante", "mes"])
                ) 
    # Extraemos listas con los valores únicos de estaciones y contaminantes 
    # para usarlas en las visualizaciones
    estaciones = df_mensual["estacion"].unique().to_list()
    contaminantes = df_mensual["contaminante"].unique().to_list()
    return df_mensual, estaciones, contaminantes

def graficos_estaciones(df_mensual, estaciones, contaminantes):
    """
    Genera una serie de gráficos en un grid de subplots, visualizando la evolución mensual de contaminantes 
    para distintas estaciones. Cada subplot representa una estación y muestra los niveles de contaminación 
    de varios contaminantes con diferentes colores y marcadores.

    Args: 
        df_mensual : pl.DataFrame
            DataFrame de Polars con datos agregados de contaminación mensual, incluyendo columnas:
            ["estacion", "contaminante", "mes", "media_mensual"].
            
        estaciones : list
            Lista con los nombres de las estaciones de monitoreo únicas.
            
        contaminantes : list
            Lista con los nombres de los contaminantes únicos en los datos.

    Returns:
        None
            La función genera los gráficos y los muestra en pantalla, pero no retorna ningún valor.
    """


    # Creamos un diccionario con un color para cada contaminante
    cmap = plt.cm.get_cmap("tab20", len(contaminantes))
    colores_dict = {cont: cmap(i) for i, cont in enumerate(contaminantes)}

    # Crear una lista de marcadores suficientemente variada para los contaminantes
    # y hacemos un diccionario con un marcador para cada contaminante
    # para facilitar la visualización
    marcadores_unicos = ['o', '^', 's', 'D', 'x', 'p', '*', 'h', '+', 'X', '|', '_', 'v', '<', '4']
    marcadores_dict = {cont: marcadores_unicos[i % len(marcadores_unicos)] for i, cont in enumerate(contaminantes)}

    # Configuramos subplots en cuadrícula
    cols_per_row = 2
    num_cols = len(estaciones)
    num_rows = math.ceil(num_cols / cols_per_row) # redondea hacia arriba en caso de que num_cols/cols_per_row no sea entero

    fig, axes = plt.subplots(num_rows, cols_per_row, figsize=(20, 5 * num_rows))

    # Convertimos ejes en lista para facilitar el acceso
    axes = axes.flatten().tolist()

    # Generamos un gráfico por cada estación
    for i, estacion in enumerate(estaciones):
        df_estacion = df_mensual.filter(pl.col("estacion") == estacion)
        ax = axes[i]

        for idx, contaminante in enumerate(contaminantes):
            df_contaminante = df_estacion.filter(pl.col("contaminante") == contaminante)
            if df_contaminante.height > 0:  # Evitar contaminantes sin datos
                ax.plot(df_contaminante["mes"], df_contaminante["media_mensual"], 
                        marker=marcadores_dict[contaminante], color=colores_dict[contaminante], label=contaminante)


            # Configuramos títulos y etiquetas
                ax.set_title(f"Estación {estacion}")
                ax.set_ylabel("Media Mensual de Contaminante")
                ax.set_xlabel("Mes")
                ax.grid(True)
                ax.set_xticks(df_contaminante["mes"].to_list())
                ax.set_xticklabels(df_contaminante["mes"], rotation=45, ha="right")


    # Creamos los elementos de la leyenda
    handles, labels = [], [] # Listas para almacenar iconos y etiquetas
    for contaminante in contaminantes:
        # Añadimos un icono que es un marcador con el color correspondiente para cada contaminante
        handles.append(plt.Line2D([0], [0], marker=marcadores_dict[contaminante], color=colores_dict[contaminante], linestyle='None', markersize=8))
        labels.append(contaminante)

    # Agregar la leyenda única con los colores y marcadores correctos
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.05), title="Contaminantes", frameon=True, ncol=4, fontsize=10)

    plt.tight_layout()
    plt.show()