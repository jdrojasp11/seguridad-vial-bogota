import re
import sqlite3
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from config import DB_PATH, FIGURES_DIR, PROCESSED_DIR, SQL_DIR

plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.bbox": "tight",
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.facecolor": "white",
})

AZUL = "#1f4e79"
ROJO = "#c0392b"
NARANJA = "#e67e22"
VERDE = "#2e7d32"
GRIS = "#7f8c8d"
PALETA = [AZUL, NARANJA, ROJO, VERDE, "#8e44ad", GRIS, "#16a085", "#d35400",
          "#2980b9", "#27ae60", "#c0392b", "#7f8c8d", "#f39c12", "#8e44ad"]


def leer_consultas(ruta: Path) -> dict:
    texto = ruta.read_text(encoding="utf-8")
    bloques = re.split(r"^--\s*name:\s*", texto, flags=re.MULTILINE)[1:]
    consultas = {}
    for bloque in bloques:
        nombre = bloque.splitlines()[0].strip()
        sql = "\n".join(bloque.splitlines()[1:]).strip().rstrip(";")
        consultas[nombre] = sql
    return consultas


def ejecutar_todas(conexion, consultas: dict) -> dict:
    return {nombre: pd.read_sql_query(sql, conexion) for nombre, sql in consultas.items()}


