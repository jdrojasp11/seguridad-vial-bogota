# Tablero Power BI (formato PBIP)

Proyecto **Power BI** en formato **PBIP** (Power BI Project), la version basada en
texto de un `.pbix`. Se puede abrir directamente con **Power BI Desktop** y es
ideal para control de versiones en Git.

```
SeguridadVialBogota/
├── SeguridadVialBogota.pbip                 # abrir este archivo en Power BI Desktop
├── SeguridadVialBogota.SemanticModel/       # modelo (estrella) + medidas DAX
│   ├── definition.pbism
│   └── definition/
│       ├── database.tmdl
│       ├── model.tmdl
│       ├── expressions.tmdl                 # parametro RutaDatos
│       ├── relationships.tmdl
│       └── tables/*.tmdl
└── SeguridadVialBogota.Report/              # paginas y visuales del tablero
    ├── definition.pbir
    └── definition/
        ├── report.json
        └── pages/*/...
```

## Como abrirlo

1. Asegurate de haber ejecutado el pipeline (`python src/run_all.py`) para que
   existan los CSV en `data/processed/`.
2. En **Power BI Desktop**: `Archivo > Abrir` y selecciona
   `powerbi/SeguridadVialBogota/SeguridadVialBogota.pbip`.
3. Al cargar, Power BI leera los CSV usando el parametro **`RutaDatos`**.

## Cambiar la ubicacion de los datos

El modelo lee los CSV desde una ruta absoluta guardada en el parametro
**`RutaDatos`** (por defecto la carpeta del repositorio en la maquina donde se
genero). Si clonas el repo en otra ruta:

- En Power BI: `Transformar datos > Administrar parametros`, edita **`RutaDatos`**
  a la ruta de tu `data/processed`, luego `Actualizar`.

## Modelo

- `fact_siniestros` -> `dim_tiempo`, `dim_localidad`, `dim_gravedad`, `dim_clase`.
- `poblacion_localidad` -> `dim_localidad` (para tasas por habitante).

### Medidas DAX

| Medida | Descripcion |
|---|---|
| `TotalSiniestros` | Numero de siniestros |
| `SiniestrosConHeridos` | Siniestros con heridos |
| `SiniestrosConMuertos` | Siniestros con muertos |
| `SiniestrosSoloDanos` | Siniestros solo con danos |
| `PctLesionados` | % de siniestros con lesionados o muertos |
| `SiniestrosPor100k` | Siniestros por 100.000 habitantes |

## Paginas

- **Resumen ejecutivo:** tarjetas de KPIs, tendencia anual y top de localidades.
- **Riesgo y severidad:** tasa por 100.000 hab., gravedad, franja horaria y clase
  de accidente.
