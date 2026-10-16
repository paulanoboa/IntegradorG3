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
docs\Semana1_ProyectoIntegrador_G3\PROYECTO INTEGRADOR - PRESENTACIÓN DEL PROYECTO 092026_G3.docx

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

**Algunos de los problemas que resuelve:**
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
En la siguiente ruta se encuentra consolidado un solo archivo(para la ejecución del proyecto se recomienda descomprimir el archivo para el usod e data) : data\raw\data_proyecto.7z

**Fuente y licencia de los datos **
Adjuntamos página web de las fuentes de datos:https://www.datosabiertos.gob.ec/
Datos abiertos del gobierno de Ecuador

**Características principales (tamaño, variables, etc.) **
**Tamaño:** El total es 17.380.602 registros en los 61 archivos revisados.
**Variables:** Fecha,provincia,Canton,Parroquia,Servicio,Subtipo,anio_archivo
**Link a los datos si son públicos**
URL de datos abiertos: ttps://www.datosabiertos.gob.ec/dataset/base-de-emergencias 

**5. Metodología:** 
**Metodología CRISP-DM para proyectos IA**
1. Comprensión del negocio
2. Comprensión de datos
3. Preparación de datos
4. Modelado
5. Evaluación
6. Despliegue

**Tecnicas de optimización empleadas -Tipos de modelo utilizado y justificación (ML)**
Reducción de dimensionalidad y clasificación eficiente:
K-Means simplifica miles de registros de incidentes en un número manejable de clusters de riesgo, permitiendo identificar patrones que serían imposibles detectar manualmente.

Predicción de riesgo:
Random Forest y XGBoost aprovechan historial mensual por provincia y estacionalidad para clasificar meses de mayor volumen. Las métricas reales se calculan con una partición temporal; no se presupone un nivel de accuracy antes de ejecutar la evaluación.

## Ejecución del pipeline y panel web

Requiere Python 3.12 y las dependencias de `requirements.txt`. 

Para la ejecución del pipeline ingresar se debe ejecutar en orden númerico los ipynb correspondientes del siguiente path:
notebooks
Aqui encontrará el pipeline de procesamiento de datos con los siguientes pasos:
1. Recolección y carga
2. Exploración EDA
3. Limpieza
4. Transformación
5. División
6. Normalización/Escalamiento
Se a generado tabién:
1. El entrenamiento de los modelos
2. Testeo reentrenamiento y ajuste
3. análisis de variables 
4. Análisis de Overfiting y underfiting
5. Implementación de ética en la IA

Se ha verificado
Para abrir el sitio local, ejecute `python src/app.py` y visite `http://127.0.0.1:5000`. El panel tiene las secciones Consultar, Ver gráficos y Ver mapa. El mapa usa Leaflet y mosaicos de OpenStreetMap; necesita acceso a internet para cargar el mapa base.

**6. Resultados:**
Los resultados se cargaran en la pagina web para acceso y transparencia de los usuarios
Ver opción Resultados. Encontrará lo siguiente:
• Resultado de datos
• Métricas finales del modelo (accuracy, F1, RMSE, etc.)
• Comparación con baseline
• Recopilación de Gráficos

**7. Instalación y uso:**
• Requisitos del sistema:
* Se requiere acceso a internet
* Memoria mínima de 16GB
* python 3.12
* instalación java jdk 17
* Navegador
* Librerias mínimas
* Instalar github
• Instrucciones paso a paso para instalar local y comandos: 
1. Ir a la siguiente url donde se encuentra el repositorio del proyecto en github: https://github.com/paulanoboa/IntegradorG3
2. Abrir el git del computador y clonar el repositorio: git clone https://github.com/paulanoboa/IntegradorG3
3. Ejecutar proyecto.app python src/app.py`
4. Abrir la URL http://127.0.0.1:5000/
5. Navegar en el proyecto

**8. Interfaz de usuario:**
*Descripción de la interfaz: la interfaz consta de una UI Web donde en su página principal se visualizara un resumen de los datos más relevantes y tendrá 2 botones: Resultados y Mapa.
*Instrucciones para usar la interfaz
- Los resultados: se visualizaran los datos resultados del entrenamiento y se visualizará las métricas de los modelos usados asi como las gráficas generadas
- Mapa: Se visualizará el mapa de calor donde se indicaran gráficamente los sectores de mayor, mediano y bajo riesgo
*Link a la aplicación desplegada: http://127.0.0.1:5000/

**9.Estructura del proyecto:**
• Descripción breve de cada carpeta principal:

**10. Consideraciones éticas:**
• Resumen de aspectos éticos considerados
•Interpretación y limitaciones

Los CSV de origen no incluyen coordenadas geográficas ni población expuesta. Por ello, el mapa y K-Means trabajan a nivel provincial, cantonal, parroquial con centroides aproximados; el color expresa volumen relativo de registros, no una tasa poblacional, ubicación exacta de incidentes ni una garantía de seguridad. Los reportes cubren eventos de múltiples servicios (seguridad, tránsito, salud y otros) y las cifras dependen de la cobertura del registro. El pronóstico es una categoría de riesgo por provincia/mes, no una predicción del número de incidentes. Evalúe cobertura, cambios de codificación y meses faltantes antes de utilizar los resultados para decisiones operativas.
• Advertencias sobre uso inadecuado

**11. Autores y contribuciones:**
• Nombres de los integrantes del equipo y rol de cada uno:
- Ing. Harold Rodrigo Angulo Arellano (MLEngineer,Developer , Security engineer)
- Ing. Paula Elizabeth Noboa Ramírez (Data engineer, QA, PO)

** 12. Licencia**
Ver LICENSE.txt (MIT LICENSE)

**13. Agradecimientos y referencias**

* Agradecimientos:
Queremos expresar nuestro más sincero agradecimiento a nuestros seres queridos, en especial a nuestros amados hijos David y Adrián, quienes han sido el motor que nos ha impulsado a continuar y culminar este proyecto de graduación. Ellos han sido testigos de nuestro esfuerzos diario y esperamos que este logro les sirva de ejemplo, recordándoles que todo sacrificio y dedicación siempre da frutos.

A nuestros queridos padres Yolanda, Humberto, Teresa, Julio, por su apoyo incondicional y constante motivación, que nos permitió mantenernos firmes en este camino. A la UEES, institución que, a través de sus docentes, hizo posible el desarrollo de este proyecto, brindándonos conocimientos y retroalimentación que hemos podido aplicar en la práctica. Finalmente, a nuestros compañeros, por sus valiosos aportes, que enriquecieron nuestro aprendizaje, todo lo mencionado a  contribuido a dar forma a esta propuesta que la hemos realizado con esfuerzo y cariño.

* Referencias:

• Floridi, L. (2019). Ethics of Artificial Intelligence. Oxford University Press.

• Ministerio de Telecomunicaciones y de la Sociedad de la Información. (2025). Reforma al acuerdo App Gob.ec (MINTEL-MINTEL-2025-0004). Gobierno del Ecuador. https://www.gob.ec/sites/default/files/2025-05/MINTEL-MINTEL-2025-0004_Reforma%20al%20acuerdo%20App%20Gob.ec_.pdf

• Gobierno del Ecuador. (s.f.). Base de emergencias. Datos Abiertos Ecuador. https://www.datosabiertos.gob.ec/dataset/base-de-emergencias
