"""Datos reales FreeToGame: carga, limpieza, análisis y filtros."""
import pandas as pd
import requests

URL="https://www.freetogame.com/api/games"
COLS=["id","title","thumbnail","short_description","game_url","genre","platform","publisher","developer","release_date","freetogame_profile_url"]

def normalize(records):
    df=pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame(columns=COLS+["year","month"])
    for c in COLS:
        if c not in df: df[c]=pd.NA
    df=df[COLS].drop_duplicates(subset="id").copy()
    df["id"]=pd.to_numeric(df["id"],errors="coerce")
    df=df.dropna(subset=["id","title","genre","platform"])
    for c in ["title","genre","platform","publisher","developer","short_description","thumbnail","game_url","freetogame_profile_url"]:
        df[c]=df[c].fillna("No informado").astype(str).str.strip()
    df["release_date"]=pd.to_datetime(df["release_date"],errors="coerce")
    df["year"]=df["release_date"].dt.year.astype("Int64")
    df["month"]=df["release_date"].dt.month.astype("Int64")
    return df.sort_values("title").reset_index(drop=True)

def load_games():
    r=requests.get(URL,timeout=35,headers={"User-Agent":"GameScope-Universidad-San-Sebastian/1.0"})
    r.raise_for_status()
    data=r.json()
    if not isinstance(data,list):raise ValueError("La API no devolvió una lista.")
    return normalize(data)

def filter_games(df,genres,platforms,search,year_range,publisher,developer):
    out=df.copy()
    if genres:out=out[out["genre"].isin(genres)]
    if platforms:out=out[out["platform"].isin(platforms)]
    if search:out=out[out["title"].str.contains(search.strip(),case=False,regex=False)]
    if publisher:out=out[out["publisher"].isin(publisher)]
    if developer:out=out[out["developer"].isin(developer)]
    if year_range:
        out=out[out["year"].between(year_range[0],year_range[1],inclusive="both")]
    return out

def insights(df):
    if df.empty:return ["Sin juegos para esta selección."]
    genre=df["genre"].value_counts()
    platform=df["platform"].value_counts()
    dated=df.dropna(subset=["year"])
    findings=[f"El género con más títulos en la selección es {genre.index[0]} ({genre.iloc[0]} juegos).",
              f"La plataforma más frecuente es {platform.index[0]} ({platform.iloc[0]} juegos)."]
    if not dated.empty:
        years=dated["year"].value_counts()
        findings.append(f"El año con más lanzamientos registrados es {int(years.idxmax())} ({years.max()} juegos).")
    return findings
