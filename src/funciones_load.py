import psycopg2

def conectar_postgres(dsn):
    """
    Establece conexión con una base de datos PostgreSQL usando una cadena DSN.

    Args:
        dsn (str): Cadena DSN con los datos de conexión. 
                   Ejemplo: "dbname=mi_base_de_datos user=mi_usuario password=mi_contraseña host=localhost port=5432"

    Returns:
        tuple: (conn, cur) si la conexión es exitosa, None en caso de error.
    """
    try:
        # Establecer conexión usando la cadena DSN
        conn = psycopg2.connect(dsn)
        
        # Crear cursor
        cur = conn.cursor()
        
        # Ejecutar una consulta de prueba
        cur.execute("SELECT 1;")
        resultado = cur.fetchone()
        
        if resultado:
            print("Conexión establecida y consulta de prueba exitosa.")
            return conn, cur
        else:
            print("Error en la consulta de prueba.")
            conn.close()
            return None

    except psycopg2.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def cargar_datos(conn, cur, lista_df, lista_tablas, dict_pk):
    """
    Inserta datos de múltiples DataFrames en sus respectivas tablas en PostgreSQL.

    Pasos del proceso:
    1. Emparejar cada DataFrame con la tabla correspondiente en la base de datos.
    2. Generar un string con los títulos de columna separados por comas.
    3. Crear una plantilla de valores con el número adecuado de marcadores "%s".
    4. Obtener la clave primaria de la tabla desde `dict_pk`, si está definida.
    5. Generar una consulta SQL para la inserción:
       - Si hay clave primaria, usar `ON CONFLICT` para evitar duplicados.
       - Si no hay clave primaria, realizar una inserción estándar.
    6. Convertir cada fila del DataFrame en una tupla para la inserción.
    7. Insertar los datos en la tabla mediante `executemany()`.
    8. Confirmar los cambios con `commit()`.
    9. Mostrar un mensaje indicando que los registros se han insertado correctamente.

    Args:
        conn (psycopg2.connection): Conexión activa a la base de datos PostgreSQL.
        cur (psycopg2.cursor): Cursor de la base de datos.
        lista_df (list): Lista de DataFrames con los datos a insertar.
        lista_tablas (list): Lista de nombres de tablas en la base de datos.
        dict_pk (dict): Diccionario con claves primarias de las tablas.

    Returns:
        None
    """
    
    for df, tabla in zip(lista_df, lista_tablas): # emparejamos pares de valores, cada df con la tabla de la base de datos a la que va
        # generamos un string con los titulos de columna separados por comas (no es una lista)
        columnas = ", ".join(df.columns)
        # generamos un string tantos valores "%s" como columnas tenga el df
        valores = ", ".join(['%s'] * len(df.columns))
        # Obtenemos la clave primaria de la tabla
        pk = dict_pk.get(tabla, None)
        # generamos la query para cada par df-tabla con las "listas" de columnas y valores que hemos obtenido
        if pk: # Si hay clave primaria definida, usa ON CONFLICT para no subir registros duplicados
            query = f"""INSERT INTO {tabla} ({columnas})  
                        VALUES ({valores})  
                        ON CONFLICT ({pk}) DO NOTHING;"""
        else: # Si no hay clave primaria definida, no usar ON CONFLICT
            query = f"""INSERT INTO {tabla} ({columnas})  
                        VALUES ({valores});  
                    """
        datos = [tuple(row) for row in df.itertuples(index=False)]
        cur.executemany(query, datos)  # Insertar un lote de filas
        conn.commit()

        print(f"Registros insertados correctamente en {tabla}")



def cargar_csv_postgres(cur, conn, archivos_tablas):
    """
    Carga archivos CSV en tablas PostgreSQL utilizando el método COPY.

    Args:
        cur (psycopg2.cursor): Cursor de la base de datos PostgreSQL.
        conn (psycopg2.connection): Conexión activa a la base de datos.
        archivos_tablas (list): Lista de tuplas con el formato (archivo_csv, tabla).

    Returns:
        None
    """
    for archivo, tabla in archivos_tablas:
        try:
            with open(archivo, "r", encoding="utf-8", errors="replace") as f:
                cur.copy_expert(f"COPY {tabla} FROM STDIN WITH CSV DELIMITER ';' ENCODING 'UTF8'", f)
            
            conn.commit()
            print(f"✅ Datos de {archivo} cargados exitosamente en {tabla}.")
        
        except psycopg2.Error as e:
            conn.rollback()
            print(f"❌ Error al cargar {archivo} en {tabla}: {e}")

def cerrar_conexion(conn, cur):
    """
    Cierra el cursor y la conexión a la base de datos PostgreSQL.

    Pasos del proceso:
    1. Cerrar el cursor para liberar recursos asociados a las consultas.
    2. Cerrar la conexión a la base de datos.

    Args:
        conn (psycopg2.connection): Conexión activa a la base de datos.
        cur (psycopg2.cursor): Cursor de la base de datos.

    Returns:
        None
    """
    cur.close()
    conn.close()
    print("Conexión cerrada")