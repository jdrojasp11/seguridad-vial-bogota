import csv
import sqlite3
import sys
import unicodedata
from pathlib import Path

import pandas as pd

from config import (
    DIAS, FRANJAS, LOCALIDADES, ALIAS_LOCALIDAD, MESES,
    PROCESSED_DIR, RAW_DIR, SOURCES, DB_PATH, SQL_DIR,
)


def quitar_acentos(texto: str) -> str:
    if texto is None:
        return ""
    normal = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in normal if not unicodedata.combining(c))


def normalizar_localidad(valor) -> str:
    limpio = quitar_acentos(str(valor)).upper().strip()
    limpio = " ".join(limpio.split())
    limpio = limpio.replace("LA CANDELARIA", "LA CANDELARIA")
    return ALIAS_LOCALIDAD.get(limpio, limpio)


def franja_horaria(hora: int) -> str:
    for nombre, ini, fin in FRANJAS:
        if ini <= hora <= fin:
            return nombre
    return "Noche"


def cargar_siniestros() -> pd.DataFrame:
    ruta = RAW_DIR / SOURCES["siniestros"]["file"]
    print(f"  Leyendo {ruta.name}...")
    df = pd.read_csv(ruta, encoding="utf-8-sig", low_memory=False)
    columnas = ["OBJECTID", "CODIGO_ACCIDENTE", "FECHA_HORA_ACC", "ANO_OCURRENCIA_ACC",
                "DIRECCION", "GRAVEDAD", "CLASE_ACC", "LOCALIDAD",
                "LATITUD", "LONGITUD", "CIV", "PK_CALZADA"]
    df = df[[c for c in columnas if c in df.columns]].copy()

    sin_tz = df["FECHA_HORA_ACC"].astype(str).str.replace(r"\+\d{2}$", "", regex=True).str.strip()
    fechas = pd.to_datetime(sin_tz, format="%Y/%m/%d %H:%M:%S", errors="coerce")
    df["fecha_hora"] = fechas

    mascara = df["fecha_hora"].isna()
    if mascara.any():
        df.loc[mascara, "fecha_hora"] = pd.to_datetime(sin_tz[mascara], errors="coerce")

    df = df[df["fecha_hora"].notna()].copy()
    df["anio"] = df["ANO_OCURRENCIA_ACC"].fillna(df["fecha_hora"].dt.year).astype(int)
    df["mes"] = df["fecha_hora"].dt.month
    df["dia_semana"] = df["fecha_hora"].dt.weekday.map(lambda x: DIAS[x] if 0 <= x <= 6 else "Sin dato")
    df["hora"] = df["fecha_hora"].dt.hour
    df["franja_horaria"] = df["hora"].map(franja_horaria)
    df["nombre_mes"] = df["mes"].map(lambda m: MESES[m - 1] if 1 <= m <= 12 else "")

    df["GRAVEDAD"] = df["GRAVEDAD"].fillna("SIN DATO").astype(str).str.upper().str.strip()
    df["CLASE_ACC"] = df["CLASE_ACC"].fillna("SIN DATO").astype(str).str.upper().str.strip()
    df["LOCALIDAD"] = df["LOCALIDAD"].map(normalizar_localidad)
    df["nombre_localidad"] = df["LOCALIDAD"]
    print(f"  Siniestros validos: {len(df):,}")
    return df


