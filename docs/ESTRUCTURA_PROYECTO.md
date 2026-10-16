# Estructura y flujo de trabajo

```text
data/
  raw/                 Fuentes originales por anio (solo lectura)
  processed/           Datos limpios, auditoria y agregados
  external/            Fuentes externas documentadas (clima, feriados, GeoJSON)
notebooks/             Cuadernos numerados de ingesta, analisis y modelado
models/                Estimadores entrenados y metadatos
apps/                  Aplicacion de monitoreo/mapa
docs/                  Metodologia,diccionario y decisiones,docs
TEMP/                  Material temporal y consignas academicas
```

## Ejecucion



## Hallazgos sobre el esquema

En los archivos inspeccionados el esquema es `Fecha;provincia;Canton;Cod_Parroquia;Parroquia;Servicio;Subtipo` (CSV separado por punto y coma; también existen XLSX). No hay campos de latitud, longitud ni hora. La serie solicitada cubre julio de 2022 agosto de 2026; el inventario de archivos muestra que 2023 tiene 11 meses (falta diciembre). La auditoria debe confirmar y registrar otras brechas antes de calcular tendencias.

La actividad de diagnostico de overfitting/underfitting se refleja en la separacion cronologica, el ajuste del preprocesador solo en train, la recomendacion de comparar baseline y modelo, y la necesidad de curvas de aprendizaje antes de aceptar el modelo. No se asume una metrica de accuracy arbitraria para un problema de conteo.
