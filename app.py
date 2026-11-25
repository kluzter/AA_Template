"""App de ejemplo. Reemplázala por la de tu equipo (conserva el nombre app.py)."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Ruta relativa a ESTE archivo: funciona en tu compu, en la de tu equipo y en la nube.
BASE = Path(__file__).parent
DATOS = BASE / "data" / "ventas.csv"

st.set_page_config(page_title="Ventas por CEDIS", layout="wide")


@st.cache_data
def cargar_datos(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta, parse_dates=["fecha"])


df = cargar_datos(DATOS)

st.title("Ventas por CEDIS")
st.caption("Plantilla de equipo. Datos sintéticos.")

cedis = st.sidebar.multiselect(
    "CEDIS", sorted(df["cedis"].unique()), default=sorted(df["cedis"].unique())
)
vista = df[df["cedis"].isin(cedis)]

if vista.empty:
    st.warning("Selecciona al menos un CEDIS.")
    st.stop()

c1, c2 = st.columns(2)
c1.metric("Ingreso total", f"${vista['ingreso'].sum():,.0f}")
c2.metric("Unidades", f"{vista['unidades'].sum():,.0f}")

semanal = vista.groupby(["fecha", "cedis"], as_index=False)["ingreso"].sum()
st.plotly_chart(px.line(semanal, x="fecha", y="ingreso", color="cedis"))

top = vista.groupby("producto", as_index=False)["ingreso"].sum().sort_values("ingreso")
st.plotly_chart(px.bar(top, x="ingreso", y="producto", orientation="h"))
