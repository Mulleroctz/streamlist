"""PokéLab Analytics · Solemne 3 · Martín Vásquez y Lizandro Delgado."""
import html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from data_utils import load,clean,filter_data,findings,STATS

st.set_page_config(page_title="PokéLab | Analytics",page_icon="⚡",layout="wide",initial_sidebar_state="expanded")
st.markdown("""<style>
.stApp{background:radial-gradient(ellipse at 88% 0%,#26355b 0%,transparent 32%),linear-gradient(140deg,#0a1120,#10182a 65%,#111d32);color:#edf3ff}
.block-container{max-width:1500px;padding-top:1.3rem}
[data-testid="stSidebar"]{background:#101a2e}
[data-testid="stMetric"]{background:linear-gradient(135deg,#1d2a46,#17243b);border:1px solid #34496d;border-radius:18px;padding:17px}
[data-testid="stTabs"] button{font-size:1rem}
.hero{padding:28px 34px;border-radius:24px;background:linear-gradient(115deg,#5b3678,#263e81 55%,#106378);border:1px solid #6574ab;margin-bottom:18px}
.hero h1{color:#fff;font-size:2.65rem;letter-spacing:-.055em;margin:0}
.hero p{color:#dceaff;font-size:1rem;margin:8px 0 0}
.pokemon-card{background:#18243b;border:1px solid #324867;border-radius:20px;overflow:hidden;margin-bottom:14px;min-height:330px}
.pokemon-card img{display:block;height:185px;width:100%;object-fit:contain;background:radial-gradient(circle,#32456f 0%,#18243b 68%)}
.pokemon-body{padding:15px}
.pokemon-id{font-size:.72rem;letter-spacing:.07em;color:#a2c0e9}
.pokemon-name{font-size:1.22rem;font-weight:800;color:#f4f7ff}
.pokemon-type{display:inline-block;padding:4px 10px;margin-top:8px;background:#294563;border:1px solid #426b91;border-radius:16px;color:#cde9ff;font-size:.78rem}
.pokemon-stats{margin-top:11px;font-size:.85rem;color:#c5d5f0}
.question{padding:12px 16px;border-left:4px solid #7bd9e9;background:#17273e;border-radius:0 12px 12px 0;margin:15px 0}
</style>""",unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>⚡ PokéLab <span style="color:#99f2ff">Analytics</span></h1><p>Una Pokédex interactiva para investigar estadísticas, tipos y diferencias entre Pokémon · Martín Vásquez & Lizandro Delgado</p></div>',unsafe_allow_html=True)
st.caption("Fuente: [PokéAPI](https://pokeapi.co/) · [Documentación oficial](https://pokeapi.co/docs/v2). Los indicadores corresponden a estadísticas base de los videojuegos, no al daño de combate.")

@st.cache_data(ttl=86400,show_spinner=False)
def get_pokemon(count):
    return load(count)

with st.sidebar:
    st.header("🎛️ Laboratorio de datos")
    n=st.selectbox("Tamaño de muestra: primeros IDs",[30,60,100,151,251],index=3,help="La selección de IDs no es una muestra aleatoria.")
    if st.button("🔄 Actualizar PokéAPI",use_container_width=True):
        get_pokemon.clear()
        st.rerun()
try:
    with st.spinner("Obteniendo datos oficiales de PokéAPI…"):
        raw,failed=get_pokemon(n)
    source="PokéAPI"
except Exception as exc:
    st.error(f"PokéAPI no respondió: {exc}")
    st.info("Para trabajar sin internet, carga un CSV real previamente exportado desde esta aplicación. No se inventan registros.")
    uploaded=st.file_uploader("CSV real de respaldo",type="csv")
    if uploaded is None:st.stop()
    try:raw=clean(pd.read_csv(uploaded))
    except Exception as exc:st.error(f"CSV inválido: {exc}");st.stop()
    source="CSV de respaldo"
    failed=[]

if raw.empty:st.warning("La fuente no contiene registros útiles.");st.stop()
if failed:st.warning(f"Consulta parcial: {len(failed)} IDs no respondieron. Los gráficos utilizan exclusivamente los {len(raw)} registros recibidos.")

all_types=sorted(set(raw["Tipo principal"]) | (set(raw["Tipo secundario"])-{""}))
max_weight=max(1,int(raw["Peso (kg)"].max())+1)
with st.sidebar:
    st.subheader("🔎 Filtros que modifican resultados")
    selected_types=st.multiselect("Tipos Pokémon",all_types)
    search=st.text_input("Buscar por nombre",placeholder="Ej.: pikachu")
    atk=st.slider("Ataque mínimo",0,200,0,5)
    speed=st.slider("Velocidad mínima",0,200,0,5)
    dual=st.checkbox("Solo Pokémon de doble tipo")
    weight=st.number_input("Peso máximo en kg",min_value=1,max_value=max_weight,value=max_weight)
    sort=st.selectbox("Ordenar catálogo",["ID","Total","Ataque","Velocidad","Defensa"],index=0)
    descending=st.toggle("Mayor a menor",value=False)
    cards_per_page=st.select_slider("Pokémon por página",options=[6,9,12,18],value=9)
    show_art=st.checkbox("Mostrar ilustraciones",value=True)

df=filter_data(raw,selected_types,search,atk,speed,dual,weight).sort_values(sort,ascending=not descending,na_position="last")
st.caption(f"Datos: {source} · {len(raw)} Pokémon cargados · {len(df)} visibles con tus filtros · IDs iniciales 1–{n}")
metrics=st.columns(5)
values=[str(len(df)),f"{df['Ataque'].mean():.1f}" if len(df) else "—",f"{df['Defensa'].mean():.1f}" if len(df) else "—",f"{df['Velocidad'].mean():.1f}" if len(df) else "—",f"{df['Total'].mean():.1f}" if len(df) else "—"]
for col,label,value in zip(metrics,["🎮 Pokémon","⚔️ Ataque medio","🛡️ Defensa media","💨 Velocidad media","⭐ Total medio"],values):col.metric(label,value)
tabs=st.tabs(["🏠 Pokédex","📊 Análisis","⚔️ Comparador","🔬 Relaciones","🗂️ Datos","🎓 Defensa"])

with tabs[0]:
    st.subheader("Pokédex visual · explora los registros")
    st.markdown('<div class="question">¿Qué Pokémon quedan cuando combinas varios filtros?</div>',unsafe_allow_html=True)
    if df.empty:st.warning("No hay Pokémon con estos criterios. Modifica los filtros.")
    else:
        total_pages=max(1,(len(df)+cards_per_page-1)//cards_per_page)
        page=st.number_input("Página del catálogo",min_value=1,max_value=total_pages,value=1)
        selection=df.iloc[(page-1)*cards_per_page:page*cards_per_page]
        for offset in range(0,len(selection),3):
            columns=st.columns(3)
            for c,(_,p) in zip(columns,selection.iloc[offset:offset+3].iterrows()):
                image_url=str(p["Imagen"])
                art=f'<img loading="lazy" src="{html.escape(image_url,quote=True)}" alt="{html.escape(str(p["Nombre"]))}">' if show_art and image_url.startswith("https://") else ""
                with c:
                    st.markdown(f'<div class="pokemon-card">{art}<div class="pokemon-body"><div class="pokemon-id">N.º {int(p["ID"]):03d}</div><div class="pokemon-name">{html.escape(str(p["Nombre"]))}</div><span class="pokemon-type">{html.escape(str(p["Tipos"]))}</span><div class="pokemon-stats">⚔️ Ataque {p["Ataque"]:.0f} &nbsp; 🛡️ Defensa {p["Defensa"]:.0f}<br>💨 Velocidad {p["Velocidad"]:.0f} &nbsp; ⭐ Total {p["Total"]:.0f}</div></div></div>',unsafe_allow_html=True)

with tabs[1]:
    st.subheader("Análisis descriptivo · preguntas que responden los gráficos")
    if df.empty:st.info("Selecciona al menos un Pokémon.")
    else:
        st.markdown('<div class="question">Pregunta 1: ¿Qué tipo principal predomina entre los Pokémon filtrados?</div>',unsafe_allow_html=True)
        counts=df["Tipo principal"].value_counts().rename_axis("Tipo").reset_index(name="Cantidad")
        st.plotly_chart(px.bar(counts,x="Tipo",y="Cantidad",color="Tipo",title="Frecuencia por tipo principal",labels={"Cantidad":"Cantidad de Pokémon"},template="plotly_dark"),use_container_width=True)
        st.markdown('<div class="question">Pregunta 2: ¿Cómo se distribuye el ataque en esta muestra?</div>',unsafe_allow_html=True)
        nbins=st.slider("Intervalos del histograma",5,30,12)
        fig=px.histogram(df,x="Ataque",nbins=nbins,title="Distribución de ataque base",template="plotly_dark")
        fig.update_layout(xaxis_title="Ataque (puntos base)",yaxis_title="Número de Pokémon")
        st.plotly_chart(fig,use_container_width=True)
        st.markdown('<div class="question">Pregunta 3: ¿Cómo se reparten los tipos principales?</div>',unsafe_allow_html=True)
        st.plotly_chart(px.pie(counts,names="Tipo",values="Cantidad",hole=.52,title="Proporción de tipos principales",template="plotly_dark"),use_container_width=True)
        st.subheader("Hallazgos automáticos basados en tus filtros")
        for result in findings(df):st.write("• "+result)

with tabs[2]:
    st.subheader("Comparación entre 2 y 4 Pokémon")
    choices=st.multiselect("Pokémon para comparar",df["Nombre"].tolist(),default=df["Nombre"].tolist()[:2],max_selections=4)
    winner_stat=st.selectbox("Estadística que define al ganador",STATS)
    if len(choices)<2:st.info("Elige al menos dos Pokémon.")
    else:
        chosen=df[df["Nombre"].isin(choices)]
        melted=chosen.melt(id_vars="Nombre",value_vars=STATS,var_name="Estadística",value_name="Puntos")
        st.plotly_chart(px.bar(melted,x="Estadística",y="Puntos",color="Nombre",barmode="group",title="Comparación de seis estadísticas base",template="plotly_dark"),use_container_width=True)
        best=chosen.nlargest(1,winner_stat).iloc[0]
        st.success(f"Mayor {winner_stat.lower()}: {best['Nombre']} ({best[winner_stat]:.0f} puntos).")
        for column,(_,p) in zip(st.columns(len(chosen)),chosen.iterrows()):
            with column:
                if show_art and str(p["Imagen"]).startswith("https://"):st.image(p["Imagen"],width=140)
                st.write(f"**{p['Nombre']}** · {p['Tipos']}")
        st.dataframe(chosen[["Nombre","Tipos",*STATS,"Total"]],hide_index=True,use_container_width=True)

with tabs[3]:
    st.subheader("Relaciones y variabilidad")
    if df.empty:st.info("Selecciona filtros menos restrictivos.")
    else:
        st.markdown('<div class="question">Pregunta 4: ¿El ataque y la velocidad se relacionan?</div>',unsafe_allow_html=True)
        a,b=st.columns(2)
        with a:x=st.selectbox("Variable horizontal",STATS,index=1)
        with b:y=st.selectbox("Variable vertical",STATS,index=5)
        st.plotly_chart(px.scatter(df,x=x,y=y,color="Tipo principal",hover_name="Nombre",size="Total",size_max=19,title=f"Relación descriptiva: {x} y {y}",template="plotly_dark"),use_container_width=True)
        if len(df)>2 and x!=y:
            corr=df[[x,y]].corr().iloc[0,1]
            if pd.notna(corr):st.metric("Correlación de Pearson",f"{corr:.2f}")
        st.caption("La correlación indica asociación lineal; no demuestra que una estadística provoque la otra.")
        st.markdown('<div class="question">Pregunta 5: ¿Qué tipos presentan más diferencias en el total de estadísticas?</div>',unsafe_allow_html=True)
        st.plotly_chart(px.box(df,x="Tipo principal",y="Total",points="outliers",title="Distribución del total por tipo principal",template="plotly_dark"),use_container_width=True)
        st.markdown('<div class="question">Pregunta 6: ¿Cómo varía el ataque promedio entre tipos?</div>',unsafe_allow_html=True)
        grouped=df.groupby("Tipo principal",as_index=False).agg(Cantidad=("ID","count"),Ataque_promedio=("Ataque","mean"),Velocidad_promedio=("Velocidad","mean")).round(1)
        st.dataframe(grouped.sort_values("Ataque_promedio",ascending=False),hide_index=True,use_container_width=True)
        st.caption("Los grupos pequeños se interpretan con cautela: el promedio puede variar mucho.")

with tabs[4]:
    st.subheader("Control de calidad, tabla y descarga")
    options=["ID","Nombre","Tipo principal","Tipo secundario",*STATS,"Total","Altura (m)","Peso (kg)","Habilidades"]
    visible=st.multiselect("Columnas visibles",options,default=["ID","Nombre","Tipos"] if "Tipos" in options else ["ID","Nombre","Tipo principal","Ataque","Defensa","Velocidad","Total"])
    if visible:st.dataframe(df[visible],hide_index=True,use_container_width=True)
    st.download_button("⬇️ Respaldo CSV real (todos los datos cargados)",raw.to_csv(index=False).encode("utf-8-sig"),file_name="pokemon_respaldo_real.csv",mime="text/csv")
    st.download_button("⬇️ Exportar selección filtrada",df.to_csv(index=False).encode("utf-8-sig"),file_name="pokemon_filtrado.csv",mime="text/csv")
    quality=pd.DataFrame({"Columna":raw.columns,"Tipo":[str(raw[c].dtype) for c in raw.columns],"Faltantes":[int(raw[c].isna().sum()) for c in raw.columns]})
    st.dataframe(quality,hide_index=True,use_container_width=True)
    st.metric("ID duplicados",int(raw["ID"].duplicated().sum()))
    with st.expander("¿Qué limpieza se hizo?"):
        st.write("Pandas convierte las estadísticas a números, comprueba valores ausentes, elimina IDs duplicados y calcula el total sumando las seis estadísticas base. Si una estadística está ausente, no se calcula un total engañoso.")

with tabs[5]:
    st.subheader("Entrenamiento para la presentación y defensa")
    st.markdown("**Ruta fácil de recordar:** API → DataFrame → limpiar → filtrar → calcular → visualizar.")
    q=st.selectbox("Pregunta que podría hacer la profesora",["¿De dónde vienen los datos?","¿Qué es un DataFrame?","¿Cómo funciona el filtro de tipo?","¿Para qué sirve groupby?","¿Por qué un histograma?","¿Qué muestra la dispersión?","¿Por qué no se inventan datos?"])
    answers={
        "¿De dónde vienen los datos?":"requests.get consulta PokéAPI y transforma la respuesta JSON en un registro de pandas.",
        "¿Qué es un DataFrame?":"Una tabla de pandas: cada fila es un Pokémon y cada columna es una característica.",
        "¿Cómo funciona el filtro de tipo?":"El componente multiselect elige tipos y filter_data conserva filas que coinciden; indicadores y gráficos reciben la tabla filtrada.",
        "¿Para qué sirve groupby?":"Agrupa Pokémon por tipo y permite calcular promedios o cantidades de cada grupo.",
        "¿Por qué un histograma?":"Para ver cuántos Pokémon tienen valores de ataque dentro de intervalos.",
        "¿Qué muestra la dispersión?":"Cada punto es un Pokémon; compara dos estadísticas y ayuda a visualizar asociación.",
        "¿Por qué no se inventan datos?":"Los resultados provienen de PokéAPI; si la consulta falla se pide un CSV real exportado previamente."}
    if st.checkbox("Revelar respuesta"):st.info(answers[q])
    with st.form("practica"):
        answer=st.radio("¿Qué función permite seleccionar varios tipos?",["st.metric","st.multiselect","st.title"],index=None)
        personal=st.text_area("Explica en tus palabras qué ocurre al cambiar un filtro")
        submitted=st.form_submit_button("Comprobar")
    if submitted:
        if answer=="st.multiselect":st.success("Correcto: multiselect permite elegir varias opciones.")
        else:st.error("Correcta: st.multiselect.")
        if personal.strip():st.info("Ahora demuéstralo en vivo cambiando el filtro de ataque mínimo.")
    st.feedback("thumbs")
st.divider()
st.caption("PokéLab Analytics · Solemne 3 · Martín Vásquez y Lizandro Delgado · Fuente: PokéAPI")
