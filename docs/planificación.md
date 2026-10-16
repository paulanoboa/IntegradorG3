** Definición del problema y objetivos **
El proyecto aborda la falta de información geográfica y temporal, accesible para turistas y operadores turísticos, sobre incidentes en Ecuador. Propone usar datos históricos del ECU 911 para identificar zonas con mayor concentración de registros y anticipar meses de mayor incidencia, con el fin de apoyar decisiones preventivas.
Sus objetivos funcionales son:
- Analizar incidentes por territorio, servicio y periodo.
- Agrupar zonas por volumen de registros mediante K-Means.
- Predecir categorías de riesgo mensual por provincia, canton, parroquia mediante modelos como Random Forest y XGBoost.
- Presentar resultados en un panel web con gráficos y mapa.
El mapa muestra volumen relativo de registros, no tasas poblacionales ni ubicaciones exactas. 

*Justificación*
Los turistas pueden encontrar información dispersa o desactualizada para planificar rutas y actividades; las agencias y alojamientos también necesitan datos que les ayuden a comunicar precauciones. El proyecto busca facilitar decisiones informadas, contribuir a la prevención y apoyar la confianza en los destinos ecuatorianos. La documentación presenta estos beneficios como objetivos del sistema, no como impactos ya medidos.

*Alcance*
Incluye: análisis de datos históricos del ECU 911, exploración y preparación de datos, análisis geográfico y temporal, agrupamiento de zonas, modelado de riesgo mensual y visualización local mediante panel web, gráficos y mapa.
No incluye o no permite afirmar: ubicación exacta de cada incidente, tasas de riesgo ajustadas por población, garantía de que una zona sea segura o peligrosa. La fuente no contiene latitud, longitud u hora; registra eventos de varios servicios y puede tener brechas de cobertura.

*Cronograma*
Las fechas estimadas del 22 de septiembre al 28 de octubre de 2026, y describe fases para planificación, exploración, modelado, despliegue y monitoreo. También contiene seguimientos semanales con porcentajes y fechas estimadas, pero hay inconsistencias: se considera un desarrollo del proyecto de seis semanas.

*Recursos necesarios*
- Datos: registros históricos del ECU 911, organizados por año; la estructura documentada contempla fecha, provincia, cantón, parroquia, servicio y subtipo. Hay que auditar cobertura y calidad, existen años qque no se considero los 12 meses dado que existe un faltante de estos datos en la data abierta del Gobierno de Ecuador. Para el mapa se usan centroides aproximados; no hay coordenadas en los archivos inspeccionados.
- Software: Python 3.12, dependencias del proyecto, Jupyter para ejecutar notebooks, Git y navegador. El panel se ejecuta localmente con python src/app.py; el mapa base usa Leaflet y mosaicos de OpenStreetMap, por lo que requiere internet.
- Hardware e infraestructura: como referencia un mínimo de 16 GB de memoria, Java JDK 17. No se detalla un servidor productivo confirmado; la plantilla de cronograma contempla infraestructura en la nube como alternativa ante problemas locales.

*Riesgos identificados y mitigación*
- Calidad o cobertura insuficiente de los datos: auditar brechas, revisar meses faltantes y cambios de codificación.
- Desempeño predictivo: comparación con un baseline, revisar variables y algoritmos, y validar temporalmente antes de aceptar el modelo. 
- Se refleja volumen relativo de registros y usa ubicaciones aproximadas, no riesgo poblacional ni coordenadas exactas, no riesgo de protección de datos dado que son abiertos.
- Infraestructura: alternativa en la nube y ejecución local en el alcance.
- Posible falta de recursos: Gestionar el alcance y prever recursos alternativos.
Estos riesgos y mitigaciones provienen de un análisis generado hasta el momento del proyecto integrador 