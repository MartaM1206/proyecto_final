CREATE TABLE contaminantes (
    id_contaminante VARCHAR(50) PRIMARY KEY,
    nombre_contaminante TEXT,
    unidad_contaminante TEXT,
    descripcion_unidad TEXT,
    codigo_tecnica_de_medida VARCHAR(50),
    descripcion_tecnica_de_medida TEXT
);

CREATE TABLE zonas (
    id_municipio VARCHAR(50) PRIMARY KEY,
    descripcion TEXT
); 

CREATE TABLE provincias (
    id_provincia VARCHAR(50) PRIMARY KEY,
    nombre_provincia TEXT
);

CREATE TABLE municipios (
    id_municipio VARCHAR(50) PRIMARY KEY,
    nombre_municipio TEXT,
    id_provincia INT REFERENCES provincias(id_provincia)
);

CREATE TABLE estaciones (
    id_estacion VARCHAR(50) PRIMARY KEY,
    nombre_estacion TEXT,
    municipio VARCHAR(50) REFERENCES municipios(id_municipio),
    direccion TEXT,
    zona VARCHAR(50) REFERENCES zonas(id_zona),
    latitud DECIMAL(9, 6),
    longitud DECIMAL(9, 6),
    altitud INT    
);

CREATE TABLE medidas (
    id_medida TEXT PRIMARY KEY,
    estacion VARCHAR(50) REFERENCES estaciones(id_estacion),
    contaminante VARCHAR(25) REFERENCES contaminantes(id_contaminante),
    punto_muestreo TEXT,
    fecha TEXT,
    hora TEXT,
    valor DECIMAL(5, 3),
    fecha_hora_f TIMESTAMP,
    validacion TEXT,
);

