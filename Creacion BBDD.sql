CREATE TABLE contaminantes (
    id_contaminante SERIAL PRIMARY KEY,
    nombre_contaminante TEXT
    unidad_contaminante TEXT,
    descripcion_unidad TEXT
);

CREATE TABLE comunidades_autonomas (
    id_ccaa SERIAL PRIMARY KEY,
    ccaa VARCHAR(255)
);

CREATE TABLE provincias (
    id_provincia SERIAL PRIMARY KEY,
    provincia VARCHAR(255),
    id_ccaa INT REFERENCES comunidades_autonomas(id_ccaa) ON DELETE CASCADE
);

CREATE TABLE municipios (
    id_municipio SERIAL PRIMARY KEY,
    municipio VARCHAR(255),
    id_provincia INT REFERENCES provincias(id_provincia) ON DELETE CASCADE
);

CREATE TABLE estaciones (
    id_estacion SERIAL PRIMARY KEY,
    nombre_estacion TEXT,
    id_municipio INT REFERENCES municipios(id_municipio) ON DELETE CASCADE,
    direccion TEXT,
    latitud DECIMAL(9, 6),
    longitud DECIMAL(9, 6),
    url_evento TEXT,
    codigo_postal TEXT, -- Cambio a texto para permitir el aviso "No disponible"
    direccion TEXT,
    horario TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    organizacion TEXT,
    id_ciudad INT REFERENCES ciudad(id_ciudad) ON DELETE CASCADE
);

CREATE TABLE medidas (
    id_medida VARCHAR(50) PRIMARY KEY,
    valor FLOAT,
    validacion TEXT,
    fecha_medida DATE,
    hora_medida TIME,
    id_estacion INT REFERENCES estaciones(id_estacion) ON DELETE CASCADE,
    id_contaminante INT REFERENCES contaminantes(id_contaminante) ON DELETE CASCADE
);
CREATE TABLE reservas (
    id_reserva VARCHAR(50) PRIMARY KEY,
    fecha_reserva DATE,
    inicio_estancia DATE,
    final_estancia DATE,
    precio_noche FLOAT CHECK (precio_noche >= 0),
    id_cliente VARCHAR(50) REFERENCES clientes(id_cliente) ON DELETE CASCADE,
    id_hotel INT REFERENCES hoteles(id_hotel) ON DELETE CASCADE
    
);