# importamos librerías
import pandas as pd
import numpy as np
import os
from unidecode import unidecode

def unir_archivos(carpeta_entrada, patron_nombre, carpeta_salida, nombre_salida):
    """
    Une múltiples archivos CSV en una sola tabla y los guarda en formato Parquet.

    Parámetros:
        carpeta_entrada (str): Ruta de la carpeta que contiene los archivos a unir.
        patron_nombre (str): Patrón en el nombre de los archivos a procesar.
        carpeta_salida (str): Ruta donde se guardará el archivo unificado.
        nombre_salida (str): Nombre del archivo de salida (sin extensión).

    Retorna:
        pd.DataFrame: DataFrame con los datos unificados.
    """
    carpeta = carpeta_entrada
    archivos = [archivo for archivo in os.listdir(carpeta) if archivo.lower().startswith(patron_nombre.lower())]
    df_lista = [pd.read_csv(os.path.join(carpeta, archivo), sep=";", parse_dates = True, encoding="latin1", low_memory = False) for archivo in archivos]
    print (archivos)
    df_unido = pd.concat(df_lista, ignore_index=True)
    df_unido.to_parquet(f"{carpeta_salida}/{nombre_salida}.parquet", index=False)
    print(f"archivo {nombre_salida}.parquet creado en {carpeta_salida}")
    return df_unido


def combinar_h_v(df):
    """
    Combina pares de columnas que comienzan con 'h' y 'v' en un solo campo concatenado.

    Parámetros:
        df (pd.DataFrame): DataFrame con columnas de medición de calidad del aire.

    Retorna:
        pd.DataFrame: DataFrame con nuevas columnas combinadas.
        list: Lista de nombres de las columnas creadas.
    """
    columnas_h = [col for col in df.columns if col.startswith('h')]
    columnas_v = [col for col in df.columns if col.startswith('v')]
    
    columnas_creadas = []  # Lista para almacenar nombres de las columnas creadas

    for col_h, col_v in zip(columnas_h, columnas_v):
        nueva_columna = f"{col_h}_{col_v}"  # Nombre de la nueva columna
        df[nueva_columna] = df[col_h].astype(str) + " " + df[col_v].astype(str)
        columnas_creadas.append(nueva_columna)  # Agregar el nombre de la columna a la lista
    
    return df, columnas_creadas

