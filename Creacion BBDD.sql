CREATE TABLE contaminantes (
    id_contaminante INT PRIMARY KEY,
    nombre_contaminante TEXT,
    unidad_contaminante TEXT,
    descripcion_unidad TEXT,
    codigo_tecnica_de_medida INT,
    descripcion_tecnica_de_medida TEXT
);

CREATE TABLE estaciones (
    id_estacion INT PRIMARY KEY,
    nombre_estacion TEXT,
    municipio VARCHAR(255),
    direccion TEXT,
    latitud DECIMAL(9, 6),
    longitud DECIMAL(9, 6),
    id_zona VARCHAR(50)
);

CREATE TABLE medidas (
    provincia INT,
    municipio INT,
    estacion INT,
    magnitud INT,
    punto_muestreo TEXT,
    fecha TEXT,
    hora TEXT,
    valor TEXT,
    fecha_hora_f TIMESTAMP,
    validacion TEXT,
    id_medida TEXT PRIMARY KEY
);