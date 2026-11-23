"""GameScope Analytics | Proyecto académico Streamlit de Martín Vásquez y Lizandro Delgado."""
import html
import pandas as pd
import plotly.express as px
import streamlit as st
from games_data import load_games,normalize,filter_games,insights

st.set_page_config(page_title="GameScope | Analytics",page_icon="🎮",layout="wide",initial_sidebar_state="expanded")
st.markdown("""<style>
.stApp{background:linear-gradient(130deg,#0a1020,#0b1323 47%,#101827);color:#e9effe}
.block-container{max-width:1440px;padding-top:1.25rem}
h1,h2,h3{letter-spacing:-.025em}
[data-testid="stMetric"]{background:#152139;border:1px solid #2c3954;border-radius:16px;padding:18px}
[data-testid="stSidebar"]{background:#111b30}
div[data-testid="stTabs"] button{font-size:1.03rem}
.hero{padding:28px 34px;background:linear-gradient(110deg,#402b83,#203b8b 55%,#105c81);border:1px solid #475b99;border-radius:22px;margin-bottom:18px}
.hero h1{font-size:2.4rem;color:white;margin:0}
.hero p{color:#dbe6ff;margin-bottom:0}
.game-card{background:#142038;border:1px solid #263750;border-radius:15px;overflow:hidden;margin-bottom:12px;min-height:350px}
.game-card img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover}
.game-body{padding:13px}
.game-title{font-weight:800;font-size:1.04rem;color:#f0f4ff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.game-meta{font-size:.82rem;color:#98b5df;margin-top:5px}
.game-desc{font-size:.8rem;color:#c9d5e8;line-height:1.35;height:48px;overflow:hidden;margin:10px 0}
.game-btn{color:#8cd7ff!important;text-decoration:none;font-weight:700}
.small-note{color:#b0bdd7}
</style>""",unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>🎮 GameScope <span style="color:#a5ecff">Analytics</span></h1><p>Explora y analiza videojuegos gratuitos con datos reales · Martín Vásquez & Lizandro Delgado</p></div>',unsafe_allow_html=True)
st.caption("Fuente obligatoria: [FreeToGame.com](https://www.freetogame.com/) · [Documentación API](https://www.freetogame.com/api-doc). Los datos representan el catálogo disponible, no todas las ventas, descargas ni jugadores del mundo.")

@st.cache_data(ttl=21600,show_spinner=False)
def get_games():
    return load_games()

with st.sidebar:
    st.title("🎛️ Centro de control")
    st.markdown("Explora el catálogo con filtros que cambian todos los resultados.")
    if st.button("↻ Actualizar desde la API",use_container_width=True):
        get_games.clear()
        st.rerun()

try:
    with st.spinner("Cargando catálogo real de videojuegos…"):
        raw=get_games()
    source="API FreeToGame"
except Exception as ex:
    st.warning(f"Sin conexión con FreeToGame: {ex}")
    st.info("Sube un CSV real exportado previamente desde la pestaña Datos para continuar; no se crean juegos ficticios.")
    upload=st.file_uploader("CSV real de respaldo",type="csv")
    if upload is None:st.stop()
    raw=normalize(pd.read_csv(upload).to_dict("records"))
    source="CSV real de respaldo"
if raw.empty:st.error("La fuente no entregó juegos utilizables.");st.stop()

genres=sorted(raw["genre"].unique())
platforms=sorted(raw["platform"].unique())
publishers=sorted(raw["publisher"].unique())
developers=sorted(raw["developer"].unique())
years=raw["year"].dropna()
low=int(years.min()) if not years.empty else 2000
high=int(years.max()) if not years.empty else 2026

with st.sidebar:
    query=st.text_input("Buscar por título",placeholder="Ej.: Fortnite")
    genre=st.multiselect("Géneros",genres)
    platform=st.multiselect("Plataformas",platforms)
    year_filter=st.slider("Años de lanzamiento",min_value=low,max_value=high,value=(low,high))
    pub=st.multiselect("Editor / publisher",publishers)
    dev=st.multiselect("Desarrollador",developers)
    sort=st.selectbox("Ordenar catálogo",["Título A–Z","Más recientes","Más antiguos","Género"])
    limit=st.select_slider("Tarjetas por página",options=[6,9,12,18],value=9)
    show_desc=st.checkbox("Mostrar descripción de juegos",value=True)
    show_images=st.toggle("Mostrar portadas",value=True)

data=filter_games(raw,genre,platform,query,year_filter,pub,dev)
if sort=="Más recientes":data=data.sort_values("release_date",ascending=False,na_position="last")
elif sort=="Más antiguos":data=data.sort_values("release_date",na_position="last")
elif sort=="Género":data=data.sort_values(["genre","title"])
else:data=data.sort_values("title")

st.caption(f"✅ Origen: {source} · {len(raw):,} juegos recibidos · {len(data):,} cumplen los filtros")
kpis=st.columns(5)
dated=data.dropna(subset=["year"])
values=[len(data),data["genre"].nunique(),data["platform"].nunique(),data["developer"].nunique(),int(dated["year"].max()) if len(dated) else "—"]
for c,l,v in zip(kpis,["🎮 Juegos","🧩 Géneros","💻 Plataformas","🏢 Desarrolladores","🗓️ Último año"],values):
    c.metric(l,str(v))

t_catalog,t_trends,t_compare,t_data,t_defense=st.tabs(["🎮 Catálogo","📊 Analítica","🧠 Comparador","🗂️ Datos y calidad","🎓 Laboratorio de defensa"])

with t_catalog:
    st.subheader("Descubre los juegos")
    if data.empty:st.warning("No hay coincidencias. Cambia los filtros de la izquierda.")
    else:
        pages=max(1,(len(data)+limit-1)//limit)
        page=st.number_input("Página",min_value=1,max_value=pages,value=1)
        cards=data.iloc[(page-1)*limit:page*limit]
        for start in range(0,len(cards),3):
            columns=st.columns(3)
            for c,(_,game) in zip(columns,cards.iloc[start:start+3].iterrows()):
                title=html.escape(str(game["title"]))
                meta=html.escape(f'{game["genre"]} · {game["platform"]}')
                desc=html.escape(str(game["short_description"])[:115])
                url=str(game["freetogame_profile_url"])
                img=str(game["thumbnail"])
                with c:
                    picture=f'<img loading="lazy" src="{html.escape(img,quote=True)}" alt="{title}">' if show_images and img.startswith("https://") else ""
                    description=f'<div class="game-desc">{desc}</div>' if show_desc else ""
                    profile=f'<a class="game-btn" href="{html.escape(url,quote=True)}" target="_blank" rel="noopener">Ver ficha ↗</a>' if url.startswith("https://www.freetogame.com/") else ""
                    st.markdown(f'<div class="game-card">{picture}<div class="game-body"><div class="game-title">{title}</div><div class="game-meta">{meta}</div>{description}{profile}</div></div>',unsafe_allow_html=True)
        st.info("Pregunta de investigación: ¿qué géneros y plataformas predominan en el catálogo después de aplicar filtros?")

with t_trends:
    if data.empty:st.warning("Sin juegos para analizar.")
    else:
        st.subheader("1 · ¿Qué géneros están más representados?")
        top=st.slider("Número de géneros",5,min(25,max(5,data["genre"].nunique())),min(10,max(5,data["genre"].nunique())))
        g=data["genre"].value_counts().head(top).rename_axis("Género").reset_index(name="Juegos")
        st.plotly_chart(px.bar(g,x="Juegos",y="Género",orientation="h",color="Juegos",color_continuous_scale="Tealgrn",title="Cantidad de juegos por género").update_layout(yaxis={"categoryorder":"total ascending"}),use_container_width=True)
        st.subheader("2 · ¿Cómo se reparte el catálogo por plataforma?")
        p=data["platform"].value_counts().rename_axis("Plataforma").reset_index(name="Juegos")
        st.plotly_chart(px.pie(p,names="Plataforma",values="Juegos",hole=.56,title="Distribución por plataforma"),use_container_width=True)
        st.subheader("3 · ¿Cómo cambiaron los lanzamientos a lo largo del tiempo?")
        time=data.dropna(subset=["year"]).groupby("year",as_index=False).size().rename(columns={"size":"Juegos"})
        if not time.empty:
            time["Año"]=time["year"].astype(int)
            st.plotly_chart(px.line(time,x="Año",y="Juegos",markers=True,title="Lanzamientos registrados por año"),use_container_width=True)
        st.subheader("4 · ¿Qué plataformas se relacionan con cada género?")
        cross=pd.crosstab(data["genre"],data["platform"])
        st.plotly_chart(px.imshow(cross,labels={"x":"Plataforma","y":"Género","color":"Juegos"},aspect="auto",title="Género × plataforma"),use_container_width=True)
        st.subheader("Hallazgos calculados")
        for finding in insights(data):st.write("• "+finding)
        st.caption("Las cifras describen registros del catálogo; no representan popularidad, usuarios o ventas.")

with t_compare:
    st.subheader("Comparador interactivo de géneros")
    if data.empty:st.info("Selecciona filtros menos restrictivos.")
    else:
        selected=st.multiselect("Selecciona hasta 4 géneros para comparar",genres,default=list(data["genre"].value_counts().head(2).index),max_selections=4)
        measure=st.radio("¿Qué deseas comparar?",["Número de juegos","Desarrolladores distintos","Editores distintos"],horizontal=True)
        if selected:
            grouped=data[data["genre"].isin(selected)].groupby("genre").agg(Juegos=("id","count"),Desarrolladores=("developer","nunique"),Editores=("publisher","nunique")).reset_index()
            key={"Número de juegos":"Juegos","Desarrolladores distintos":"Desarrolladores","Editores distintos":"Editores"}[measure]
            st.plotly_chart(px.bar(grouped,x="genre",y=key,color="genre",title=f"{measure} por género"),use_container_width=True)
            st.dataframe(grouped,hide_index=True,use_container_width=True)
        st.subheader("5 · ¿Qué desarrolladores tienen más títulos?")
        n=st.slider("Top de desarrolladores",3,20,10)
        devcounts=data["developer"].value_counts().head(n).rename_axis("Desarrollador").reset_index(name="Juegos")
        st.plotly_chart(px.bar(devcounts,y="Desarrollador",x="Juegos",orientation="h",title="Desarrolladores con más juegos").update_layout(yaxis={"categoryorder":"total ascending"}),use_container_width=True)

with t_data:
    st.subheader("Tabla interactiva y calidad del DataFrame")
    visible=["title","genre","platform","publisher","developer","release_date","year","short_description"]
    chosen=st.multiselect("Columnas de la tabla",visible,default=visible[:6])
    if chosen:st.dataframe(data[chosen],use_container_width=True,hide_index=True)
    st.download_button("⬇️ Descargar catálogo real en CSV",raw.to_csv(index=False).encode("utf-8-sig"),file_name="freetogame_catalogo_real.csv",mime="text/csv")
    st.download_button("⬇️ Descargar selección filtrada",data.to_csv(index=False).encode("utf-8-sig"),file_name="gamescope_filtrado.csv",mime="text/csv")
    quality=pd.DataFrame({"Variable":raw.columns,"Tipo de dato":[str(raw[c].dtype) for c in raw.columns],"Faltantes":[int(raw[c].isna().sum()) for c in raw.columns]})
    st.dataframe(quality,use_container_width=True,hide_index=True)
    st.metric("IDs duplicados tras limpieza",int(raw["id"].duplicated().sum()))
    with st.expander("Explicación de la preparación de datos"):
        st.markdown("Se utiliza **requests.get** para solicitar JSON. Después **pandas.DataFrame** organiza las filas; **drop_duplicates** elimina IDs repetidos; **to_datetime** convierte fechas; **groupby** y **value_counts** calculan las estadísticas. La función **filter_games** conecta los controles con todos los resultados.")

with t_defense:
    st.subheader("🎓 Entrenamiento para la defensa oral")
    st.write("Aprende una operación por vez: **API → DataFrame → limpieza → filtros → indicadores → gráficos**.")
    question=st.selectbox("Pregunta de la profesora",["¿De dónde salen los datos?","¿Para qué sirve DataFrame?","¿Qué hace un filtro?","¿Por qué usamos barras?","¿Para qué sirve el gráfico de línea?","¿Por qué no contamos jugadores?"])
    answers={
        "¿De dónde salen los datos?":"De FreeToGame. requests.get descarga JSON y pandas lo organiza en un DataFrame.",
        "¿Para qué sirve DataFrame?":"Permite almacenar registros en filas y variables en columnas y analizarlos con pandas.",
        "¿Qué hace un filtro?":"Crea un subconjunto de filas que cumplen condiciones. Los gráficos y métricas se recalculan.",
        "¿Por qué usamos barras?":"Para comparar cantidades de juegos entre géneros o desarrolladores.",
        "¿Para qué sirve el gráfico de línea?":"Para observar cómo varía el número de lanzamientos por año.",
        "¿Por qué no contamos jugadores?":"La API no incluye usuarios activos ni descargas; inventarlos sería incorrecto."}
    if st.checkbox("Mostrar respuesta breve"):st.success(answers[question])
    with st.form("practice"):
        choice=st.radio("¿Qué función agrupa registros por género?",["requests.get()","groupby()","st.title()"],index=None)
        explanation=st.text_area("Explica con tus palabras qué ocurre al filtrar por plataforma")
        sent=st.form_submit_button("Comprobar")
        if sent:
            if choice=="groupby()":st.success("Correcto: groupby permite agrupar filas.")
            else:st.error("La respuesta correcta es groupby().")
            if explanation.strip():st.info("Ahora intenta mostrarlo en el dashboard cambiando PC / navegador.")
    st.feedback("thumbs")
st.divider()
st.caption("Proyecto académico · Martín Vásquez y Lizandro Delgado · Universidad San Sebastián · Fuente: FreeToGame.com")
