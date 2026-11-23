"""PokéDashboard | Martín Vásquez y Lizandro Delgado | Solemne 3."""
import pandas as pd
import plotly.express as px
import streamlit as st
from data_utils import NAMES,STATS,load,clean,filter_data,findings

st.set_page_config(page_title="PokéDashboard | Solemne 3",page_icon="⚡",layout="wide")
st.title("⚡ PokéDashboard · Laboratorio Pokémon")
st.write("**Martín Vásquez · Lizandro Delgado** | Taller de Programación II")
st.caption("Fuente: [PokéAPI](https://pokeapi.co/) · [Documentación](https://pokeapi.co/docs/v2). Estadísticas base de videojuegos; no son valores de daño real.")

with st.expander("📖 Instrucciones y preguntas de investigación"):
    st.write("Selecciona la muestra, usa los filtros de la barra lateral y cambia de pestaña. Todas las cifras provienen de la API o de un CSV real exportado previamente.")
    st.markdown("**Investigamos:** ¿Qué tipo predomina? ¿Cómo se distribuye el ataque? ¿Qué Pokémon se destaca? ¿Hay relación entre velocidad y ataque? ¿Cómo varían las estadísticas entre tipos? ¿Qué cambia al aplicar filtros?")

@st.cache_data(ttl=86400,show_spinner=False)
def get_data(n):
    return load(n)

with st.sidebar:
    st.header("🎛️ Panel de control")
    n=st.selectbox("Primeros Pokémon por ID",[30,60,100,151,251],index=3)
    if st.button("🔄 Actualizar datos desde PokéAPI"):
        get_data.clear()
        st.rerun()

try:
    with st.spinner("Consultando PokéAPI…"):
        original,failed=get_data(n)
    origen="PokéAPI"
except Exception as exc:
    st.warning(f"No se logró conectar a PokéAPI: {exc}")
    st.info("Puedes subir un CSV REAL exportado desde este dashboard en una ejecución anterior. No se generan datos inventados.")
    upload=st.file_uploader("CSV de respaldo real",type=["csv"])
    if upload is None:st.stop()
    original=clean(pd.read_csv(upload))
    failed=[]
    origen="CSV de respaldo"
if failed:st.warning(f"Consulta parcial: fallaron {len(failed)} IDs. Solo se analizan {len(original)} registros recibidos.")
if original.empty:st.error("Sin datos válidos.");st.stop()

all_types=sorted(set(original["Tipo principal"]) | (set(original["Tipo secundario"])-{""}))
with st.sidebar:
    st.subheader("🔍 Filtros efectivos")
    types=st.multiselect("Tipos (principal o secundario)",all_types)
    name=st.text_input("Buscar Pokémon",placeholder="Ej.: pika")
    attack=st.slider("Ataque mínimo",0,200,0,5)
    speed=st.slider("Velocidad mínima",0,200,0,5)
    dual=st.checkbox("Solo Pokémon con dos tipos")
    weight=st.number_input("Peso máximo (kg)",min_value=1,max_value=max(1,int(original["Peso (kg)"].max())+1),value=max(1,int(original["Peso (kg)"].max())+1))
    sort=st.radio("Ordenar por",["ID","Ataque","Velocidad","Total"])
    reverse=st.toggle("Orden descendente",value=(sort!="ID"))
    show_images=st.checkbox("Mostrar imágenes",value=True)

df=filter_data(original,types,name,attack,speed,dual,weight).sort_values(sort,ascending=not reverse)
st.caption(f"Fuente: {origen} · {len(original)} registros originales · {len(df)} registros tras filtros")
kpis=st.columns(5)
labels=["Pokémon","Ataque medio","Velocidad media","Total medio","De dos tipos"]
values=[str(len(df)),f"{df['Ataque'].mean():.1f}" if len(df) else "—",f"{df['Velocidad'].mean():.1f}" if len(df) else "—",f"{df['Total'].mean():.1f}" if len(df) else "—",str(int((df["Tipo secundario"].str.len()>0).sum()))]
for col,label,value in zip(kpis,labels,values):col.metric(label,value)
tab1,tab2,tab3,tab4,tab5=st.tabs(["📊 Explorar","⚔️ Comparar","🔬 Relaciones","📋 Datos y calidad","🎓 Defensa"])

with tab1:
    st.subheader("Pregunta 1 · ¿Qué tipo es más frecuente?")
    if not df.empty:
        kind=st.select_slider("Contar tipo",["Tipo principal","Tipo secundario"])
        counts=df[kind].replace("",pd.NA).dropna().value_counts().rename_axis("Tipo").reset_index(name="Cantidad")
        if not counts.empty:
            fig=px.bar(counts,x="Tipo",y="Cantidad",color="Tipo",title="Frecuencia por tipo",labels={"Cantidad":"Número de Pokémon"})
            st.plotly_chart(fig,use_container_width=True)
        st.subheader("Pregunta 2 · ¿Cómo se distribuye el ataque?")
        bins=st.slider("Cantidad de intervalos",5,30,12)
        hist=px.histogram(df,x="Ataque",nbins=bins,title="Distribución del ataque base")
        hist.update_layout(xaxis_title="Ataque (puntos base)",yaxis_title="Cantidad de Pokémon")
        st.plotly_chart(hist,use_container_width=True)
        st.markdown("**Hallazgos automáticos calculados con la selección:**")
        for f in findings(df):st.write("• "+f)
    else:st.warning("Sin resultados: reduce los filtros.")

