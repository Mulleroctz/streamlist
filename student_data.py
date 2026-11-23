"""Datos UCI Student Performance; dos materias sin combinar alumnos idénticos."""
import io
import zipfile
import pandas as pd
import requests

SOURCE="https://archive.ics.uci.edu/static/public/320/student+performance.zip"
SOURCE_PAGE="https://archive.ics.uci.edu/dataset/320/student+performance"
FIELDS=["school","sex","age","address","studytime","failures","schoolsup","famsup","internet","activities","higher","absences","G1","G2","G3","health","goout","traveltime"]
LABELS={"GP":"Gabriel Pereira","MS":"Mousinho da Silveira","F":"Mujer","M":"Hombre"}
STUDY={1:"< 2 h",2:"2–5 h",3:"5–10 h",4:"> 10 h"}

def parse_csv(data,subject):
    df=pd.read_csv(io.BytesIO(data),sep=";")
    missing=[c for c in FIELDS if c not in df.columns]
    if missing: raise ValueError(f"Faltan columnas: {', '.join(missing)}")
    df=df.drop_duplicates().copy()
    numeric=["age","studytime","failures","absences","G1","G2","G3","health","goout","traveltime"]
    for c in numeric:df[c]=pd.to_numeric(df[c],errors="coerce")
    df=df.dropna(subset=["G3","studytime","absences","age"])
    df["Materia"]=subject
    df["Sexo"]=df["sex"].map(LABELS).fillna("No informado")
    df["Centro"]=df["school"].map(LABELS).fillna(df["school"])
    df["Estudio semanal"]=df["studytime"].map(STUDY)
    df["Nota final"]=df["G3"]
    df["Ausencias"]=df["absences"]
    df["Edad"]=df["age"]
    df["Aprobación (≥10/20)"]=df["G3"].ge(10)
    df["Apoyo escolar"]=df["schoolsup"].map({"yes":"Sí","no":"No"})
    df["Internet"]=df["internet"].map({"yes":"Sí","no":"No"})
    return df

def extract_files(raw):
    archive=zipfile.ZipFile(io.BytesIO(raw))
    output={}
    for name in archive.namelist():
        low=name.lower()
        if low.endswith(("student-mat.csv","student-por.csv")):
            output["Matemáticas" if low.endswith("student-mat.csv") else "Portugués"]=archive.read(name)
        elif low.endswith(".zip"):
            try:output.update(extract_files(archive.read(name)))
            except (zipfile.BadZipFile,ValueError):pass
    return output

def load_uci():
    resp=requests.get(SOURCE,timeout=35,headers={"User-Agent":"StudentInsight-Academic-Dashboard/1.0"})
    resp.raise_for_status()
    files=extract_files(resp.content)
    if not files:raise ValueError("El ZIP oficial no contiene los CSV esperados.")
    pieces=[parse_csv(data,subject) for subject,data in files.items()]
    return pd.concat(pieces,ignore_index=True)

def filter_rows(df,subjects,schools,sexes,study,age,absmax,internet,support):
    d=df.copy()
    if subjects:d=d[d["Materia"].isin(subjects)]
    if schools:d=d[d["Centro"].isin(schools)]
    if sexes:d=d[d["Sexo"].isin(sexes)]
    if study:d=d[d["Estudio semanal"].isin(study)]
    d=d[d["Edad"].between(*age)&d["Ausencias"].le(absmax)]
    if internet!="Todos":d=d[d["Internet"]==internet]
    if support!="Todos":d=d[d["Apoyo escolar"]==support]
    return d

def describe(df):
    if df.empty:return ["No hay registros con estos filtros."]
    statements=[f"Promedio final de la selección: {df['Nota final'].mean():.2f} sobre 20.",
                f"Porcentaje con nota ≥10: {df['Aprobación (≥10/20)'].mean()*100:.1f}%.",
                f"Media de ausencias registradas: {df['Ausencias'].mean():.1f}."]
    grouped=df.groupby("Estudio semanal",observed=True)["Nota final"].agg(["mean","size"])
    if not grouped.empty:
        g=grouped[grouped["size"]>=5]
        if not g.empty:statements.append(f"Entre categorías con al menos 5 registros, el promedio más alto aparece en {g['mean'].idxmax()} de estudio semanal ({g['mean'].max():.2f}/20).")
    return statements
