CREATE TABLE provincias (
    codigo_provincia VARCHAR(25) PRIMARY KEY,
    nombre_provincia TEXT
);

CREATE TABLE municipios (
    codigo_municipio VARCHAR(50) PRIMARY KEY,
    nombre_municipio TEXT,
    codigo_provincia VARCHAR(25) REFERENCES provincias(codigo_provincia)
);

CREATE TABLE contaminantes (
    codigo_magnitud VARCHAR(50) PRIMARY KEY,
    descripcion_magnitud TEXT,
    unidad TEXT,
    descripcion_unidad TEXT
);
 
CREATE TABLE tecnicas_medida (
    codigo_tecnica_de_medida VARCHAR(50) primary KEY,
 	descripcion_tecnica_de_medida TEXT
);

CREATE TABLE zonas (
    codigo_zona VARCHAR(50) PRIMARY KEY,
    descripcion TEXT
); 

CREATE TABLE estaciones (
    codigo_estacion VARCHAR(50) PRIMARY KEY,
    fecha_alta DATE,
    tipo_area VARCHAR(50),
    tipo_estacion VARCHAR(50),
    subarea_rural VARCHAR(50),
    direccion TEXT,
    coord_latitud DECIMAL(9, 6),
    coord_longitud DECIMAL(9, 6),
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
    codigo_zona VARCHAR(50) REFERENCES zonas(codigo_zona),
    analizador_BTX BOOL,
    nombre_estacion TEXT,
    codigo_municipio VARCHAR(25) REFERENCES municipios(codigo_municipio)
);
     
CREATE TABLE medidas (
    provincia VARCHAR(25) REFERENCES provincias(codigo_provincia),
    municipio VARCHAR(25) REFERENCES municipios(codigo_municipio),
    estacion VARCHAR(25),
    magnitud VARCHAR(25) REFERENCES contaminantes(codigo_magnitud),
    punto_muestreo TEXT,
    fecha TEXT,
    hora TEXT,
    valor DECIMAL(5, 3),
    fecha_hora_f TIMESTAMP,
    validacion TEXT,
    id_medida VARCHAR(75) PRIMARY KEY,
    codigo_estacion VARCHAR(50) REFERENCES estaciones(codigo_estacion)
);
