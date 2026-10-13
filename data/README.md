# Datos del proyecto

- `raw/`: archivos de origen, organizados por anio. No modificar los originales.

Los archivos revisados contienen `Fecha`, provincia, canton, parroquia, servicio y subtipo. No contienen latitud/longitud ni hora; un mapa de puntos requiere una fuente geografica valida que complemente los registros. Un mes sin archivo no se considera autom?ticamente mes con cero incidentes.

Flujo recomendado: ejecutar `notebooks/0_ingesta_limpieza.ipynb` y despu?s `notebooks/5_eda_features_split.ipynb`. Los filtros de relevancia son reglas iniciales editables, no etiquetas oficiales.
