# ProyectoIntegradorG3

**1. Encabezado y badges: **

Este repositorio contendra el proyecto integrador de la maestria de IA:
Se levanta la información de definición y planificación del proyecto Integrador:

**Título del proyecto:** Generación de los puntos más peligrosos de Ecuador para detectar zonas de riesgo 
para alertar a los turistas para que tomen precauciones usando modelos que puedan predecir los meses de 
mayores incidentes. 

**Integrantes:**  
* Harold Rodrigo Angulo Arellano
* Paula Elizabeth Noboa Ramírez 

**Fecha:** Octubre2026 

**Python versión:** 3.12.10

**License: **
MIT License
Copyright (c) 2026 Harol Angulo, Paula Noboa

**Descripción breve del proyecto:** 
Sistema de IA que utiliza K-Means para detectar zonas de riesgo en Ecuador y XGBoost/Random Forest para predecir los meses críticos de mayor incidencia, generando alertas preventivas para turistas y agencias de viajes. La solución integra análisis geoespacial y predicción temporal para apoyar la toma de decisiones seguras en turismo.

**Documentación definciión y planificación:**
#Datasets
Analisis_de_Datasets_Disponibles_Template_Grupo3.docx
#Stakeholders
Analisis_de_Stakeholders_Template_Grupo3.docx
#Mapa inicial del contexto del proyecto papers investigación
Mapa_del_Estado_del_Arte_Template_Grupo3.docx
#KPIS que se mediran en el proyecto análisis de KPIs
Matriz de KPIs Comunes en Proyectos de IA.docx
#Timeline del proyecto contemplada para el proyecto
Timeline Template para Proyectos de IA_Grupo3.docx
#Análisis SMART del proyecto integrador
Canvas SMART para Proyectos de IA_grupo3.docx
#Checklist del SMART realizado sobre nuestro tema
Checklist de Validación de Objetivos SMART para IA_grupo3.docx

**2. Tabla de contenidos:**

1.	Mapa del Estado del Arte — Proyecto Integrador de IA	
1.1.	Registro de Fuentes Revisadas	
2.	Análisis de Datasets Disponibles — Proyecto Integrador de IA	
2.1.	Tabla Comparativa Resumen	
2.2.	Recomendación:	
2.3.	Plan B	
2.4.	Plan de Adquisición / Preprocesamiento
3.	Matriz de KPIs Comunes en Proyectos de IA
4.	Análisis de Stakeholders — Proyecto Integrador de IA	
4.1.	Identificación de Stakeholders	
4.2.	Matriz de Influencia / Interés	
4.3.	Plan de Comunicación Diferenciado	
5.	Canvas SMART para Proyectos de IA	
5.1.	S - ESPECÍFICO (Specific)	
5.2.	M - MEDIBLE (Measurable)	
5.3.	A - ALCANZABLE (Achievable)	
5.4.	R - RELEVANTE (Relevant)	
5.5.	T - TEMPORAL (Time-bound)	
5.6.	Validación Final	
6.	Checklist de Validación de Objetivos SMART para IA	
6.1.	PUNTUACIÓN TOTAL	
6.2.	INTERPRETACIÓN DE RESULTADOS	
6.3.	RECOMENDACIONES DE MEJORA	
6.4.	Acciones Prioritarias:	
6.5.	PRÓXIMOS PASOS	
7.	Anexos	

** 3. Descripción del problema:** 
**¿Qué problema resuelve el proyecto?**
El proyecto resuelve la falta de información geográfica, temporal y accesible sobre zonas de riesgo en Ecuador que dificulta que los turistas tomen decisiones preventivas informadas.
Algunos de los problemas que resuelve:
* Los turistas nacionales e internacionales no cuentan con herramientas centralizadas que les permitan identificar sectores o zonas con mayor concentración de incidentes delictivos.
* No existe información clara y actualizada sobre los meses o periodos en los que aumenta la incidencia de delitos en diferentes sectores del país.
* Las agencias de viajes y operadores turísticos recurren a información dispersa, desactualizada o poco confiable para planificar rutas seguras.
* Esta brecha genera exposición innecesaria a riesgos, limita la prevención y afecta la percepción de seguridad de los visitantes hacia los destinos ecuatorianos.

**¿Por qué es importante?** 
* Seguridad del turista:
El turismo es una industria vital en Ecuador, pero la percepción de inseguridad puede desalentar viajes, reducir ingresos y dañar la reputación del destino. Información clara y preventiva empodera a los visitantes para tomar decisiones seguras sin generar alarma innecesaria.
* Fortalecimiento de la confianza:
Un sistema transparente que comunique riesgos de forma responsable mejora la confianza de turistas nacionales e internacionales en los destinos ecuatorianos.

* Optimización de la experiencia:
Turistas mejor informados pueden planificar rutas alternativas, evitar periodos de mayor riesgo o tomar precauciones adicionales, mejorando su experiencia general y seguridad.

**¿Quiénes son los usuarios objetivo?**
* Turistas Nacionales e Internacionales
Necesidad: Información clara, accesible y oportuna sobre zonas de riesgo y periodos críticos antes de viajar o durante su estancia.
Beneficio: Tomar decisiones informadas sobre rutas, actividades y desplazamientos; minimizar riesgos evitables; mejorar la confianza en destinos ecuatorianos.
* Agencias de Viajes y Operadores Turísticos
Necesidad: Datos predictivos para diseñar itinerarios seguros, comunicar riesgos a clientes y diferenciar sus servicios.
Beneficio: Reducir incidentes, mejorar reputación, aumentar confianza del cliente, acceso a información actualizada sobre zonas y meses críticos.
* Hoteles, Hostales y Redes de Alojamiento
Necesidad: Información sobre riesgos en sectores cercanos a sus instalaciones para mejorar seguridad de huéspedes.
Beneficio: Brindar recomendaciones preventivas personalizadas, implementar planes de contingencia, fortalecer la percepción de seguridad.

** 4. Dataset:** 
** Descripción de los datos utilizados** 
En la carpeta Data/raw se encuentra administrados los datos históricos del 911 de Ecuador desde el 2021
Los historiales se encuentran organizados por año desde 2021 hasta 2026
Teniendo la siguiente información mensual respecto a cada año
2021 : 6 meses
2022 : 12 meses
2023 : 12 meses
2024 : 12 meses
2025 : 12 meses
2026 : 8 meses

**Fuente y licencia de los datos **
Adjuntamos página web de las fuentes de datos:https://www.datosabiertos.gob.ec/
Datos abiertos del gobierno de Ecuador

**Características principales (tamaño, variables, etc.) **
**Tamaño:** El total es 17.380.602 registros en los 61 archivos revisados.
**Variables:** Fecha,provincia,Canton,Parroquia,Servicio,Subtipo,anio_archivo
**Link a los datos si son públicos**
URL de datos abiertos: ttps://www.datosabiertos.gob.ec/dataset/base-de-emergencias 

**5. Metodología:** 
**Tipo de modelo utilizado y justificación **
Reducción de dimensionalidad y clasificación eficiente:
K-Means simplifica miles de registros de incidentes en un número manejable de clusters de riesgo, permitiendo identificar patrones que serían imposibles detectar manualmente.

Predicción de riesgos con alta precisión:
XGBoost y Random Forest aprovechan múltiples variables (ubicación, mes, tipo de incidente, tendencias históricas) para generar predicciones con accuracy superior al 80%, permitiendo alertas confiables.
