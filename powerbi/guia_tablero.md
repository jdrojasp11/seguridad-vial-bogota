# Guia del tablero en Power BI

El pipeline de Python deja los datos listos para Power BI en `data/processed/`
(en formato estrella). Sigue estos pasos para construir el tablero.

## 1. Obtener los datos

Ejecuta primero el pipeline (genera los CSV y la base SQLite):

```bash
python src/run_all.py
```

Archivos generados en `data/processed/`:

| Archivo | Rol |
|---|---|
| `fact_siniestros.csv` | Tabla de hechos (199.146 filas) |
| `dim_tiempo.csv` | Dimension tiempo |
| `dim_localidad.csv` | Dimension localidad (21 filas) |
| `dim_gravedad.csv` | Dimension gravedad |
| `dim_clase.csv` | Dimension clase de accidente |
| `poblacion_localidad.csv` | Poblacion por localidad y anio |

> Alternativa: conectarse a la base SQLite `data/warehouse.db` con el driver
> **ODBC SQLite** (Obtener datos > ODBC). La via mas sencilla es importar los CSV.

## 2. Cargar y modelar

1. **Obtener datos > Texto/CSV** e importa los 6 archivos de `data/processed/`.
2. En el Editor de Power Query revisa tipos: `id_*` y `anio` como **Entero**,
   `latitud`/`longitud` como **Decimal**.
3. Crea las relaciones (Vista de modelo):

| Desde | Hacia | Cardinalidad |
|---|---|---|
| `fact_siniestros[id_tiempo]` | `dim_tiempo[id_tiempo]` | Muchos a uno |
| `fact_siniestros[id_localidad]` | `dim_localidad[codigo_localidad]` | Muchos a uno |
| `fact_siniestros[id_gravedad]` | `dim_gravedad[id_gravedad]` | Muchos a uno |
| `fact_siniestros[id_clase]` | `dim_clase[id_clase]` | Muchos a uno |
| `poblacion_localidad[codigo_localidad]` | `dim_localidad[codigo_localidad]` | Muchos a uno |

4. Marca `dim_tiempo` como **tabla de fechas** usando la columna `fecha`.
5. Crea las medidas de `powerbi/medidas_dax.md`.

## 3. Diseno de paginas sugerido

### Pagina 1 - Resumen ejecutivo

- **Tarjetas (KPI):** Total Siniestros, Total con Heridos, Total con Muertos,
  `% Siniestros con Lesionados`.
- **Grafico de lineas:** Total Siniestros por `dim_tiempo[anio]`.
- **Barras:** Total Siniestros por `dim_localidad[nombre_localidad]` (Top N).

### Pagina 2 - Territorio y riesgo

- **Mapa (latitud/longitud):** dispersion de siniestros, tamano por conteo.
- **Tabla con formato condicional:** localidad, Total Siniestros,
  `Siniestros por 100.000 Hab`, ranking.
- **Barras:** Top localidades por tasa de riesgo (destacar el centro).

### Pagina 3 - Tiempo y severidad

- **Mapa de calor / matriz:** `dim_tiempo[dia_semana]` (filas) x
  `dim_tiempo[hora]` (columnas) con Total Siniestros.
- **Barras:** por `franja_horaria`.
- **Donut:** por `dim_gravedad[gravedad]`.
- **Barras:** por `dim_clase[clase_accidente]`.

### Pagina 4 - Puntos criticos

- **Tabla Top 20:** localidad, direccion, Total Siniestros, con muertos.
- **Segmentacion (slicer)** por localidad y anio.

## 4. Formato e interacciones

- Segmentaciones globales: `anio`, `nombre_localidad`, `gravedad`.
- Tema visual con un color principal (ej. azul `#1F4E79`) y rojo `#C0392B` para
  muertos.
- Tooltips con `% Siniestros con Lesionados`.
- Boton "Limpiar filtros" y narracion inteligente en la pagina 1.

## 5. Publicar

- Archivo > Publicar > area de trabajo.
- Para actualizacion automatica, programa la ejecucion del pipeline (Task
  Scheduler / cron) y la actualizacion del dataset en el servicio.