def cargar_poblacion() -> pd.DataFrame:
    ruta = RAW_DIR / SOURCES["poblacion"]["file"]
    print(f"  Leyendo {ruta.name}...")
    df = pd.read_csv(ruta, encoding="utf-8-sig", sep=";", low_memory=False)
    df.columns = [c.strip().upper() for c in df.columns]
    df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce")
    df["POBLACION"] = pd.to_numeric(df["POBLACION"], errors="coerce")
    df = df[df["ANO"].notna() & df["POBLACION"].notna()].copy()

    sexos = set(df["SEXO"].astype(str).str.upper().unique())
    agregados = {"TOTAL", "AMBOS SEXOS", "AMBOS", "INDISTINTO"}
    if sexos & agregados:
        usar = df["SEXO"].astype(str).str.upper().isin(agregados)
        df = df[usar].copy()

    df["nombre_localidad"] = df["NOMBRE_LOCALIDAD"].map(normalizar_localidad)
    df["codigo_localidad"] = df["nombre_localidad"].map(codigo_de_localidad)
    df = df[df["codigo_localidad"].notna()].copy()
    df["codigo_localidad"] = df["codigo_localidad"].astype(int)

    agrupado = (df.groupby(["codigo_localidad", "ANO"], as_index=False)["POBLACION"]
                  .sum()
                  .rename(columns={"ANO": "anio", "POBLACION": "poblacion"}))
    agrupado["anio"] = agrupado["anio"].astype(int)
    agrupado["poblacion"] = agrupado["poblacion"].astype(int)
    print(f"  Registros poblacion agregados: {len(agrupado):,}")
    return agrupado


def codigo_de_localidad(nombre: str):
    if nombre == "BOGOTA":
        return 0
    if nombre in LOCALIDADES:
        return LOCALIDADES.index(nombre) + 1
    return None


def construir_dims(df: pd.DataFrame):
    dim_tiempo = df[["fecha_hora", "anio", "mes", "nombre_mes", "dia_semana", "hora", "franja_horaria"]].copy()
    dim_tiempo["id_tiempo"] = (dim_tiempo["fecha_hora"].dt.year * 1000000
                               + dim_tiempo["fecha_hora"].dt.month * 10000
                               + dim_tiempo["fecha_hora"].dt.day * 100
                               + dim_tiempo["fecha_hora"].dt.hour)
    dim_tiempo = dim_tiempo.drop_duplicates(subset=["id_tiempo"]).copy()
    dim_tiempo["fecha"] = dim_tiempo["fecha_hora"].dt.strftime("%Y-%m-%d")

    dim_gravedad = (df["GRAVEDAD"].drop_duplicates().sort_values()
                    .reset_index(drop=True))
    dim_gravedad = pd.DataFrame({
        "id_gravedad": range(1, len(dim_gravedad) + 1),
        "gravedad": dim_gravedad.values,
    })

    dim_clase = (df["CLASE_ACC"].drop_duplicates().sort_values().reset_index(drop=True))
    dim_clase = pd.DataFrame({
        "id_clase": range(1, len(dim_clase) + 1),
        "clase_accidente": dim_clase.values,
    })

    dim_localidad = pd.DataFrame({
        "codigo_localidad": [0] + list(range(1, len(LOCALIDADES) + 1)),
        "nombre_localidad": ["SIN LOCALIDAD / BOGOTA"] + LOCALIDADES,
    })

    df = df.merge(dim_gravedad, left_on="GRAVEDAD", right_on="gravedad", how="left")
    df = df.merge(dim_clase, left_on="CLASE_ACC", right_on="clase_accidente", how="left")
    df["id_localidad"] = df["nombre_localidad"].map(codigo_de_localidad)
    df["id_tiempo"] = (df["fecha_hora"].dt.year * 1000000
                       + df["fecha_hora"].dt.month * 10000
                       + df["fecha_hora"].dt.day * 100
                       + df["fecha_hora"].dt.hour)

    fact = pd.DataFrame({
        "id_siniestro": pd.to_numeric(df["OBJECTID"], errors="coerce"),
        "codigo_accidente": pd.to_numeric(df["CODIGO_ACCIDENTE"], errors="coerce"),
        "id_tiempo": df["id_tiempo"],
        "id_localidad": df["id_localidad"].fillna(0),
        "id_gravedad": df["id_gravedad"].fillna(0),
        "id_clase": df["id_clase"].fillna(0),
        "direccion": df["DIRECCION"],
        "latitud": pd.to_numeric(df["LATITUD"], errors="coerce"),
        "longitud": pd.to_numeric(df["LONGITUD"], errors="coerce"),
        "civ": pd.to_numeric(df["CIV"], errors="coerce"),
        "pk_calzada": pd.to_numeric(df["PK_CALZADA"], errors="coerce"),
    }).dropna(subset=["id_siniestro"])
    fact["id_siniestro"] = fact["id_siniestro"].astype("int64")
    fact["id_tiempo"] = fact["id_tiempo"].astype("int64")
    fact["id_localidad"] = fact["id_localidad"].astype("int64")
    fact["id_gravedad"] = fact["id_gravedad"].astype("int64")
    fact["id_clase"] = fact["id_clase"].astype("int64")
    fact = fact.drop_duplicates(subset=["id_siniestro"], keep="first")
    return fact, dim_tiempo, dim_gravedad, dim_clase, dim_localidad