def formato_df(df):
    """
    Formatea un DataFrame con datos de calidad del aire, garantizando una estructura homogénea y bien organizada.

    Este proceso incluye:
    1. Conversión de columnas clave ("provincia", "municipio", "estacion", "magnitud", "ano", "mes" y "dia") a tipo string.
    2. Aseguramiento de que "mes" y "dia" tengan siempre dos dígitos.
    3. Creación de la columna "fecha" combinando año, mes y día.
    4. Unificación de las columnas de hora y validación mediante `combinar_h_v()`.
    5. Transformación de las columnas de hora en filas con `pd.melt()`.
    6. Extracción de la validación del valor y ajuste de la columna "hora".
    7. Modificación del valor "24" en "hora" a "23:59" y formato adecuado para otras horas.
    8. Creación de la columna "fecha_hora_f" en formato datetime.
    9. Extracción del estado de validación de la medida desde la columna "valor".
    10. Corrección de valores con comas decimales en todas las columnas tipo `str`, reemplazando `,` por `.`.
    11. Conversión de "valor" a tipo `float` para garantizar cálculos precisos.
    12. Generación de un identificador único "id_medida" para cada observación.
    13. Construcción del código "codigo_estacion" combinando "provincia", "municipio" y "estacion".
    14. Eliminación de filas con valores nulos o extremos.

    Args:
        df (pd.DataFrame): DataFrame con los datos de calidad del aire.

    Returns:
        pd.DataFrame: DataFrame formateado con la estructura correcta y listo para su análisis.

    """
    # Pasamos las columnas de "provincia", "municipio", "estacion" y "magnitud" a str porque no vamos a operar con esos números
    df[["provincia", "municipio", "estacion", "magnitud"]] = df[["provincia", "municipio", "estacion", "magnitud"]].astype(str)
    # Nos aseguramos de que las columnas de fecha sean str
    df[["ano", "mes", "dia"]] = df[["ano", "mes", "dia"]].astype(str)

    # Rellenamos mes y día para que siempre tengan 2 dígitos
    df["mes"] = df["mes"].str.zfill(2)
    df["dia"] = df["dia"].str.zfill(2)

    # Creamos la columna de fecha
    df["fecha"] = df["ano"] + "-" + df["mes"] + "-" + df["dia"]

    # Aseguramos que todos los valores con decimales tengan un punto como separador
    df = df.replace(",", ".", regex=True)

    # Combinamos las columnas de hora y validación
    df, columnas_creadas = combinar_h_v(df)

    # Transformamos el DataFrame para que las columnas de hora queden en filas
    df = df.melt(
        id_vars=["provincia", "municipio", "estacion", "magnitud", "punto_muestreo", "fecha"],
        value_vars=columnas_creadas,
        var_name="hora",
        value_name="valor"
    )

    # Ahora separamos la letra que acompaña al valor para crear la columna de validación y dejamos solo la hora
    df["hora"] = df["hora"].str.split("_", expand=True)[0].str.extract("(\\d+)")[0]

    # Ajustamos el formato de la hora para casos especiales
    df["hora"] = df["hora"].apply(lambda x: '23:59' if x == '24' else f"{str(x)}:00")

    # Creamos una columna de fecha y hora con formato datetime
    df["fecha_hora_f"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["hora"].astype(str))

    # Extraemos el estado de validación de la medida
    df["validacion"] = df["valor"].str.split(" ", expand=True)[1]
    df["valor"] = df["valor"].str.split(" ", expand=True)[0]

    # Corrige los valores con comas decimales antes de convertir a float
    df["valor"] = df["valor"].str.replace(",", ".")  # Reemplaza comas por puntos en decimales

    # Convertimos "valor" a float
    df["valor"] = df["valor"].astype(float)

    # Creamos un id único para cada medida
    df["id_medida"] = df["punto_muestreo"] + "_" + df["fecha"] + "_" + df["hora"] + "_" + df["validacion"]

    # Formamos el código de estación
    df["codigo_estacion"] = df["provincia"].astype(str).str.zfill(2) + \
                            df["municipio"].astype(str).str.zfill(3) + \
                            df["estacion"].astype(str).str.zfill(3)
    df["municipio"] = df["municipio"].astype(str).str.zfill(3)
    df["codigo_tecnica"] = df["punto_muestreo"].apply(lambda x: x.split('_')[-1])
    df["codigo_tecnica"] = df["codigo_tecnica"].str.replace("A", "47")
    df = df[df["valor"].abs() < 1000]
    df = df.dropna()
    df.drop_duplicates(subset=["id_medida"],inplace=True)
    return df

def formato_df_madrid(df):
    """
    Formatea el DataFrame de Madrid para que tenga el mismo formato que el de la Comunidad de Madrid.

    Este proceso incluye:
    1. Eliminación de filas duplicadas para asegurar datos únicos.
    2. Eliminación de la columna `"ï»¿PROVINCIA"` que contiene valores mayoritariamente nulos.
    3. Normalización de los nombres de las columnas, convirtiéndolos a minúsculas.
    4. Inserción de la columna `"provincia"` con el valor `"28"` para identificar la región.
    5. Corrección de valores con comas decimales (`","`) reemplazándolas por puntos (`"."`) en todas las celdas.

    Args:
        df (pd.DataFrame): DataFrame original de Madrid.

    Returns:
        pd.DataFrame: DataFrame formateado y listo para su análisis.
    """
   
    # eliminamos duplicados
    df.drop_duplicates(inplace=True)
    # eliminamos una columna con muchos nulos
    df.drop(columns = ["ï»¿PROVINCIA"], inplace=True)
    # pasamos todos los encabezdos a minúsculas
    df.columns = df.columns.str.lower()
    # añadimos la columna de provincia al principio
    df.insert(0, "provincia", "28")
    df["provincia"] = df["provincia"].astype(str)
    df = df.replace(",", ".", regex=True)
    return df

