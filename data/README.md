# Datos del proyecto

- `raw/`: archivos de origen, organizados por a?o. No modificar los originales.
- `processed/`: productos reproducibles del pipeline (`auditoria_ingesta.csv`, cobertura, datos integrados y tablas mensuales).
- `external/` (opcional): calendarios oficiales, clima y l?mites administrativos/GeoJSON; documentar URL, licencia y fecha de descarga.

Los archivos revisados contienen `Fecha`, provincia, cant?n, parroquia, servicio y subtipo. No contienen latitud/longitud ni hora; un mapa de puntos requiere una fuente geogr?fica v?lida que complemente los registros. Un mes sin archivo no se considera autom?ticamente mes con cero incidentes.

Flujo recomendado: ejecutar `notebooks/0_ingesta_limpieza.ipynb` y despu?s `notebooks/5_eda_features_split.ipynb`. Los filtros de relevancia son reglas iniciales editables, no etiquetas oficiales.
