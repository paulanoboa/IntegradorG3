# Estructura y flujo de trabajo

```text
data/
  raw/                 Fuentes originales por a?o (solo lectura)
  processed/           Datos limpios, auditor?a y agregados
  external/            Fuentes externas documentadas (clima, feriados, GeoJSON)
notebooks/             Cuadernos numerados de ingesta, an?lisis y modelado
models/                Estimadores entrenados y metadatos
apps/                  Aplicaci?n de monitoreo/mapa
docs/                  Metodolog?a, diccionario y decisiones
TEMP/                  Material temporal y consignas acad?micas
```

## Ejecuci?n

1. Instalar las dependencias del proyecto.
2. Ejecutar `notebooks/0_ingesta_limpieza.ipynb`.
3. Revisar `data/processed/auditoria_ingesta.csv` y `cobertura_mensual.csv`.
4. Validar el diccionario de relevancia con el equipo y ejecutar `notebooks/5_eda_features_split.ipynb`.
5. A?adir fuentes verificables de coordenadas, clima y feriados antes de activar funciones que dependan de ellas.

## Hallazgos sobre el esquema

En los archivos inspeccionados el esquema com?n es `Fecha;provincia;Canton;Cod_Parroquia;Parroquia;Servicio;Subtipo` (CSV separado por punto y coma; tambi?n existen XLSX). No hay campos de latitud, longitud ni hora. La serie solicitada cubre julio de 2022?agosto de 2026; el inventario de archivos muestra que 2023 tiene 11 meses (falta diciembre). La auditor?a debe confirmar y registrar otras brechas antes de calcular tendencias.

La actividad de diagn?stico de overfitting/underfitting se refleja en la separaci?n cronol?gica, el ajuste del preprocesador solo en train, la recomendaci?n de comparar baseline y modelo, y la necesidad de curvas de aprendizaje antes de aceptar el modelo. No se asume una m?trica de accuracy arbitraria para un problema de conteo.