def formato_contaminantes(df):
    """
    Formatea el DataFrame de contaminantes para que tenga el formato adecuado.

    Args:
        df (pd.DataFrame): DataFrame original de contaminantes.

    Returns:
        pd.DataFrame: DataFrame formateado.
    """
    
    # cambiamos el nombre de las columnas a snake_case y quitamos las tildes
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    df.columns = df.columns.map(unidecode)
    df.columns = df.columns.str.replace('\r', '', regex=True).str.strip()
    df.columns = df.columns.str.replace('\n', '', regex=True).str.strip()
    
    return df

def crear_df_medidas(df_cmadrid, df_madrid, carpeta_salida):
    """
    Une y transforma los datos de calidad del aire de la Comunidad de Madrid y Madrid.

    Parámetros:
        df_cmadrid (pd.DataFrame): Datos de calidad del aire de la Comunidad de Madrid.
        df_madrid (pd.DataFrame): Datos de calidad del aire de Madrid.
        carpeta_salida (str): Carpeta donde se guardará el archivo final.

    Retorna:
        pd.DataFrame: DataFrame con los datos combinados y formateados.
    """
    df_madrid = formato_df_madrid(df_madrid)
    if df_cmadrid.columns.equals(df_madrid.columns):
        df_medidas = pd.concat([df_madrid, df_cmadrid], ignore_index=True)
        df_medidas = formato_df(df_medidas)
        df_medidas.to_parquet(f"{carpeta_salida}/medidas.parquet", index=False)
        print(f"Archivo medidas.parquet creado en {carpeta_salida}")
    return df_medidas

def diccionario_unidades(df):
    """
    Crea un diccionario de unidades basado en el DataFrame de contaminantes.

    Parámetros:
        df (pd.DataFrame): DataFrame con información de contaminantes.

    Retorna:
        dict: Diccionario con claves de unidades y descripciones.
    """
    
    # Obtenemos el diccionario de unidades
    df_unidades = df[["UNIDAD", "DESCRIPCIÓN UNIDAD"]].drop_duplicates()
    dict_unidades = df_unidades.set_index("UNIDAD")["DESCRIPCIÓN UNIDAD"].to_dict()
    
    return dict_unidades

def tablas_contaminantes(df_cmadrid, df_madrid, dict_unidades):
    """
    Procesa y estructura los datos de contaminantes atmosféricos de Madrid y la Comunidad de Madrid.

    Pasos realizados:
    1. Normaliza la unidad de medida en `df_madrid`, ajustando formatos de unidades.
    2. Mapea las unidades con sus descripciones usando `dict_unidades`.
    3. Reordena y homogeneiza las columnas de `df_madrid` para que coincidan con `df_cmadrid`.
    4. Concatenación de datos en `df_datos_contaminantes`.
    5. Conversión de valores numéricos a `str` para mantener coherencia.
    6. Extracción de técnicas de medida y contaminantes en DataFrames separados.

    Args:
        df_cmadrid (pd.DataFrame): Datos de contaminantes de la Comunidad de Madrid.
        df_madrid (pd.DataFrame): Datos de contaminantes de Madrid.
        dict_unidades (dict): Diccionario de unidades y sus descripciones.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]:  
            - `df_tecnicas`: DataFrame con técnicas de medida únicas.  
            - `df_contaminantes`: DataFrame con contaminantes procesados y estructurados.
    """

    df_madrid["Unidad"] = df_madrid["Unidad"].str.replace("µg/m 3", "µg/m3")
    df_madrid["Unidad"] = df_madrid["Unidad"].str.replace("3", "³")
    df_madrid["descripcion_unidad"] = df_madrid["Unidad"].map(dict_unidades)
    df_madrid.drop(columns=["Abrevia."], inplace=True)
    columnas_madrid_orden = ['Cod.', 'Mágnitud', 'Código \nTécnica', 'Técnica de medida', 'Unidad', "descripcion_unidad"]
    df_madrid = df_madrid[columnas_madrid_orden]
    formato_contaminantes(df_cmadrid)
    df_madrid.columns = df_cmadrid.columns
    df_datos_contaminantes = pd.concat([df_cmadrid, df_madrid], ignore_index=True)
    # cambiamos todas las columnas con números a string porque no operaremos con ellas
    df_datos_contaminantes[["codigo_tecnica_de_medida", "codigo_magnitud"]] = df_datos_contaminantes[["codigo_tecnica_de_medida", "codigo_magnitud"]].astype(str)
    df_tecnicas = df_datos_contaminantes[["codigo_tecnica_de_medida", "descripcion_tecnica_de_medida"]].drop_duplicates()
    df_tecnicas["descripcion_tecnica_de_medida"] = df_tecnicas["descripcion_tecnica_de_medida"].str.replace('\n', '', regex=True).str.strip()
    df_contaminantes = df_datos_contaminantes[['codigo_magnitud', 'descripcion_magnitud', 'unidad', 'descripcion_unidad']]
    df_contaminantes = df_contaminantes.drop(df_contaminantes[df_contaminantes["descripcion_magnitud"] == "Ozono Quimioluminiscencia"].index)
    df_contaminantes = df_contaminantes.drop_duplicates(subset=["codigo_magnitud"])
    return df_tecnicas, df_contaminantes