def _guardar(fig, nombre: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    destino = FIGURES_DIR / nombre
    fig.savefig(destino, dpi=120)
    plt.close(fig)
    print(f"  Figura -> reports/figures/{nombre}")


def fig_tendencia(datos: dict) -> None:
    df = datos["tendencia_anual"]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(df["anio"], df["siniestros"], marker="o", color=AZUL, linewidth=2.2, label="Total")
    ax.plot(df["anio"], df["con_heridos"], marker="s", color=NARANJA, linewidth=1.8, label="Con heridos")
    ax.plot(df["anio"], df["con_muertos"], marker="^", color=ROJO, linewidth=1.8, label="Con muertos")
    ax.set_title("Tendencia anual de siniestros viales en Bogota")
    ax.set_xlabel("Anio")
    ax.set_ylabel("Numero de siniestros")
    ax.set_xticks(df["anio"])
    ax.legend()
    _guardar(fig, "fig1_tendencia_anual.png")


def fig_top_localidades(datos: dict) -> None:
    df = datos["top_localidades"].head(12).sort_values("siniestros")
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(df["nombre_localidad"], df["siniestros"], color=AZUL, alpha=0.85)
    ax.set_title("Top 12 localidades por numero de siniestros (2015-2021)")
    ax.set_xlabel("Siniestros")
    _guardar(fig, "fig2_top_localidades.png")


def fig_tasa_100k(datos: dict) -> None:
    df = datos["tasa_100k"].head(12).sort_values("siniestros_x100k")
    fig, ax = plt.subplots(figsize=(9, 6))
    colores = [ROJO if v >= df["siniestros_x100k"].median() * 1.5 else AZUL
               for v in df["siniestros_x100k"]]
    ax.barh(df["nombre_localidad"], df["siniestros_x100k"], color=colores, alpha=0.9)
    ax.set_title("Siniestros por 100.000 habitantes por localidad")
    ax.set_xlabel("Siniestros por 100.000 hab.")
    _guardar(fig, "fig3_tasa_100k.png")


def fig_franja(datos: dict) -> None:
    df = datos["franja_horaria"]
    orden = ["Madrugada", "Manana", "Tarde", "Noche"]
    df = df.set_index("franja_horaria").reindex(orden).reset_index()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(df["franja_horaria"], df["siniestros"],
           color=[GRIS, NARANJA, AZUL, ROJO], alpha=0.9)
    ax.set_title("Siniestros por franja horaria")
    ax.set_xlabel("Franja horaria")
    ax.set_ylabel("Siniestros")
    _guardar(fig, "fig4_franja_horaria.png")


def fig_clase(datos: dict) -> None:
    df = datos["clase_accidente"].head(8).sort_values("siniestros")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(df["clase_accidente"], df["siniestros"], color=VERDE, alpha=0.9)
    ax.set_title("Siniestros por clase de accidente")
    ax.set_xlabel("Siniestros")
    _guardar(fig, "fig5_clase_accidente.png")


def fig_heatmap(datos: dict) -> None:
    df = datos["hora_dia"]
    orden_dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    tabla = (df.pivot_table(index="dia_semana", columns="hora", values="siniestros", fill_value=0)
               .reindex(orden_dias))
    fig, ax = plt.subplots(figsize=(12, 4.5))
    im = ax.imshow(tabla.values, aspect="auto", cmap="YlOrRd")
    ax.set_yticks(range(len(tabla.index)))
    ax.set_yticklabels(tabla.index)
    ax.set_xticks(range(0, 24))
    ax.set_xticklabels(range(0, 24))
    ax.set_title("Concentracion de siniestros: dia de la semana vs hora")
    ax.set_xlabel("Hora del dia")
    fig.colorbar(im, ax=ax, label="Siniestros")
    ax.grid(False)
    _guardar(fig, "fig6_heatmap_hora_dia.png")


def fig_severidad(datos: dict) -> None:
    df = datos["resumen_gravedad"]
    fig, ax = plt.subplots(figsize=(6, 5))
    colores = {"SOLO DANOS": GRIS, "CON HERIDOS": NARANJA, "CON MUERTOS": ROJO}
    etiquetas = [c if c in colores else GRIS for c in df["gravedad"]]
    ax.pie(df["siniestros"], labels=df["gravedad"], autopct="%1.1f%%",
           colors=[colores.get(g, AZUL) for g in df["gravedad"]],
           startangle=90, wedgeprops={"edgecolor": "white"})
    ax.set_title("Distribucion por gravedad")
    _guardar(fig, "fig7_gravedad.png")


def guardar_kpis(datos: dict) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for nombre, tabla in datos.items():
        tabla.to_csv(PROCESSED_DIR / f"kpi_{nombre}.csv", index=False, encoding="utf-8-sig")
    print(f"  KPIs exportados en {PROCESSED_DIR} (kpi_*.csv)")


def imprimir_resumen(datos: dict) -> None:
    print("\n================= RESUMEN EJECUTIVO =================")
    tend = datos["tendencia_anual"]
    total = int(tend["siniestros"].sum())
    print(f"Total de siniestros (2015-2021): {total:,}")
    print(f"Con heridos: {int(tend['con_heridos'].sum()):,} | "
          f"Con muertos: {int(tend['con_muertos'].sum()):,}")

    print("\nPor gravedad:")
    print(datos["resumen_gravedad"].to_string(index=False))

    print("\nTop 5 localidades por siniestros:")
    print(datos["top_localidades"].head(5).to_string(index=False))

    print("\nTop 5 localidades por siniestros x 100k hab.:")
    print(datos["tasa_100k"].head(5).to_string(index=False))

    print("\nFranja horaria:")
    print(datos["franja_horaria"].to_string(index=False))

    print("\nClase de accidente (top 5):")
    print(datos["clase_accidente"].head(5).to_string(index=False))
    print("=====================================================")


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit("No existe data/warehouse.db. Ejecuta primero el ETL (run_all.py).")
    consultas = leer_consultas(SQL_DIR / "02_kpi_queries.sql")
    conexion = sqlite3.connect(DB_PATH)
    try:
        datos = ejecutar_todas(conexion, consultas)
    finally:
        conexion.close()

    print("Generando figuras y KPIs...")
    fig_tendencia(datos)
    fig_top_localidades(datos)
    fig_tasa_100k(datos)
    fig_franja(datos)
    fig_clase(datos)
    fig_heatmap(datos)
    fig_severidad(datos)
    guardar_kpis(datos)
    imprimir_resumen(datos)
    print("\nAnalitica finalizada.")


if __name__ == "__main__":
    sys.exit(main())
