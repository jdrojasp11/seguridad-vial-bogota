# Medidas DAX del modelo (Power BI)

Crear las medidas sobre la tabla `fact_siniestros` (o una tabla de medidas
dedicada). El modelo sigue un esquema en estrella.

## Medidas base

```DAX
Total Siniestros = COUNTROWS ( fact_siniestros )

Total Siniestros con Heridos =
CALCULATE ( [Total Siniestros], dim_gravedad[gravedad] = "CON HERIDOS" )

Total Siniestros con Muertos =
CALCULATE ( [Total Siniestros], dim_gravedad[gravedad] = "CON MUERTOS" )

Total Solo Danos =
CALCULATE ( [Total Siniestros], dim_gravedad[gravedad] = "SOLO DANOS" )
```

## Indicadores de severidad

```DAX
% Siniestros con Lesionados =
DIVIDE ( [Total Siniestros con Heridos] + [Total Siniestros con Muertos], [Total Siniestros] )

% Siniestros con Muertos =
DIVIDE ( [Total Siniestros con Muertos], [Total Siniestros] )
```

## Poblacion y tasa de riesgo

Requiere la tabla `poblacion_localidad` relacionada por `codigo_localidad`.

```DAX
Poblacion Promedio Localidad =
AVERAGEX (
    VALUES ( dim_tiempo[anio] ),
    CALCULATE ( AVERAGE ( poblacion_localidad[poblacion] ) )
)

Siniestros por 100.000 Hab =
DIVIDE ( [Total Siniestros] * 100000, [Poblacion Promedio Localidad] )
```

## Indicadores temporales

Marca `dim_tiempo` como tabla de fechas (columna `fecha`).

```DAX
Siniestros Anio Anterior =
CALCULATE ( [Total Siniestros], SAMEPERIODLASTYEAR ( dim_tiempo[fecha] ) )

Variacion Anual % =
DIVIDE ( [Total Siniestros] - [Siniestros Anio Anterior], [Siniestros Anio Anterior] )

Siniestros Acumulado Anual (YTD) =
TOTALYTD ( [Total Siniestros], dim_tiempo[fecha] )
```

## Ranking y priorizacion

```DAX
Ranking Localidad por Volumen =
RANKX ( ALL ( dim_localidad[nombre_localidad] ), [Total Siniestros], , DESC )

Ranking Localidad por Riesgo =
RANKX ( ALL ( dim_localidad[nombre_localidad] ), [Siniestros por 100.000 Hab], , DESC )

Indice de Prioridad =
RANKX ( ALL ( dim_localidad[nombre_localidad] ), [Total Siniestros], , DESC )
    + RANKX ( ALL ( dim_localidad[nombre_localidad] ), [Siniestros por 100.000 Hab], , DESC )
```

Las localidades con el **menor** `Indice de Prioridad` (mejor ranking en volumen
y en riesgo a la vez) deben atenderse primero.

## Etiqueta dinamica de severidad (opcional)

```DAX
Etiqueta Gravedad =
SWITCH (
    TRUE (),
    [% Siniestros con Muertos] >= 0.02, "Critica",
    [% Siniestros con Lesionados] >= 0.35, "Alta",
    "Media"
)
```