def obtener_zonas(df):
    """
    Extrae y formatea la información de zonas de calidad del aire desde un DataFrame.

    Pasos realizados:
    1. Extrae valores únicos de la columna `"zona_calidad_aire_descripcion"`.
    2. Separa la zona numérica y su descripción en columnas independientes.
    3. Elimina información redundante y estandariza nombres.
    4. Añade manualmente la zona de Madrid.

    Args:
        df (pd.DataFrame): DataFrame con la columna `"zona_calidad_aire_descripcion"`.

    Returns:
        pd.DataFrame: DataFrame con dos columnas:  
            - `"codigo_zona"`: Número de la zona.  
            - `"descripcion"`: Nombre descriptivo de la zona de calidad del aire.
    """
    # cogemos los valores únicos de la columna "zona_calidad_aire_descripcion" de estaciones_cmadrid
    df_zonas = pd.DataFrame(df["zona_calidad_aire_descripcion"].unique())
    # eliminamos la palabra "Zona" de la columna
    df_zonas[0] = df_zonas[0].str.replace("Zona ", "")
    # separamos en dos columnas: zona con el número de la zona y descripcion con el nombre de la zona y eliminamos la columnna original
    df_zonas[["codigo_zona", "descripcion"]]= df_zonas[0].str.split(" ", n=1,  expand = True)
    df_zonas.drop(columns=[0], inplace=True)
    # añadimos la fila con la informacion de la zona de Madrid
    df_zonas.loc[6] = ["1", "Madrid"]
    return df_zonas

def dms_to_decimal(dms_str):
    """
    Convierte una coordenada en formato DMS (Grados, Minutos, Segundos) a decimal.

    La función extrae los grados, minutos y segundos de una cadena en formato DMS
    y los convierte a un número en grados decimales, aplicando el signo correspondiente
    si la dirección es 'S' (Sur) o 'W' (Oeste).

    Args:
        dms_str (str): Cadena con la coordenada en formato DMS.  
                      Ejemplo: `'40°26'46"N'`, `'79°58'56"W'`.

    Returns:
        float: Coordenada convertida a formato decimal.  
               Los valores en el hemisferio sur y oeste son negativos.

    Ejemplo de uso:
    --------------
    >>> dms_to_decimal("40°26'46\"N")
    40.446111
    >>> dms_to_decimal("79°58'56\"W")
    -79.982222
    """
    partes = dms_str[:-1].replace("°", " ").replace("'", " ").replace('"', "").split()
    grados = float(partes[0])
    minutos = float(partes[1])
    segundos = float(partes[2]) if len(partes) > 2 else 0  # Puede que no incluya segundos
    direccion = dms_str[-1]  # Último carácter indica dirección (N, S, E, W)

    decimal = grados + (minutos / 60) + (segundos / 3600)

    if direccion in ["S", "W"]:  # Hacer negativo si es Sur u Oeste
        decimal *= -1
    return decimal

