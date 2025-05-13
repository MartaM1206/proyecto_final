import requests
from datetime import datetime
import os
import zipfile
import pandas as pd
import camelot

def descargar_datos_cmadrid(url, carpeta_salida, formato = None, mes = False, dia = False):
    """
    Descarga archivos de datos desde una URL de la Comunidad de Madrid y los guarda localmente.

    Parámetros:
        url (str): URL de la API desde donde se obtendrán los datos.
        formato (str, opcional): Formato específico de los archivos a descargar (ejemplo: "csv", "json").
        mes (bool, opcional): Si es True, el archivo incluirá el mes y el año actual en el nombre.
        dia (bool, opcional): Si es True, el archivo incluirá la fecha completa actual en el nombre.
        carpeta_salida (str): Ruta de la carpeta donde se guardarán los archivos descargados.

    Retorna:
        list: Lista con los nombres de los archivos descargados correctamente.
    """
    # Obtenemos la fecha actual
    hoy =  datetime.now().date()
    # Hacemos la solicitud a la API  
    response = requests.get(url)
    archivos_descargados = [] # Lista para guardar los nombres de los archivos descargados
    # Comprobamos si la solicitud fue exitosa (código 200)
    if response.status_code == 200:
        data = response.json() # Convertimos la respuesta a JSON
        info = data.get("result", {}).get("resources") # Accedemos a la lista de archivos que necesitamos
        archivos_guardados = 0 # Inicio contador de archivos guardados
        archivos_totales = len(info) # Total de archivos disponibles
        # Convertimos el formato introducido a minúsculas para evitar errores
        formato_usuario = formato.lower() if formato else None 
        # Iteramos por cada archivo en la lista
        for elemento in info:
            # Obtenemos el formato y lo pasamos a minúsculas para comparar con el introducido
            formato_archivo = elemento.get("format").lower()
            # Obtenemos el nombre del archivo
            nombre = elemento.get("name")
            # Si no se especifica formato descargamos todos los archivos
            #  y si se especifica, descargamos solo los que coinciden
            if formato_usuario is None or formato_archivo == formato_usuario:
                datos = elemento.get("url") # url del archivo a descargar
                response = requests.get(datos) # Petición de descarga
                # Verificar si la descarga fue exitosa
                if response.status_code == 200:
                    # Especificamos nombre del archivo según los parámetros introducidos
                    if not mes and not dia: # si no hay mes ni dia
                        nombre = f'{carpeta_salida}/cmadrid_{nombre}.{formato_archivo}'
                    elif mes and not dia: # si hay mes pero no dia
                        nombre = f'{carpeta_salida}/cmadrid_{hoy.year}_{hoy.month}.{formato_archivo}'
                    elif dia and not mes: #si hay dia pero no mes
                        nombre = f'{carpeta_salida}/cmadrid_{hoy}.{formato_archivo}'
                    # Guardamos el archivo localmente
                    with open(nombre, 'wb') as file:
                        file.write(response.content) 
                    archivos_guardados +=1 # incrementamos el contador
                    archivos_descargados.append(elemento["name"]) # añadimos el nombre del archivo descargado a la lista
            else:
                    print(f"No se descargó el archivo {elemento["name"]}.{elemento["format"]}. Código de estado: {response.status_code}")
    print(f"{archivos_guardados} de {archivos_totales} archivos guardados exitosamente.")
    return archivos_descargados



def descargar_datos_madrid(url, carpeta_salida):
    """
    Descarga archivos de calidad del aire desde la API del Ayuntamiento de Madrid.
    
    Parámetros:
    - url (str): URL de la API donde se encuentran los datos de calidad del aire.
    - carpeta_salida (str): Ruta de la carpeta donde se guardarán los archivos descargados.

    La función consulta la API, filtra los archivos relevantes y los guarda en la carpeta indicada
    """
    # Obtenemos la fecha actual
    hoy =  datetime.now().date()  
    # hacemos perición a la API
    response = requests.get(url)
    # si la respuesta es exitosa obtenemos los datos en formato JSON
    if response.status_code == 200:
        data = response.json()
        elementos = data.get("result", {}).get("items") # accedemos a la lista de archivos que necesitamos
        # iteramos por cada elemento en la lista para filtrar los que necesitamos por su título
        for elemento in elementos:
            # Caso 1: "Calidad del aire. Estaciones de control"
            if elemento["title"] == "Calidad del aire. Estaciones de control":
                datos_est = elemento.get("distribution")
                for i in datos_est:
                    print(i.get("title"))
                    formato = i.get("format",{}).get("value").split('/')[-1]
                    if formato.lower() == "csv": # solo descargamos el csv
                        archivo = i.get("accessURL")
                        print(f"Descargando: {archivo} como madrid_{elemento["title"]}.{formato}")
                        response_est = requests.get(archivo)
                        if response_est.status_code == 200:
                            with open(f'{carpeta_salida}/madrid_{elemento["title"]}.{formato}', 'wb') as file:
                                file.write(response_est.content)
                                print("Archivo guardado exitosamente.")
                        else:
                            print(f"No se pudo descargar el archivo {elemento["title"]}. Código de estado: {response.status_code}")
             # Caso 2: "Calidad del aire. Datos en tiempo real acumulado"               
            elif elemento["title"] == "Calidad del aire. Datos en tiempo real acumulado":
                datos_tra = elemento.get("distribution")
                for i in datos_tra:
                    print(i.get("title"))
                    formato = i.get("format",{}).get("value").split('/')[-1]
                    if "csv" in i.get("title"): #descargamos solo el que tiene csv en su título
                        archivo = i.get("accessURL")
                        print(f"Descargando: {archivo} como madrid_{elemento["title"]}.{formato}")
                        response_tra = requests.get(archivo)
                        if response_tra.status_code == 200:
                            with open(f'{carpeta_salida}/madrid_{hoy}.{formato}', 'wb') as file:
                                file.write(response_tra.content)
                                print("Archivo guardado exitosamente.")
                        else:
                            print(f"No se pudo descargar el archivo {elemento["title"]}. Código de estado: {response.status_code}")
            # Caso 3: "Calidad del aire. Datos horarios desde 2001"
            elif elemento["title"] == "Calidad del aire. Datos horarios desde 2001":
                archivos_dh = []
                datos = elemento.get("distribution")
                for i in datos:
                    print(i.get("title"))
                    formato = i.get("format",{}).get("value").split('/')[-1]
                    archivo = i.get("accessURL")
                    print(f"Descargando: {archivo} como madrid_{i["title"]}.{formato}")
                    response_dh = requests.get(archivo)
                    if response_dh.status_code == 200:
                        with open(f'{carpeta_salida}/madrid_{i["title"]}.{formato}', 'wb') as file:
                            file.write(response_dh.content)
                            archivos_dh.append(i["title"])
                            print("Archivo guardado exitosamente.")
                    else:
                        print(f"No se pudo descargar el archivo {i["title"]}. Código de estado: {response.status_code}")
        else:
            print(f"No se pudo acceder a la API. Código de estado: {response.status_code}")
        return archivos_dh
    

