PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS fact_siniestros;
DROP TABLE IF EXISTS dim_tiempo;
DROP TABLE IF EXISTS dim_localidad;
DROP TABLE IF EXISTS dim_gravedad;
DROP TABLE IF EXISTS dim_clase;
DROP TABLE IF EXISTS poblacion_localidad;

CREATE TABLE dim_localidad (
    codigo_localidad INTEGER PRIMARY KEY,
    nombre_localidad TEXT NOT NULL
);

CREATE TABLE dim_gravedad (
    id_gravedad INTEGER PRIMARY KEY,
    gravedad TEXT NOT NULL
);

CREATE TABLE dim_clase (
    id_clase INTEGER PRIMARY KEY,
    clase_accidente TEXT NOT NULL
);

CREATE TABLE dim_tiempo (
    id_tiempo INTEGER PRIMARY KEY,
    fecha TEXT NOT NULL,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    nombre_mes TEXT NOT NULL,
    dia_semana TEXT NOT NULL,
    hora INTEGER NOT NULL,
    franja_horaria TEXT NOT NULL
);

CREATE TABLE poblacion_localidad (
    codigo_localidad INTEGER NOT NULL,
    anio INTEGER NOT NULL,
    poblacion INTEGER NOT NULL,
    PRIMARY KEY (codigo_localidad, anio)
);

CREATE TABLE fact_siniestros (
    id_siniestro INTEGER PRIMARY KEY,
    codigo_accidente INTEGER,
    id_tiempo INTEGER NOT NULL,
    id_localidad INTEGER NOT NULL,
    id_gravedad INTEGER NOT NULL,
    id_clase INTEGER NOT NULL,
    direccion TEXT,
    latitud REAL,
    longitud REAL,
    civ INTEGER,
    pk_calzada REAL,
    FOREIGN KEY (id_tiempo) REFERENCES dim_tiempo (id_tiempo),
    FOREIGN KEY (id_localidad) REFERENCES dim_localidad (codigo_localidad),
    FOREIGN KEY (id_gravedad) REFERENCES dim_gravedad (id_gravedad),
    FOREIGN KEY (id_clase) REFERENCES dim_clase (id_clase)
);

CREATE INDEX idx_fact_tiempo ON fact_siniestros (id_tiempo);
CREATE INDEX idx_fact_localidad ON fact_siniestros (id_localidad);
CREATE INDEX idx_fact_gravedad ON fact_siniestros (id_gravedad);
CREATE INDEX idx_fact_clase ON fact_siniestros (id_clase);