with tab2:
    st.subheader("Pregunta 3 · ¿Quién destaca al comparar varios Pokémon?")
    selected=st.multiselect("Selecciona 2–4 Pokémon",df["Nombre"].tolist(),default=df["Nombre"].tolist()[:2],max_selections=4)
    stat=st.selectbox("Estadística para elegir ganador",STATS)
    if len(selected)>1:
        chosen=df[df["Nombre"].isin(selected)]
        long=chosen.melt(id_vars="Nombre",value_vars=STATS,var_name="Estadística",value_name="Puntos")
        st.plotly_chart(px.bar(long,x="Estadística",y="Puntos",color="Nombre",barmode="group",title="Comparación de estadísticas base"),use_container_width=True)
        winner=chosen.nlargest(1,stat).iloc[0]
        st.success(f"Mayor {stat.lower()}: {winner['Nombre']} con {winner[stat]:.0f} puntos base.")
        if show_images:
            for col,(_,p) in zip(st.columns(len(chosen)),chosen.iterrows()):
                with col:
                    if p["Imagen"]:st.image(p["Imagen"],width=120)
                    st.write(f"**{p['Nombre']}** · {p['Tipos']}")
        st.dataframe(chosen[["Nombre","Tipos",*STATS,"Total"]],hide_index=True,use_container_width=True)
    else:st.info("Selecciona al menos dos Pokémon.")

with tab3:
    st.subheader("Pregunta 4 · ¿Qué relación tienen dos estadísticas?")
    a,b=st.columns(2)
    with a:x=a.selectbox("Eje horizontal",STATS,index=1)
    with b:y=b.selectbox("Eje vertical",STATS,index=5)
    if not df.empty:
        st.plotly_chart(px.scatter(df,x=x,y=y,color="Tipo principal",hover_name="Nombre",title=f"{x} frente a {y}"),use_container_width=True)
        st.caption("Cada punto representa un Pokémon. Asociación no significa causalidad.")
        st.subheader("Pregunta 5 · ¿Qué tipos presentan mayor dispersión?")
        st.plotly_chart(px.box(df,x="Tipo principal",y="Total",points="outliers",title="Distribución del total estadístico por tipo"),use_container_width=True)
        st.subheader("Pregunta 6 · ¿Qué tipos tienen mayor ataque promedio?")
        summary=df.groupby("Tipo principal",as_index=False).agg(Cantidad=("ID","count"),Ataque_promedio=("Ataque","mean"),Velocidad_promedio=("Velocidad","mean"))
        st.dataframe(summary.sort_values("Ataque_promedio",ascending=False).round(1),hide_index=True,use_container_width=True)
    else:st.info("No hay registros para analizar.")

with tab4:
    st.subheader("Tabla y control de calidad de los datos")
    cols=["ID","Nombre","Tipo principal","Tipo secundario",*STATS,"Total","Altura (m)","Peso (kg)","Habilidades"]
    chosen_cols=st.multiselect("Columnas visibles",cols,default=["ID","Nombre","Tipo principal","Ataque","Defensa","Velocidad","Total"])
    if chosen_cols:st.dataframe(df[chosen_cols],hide_index=True,use_container_width=True)
    st.download_button("⬇️ Exportar datos reales originales",original.to_csv(index=False).encode("utf-8-sig"),file_name="pokemon_respaldo_real.csv",mime="text/csv")
    st.download_button("⬇️ Descargar selección filtrada",df.to_csv(index=False).encode("utf-8-sig"),file_name="pokemon_filtrados.csv",mime="text/csv")
    quality=pd.DataFrame({"Columna":original.columns,"Tipo":[str(original[c].dtype) for c in original.columns],"Faltantes":[int(original[c].isna().sum()) for c in original.columns]})
    st.dataframe(quality,hide_index=True,use_container_width=True)
    st.write(f"IDs duplicados tras limpiar: **{original['ID'].duplicated().sum()}**.")
    st.caption("Limitaciones: primeros IDs elegidos, API pública sujeta a fallos y estadísticas propias del videojuego.")

with tab5:
    st.subheader("Laboratorio de preguntas de la profesora")
    task=st.selectbox("Pregunta para investigar",["¿Quién tiene más ataque?","¿Qué tipo principal aparece más?","¿Cuántos tienen doble tipo?","¿Qué ocurre al subir el ataque mínimo?","¿Para qué sirve un DataFrame?"])
    if len(df):
        if task=="¿Quién tiene más ataque?":
            top=df.nlargest(1,"Ataque").iloc[0]
            st.info(f"{top['Nombre']}: {top['Ataque']:.0f} puntos base de ataque.")
        elif task=="¿Qué tipo principal aparece más?":
            counts=df["Tipo principal"].value_counts()
            st.info(f"{counts.index[0]}: {counts.iloc[0]} registros.")
        elif task=="¿Cuántos tienen doble tipo?":st.info(f"{(df['Tipo secundario'].str.len()>0).sum()} registros de la selección.")
        else:st.info("Cambia los filtros, observa cómo varían los resultados y explícalo con tus palabras.")
    with st.form("quiz"):
        answer=st.radio("¿Para qué sirve st.multiselect?",["Para subir una foto","Para seleccionar varias opciones","Para borrar datos"],index=None)
        st.text_area("Explica qué hace filter_data() en tus palabras")
        submitted=st.form_submit_button("Comprobar respuesta")
    if submitted:
        if answer=="Para seleccionar varias opciones":st.success("Correcto: permite seleccionar varias opciones.")
        else:st.error("Respuesta correcta: permite seleccionar varias opciones.")
    st.feedback("thumbs")
    st.caption("Martín Vásquez y Lizandro Delgado · Solemne 3 · PokéAPI")
