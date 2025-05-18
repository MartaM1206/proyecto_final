CREATE TABLE provincias (
    codigo_provincia VARCHAR(10) PRIMARY KEY,
    nombre_provincia TEXT
);

CREATE TABLE municipios (
    codigo_municipio VARCHAR(10) PRIMARY KEY,
    municipio TEXT,
    codigo_provincia VARCHAR(10) REFERENCES provincias(codigo_provincia)
);

CREATE TABLE contaminantes (
    codigo_magnitud VARCHAR(10) PRIMARY KEY,
    descripcion_magnitud TEXT,
    unidad TEXT,
    descripcion_unidad TEXT
);

CREATE TABLE tecnicas_medida (
    codigo_tecnica_de_medida VARCHAR(10) PRIMARY KEY,
 	descripcion_tecnica_de_medida TEXT
);

CREATE TABLE zonas (
    codigo_zona VARCHAR(10) PRIMARY KEY,
    descripcion TEXT
); 

CREATE TABLE estaciones (
    codigo_estacion VARCHAR(20) PRIMARY KEY,
    fecha_alta TIMESTAMP,
    tipo_area VARCHAR(50),
    tipo_estacion VARCHAR(50),
    subarea_rural VARCHAR(50),
    direccion TEXT,
    latitud DECIMAL(9, 6),
    longitud DECIMAL(9, 6),
    altitud INT,
    analizador_NO BOOL,
    analizador_NO2 BOOL,
    analizador_PM10 BOOL,
    analizador_PM2_5 BOOL,
    analizador_PM1 BOOL,
    analizador_O3 BOOL,
    analizador_O3Q BOOL,
    analizador_CO BOOL,
    analizador_SO2 BOOL,
    analizador_HCT BOOL,
    analizador_HNM BOOL,
    codigo_zona VARCHAR(10) REFERENCES zonas(codigo_zona),
    analizador_BTX BOOL,
    nombre_estacion TEXT,
    codigo_municipio VARCHAR(10) REFERENCES municipios(codigo_municipio)
);
     
CREATE TABLE medidas (
    provincia VARCHAR(10) REFERENCES provincias(codigo_provincia),
    municipio VARCHAR(10) REFERENCES municipios(codigo_municipio),
    estacion VARCHAR(10),
    magnitud VARCHAR(10) REFERENCES contaminantes(codigo_magnitud),
    punto_muestreo TEXT,
    fecha TEXT,
    hora TEXT,
    valor DECIMAL(5, 3),
    fecha_hora_f TIMESTAMP,
    validacion TEXT,
    id_medida VARCHAR(75) PRIMARY KEY,
    codigo_estacion VARCHAR(20) REFERENCES estaciones(codigo_estacion),
    codigo_tecnica VARCHAR(10) REFERENCES tecnicas_medida(codigo_tecnica_de_medida)
);



-- Crear la función que ejecutará la eliminación de registros
CREATE OR REPLACE FUNCTION reemplazar_medida()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM medidas
    WHERE LEFT(NEW.id_medida, LENGTH(NEW.id_medida)-1) = LEFT(id_medida, LENGTH(id_medida)-1)
    AND RIGHT(id_medida, 1) IN ('N', 'T');

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear el trigger que ejecuta la función antes de insertar un nuevo id_medida terminado en V
CREATE TRIGGER trigger_reemplazo_medida
BEFORE INSERT ON medidas
FOR EACH ROW
WHEN (RIGHT(NEW.id_medida, 1) = 'V')
EXECUTE FUNCTION reemplazar_medida();