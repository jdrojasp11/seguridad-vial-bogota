-- =====================================================================
-- Consultas analiticas del caso: Seguridad vial en Bogota (2015-2021)
-- Se ejecutan desde src/analytics.py. El separador "-- name:" identifica
-- cada consulta.
-- =====================================================================

-- name: tendencia_anual
SELECT t.anio,
       COUNT(*) AS siniestros,
       SUM(CASE WHEN g.gravedad = 'CON MUERTOS' THEN 1 ELSE 0 END) AS con_muertos,
       SUM(CASE WHEN g.gravedad = 'CON HERIDOS' THEN 1 ELSE 0 END) AS con_heridos,
       SUM(CASE WHEN g.gravedad = 'SOLO DANOS' THEN 1 ELSE 0 END) AS solo_danos
FROM fact_siniestros f
JOIN dim_tiempo t ON t.id_tiempo = f.id_tiempo
JOIN dim_gravedad g ON g.id_gravedad = f.id_gravedad
GROUP BY t.anio
ORDER BY t.anio;

-- name: resumen_gravedad
SELECT g.gravedad, COUNT(*) AS siniestros
FROM fact_siniestros f
JOIN dim_gravedad g ON g.id_gravedad = f.id_gravedad
GROUP BY g.gravedad
ORDER BY siniestros DESC;

-- name: top_localidades
SELECT l.nombre_localidad,
       COUNT(*) AS siniestros,
       SUM(CASE WHEN g.gravedad = 'CON MUERTOS' THEN 1 ELSE 0 END) AS con_muertos,
       SUM(CASE WHEN g.gravedad = 'CON HERIDOS' THEN 1 ELSE 0 END) AS con_heridos
FROM fact_siniestros f
JOIN dim_localidad l ON l.codigo_localidad = f.id_localidad
JOIN dim_gravedad g ON g.id_gravedad = f.id_gravedad
GROUP BY l.nombre_localidad
ORDER BY siniestros DESC;

-- name: tasa_100k
SELECT l.nombre_localidad,
       COUNT(*) AS siniestros,
       CAST((SELECT AVG(p.poblacion) FROM poblacion_localidad p
             WHERE p.codigo_localidad = l.codigo_localidad
               AND p.anio BETWEEN 2015 AND 2021) AS INTEGER) AS poblacion_promedio,
       ROUND(COUNT(*) * 100000.0 /
             (SELECT AVG(p.poblacion) FROM poblacion_localidad p
              WHERE p.codigo_localidad = l.codigo_localidad
                AND p.anio BETWEEN 2015 AND 2021), 1) AS siniestros_x100k
FROM fact_siniestros f
JOIN dim_localidad l ON l.codigo_localidad = f.id_localidad
WHERE l.codigo_localidad > 0
GROUP BY l.nombre_localidad
ORDER BY siniestros_x100k DESC;

-- name: franja_horaria
SELECT t.franja_horaria, COUNT(*) AS siniestros
FROM fact_siniestros f
JOIN dim_tiempo t ON t.id_tiempo = f.id_tiempo
GROUP BY t.franja_horaria
ORDER BY siniestros DESC;

-- name: dia_semana
SELECT t.dia_semana,
       CASE t.dia_semana
            WHEN 'Lunes' THEN 1 WHEN 'Martes' THEN 2 WHEN 'Miercoles' THEN 3
            WHEN 'Jueves' THEN 4 WHEN 'Viernes' THEN 5 WHEN 'Sabado' THEN 6
            WHEN 'Domingo' THEN 7 ELSE 8 END AS orden,
       COUNT(*) AS siniestros
FROM fact_siniestros f
JOIN dim_tiempo t ON t.id_tiempo = f.id_tiempo
GROUP BY t.dia_semana
ORDER BY orden;

-- name: clase_accidente
SELECT c.clase_accidente, COUNT(*) AS siniestros
FROM fact_siniestros f
JOIN dim_clase c ON c.id_clase = f.id_clase
GROUP BY c.clase_accidente
ORDER BY siniestros DESC;

-- name: hora_dia
SELECT t.dia_semana, t.hora, COUNT(*) AS siniestros
FROM fact_siniestros f
JOIN dim_tiempo t ON t.id_tiempo = f.id_tiempo
GROUP BY t.dia_semana, t.hora;

-- name: puntos_criticos
SELECT l.nombre_localidad,
       f.direccion,
       COUNT(*) AS siniestros,
       SUM(CASE WHEN g.gravedad = 'CON MUERTOS' THEN 1 ELSE 0 END) AS con_muertos
FROM fact_siniestros f
JOIN dim_localidad l ON l.codigo_localidad = f.id_localidad
JOIN dim_gravedad g ON g.id_gravedad = f.id_gravedad
WHERE f.direccion IS NOT NULL AND f.direccion <> ''
GROUP BY l.nombre_localidad, f.direccion
ORDER BY siniestros DESC
LIMIT 20;

-- name: severidad_localidad
SELECT l.nombre_localidad,
       COUNT(*) AS siniestros,
       ROUND(100.0 * SUM(CASE WHEN g.gravedad <> 'SOLO DANOS' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_con_lesionados
FROM fact_siniestros f
JOIN dim_localidad l ON l.codigo_localidad = f.id_localidad
JOIN dim_gravedad g ON g.id_gravedad = f.id_gravedad
WHERE l.codigo_localidad > 0
GROUP BY l.nombre_localidad
HAVING COUNT(*) >= 200
ORDER BY pct_con_lesionados DESC;
