import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def fetch_records():
    try:
        r = requests.get(f"{API_URL}/records", timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.RequestException as e:
        return None, str(e)


st.set_page_config(page_title="Дашборд: потребление и цены", layout="wide")
st.title("Дашборд: потребление энергии и цены")

data, error = fetch_records()
if error:
    st.error(f"Не удалось загрузить данные: {error}")
    st.stop()

if not data:
    df = pd.DataFrame(columns=["id", "timestep", "consumption_eur", "consumption_sib", "price_eur", "price_sib"])
else:
    df = pd.DataFrame(data)

st.subheader("Таблица данных")
st.dataframe(df, use_container_width=True)

# График 1 — Потребление по времени
st.subheader("Потребление энергии: Европейская и Азиатская часть")
if not df.empty and "timestep" in df.columns:
    df_plot = df.copy()
    df_plot["timestep"] = pd.to_datetime(df_plot["timestep"], errors="coerce")
    df_plot = df_plot.dropna(subset=["timestep"])
    if not df_plot.empty:
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(x=df_plot["timestep"], y=df_plot["consumption_eur"], name="Европейская часть", mode="lines")
        )
        fig1.add_trace(
            go.Scatter(x=df_plot["timestep"], y=df_plot["consumption_sib"], name="Азиатская часть", mode="lines")
        )
        fig1.update_layout(xaxis_title="Время", yaxis_title="Потребление")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.caption("Нет данных для графика.")
else:
    st.caption("Нет данных для графика.")

# График 2 — Цены по времени
st.subheader("Цены: Европейская и Азиатская часть")
if not df.empty and "timestep" in df.columns:
    df_plot = df.copy()
    df_plot["timestep"] = pd.to_datetime(df_plot["timestep"], errors="coerce")
    df_plot = df_plot.dropna(subset=["timestep"])
    if not df_plot.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_plot["timestep"], y=df_plot["price_eur"], name="Европейская часть", mode="lines"))
        fig2.add_trace(go.Scatter(x=df_plot["timestep"], y=df_plot["price_sib"], name="Азиатская часть", mode="lines"))
        fig2.update_layout(xaxis_title="Время", yaxis_title="Цена")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.caption("Нет данных для графика.")
else:
    st.caption("Нет данных для графика.")

# Форма добавления записи
st.subheader("Добавить запись")
with st.form("add_record"):
    col1, col2 = st.columns(2)
    with col1:
        timestep_input = st.datetime_input("Время (timestep)", value=datetime.now())
        consumption_eur = st.number_input("consumption_eur", min_value=0.0, value=0.0)
        consumption_sib = st.number_input("consumption_sib", min_value=0.0, value=0.0)
    with col2:
        price_eur = st.number_input("price_eur", min_value=0.0, value=0.0)
        price_sib = st.number_input("price_sib", min_value=0.0, value=0.0)
    submit = st.form_submit_button("Добавить")

if submit:
    payload = {
        "timestep": timestep_input.isoformat(),
        "consumption_eur": consumption_eur,
        "consumption_sib": consumption_sib,
        "price_eur": price_eur,
        "price_sib": price_sib,
    }
    try:
        r = requests.post(f"{API_URL}/records", json=payload, timeout=10)
        if r.ok:
            st.success("Запись добавлена.")
            st.rerun()
        else:
            detail = r.json().get("detail", r.text) if r.headers.get("content-type", "").startswith("application/json") else r.text
            st.error(f"Ошибка: {detail}")
    except requests.RequestException as e:
        st.error(f"Ошибка запроса: {e}")

# Удаление по id
st.subheader("Удалить запись")
del_id = st.number_input("ID записи для удаления", min_value=0, value=0, step=1, key="delete_id")
if st.button("Удалить"):
    try:
        r = requests.delete(f"{API_URL}/records/{del_id}", timeout=10)
        if r.status_code == 404:
            st.error("Запись с таким id не найдена")
        elif r.ok:
            st.success("Запись удалена.")
            st.rerun()
        else:
            detail = r.json().get("detail", r.text) if r.headers.get("content-type", "").startswith("application/json") else r.text
            st.error(f"Ошибка: {detail}")
    except requests.RequestException as e:
        st.error(f"Ошибка запроса: {e}")
