from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
SQL_DIR = BASE_DIR / "sql"
DB_PATH = DATA_DIR / "warehouse.db"

SOURCES = {
    "siniestros": {
        "url": "https://datosabiertos.bogota.gov.co/dataset/8624f916-1db2-4c17-b669-19a19b35d1ca/resource/f5862aaa-4e1c-463e-94d5-f04db8164360/download/historico_siniestros_bogota_d.c_-.csv",
        "file": "siniestros_viales.csv",
        "dataset": "Historico Siniestros Bogota D.C.",
        "entity": "Secretaria Distrital de Movilidad (SDM)",
        "page": "https://datosabiertos.bogota.gov.co/dataset/historico-siniestros-bogota-d-c",
        "license": "CC-BY-4.0",
    },
    "poblacion": {
        "url": "https://datosabiertos.bogota.gov.co/dataset/85bf790d-84d1-4eda-bd6f-40af62e71d95/resource/37e58cb3-c870-4608-8c37-ce45db0eb7c1/download/osb_demografia-poblacion-localidad.csv",
        "file": "poblacion_localidad.csv",
        "dataset": "Poblacion en Bogota D.C. por Localidad 2005-2035",
        "entity": "Secretaria Distrital de Salud (SDS)",
        "page": "https://datosabiertos.bogota.gov.co/dataset/poblacion-en-bogota-d-c-2005-2035",
        "license": "CC-BY-4.0",
    },
}

FRANJAS = [
    ("Madrugada", 0, 5),
    ("Manana", 6, 11),
    ("Tarde", 12, 17),
    ("Noche", 18, 23),
]

DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

LOCALIDADES = [
    "USAQUEN", "CHAPINERO", "SANTA FE", "SAN CRISTOBAL", "USME",
    "TUNJUELITO", "BOSA", "KENNEDY", "FONTIBON", "ENGATIVA",
    "SUBA", "BARRIOS UNIDOS", "TEUSAQUILLO", "LOS MARTIRES",
    "ANTONIO NARINO", "PUENTE ARANDA", "LA CANDELARIA",
    "RAFAEL URIBE URIBE", "CIUDAD BOLIVAR", "SUMAPAZ",
]

ALIAS_LOCALIDAD = {
    "CANDELARIA": "LA CANDELARIA",
    "RAFAEL URIBE": "RAFAEL URIBE URIBE",
    "ANTONIO NARINO": "ANTONIO NARINO",
    "LOS MARTIRES": "LOS MARTIRES",
    "MARTIRES": "LOS MARTIRES",
    "CIUDAD BOLIVAR": "CIUDAD BOLIVAR",
    "BOGOTA": "BOGOTA",
    "BOGOTA D.C.": "BOGOTA",
    "BOGOTA DC": "BOGOTA",
    "SIN LOCALIDAD": "SIN LOCALIDAD",
    "SIN INFORMACION": "SIN LOCALIDAD",
}