def obtener_estaciones_y_municipios(estaciones_cmadrid, estaciones_madrid):
    """
    Procesa y unifica los datos de estaciones de calidad del aire de la Comunidad de Madrid y Madrid.

    Pasos realizados:
    1. Extrae el código de zona desde `zona_calidad_aire_descripcion`.
    2. Renombra columnas y elimina información redundante para homogenizar el formato.
    3. Agrupa valores de benceno, tolueno y xileno en la nueva columna `analizador_BTX`.
    4. Convierte `fecha_alta` a formato datetime para evitar errores en la base de datos.
    5. Ajusta el formato de coordenadas (`coord_latitud`, `coord_longitud`) de DMS a decimal.
    6. Normaliza los nombres de columnas a **snake_case** y renombra claves.
    7. Mapea valores de contaminantes en Madrid al mismo formato que los de la Comunidad de Madrid.
    8. Convierte las columnas de contaminantes (`analizador_`) a tipo booleano (`True` / `False`).
    9. Concatena los datos en un único DataFrame `df_estaciones` con estructura unificada.
    10. Extrae y procesa los municipios en un DataFrame separado `df_municipios`.

    Args:
        estaciones_cmadrid (pd.DataFrame): Datos de estaciones de la Comunidad de Madrid.
        estaciones_madrid (pd.DataFrame): Datos de estaciones de Madrid.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]:  
            - `df_estaciones`: DataFrame con estaciones unificadas y procesadas.  
            - `df_municipios`: DataFrame con municipios únicos y códigos asignados.
    """

    # empezamos con estaciones_cmadrid
    # extraemos el número de zona de la columna "zona_calidad_aire_descripcion" en una nueva columna "codigo_zona"
    estaciones_cmadrid["codigo_zona"] = estaciones_cmadrid["zona_calidad_aire_descripcion"].str.extract(r"Zona (\d+)")
    # eliminamos la cadena "estacion_" de todas las columnas
    estaciones_cmadrid.columns = estaciones_cmadrid.columns.str.replace("estacion_", "")
    # las estaciones de Madrid unifican benceno, tolueno y xileno en la columna BTX, por lo que creamos una nueva columna "analizador_BTX" en estaciones_cmadrid
    # con el valor correspondiente a las 3 columnas individuales, si no fueran las 3 iguales, nos da un "Fallo"
    estaciones_cmadrid["analizador_BTX"] = estaciones_cmadrid.apply(lambda row: row["analizador_TOL"] if row["analizador_TOL"] == row["analizador_BEN"] == row["analizador_XIL"] else "Fallo", axis=1)
    # se pueden eliminar las columnas individuales que ahora son redundantes ["analizador_TOL", "analizador_BEN", "analizador_XIL"]
    # por dar la misma estructura que estaciones_madrid, duplicamos la columna "municipio" como "nombre_estacion"
    estaciones_cmadrid["nombre_estacion"] = estaciones_cmadrid["municipio"]
    # y cambiamos "direccion_postal" a "direccion"
    estaciones_cmadrid = estaciones_cmadrid.rename(columns={"direccion_postal":"direccion"})
    # convertimos "fecha_alta" a pydatetime para que no genere problemas con la BBDD
    estaciones_cmadrid["fecha_alta"] = pd.to_datetime(estaciones_cmadrid["fecha_alta"])
    estaciones_cmadrid["fecha_alta"] = estaciones_cmadrid["fecha_alta"].apply(lambda x: x.to_pydatetime())
    # como los sistemas de coordenadas no son exactamente los mismos, transformaremos las columnas 
    # "coord_longitud" y "coord_latitud" de estaciones_cmadrid al sistema decimal, equivalente a las 
    # columnas "LONGITUD" y "LATITUD" de estaciones_madrid
    # primero tenemos que cambiar comas por puntos y covertir a str
    estaciones_cmadrid[["coord_longitud", "coord_latitud"]] = estaciones_cmadrid[["coord_longitud", "coord_latitud"]].apply(lambda x: x.str.replace(",", "."))
    estaciones_cmadrid[["coord_longitud", "coord_latitud"]] = estaciones_cmadrid[["coord_longitud", "coord_latitud"]].astype(str)
    # aplicamos la función para convertir DMS a decimal
    estaciones_cmadrid["latitud"] = estaciones_cmadrid["coord_latitud"].apply(dms_to_decimal)
    estaciones_cmadrid["longitud"] = estaciones_cmadrid["coord_longitud"].apply(dms_to_decimal)
    # eliminamos columnas que no necesitamos
    estaciones_cmadrid.drop(columns=['analizador_TOL', 'analizador_BEN', 'analizador_XIL', 'zona_calidad_aire_descripcion', 'coord_UTM_ETRS89_x', 'coord_UTM_ETRS89_y', "coord_latitud", "coord_longitud"], inplace=True)
    # cambiamos también estaciones_madrid
    # separamos nom_tipo en tipo area y tipo estacion
    estaciones_madrid[["tipo_area", "tipo_estacion"]] = estaciones_madrid["NOM_TIPO"].str.split(" ", expand=True)
    # mapeamos los valores de las columnas de contaminantes al mismo formato que los de cmadrid
    estaciones_madrid[['NO2', 'SO2', 'CO', 'PM10', 'PM2_5', 'O3', 'BTX']] = estaciones_madrid[['NO2', 'SO2', 'CO', 'PM10', 'PM2_5', 'O3', 'BTX']].map(lambda x: "Si" if x == "X" else "No")
    # renombramos las columnas de contaminantes para que tengan el mismo formato que los de cmadrid
    estaciones_madrid = estaciones_madrid.rename(columns={col: f"analizador_{col}" for col in ['NO2', 'SO2', 'CO', 'PM10', 'PM2_5', 'O3', 'BTX']})
    # convertimos "fecha_alta" a pydatetime para que no genere problemas con la BBDD
    estaciones_madrid["Fecha alta"] = pd.to_datetime(estaciones_madrid["Fecha alta"], format = "%d/%m/%Y")
    estaciones_madrid["Fecha alta"] = estaciones_madrid["Fecha alta"].apply(lambda x: x.to_pydatetime())
    # elegimos el mismo formato de coordenadas que en estaciones_cmadrid y eliminamos columnas sobrantes
    estaciones_madrid.drop(columns=["CODIGO_CORTO", "COD_TIPO", "COD_VIA", "VIA_CLASE", "VIA_PAR", "VIA_NOMBRE", "NOM_TIPO", 
                                    'COORDENADA_X_ETRS89','COORDENADA_Y_ETRS89', 'LONGITUD_ETRS89', 'LATITUD_ETRS89'], inplace=True)
    # pasamos las columnas que lo necesitan a snake case
    columnas_cambio = ['CODIGO', 'ESTACION', 'DIRECCION','LONGITUD', 'LATITUD',
        'ALTITUD','Fecha alta']
    estaciones_madrid= estaciones_madrid.rename(columns ={col: col.lower().replace(" ", "_") for col in columnas_cambio})
    # renombramos columnas
    estaciones_madrid = estaciones_madrid.rename(columns={"estacion": "nombre_estacion"})
    # añadimos columnas que nos faltan y que, al tratarse de Madrid tienen un valor fijo
    estaciones_madrid["municipio"] = "Madrid"
    estaciones_madrid["subarea_rural"] = "No aplica"
    estaciones_madrid["codigo_zona"] = "1"
    df_estaciones = pd.concat([estaciones_cmadrid, estaciones_madrid], ignore_index=True)
    # capitalizamos la columna tipo_estacion y rellenamos con "Fondo" los valores nulos, ya que son estaciones colocadas en parques y ese parece ser el valor típico para parques
    df_estaciones["tipo_estacion"] = df_estaciones["tipo_estacion"].fillna("fondo").str.title()
    # Rellenamos valores nulos
    df_estaciones[["analizador_NO", "analizador_PM1", "analizador_O3Q",
                    "analizador_HCT", "analizador_HNM"]] = df_estaciones[["analizador_NO", "analizador_PM1",
                                                                        "analizador_O3Q", "analizador_HCT", "analizador_HNM"]] .fillna("No")
    # convertimos todas las columnas de "analizador_" en tipo bool para eso aplicamos una lambda que mapee "Si" por True y "No" por False
    analizadores = [col for col in df_estaciones.columns if col.startswith("analizador_")]
    df_estaciones[analizadores] = df_estaciones[analizadores].apply(lambda x: x.map({"Si": True, "No": False})).astype(bool)
    df_estaciones = df_estaciones.rename(columns={"codigo":"codigo_estacion"})
    df_estaciones["codigo_estacion"] = df_estaciones["codigo_estacion"].astype(str)
    df_estaciones["codigo_municipio"] = df_estaciones["codigo_estacion"].str[2:5]
    df_municipios = df_estaciones[["codigo_municipio", "municipio"]].drop_duplicates()
    df_municipios["codigo_provincia"] = "28"
    df_estaciones.drop(columns=["municipio"], inplace=True)
    return df_estaciones, df_municipios