def procesar_zips(ruta_entrada, lista_archivos, ruta_guardado):
    """
    Maneja archivos ZIP en la ruta especificada, extrayendo y concatenando los CSV dentro de ellos.

    Parámetros:
        ruta_entrada (str): Ruta donde se encuentran los archivos ZIP.
        lista_archivos (list): Lista de nombres de archivos ZIP a procesar.
        ruta_guardado (str): Ruta donde se guardan los archivos csv concatenados.

    La función extrae los archivos CSV de cada ZIP, los concatena y guarda el resultado en un nuevo archivo CSV, después elimina los ZIP.
    """
   
    # Diccionarios para almacenar listas de DataFrames y nombres de CSV
    listas_dfs = {}
    listas_csv = {}

    # Crear una carpeta para guardar los archivos concatenados si no existe
    carpeta_guardado = ruta_guardado
    os.makedirs(carpeta_guardado, exist_ok=True)

    for archivo in lista_archivos:
        ruta_zip = f"{ruta_entrada}/madrid_{archivo}.zip"  # Construir la ruta al archivo ZIP
        listas_dfs[archivo] = []  # Inicializar una lista de DataFrames para este archivo
        listas_csv[archivo] = []  # Inicializar una lista de nombres de CSV para este archivo

        # Abrir el ZIP y cargar los CSV
        with zipfile.ZipFile(ruta_zip, 'r') as zip_ref:
            listas_csv[archivo] = [nombre for nombre in zip_ref.namelist() if nombre.endswith(".csv")]
            
            for nombre_csv in listas_csv[archivo]:
                with zip_ref.open(nombre_csv) as f:
                    df = pd.read_csv(f, sep=";", index_col=0)
                    listas_dfs[archivo].append(df)

        # Concatenar los DataFrames de la lista en uno solo
        df_concatenado = pd.concat(listas_dfs[archivo], ignore_index=True)

        # Guardar el DataFrame concatenado en un archivo CSV
        ruta_salida = os.path.join(carpeta_guardado, f"madrid_{archivo}.csv")
        df_concatenado.to_csv(ruta_salida, sep=";", index=False)

        print(f"Archivo concatenado guardado en: {ruta_salida}")
    
        # Eliminar el archivo ZIP
        os.remove(ruta_zip)
        print(f"Archivo ZIP eliminado: {ruta_zip}")




def extraer_tabla_pdf(archivo_pdf, pagina, carpeta_salida):
    """
    Extrae la primera tabla de una página específica de un archivo PDF y la guarda como CSV.

    Args:
        archivo_pdf (str): Ruta del archivo PDF del cual se extraerán los datos.
        pagina (str): Número de la página donde se encuentra la tabla a extraer.
        carpeta_salida (str): Ruta donde se guardará el archivo CSV.

    Returns:
        bool: True si se extrajo y guardó la tabla correctamente, False si no se encontraron tablas.

    Raises:
        FileNotFoundError: Si el archivo PDF no existe.
        Exception: Para errores inesperados en la extracción de la tabla.
    """
    try:
        # Extraer tablas de la página indicada
        tablas = camelot.read_pdf(archivo_pdf, pages=pagina)

        # Verificar si se extrajeron tablas
        if len(tablas) > 0:
            tablas[0].to_csv(f"{carpeta_salida}/tabla_contaminantes.csv")  # Guardar la primera tabla como CSV
            print(f"✅ Tabla guardada en {carpeta_salida}")
            return True
        else:
            print("⚠️ No se encontraron tablas en la página indicada.")
            return False

    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {archivo_pdf}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")