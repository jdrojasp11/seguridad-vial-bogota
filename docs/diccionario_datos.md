# Diccionario de datos

Modelo en estrella construido por `src/etl.py` a partir de los datos abiertos de
Bogotá. Se materializa en SQLite (`data/warehouse.db`) y en CSV
(`data/processed/`).

## Diagrama del modelo

```
        dim_tiempo            dim_gravedad
             \                     /
              \                   /
  dim_localidad ---- fact_siniestros ---- dim_clase
             \        (199.146)
              \
        poblacion_localidad
```

## `fact_siniestros` — tabla de hechos

Un registro por **siniestro** (evento), no por víctima.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_siniestro` | entero | Identificador del siniestro (`OBJECTID`). Clave |
| `codigo_accidente` | entero | Código del accidente |
| `id_tiempo` | entero | Clave a `dim_tiempo` (AAAAMMDDHH) |
| `id_localidad` | entero | Clave a `dim_localidad` (0 = sin localidad) |
| `id_gravedad` | entero | Clave a `dim_gravedad` |
| `id_clase` | entero | Clave a `dim_clase` |
| `direccion` | texto | Dirección del siniestro |
| `latitud` | decimal | Coordenada de latitud |
| `longitud` | decimal | Coordenada de longitud |
| `civ` | entero | Código de la vía (CIV) |
| `pk_calzada` | decimal | Abscisa (PK) sobre la calzada |

## `dim_tiempo`

| Campo | Tipo | Descripción |
|---|---|---|
| `id_tiempo` | entero | Clave (año·10^6 + mes·10^4 + día·10^2 + hora) |
| `fecha` | fecha | Fecha del siniestro (AAAA-MM-DD) |
| `anio` | entero | Año |
| `mes` | entero | Mes (1–12) |
| `nombre_mes` | texto | Nombre del mes |
| `dia_semana` | texto | Día de la semana (Lunes–Domingo) |
| `hora` | entero | Hora (0–23) |
| `franja_horaria` | texto | Madrugada (0–5), Mañana (6–11), Tarde (12–17), Noche (18–23) |

## `dim_localidad`

| Campo | Tipo | Descripción |
|---|---|---|
| `codigo_localidad` | entero | Clave (0 = sin localidad, 1–20 localidades) |
| `nombre_localidad` | texto | Nombre de la localidad |

## `dim_gravedad`

| Campo | Tipo | Descripción |
|---|---|---|
| `id_gravedad` | entero | Clave |
| `gravedad` | texto | SOLO DAÑOS, CON HERIDOS, CON MUERTOS |

## `dim_clase`

| Campo | Tipo | Descripción |
|---|---|---|
| `id_clase` | entero | Clave |
| `clase_accidente` | texto | CHOQUE, ATROPELLO, CAÍDA DE OCUPANTE, VOLCAMIENTO, INCENDIO, OTRO, AUTOLESIÓN |

## `poblacion_localidad`

Población por localidad y año (para calcular tasas por habitante).

| Campo | Tipo | Descripción |
|---|---|---|
| `codigo_localidad` | entero | Clave a `dim_localidad` |
| `anio` | entero | Año |
| `poblacion` | entero | Población total (ambos sexos) |

## Relaciones

| Desde | Hacia | Cardinalidad |
|---|---|---|
| `fact_siniestros[id_tiempo]` | `dim_tiempo[id_tiempo]` | Muchos a uno |
| `fact_siniestros[id_localidad]` | `dim_localidad[codigo_localidad]` | Muchos a uno |
| `fact_siniestros[id_gravedad]` | `dim_gravedad[id_gravedad]` | Muchos a uno |
| `fact_siniestros[id_clase]` | `dim_clase[id_clase]` | Muchos a uno |
| `poblacion_localidad[codigo_localidad]` | `dim_localidad[codigo_localidad]` | Muchos a uno |
