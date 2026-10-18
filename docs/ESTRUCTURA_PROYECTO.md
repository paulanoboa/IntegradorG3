# Estructura y flujo de trabajo

```text
app/                          Aplicacion de monitoreo/mapa
data/                         Datos usados en el proyecto integrador
  raw/                        Fuentes originales 
  processed/                  Datos limpios, auditoria y agregados
docs/                         Dcoumentación
  Anexos/                     Información adcional
  eda_graficos/               Gráficos generados del EDA
  Entregables/                Entregables semanales del proyecto integrador
  planificacion.md            Documento de planificación inicial
  analisis_datos.md           Análisis exploratorio de datos
  arquitectura.md             Diseño del modelo y arquitectura
  optimizacion.md             Proceso de optimización (Workshop S5)
  consideraciones_eticas.md   Análisis ético del proyecto
  manual_usuario.md           Guía para usuarios finales
  estructura_proyecto.md      Estructura de carpetas del proyecto
models/                       Estimadores entrenados y metadatos
notebooks/                    Jupyter notebooks
  01_exploracion.ipynb        EDA
  02_preprocesamiento.ipynb   Limpieza y preparación
  03_modelado.ipynb           Entrenamiento de modelos
  04_optimizacion.ipynb       Optimización de hiperparámetros
  05_evaluacion.ipynb         Evaluación final
src/                          Fuentes de desarrollo
results/                      Resultado de los datos, métricas y gráficos
tests/                        Pruebas

## Ejecucion

## Hallazgos sobre el esquema

En los archivos inspeccionados el esquema es `Fecha;provincia;Canton;Cod_Parroquia;Parroquia;Servicio;Subtipo` (CSV separado por punto y coma; también existen XLSX). No hay campos de latitud, longitud ni hora. La serie solicitada cubre julio de 2022 agosto de 2026; el inventario de archivos muestra que 2023 tiene 11 meses (falta diciembre). La auditoria debe confirmar y registrar otras brechas antes de calcular tendencias.

La actividad de diagnostico de overfitting/underfitting se refleja en la separacion cronologica, el ajuste del preprocesador solo en train, la recomendacion de comparar baseline y modelo, y la necesidad de curvas de aprendizaje antes de aceptar el modelo. No se asume una metrica de accuracy arbitraria para un problema de conteo.
