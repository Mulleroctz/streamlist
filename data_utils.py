"""Carga y análisis de PokéAPI para la Solemne 3."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import requests

API = "https://pokeapi.co/api/v2/pokemon"
NAMES = {"hp":"PS", "attack":"Ataque", "defense":"Defensa", "special-attack":"Ataque especial", "special-defense":"Defensa especial", "speed":"Velocidad"}
STATS = list(NAMES.values())
# Traducciones de los 18 tipos oficiales al español.
TYPE_ES = {
    "normal":"Normal", "fire":"Fuego", "water":"Agua", "electric":"Eléctrico",
    "grass":"Planta", "ice":"Hielo", "fighting":"Lucha", "poison":"Veneno",
    "ground":"Tierra", "flying":"Volador", "psychic":"Psíquico", "bug":"Bicho",
    "rock":"Roca", "ghost":"Fantasma", "dragon":"Dragón", "dark":"Siniestro",
    "steel":"Acero", "fairy":"Hada"
}

def translated_ability(slug):
    """Nombre oficial en español, consultado en PokéAPI. Sin inventar traducciones."""
    try:
        r=requests.get(f"https://pokeapi.co/api/v2/ability/{slug}/",timeout=12)
        r.raise_for_status()
        names=r.json().get("names",[])
        return slug, next((row["name"] for row in names if row["language"]["name"]=="es"),
                          "Traducción no disponible")
    except (requests.RequestException,ValueError,KeyError):
        return slug,"Traducción no disponible"

# Debut de videojuegos por generación, no fecha individual del Pokémon.
GENERATIONS = [(151, 1, 1996), (251, 2, 1999), (386, 3, 2002),
               (493, 4, 2006), (649, 5, 2010), (721, 6, 2013),
               (809, 7, 2016), (905, 8, 2019), (1025, 9, 2022)]

def generation_for_id(pokemon_id):
    for last_id, generation, year in GENERATIONS:
        if pokemon_id <= last_id:
            return generation, year
    return None, None

def parse_pokemon(p):
    tipos = sorted(p["types"], key=lambda v:v["slot"])
    t = [TYPE_ES.get(v["type"]["name"],"Tipo no disponible") for v in tipos]
    d = {"ID":int(p["id"]), "Nombre":p["name"].replace("-"," ").title(),
         "Tipo principal":t[0] if t else "", "Tipo secundario":t[1] if len(t)>1 else "",
         "Tipos":", ".join(t), "Habilidades":", ".join(v["ability"]["name"] for v in p["abilities"]),
         "Altura (m)":p["height"]/10, "Peso (kg)":p["weight"]/10,
         "Imagen":((p.get("sprites") or {}).get("other") or {}).get("official-artwork",{}).get("front_default") or ""}
    stat = {v["stat"]["name"]:v["base_stat"] for v in p["stats"]}
    generation, year = generation_for_id(d["ID"])
    d["Generación"] = generation
    d["Año debut generación"] = year
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
    for c,idx in [("Generación",0),("Año debut generación",1)]:
        if c not in df.columns:df[c]=df["ID"].apply(lambda v: generation_for_id(int(v))[idx] if pd.notna(v) else None)
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
    # Traducción de nombres de habilidades usando el campo names[language=es] de la API.
    slugs=sorted({name.strip() for row in rows for name in row["Habilidades"].split(",") if name.strip()})
    with ThreadPoolExecutor(max_workers=12) as pool:
        translations=dict(pool.map(translated_ability,slugs))
    for row in rows:
        row["Habilidades"]=", ".join(translations.get(name.strip(),"Traducción no disponible")
                                     for name in row["Habilidades"].split(",") if name.strip())
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
