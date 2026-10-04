# Resumen global de métricas

| modelo               |   accuracy |   precision |   recall |       f1 |   auc_roc |   silhouette_score |   n_test |   umbral_registros_alto_promedio |   umbral_probabilidad |
|:---------------------|-----------:|------------:|---------:|---------:|----------:|-------------------:|---------:|---------------------------------:|----------------------:|
| Random Forest        |     0.8642 |      0.7273 |   0.2963 |   0.4211 |    0.8833 |           nan      |      324 |                       11270.0370 |              nan      |
| XGBoost              |     0.6698 |      0.3172 |   0.8519 |   0.4623 |    0.8416 |           nan      |      324 |                       11270.0370 |                0.2000 |
| K-Means (provincias) |   nan      |    nan      | nan      | nan      |  nan      |             0.2741 |       24 |                         nan      |              nan      |

El mapa usa centroides provinciales aproximados y los grupos reflejan volumen observado, no riesgo individual ni tasa ajustada por población. La evaluación supervisada es temporal (entrenamiento en meses anteriores y prueba en el tramo final).
