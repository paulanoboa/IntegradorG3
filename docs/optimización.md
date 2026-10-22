# Optimización de hiperparámetros (Workshop S5)

## Alcance y protocolo

El notebook [`optimizacion_modelo.ipynb`] optimiza un clasificador `XGBClassifier` para predecir `Mes_Alto_Riesgo`. El dataset contiene 13.722 registros cantonales-mensuales: entrenamiento temporal 2021–2024 (9.282 observaciones) y prueba 2025–2026 (4.440 observaciones). El entrenamiento incorpora `Peso_Muestra_Fairness` como `sample_weight`.

La búsqueda utiliza Optuna con el sampler TPE, semilla 42 y 35 ensayos. En cada ensayo se calcula el F1 promedio de una validación cruzada `StratifiedKFold` de cuatro pliegues sobre el conjunto de entrenamiento. El mejor F1 es ; **F1 = 0,7258** en validación cruzada. El conjunto de prueba temporal se reserva para la comparación final.

## Hiperparámetros explorados y rangos

| Hiperparámetro | Rango explorado | Muestreo | Valor base antes de optimizar |
|---|---:|---|---:|
| `n_estimators` | 100–300 | Entero, paso 25 | 160 |
| `max_depth` | 3–7 | Entero | 5 |
| `learning_rate` | 0,02–0,12 | Logarítmico | 0,05 |
| `subsample` | 0,70–0,95 | Paso 0,05 | 0,85 |
| `colsample_bytree` | 0,70–0,95 | Paso 0,05 | 0,85 |
| `min_child_weight` | 1–6 | Entero | 1 |
| `scale_pos_weight` | 1,2–2,2 | Paso 0,2 | 1,5 |
| `reg_alpha` (L1) | 0,05–3,0 | Logarítmico | 0,1 |
| `reg_lambda` (L2) | 0,5–8,0 | Logarítmico | 1,2 |
| `gamma` | 0,0–2,5 | Paso 0,5 | 0,0 |

El XGBoost de cada pliegue se entrena con `sample_weight` y usa `logloss` como métrica interna del estimador. La función objetivo de Optuna, en cambio, maximiza F1.

## Resultados del análisis de sensibilidad

El notebook grafica los ensayos para seis parámetros (`learning_rate`, `max_depth`, `n_estimators`, `scale_pos_weight`, `subsample` y `reg_lambda`) y ajusta una curva polinomial. La tabla de sensibilidad reporta para los seis, de forma idéntica, F1 mínimo **0,6592**, máximo **0,7258**, rango **0,0666**, desviación estándar **0,0154** e IQR **0,011**, y los clasifica como “Alta Sensibilidad”.

**Esta tabla no permite concluir que cada parámetro tenga esa misma sensibilidad.** El código calcula mínimo, máximo, desviación e IQR sobre todos los ensayos dentro del bucle, sin filtrar los resultados por el valor del parámetro. Por ello repite las mismas estadísticas globales seis veces. Además, los ensayos TPE cambian varios hiperparámetros a la vez; las curvas de dispersión no aíslan un efecto causal. Los gráficos pueden orientar una inspección, pero el dictamen cuantitativo debe considerarse pendiente de corregir mediante análisis por grupos o experimentos controlados de un factor a la vez.

## Partial dependence plots (PDP)

El notebook genera dos tipos de gráficos:

1. **Resumen de ensayos para hiperparámetros:** `max_depth`, `learning_rate`, `scale_pos_weight` y `subsample`. Para `max_depth` agrupa los F1 por valor; para los parámetros continuos dibuja una media móvil de siete ensayos ordenados por parámetro y una banda de una desviación estándar. Son suavizados descriptivos de los ensayos TPE, no PDP formales de una función objetivo entrenada.
2. **PDP de características del modelo:** usa `PartialDependenceDisplay` con un XGBoost ajustado con los mejores parámetros y el conjunto `X_train`. Presenta el efecto marginal promedio de `Proporcion_Delitos`, `Media_Movil_3M`, `Cluster_Riesgo` y `Total_Incidentes` sobre la probabilidad estimada de alto riesgo.

Las salidas guardadas contienen las figuras, no valores numéricos de las curvas. Por tanto, aquí no se asignan puntos de corte ni magnitudes específicas a los efectos visuales. Los PDP describen asociaciones del modelo y no relaciones causales; en variables correlacionadas, el promedio marginal también puede representar combinaciones poco frecuentes de datos.

## Ranking de importancia de hiperparámetros

La importancia se calcula con fANOVA sobre los ensayos de Optuna y su métrica F1 de validación:

| Posición | Hiperparámetro | Importancia reportada |
|---:|---|---:|
| 1 | `scale_pos_weight` | 27,01 % |
| 2 | `n_estimators` | 25,42 % |
| 3 | `max_depth` | 11,21 % |
| 4 | `subsample` | 10,81 % |
| 5 | `reg_lambda` | 9,32 % |
| 6 | `learning_rate` | 8,83 % |
| 7 | `colsample_bytree` | 2,79 % |
| 8 | `reg_alpha` | 2,72 % |
| 9 | `gamma` | 1,19 % |
| 10 | `min_child_weight` | 0,71 % |

Según esta estimación, `scale_pos_weight` y `n_estimators` explican conjuntamente el 52,43 % de la variación observada en el objetivo entre ensayos. Estas importancias dependen del espacio explorado, de los 35 ensayos y de sus resultados; no son medidas universales de relevancia ni importancia de características del modelo.

## Análisis de interacciones

El notebook grafica superficies de contorno interpoladas para cuatro pares, a partir de F1 y de los valores evaluados en los ensayos:

- `max_depth` y `learning_rate`;
- `subsample` y `colsample_bytree`;
- `scale_pos_weight` y `min_child_weight`;
- `reg_alpha` y `reg_lambda`.

La superficie usa interpolación lineal entre puntos y vecino más próximo en zonas no cubiertas. Las figuras ayudan a localizar combinaciones que merecen exploración, pero con 35 ensayos en un espacio de diez dimensiones no constituyen una estimación exhaustiva de las interacciones. Las regiones interpoladas sin ensayos cercanos deben leerse con especial cautela( pocos datos respecto a otras provincias o cnatones).

## Configuración final seleccionada y justificación

La configuración seleccionada es el mejor ensayo TPE, con F1 promedio de validación cruzada **0,7258**:

| Parámetro | Valor seleccionado | Valor base |
|---|---:|---:|
| `n_estimators` | 300 | 160 |
| `max_depth` | 6 | 5 |
| `learning_rate` | 0,0447 | 0,05 |
| `subsample` | 0,70 | 0,85 |
| `colsample_bytree` | 0,90 | 0,85 |
| `min_child_weight` | 3 | 1 |
| `scale_pos_weight` | 2,20 | 1,50 |
| `reg_alpha` | 0,3298 | 0,10 |
| `reg_lambda` | 4,0918 | 1,20 |
| `gamma` | 0,50 | 0,0 |

Se eligió por maximizar F1 en la validación interna y luego se volvió a ajustar sobre todo el conjunto de entrenamiento con los pesos de equidad. El mayor peso positivo favorece la detección de meses críticos; esta decisión aumenta el recall en prueba, pero reduce la precisión y empeora el Brier score frente al XGBoost base. La configuración es un resultado experimental, no una recomendación de despliegue sin validación adicional.

## Comparación antes/después de la optimización

Métricas reportadas para el conjunto de prueba temporal 2025–2026:

| Modelo | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | Brier | Brecha F1 (Train–Test) | Brecha AUC (Train–Test) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Random Forest (baseline) | 0,8408 | 0,6570 | 0,6116 | 0,6335 | 0,8871 | 0,6908 | 0,1143 | 11,54 % | 4,43 % |
| XGBoost antes de optimizar | 0,8304 | 0,5967 | 0,7598 | **0,6684** | 0,8948 | 0,7103 | **0,1179** | **9,77 %** | **2,74 %** |
| XGBoost optimizado (S5) | 0,8124 | 0,5562 | **0,8228** | 0,6637 | **0,8981** | **0,7174** | 0,1278 | 14,62 % | 5,11 % |

Frente al XGBoost base, el modelo optimizado aumenta el recall en **6,31 puntos porcentuales**, el ROC-AUC en **0,33 puntos** y el PR-AUC en **0,70 puntos**. A cambio, la precisión cae **4,05 puntos**, el F1 cae **0,47 puntos**, la exactitud baja **1,80 puntos** y el Brier score empeora en **0,0099** (menor es mejor). También aumenta la brecha Train–Test de F1 de 9,77 % a 14,62 % y la brecha AUC de 2,74 % a 5,11 %.

Por tanto, la optimización **no mejora todas las métricas**: prioriza detectar más meses de alto riesgo y logra mejores métricas de ranking, con menor precisión y calibración probabilística, F1 de prueba ligeramente inferior y una brecha de generalización mayor. El F1 optimizado supera al Random Forest en 3,02 puntos porcentuales, pero el XGBoost previo obtiene el mayor F1 de prueba de los tres modelos.


## Conclusión
La optimización usa TPE reproducible y una evaluación temporal separada. El mejor ensayo eleva el recall y las métricas ROC/PR respecto al XGBoost base, pero no mejora su F1 de prueba ni su calibración y presenta una brecha Train–Test mayor. Antes de recomendarlo para alertas operativas, se deben corregir las estadísticas de sensibilidad, revisar las discrepancias de resultados y repetir la evaluación con variabilidad entre semillas o ventanas temporales adicionales.