def escribir_db(fact, dim_tiempo, dim_gravedad, dim_clase, dim_localidad, poblacion) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    esquema = (SQL_DIR / "01_schema.sql").read_text(encoding="utf-8")
    conexion = sqlite3.connect(DB_PATH)
    conexion.executescript(esquema)
    conexion.execute("PRAGMA foreign_keys = OFF;")

    dim_localidad.to_sql("dim_localidad", conexion, if_exists="append", index=False)
    dim_gravedad.to_sql("dim_gravedad", conexion, if_exists="append", index=False)
    dim_clase.to_sql("dim_clase", conexion, if_exists="append", index=False)
    dim_tiempo[["id_tiempo", "fecha", "anio", "mes", "nombre_mes", "dia_semana", "hora", "franja_horaria"]].to_sql(
        "dim_tiempo", conexion, if_exists="append", index=False)
    poblacion.to_sql("poblacion_localidad", conexion, if_exists="append", index=False)
    fact.to_sql("fact_siniestros", conexion, if_exists="append", index=False)
    conexion.commit()
    conexion.execute("ANALYZE;")
    conexion.commit()
    conexion.close()
    print(f"  Base de datos: {DB_PATH.name} ({DB_PATH.stat().st_size / 1e6:.1f} MB)")


def exportar_para_powerbi(fact, dim_tiempo, dim_gravedad, dim_clase, dim_localidad, poblacion) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    dim_localidad.to_csv(PROCESSED_DIR / "dim_localidad.csv", index=False, encoding="utf-8-sig")
    dim_gravedad.to_csv(PROCESSED_DIR / "dim_gravedad.csv", index=False, encoding="utf-8-sig")
    dim_clase.to_csv(PROCESSED_DIR / "dim_clase.csv", index=False, encoding="utf-8-sig")
    dim_tiempo[["id_tiempo", "fecha", "anio", "mes", "nombre_mes", "dia_semana", "hora", "franja_horaria"]].to_csv(
        PROCESSED_DIR / "dim_tiempo.csv", index=False, encoding="utf-8-sig")
    poblacion.to_csv(PROCESSED_DIR / "poblacion_localidad.csv", index=False, encoding="utf-8-sig")
    fact.to_csv(PROCESSED_DIR / "fact_siniestros.csv", index=False, encoding="utf-8-sig")
    fact.head(5000).to_csv(PROCESSED_DIR / "fact_siniestros_muestra.csv", index=False, encoding="utf-8-sig")
    print(f"  CSV exportados en {PROCESSED_DIR}")


def main() -> None:
    print("ETL - construccion del modelo estrella")
    df = cargar_siniestros()
    poblacion = cargar_poblacion()
    fact, dim_tiempo, dim_gravedad, dim_clase, dim_localidad = construir_dims(df)
    escribir_db(fact, dim_tiempo, dim_gravedad, dim_clase, dim_localidad, poblacion)
    exportar_para_powerbi(fact, dim_tiempo, dim_gravedad, dim_clase, dim_localidad, poblacion)
    print(f"  Hechos: {len(fact):,} | dim_tiempo: {len(dim_tiempo):,} | "
          f"dim_localidad: {len(dim_localidad)} | gravedad: {len(dim_gravedad)} | clase: {len(dim_clase)}")
    print("ETL finalizado.")


if __name__ == "__main__":
    sys.exit(main())
