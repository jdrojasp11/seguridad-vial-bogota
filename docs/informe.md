# Informe de hallazgos: siniestralidad vial en Bogota (2015-2021)

Documento de negocio que resume el analisis de **199.146 siniestros viales**
registrados por la Secretaria Distrital de Movilidad y la poblacion por localidad
de la Secretaria Distrital de Salud.

## 1. Contexto

La seguridad vial es una prioridad de salud publica y de movilidad. Con un
presupuesto de prevencion limitado, la pregunta clave no es solo *cuantos*
siniestros ocurren, sino *donde*, *cuando* y *que tan graves* son, para asignar
recursos de forma eficiente.

## 2. Indicadores globales

| Indicador | Valor |
|---|---|
| Siniestros totales | 199.146 |
| Solo danos | 128.207 (64,4%) |
| Con heridos | 67.700 (34,0%) |
| Con muertos | 3.239 (1,6%) |
| Promedio anual | 28.449 |
| Anio pico | 2018 (33.418) |

## 3. Hallazgos

### 3.1 Tendencia

- Crecimiento sostenido entre 2015 y 2018 (pico de 33.418).
- Descenso marcado en 2020 (22.424) y 2021 (18.114), consistente con la
  reduccion de movilidad por la pandemia. Se debe contrastar con la
  recuperacion post-pandemia antes de declarar una mejora estructural.

### 3.2 Territorio: volumen vs. riesgo

- **Volumen:** Kennedy, Engativa, Usaquen y Suba (las mas pobladas y con mas
  vias arteriales).
- **Riesgo relativo (por 100.000 hab.):** Los Martires, Barrios Unidos,
  Chapinero y Teusaquillo, con valores entre 4 y 9 veces la tasa de las
  localidades perifericas.
- Implicacion: una estrategia basada solo en volumen subestima el riesgo en el
  centro de la ciudad; se recomienda **priorizacion mixta**.

### 3.3 Tiempo

- Mayor concentracion en la **tarde** y la **manana** (hora pico de movilidad).
- **Viernes** es el dia mas critico; **domingo**, el menos.
- El mapa de calor (dia vs. hora) permite programar operativos en las ventanas
  de mayor incidencia.

### 3.4 Severidad

- **SAN CRISTOBAL (53,2%)**, **RAFAEL URIBE URIBE (52,2%)** y **USME (49,9%)**
  presentan la mayor proporcion de siniestros con lesionados, lo que sugiere
  mayor presencia de usuarios vulnerables (motociclistas/peatones).
- En el norte (Usaquen 22,2%, Chapinero 23,9%) predominan los "solo danos".

### 3.5 Puntos criticos

| Localidad | Direccion | Siniestros |
|---|---|---|
| Kennedy | KR 80 - CL 2 | 213 |
| Engativa | AV Boyaca - CL 80 | 150 |
| Fontibon | CL 13 - KR 72 | 148 |
| Engativa | CL 80 - KR 72 | 135 |
| Puente Aranda | KR 50 - CL 3 | 132 |

## 4. Recomendaciones

1. Intervenir con **doble criterio** (volumen + tasa por habitante).
2. Campanas y operativos en **hora pico** (tarde/manana) y **viernes**.
3. Enfoque de **usuario vulnerable** en el sur (motociclistas y peatones).
4. Tratamiento de **puntos negros** en corredores arteriales (Av. Boyaca,
   Av. Americas, Av. Caracas).
5. **Automatizar** el pipeline para incorporar datos nuevos y monitorear
   resultados de las intervenciones.

## 5. Notas metodologicas

- Un registro = un siniestro (evento), no una victima.
- "Con heridos"/"Con muertos" son categorias de gravedad del evento.
- La tasa por 100.000 hab. usa el promedio de poblacion por localidad 2015-2021.
- 46 registros (0,02%) sin localidad valida se asignan a "sin localidad".
- Fuente de los datos: portal de Datos Abiertos de Bogota (CC-BY-4.0).
