# PokéLab Analytics — Solemne 3

**Integrantes:** Martín Vásquez y Lizandro Delgado.

Dashboard Streamlit para analizar estadísticas reales de Pokémon desde PokéAPI. Está organizado en seis pestañas: Pokédex, Análisis, Comparador, Relaciones, Datos y Defensa.

## Fuentes
- API REST: https://pokeapi.co/api/v2/pokemon/
- Documentación: https://pokeapi.co/docs/v2

## Ejecutar
1. Instalar Python 3.10+.
2. Ejecutar `pip install -r requirements.txt`.
3. Ejecutar `streamlit run app.py`.
4. Elegir 30, 60, 100, 151 o 251 primeros Pokémon. La primera carga necesita acceso a la API, y luego se almacena en caché.

## Qué investiga la app
- Tipo principal más frecuente (barras y gráfico circular).
- Distribución del ataque base (histograma).
- Comparaciones de hasta cuatro Pokémon (barras agrupadas).
- Relación entre ataque y velocidad (dispersión/correlación).
- Diferencias de estadísticas totales según tipo (cajas y tabla de promedios).
- Cambios en indicadores después de aplicar filtros.

## Requisitos de la rúbrica
- API REST mediante requests.get, respuestas JSON y DataFrame de pandas.
- Limpieza de duplicados, conversión numérica, revisión de faltantes y cálculos en funciones separadas.
- Más de 16 instancias de Streamlit y más de 12 tipos de componentes: selectbox, multiselect, slider, checkbox, number_input, toggle, text_input, select_slider, button, metric, tabs, columns, dataframe, plotly_chart, download_button, expander, file_uploader, radio, text_area, form, form_submit_button, feedback, entre otros.
- Seis tipos de gráfico: barras, histograma, circular, dispersión, cajas y barras comparativas; **cinco familias distintas** (barras comparativas comparten familia con barras).
- Filtros funcionales que recalculan gráficos, indicadores y tabla.
- Descarga CSV de los datos reales y selección filtrada.

## Limitaciones
El análisis usa los primeros IDs de la API, no una muestra aleatoria de todas las especies. Los resultados describen estadísticas base de videojuegos, no daño en combate. La API pública puede no responder; es posible cargar una copia real previamente exportada como CSV, pero no se incluyen registros inventados. Al filtrar, grupos pequeños requieren precaución.

## Distribución sugerida de exposición (9 minutos)
- Martín, 0:00–1:15: tema, preguntas, fuente.
- Lizandro, 1:15–2:45: API, DataFrame, limpieza.
- Martín, 2:45–5:20: filtros, KPIs, análisis visual.
- Lizandro, 5:20–7:45: comparador, relaciones, resultados y limitaciones.
- Ambos, 7:45–9:00: preguntas y conclusión.

## Archivos
- `app.py`: UI, filtros y gráficos.
- `data_utils.py`: consultas REST, limpieza, filtrado y hallazgos.
- `requirements.txt`: dependencias.
- `respaldo_pokedashboard/app.py`: versión anterior de Pokémon.
- `respaldo_clase_autos/app.py`: versión anterior del trabajo de autos.

**Importante:** la entrega Blackboard exige ZIP con los nombres y apellidos, README.txt, informe PDF máximo tres páginas, presentación y enlace público. Preparar esos documentos conforme a la versión definitiva y comprobar el deploy antes de entregar.
