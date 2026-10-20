# Consideraciones éticas del modelo de alertas turísticas

## Alcance y contexto

El proyecto analiza registros históricos de llamadas y despachos del ECU 911 de 2021 a 2026 para construir un panel mensual por cantón y predecir si un cantón superará su umbral histórico de delitos críticos (`Mes_Alto_Riesgo`). El notebook `models/generacion_dataset_model_pry_v1.1.ipynb` reporta 17.680.253 incidentes originales y un dataset agregado de 13.722 observaciones, sin valores nulos en la exportación. La predicción representa un indicador histórico agregado; no mide la probabilidad individual.

Las cifras de fairness son 4.440 observaciones de prueba de 2025–2026. Se realizó una auditoría exploratoria, no como una certificación de equidad ni como garantía de desempeño futuro.

## 1. Análisis de sesgos

## ¿El dataset tiene sesgos demográficos, culturales o de otro tipo?

Sí,Los datos provienen de llamadas y despachos al sistema de emergencias 911. La probabilidad de que un evento se registre puede variar según el acceso al servicio, la confianza institucional, la conectividad, la disposición a denunciar, la presencia de visitantes y las prácticas locales de clasificación. El volumen también depende del tamaño poblacional y del uso del ECU 911. El notebook señala que Guayas y Pichincha concentran aproximadamente el 49% del volumen de llamadas al 911.

La agregación territorial, el uso de macrorregiones y la clasificación de subtipos pueden ocultar diferencias entre cantones y dentro de cada cantón. Los datos no contienen atributos individuales de etnia, género, edad, discapacidad, idioma o condición socioeconómica; por tanto, no permiten medir directamente esos sesgos.

## ¿Cómo podrían afectar estos sesgos las predicciones?

Las zonas con mayor reporte pueden aparecer con más incidentes aunque la diferencia refleje, en parte, población, afluencia o propensión a reportar. En áreas con menor cobertura, el modelo puede subestimar el riesgo observado. La falta de datos de visitantes, población expuesta, estacionalidad local y subregistro limita la interpretación de los conteos y de las tasas. La clasificación basada en subtipos textuales también puede omitir o incluir eventos de forma inconsistente.

## ¿Qué grupos podrían ser perjudicados?

Podrían verse perjudicados residentes, visitantes y pequeños operadores turísticos de cantones con registros escasos o variables, así como comunidades rurales, indígenas o con menor acceso a servicios si sus incidentes se registran de manera distinta. Una alerta excesiva puede estigmatizar localidades y reducir visitas e ingresos; una alerta insuficiente puede dejar a visitantes y residentes con menos información preventiva. Estos efectos son riesgos plausibles.

## 2. Equidad y fairness

## ¿El modelo trata a todos los grupos de forma equitativa?

Los resultados no respaldan una conclusión de equidad uniforme. La auditoría se realizó por macrorregión, usando Metropolitana (Pichincha y Guayas) como referencia. Las tasas de selección y los errores difieren entre regiones. En particular, `Otras_Regiones` presenta DIR 0,330 y TPR 0,500, mientras `Sierra_Sur` presenta DIR 2,284 y FPR 0,156. Estos valores muestran diferencias.

Se marca como “equitativas” algunas regiones cuando el DIR está entre 0,80 y 1,25 y el TPR es al menos 0,70. Sin embargo, esas dos condiciones no prueban equidad general: los valores de precisión, FPR y FNR también varían, y los grupos tienen tamaños muy distintos (por ejemplo, 60 casos de prueba en Galápagos y 40 en Otras_Regiones). No se reportan intervalos de confianza ni pruebas de significancia, por lo que las estimaciones de grupos pequeños son inestables.

## Métricas de fairness evaluadas

Por región: muestras, tasa base real, tasa de selección positiva, Dispar Impact Ratio (DIR), TPR/recall, PPV/precision, FPR, FNR, exactitud, F1, Brier score y ROC-AUC. También registra una métrica de integridad como porcentaje de valores presentes en `Delitos_Lag_1`; en el conjunto exportado no había nulos, por lo que esta medida no informa sobre sesgos de cobertura del dato fuente.

Resultados ilustrativos reportados:

| Región | Muestras de prueba | DIR | TPR | PPV | FPR | FNR |
|---|---:|---:|---:|---:|---:|---:|
| Amazonía | 840 | 1,391 | 0,395 | 0,701 | 0,101 | 0,605 |
| Costa Turística | 500 | 1,465 | 0,891 | 0,514 | 0,124 | 0,109 |
| Insular Galápagos | 60 | 1,870 | 0,737 | 0,824 | 0,073 | 0,263 |
| Metropolitana (referencia) | 660 | 1,000 | 0,787 | 0,590 | 0,070 | 0,213 |
| Otras Regiones | 40 | 0,330 | 0,500 | 0,500 | 0,026 | 0,500 |
| Sierra Sur | 760 | 2,284 | 0,855 | 0,673 | 0,156 | 0,145 |

El desempeño agregado de validación cruzada temporal reportado es ROC-AUC 0,8680 (desviación 0,0305) y F1 0,6573 (desviación 0,0467). La auditoría por subgrupo no sustituye el análisis de errores para comunidades y cantones concretos.

## Estrategias implementadas para mitigar inequidades 

El procesamiento agrega a nivel cantonal-mensual, crea `Proporcion_Delitos`, calcula un umbral local por cantón y agrega `Peso_Muestra_Fairness`, limitado al intervalo [0,5; 2,5] e inversamente relacionado con el DIR regional. Se exporta además el dictamen y métricas regionales para facilitar una auditoría posterior.

Estas son medidas de preparación y reponderación. La fase de evaluación ajusta `HistGradientBoostingClassifier` sin pasar `Peso_Muestra_Fairness` al método `fit`. Conviene validar definiciones de grupos, cobertura territorial y umbrales con actores locales.

## 3. Privacidad

## ¿Se utilizan datos personales o sensibles?

Como fuente se tiene registros de llamadas y despachos del ECU 911 se tiene fecha, provincia, cantón, servicio y subtipo. El archivo analítico final trabaja con agregados territoriales y temporales, y no muestra nombres, teléfonos, identificadores personales ni coordenadas individuales.

## ¿Cómo se protege la privacidad de los usuarios?

La agregación mensual por cantón reduce el detalle individual en la salida analítica se elimina campos residuales de exportación. No se documentan controles de acceso, cifrado, retención, eliminación segura, anonimización formal, la anonimización se recomienda cuando existen datos sensibles y personales en este caso no aplica anonimización, ni evaluación de riesgo de reidentificación. La data generada es de acceso abierto y público del gobierno de Ecuador

## Cumplimiento con regulaciones (GDPR, CCPA, etc.)

No incluye una evaluación jurídica ni evidencia de cumplimiento de GDPR, CCPA u otra regulación. Al tratarse de datos del Ecuador, el responsable debe determinar la aplicabilidad de la normativa ecuatoriana de protección de datos personales y las obligaciones contractuales e institucionales de la fuente, con asesoría competente. No debe declararse cumplimiento hasta documentar base legal, finalidad, minimización, conservación, medidas de seguridad, derechos de titulares y transferencias aplicables. En Ecuador se a generado la "Estrategia para el fomento del desarrollo y uso ético y responsable de la 
Inteligencia Artificial en el Ecuador " acuerdo 2025-0030 publicado por el MINTEL  [MINTEL2025-0030](/docs/Anexos/MINTEL-2025-0030.pdf)

## 4. Transparencia y explicabilidad

## ¿El modelo es interpretable?
 ¿Los usuarios entienden cómo funciona?

El clasificador del experimento es `HistGradientBoostingClassifier`, un ensamble de árboles que no ofrece una explicación directa y sencilla de cada predicción. Se describe el objetivo, variables, umbrales y partición temporal, lo que favorece la transparencia metodológica. Los turistas, comunidades o autoridades deben recibir capacitación explicable para que comprendan las salidas.

## Técnicas de explicabilidad

No se reporta la implementación de SHAP, LIME ni explicaciones locales por predicción. Para un uso operativo, las explicaciones deben dejar claro que asociación predictiva no implica causalidad.

## 5. Impacto social

## ¿Qué impacto positivo puede tener el proyecto? 

Una alerta estacional y territorial ayuda a viajeros a planificar con información preventiva, facilitando que autoridades y operadores preparen recursos y llamar la atención sobre zonas con repuntes históricos. El panel puede servir para priorizar análisis y mejorar la conversación sobre seguridad turística en Ecuador.

## ¿Qué impactos negativos podrían surgir?

Las alertas falsas pueden causar alarma, estigmatizar cantones y afectar a negocios y trabajadores turísticos; las omisiones pueden dar una falsa sensación de seguridad. Una señal basada en llamadas registradas puede reforzar desigualdades de vigilancia o de denuncia.

