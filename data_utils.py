"""Carga y análisis de PokéAPI para la Solemne 3."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import requests

API = "https://pokeapi.co/api/v2/pokemon"
NAMES = {"hp":"PS", "attack":"Ataque", "defense":"Defensa", "special-attack":"Ataque especial", "special-defense":"Defensa especial", "speed":"Velocidad"}
STATS = list(NAMES.values())

def parse_pokemon(p):
    tipos = sorted(p["types"], key=lambda v:v["slot"])
    t = [v["type"]["name"].title() for v in tipos]
    d = {"ID":int(p["id"]), "Nombre":p["name"].replace("-"," ").title(),
         "Tipo principal":t[0] if t else "", "Tipo secundario":t[1] if len(t)>1 else "",
         "Tipos":", ".join(t), "Habilidades":", ".join(v["ability"]["name"] for v in p["abilities"]),
         "Altura (m)":p["height"]/10, "Peso (kg)":p["weight"]/10,
         "Imagen":((p.get("sprites") or {}).get("other") or {}).get("official-artwork",{}).get("front_default") or ""}
    stat = {v["stat"]["name"]:v["base_stat"] for v in p["stats"]}
    d.update({col:stat.get(raw) for raw,col in NAMES.items()})
    return d

def fetch_one(i):
    r=requests.get(f"{API}/{i}",timeout=18)
    r.raise_for_status()
    return parse_pokemon(r.json())

def clean(df):
    df=df.copy().drop_duplicates(subset="ID")
    for c in ["ID",*STATS,"Altura (m)","Peso (kg)"]:
        df[c]=pd.to_numeric(df[c],errors="coerce")
    df=df.dropna(subset=["ID","Nombre","Tipo principal"])
    for c in ["Tipos","Tipo secundario","Imagen","Habilidades"]:
        df[c]=df[c].fillna("")
    df["Total"]=df[STATS].sum(axis=1,min_count=6)
    return df.sort_values("ID").reset_index(drop=True)

def load(n):
    rows,failed=[],[]
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures={pool.submit(fetch_one,i):i for i in range(1,n+1)}
        for fut in as_completed(futures):
            try: rows.append(fut.result())
            except (requests.RequestException,ValueError,KeyError,TypeError) as e: failed.append(futures[fut])
    if not rows: raise RuntimeError("No se recibieron datos de PokéAPI.")
    return clean(pd.DataFrame(rows)),sorted(failed)

def filter_data(df,types,search,attack,speed,dual,weight):
    out=df.copy()
    if types: out=out[out["Tipos"].apply(lambda x:any(t in x.split(", ") for t in types))]
    if search.strip():out=out[out["Nombre"].str.contains(search.strip(),case=False,regex=False)]
    out=out[(out["Ataque"]>=attack)&(out["Velocidad"]>=speed)&(out["Peso (kg)"]<=weight)]
    if dual:out=out[out["Tipo secundario"].str.len()>0]
    return out

def findings(df):
    if df.empty:return ["No hay datos con estos filtros."]
    counts=df["Tipo principal"].value_counts()
    texts=[f"En {len(df)} registros, el tipo principal más frecuente es {counts.index[0]} ({counts.iloc[0]})."]
    valid=df.dropna(subset=["Total"])
    if not valid.empty:
        best=valid.nlargest(1,"Total").iloc[0]
        texts.append(f"El mayor total de seis estadísticas base es {best['Nombre']}: {best['Total']:.0f} puntos.")
    texts.append(f"El ataque promedio es {df['Ataque'].mean():.1f} puntos base.")
    return texts
