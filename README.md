# GameScope Analytics · Tercera Solemne de Programación II

**Integrantes:** Martín Vásquez · Lizandro Delgado

## Descripción
Aplicación web de exploración y análisis del catálogo de videojuegos gratuitos de FreeToGame. La fuente entrega títulos, portadas, géneros, plataformas, desarrolladores, editores y fechas de lanzamiento. No se inventan ventas, usuarios activos ni valoraciones.

**Fuente:** https://www.freetogame.com/  
**Documentación:** https://www.freetogame.com/api-doc  
**Consulta utilizada:** https://www.freetogame.com/api/games

## Ejecución
1. Instalar Python 3.10 o superior.
2. `pip install -r requirements.txt`
3. `streamlit run app.py`
4. Abrir la dirección local que indique Streamlit.

La API se consulta mediante `requests.get()` y se convierte en un DataFrame con `pandas`. Si la API está caída, se puede subir un CSV previamente exportado desde la app. No se distribuye un respaldo ficticio.

## Preguntas de investigación
1. ¿Qué géneros tienen más juegos?
2. ¿Cómo se distribuyen por plataforma?
3. ¿Cómo evolucionó el número de lanzamientos registrados por año?
4. ¿Qué asociación descriptiva existe entre plataforma y género?
5. ¿Qué desarrolladores tienen más títulos?
6. ¿Cómo cambian estos resultados al aplicar filtros?

## Componentes
Usa selectbox, multiselect, text_input, slider, select_slider, radio, checkbox, toggle, button, file_uploader, number_input, download_button, metric, tabs, columns, expander, dataframe, plotly_chart, form, form_submit_button, text_area, feedback, entre otros. Los filtros modifican las filas analizadas y actualizan gráficos e indicadores.

## Archivos
- `app.py`: interfaz y gráficos
- `games_data.py`: obtención, limpieza, filtros, análisis
- `requirements.txt`: dependencias
- `respaldo_pokedashboard/app.py`: copia del trabajo anterior
- `respaldo_clase_autos/app.py`: copia del antiguo trabajo de autos

## Limitaciones
Los datos representan el catálogo registrado en FreeToGame en la fecha de consulta, no la totalidad de videojuegos. Fecha de lanzamiento puede faltar; gráficos temporales excluyen esos registros. Una mayor cantidad de títulos registrados no demuestra popularidad ni más jugadores.

## Presentación
La defensa grupal dura 8–10 minutos. Mostrar una consulta, filtrar por género/plataforma y explicar el cambio en métricas y al menos tres tipos de gráficos. Los hallazgos deben obtenerse con el catálogo real cargado el día de la presentación.