## ¿Quiénes se benefician? 
 Se benefician potencialmente turistas, autoridades y operadores que reciben información útil.

## ¿Quiénes podrían ser perjudicados?
Podrían cargar con los costos comunidades locales y negocios señalados por alertas imprecisas, el presente alcance no mide estos impactos sociales ni económicos.

Las alertas deben presentarse como orientación preventiva, no como ranking definitivo de lugares ni como sustituto de información local, criterios oficiales o decisiones de seguridad.

## 6. Responsabilidad y rendición de cuentas

## ¿Quién es responsable si el modelo falla?

La responsabilidad corresponde a la organización y creadores que desarrollan, validan, publican y operan el sistema, y a las personas designadas para gobernar su uso. No se identifica un propietario operativo, responsable de producto ni autoridad de aprobación. Antes de cualquier despliegue deben quedar asignados responsables técnicos y de gestión, canales de contacto, atención al público y procedimiento de respuesta a incidentes.

## ¿Qué mecanismos de accountability existen?

Se implementa una separación temporal (entrenamiento 2021–2024 y prueba 2025–2026), `TimeSeriesSplit` y auditoría regional de métricas. Se debe asignar un sistema de monitoreo en producción, revisión humana, mecanismo o calendario de actualización. 


## Plan de monitoreo y actualización del modelo 

Un plan responsable de monitoreo debe cumplir lo siguiente(el alcance no considera esto):

- Registrar versión del modelo, datos, umbrales y cambios;
- Revisar periódicamente la  calidad, cobertura, calibración y desempeño global y por región/cantón;
- Alertar sobre cambios de distribución, aumento de errores o brechas, especialmente en grupos con pocas muestras;
- Revisar incidentes y reclamos con responsables identificados, y corregir, retirar o suspender alertas cuando corresponda;
- Revalidar con datos recientes antes de actualizar y conservar evaluación temporal independiente;
- Comunicar cambios y limitaciones a usuarios y comunidades afectadas.
- Mantener disponibilidad y en caso de actualizaciones incorrectas tener un plan de rollback

## 7. Uso dual y mal uso

##¿Podría el modelo usarse con fines maliciosos?

El sistema podría usarse indebidamente para estigmatizar territorios, orientar vigilancia desproporcionada, justificar restricciones o presentar predicciones como hechos confirmados.

##¿Qué salvaguardas se han implementado? 

Como salvaguardas documentadas, el proyecto agrega los registros por cantón y mes, fija una partición temporal y construye métricas regionales para revisión. Proponemos un semáforo preventivo gradual para evitar alertas binarias alarmistas, pero no se documenta controles de acceso, política de uso, revisión humana ni mecanismos técnicos contra esos usos(esto se encuenytra fuera del alcance). 

##Limitaciones de uso claramente documentadas

Debe limitarse su uso a planificación preventiva y comunicación contextual; no debe utilizarse para decisiones o beneficios individuales, sanciones, vigilancia o asignación automática de recursos.

## 8. Limitaciones reconocidas:

## ¿En qué casos NO debe usarse el modelo?
No debe usarse para:

- Predecir la peligrosidad de una persona, identificar sospechosos o tomar decisiones individuales por el sector en el que habita.
- Garantizar seguridad, reemplazar alertas oficiales o aconsejar por sí solo una ruta o destino
- Comparar directamente cantones como si tuvieran igual población, afluencia.
- Justificar sanciones, restricciones, seguros, inversión o vigilancia sin revisión humana, contexto y evidencia adicional;
- Extrapolar a períodos posteriores a 2026, territorios no representados o eventos raros sin nueva validación.

## ¿Qué advertencias deben darse a los usuarios? 

La salida es una clasificación mensual relativa a un umbral histórico cantonal, no una probabilidad individual ni una medida absoluta comparable entre cantones. Los registros reflejan llamadas/despachos, no necesariamente todos los delitos ocurridos. Una predicción puede fallar si cambian patrones de reporte, población visitante, clasificación de eventos, condiciones locales o distribución temporal.

## Casos límite donde el modelo no es confiable 

Debe tratarse con especial cautela cuando hay pocas observaciones por región por ejemplo las detectadas en (Galápagos: 60 y Otras Regiones: 40 en la prueba reportada), ante cambios abruptos, cantones con registros incompletos, delitos muy raros o situaciones que no aparecen en el histórico. El período de prueba incluye datos pero no garantiza validez futura; siempre se debe validar independiente antes de cualquier uso público u operativo.
