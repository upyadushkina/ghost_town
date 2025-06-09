import streamlit as st
import pandas as pd
import pydeck as pdk
import os

# Устанавливаем Mapbox Access Token
os.environ["MAPBOX_ACCESS_TOKEN"] = "вставь_сюда_свой_mapbox_token"

# === Цветовая схема и параметры ===
PAGE_BG_COLOR = "#191A1A"
PAGE_TEXT_COLOR = "#FFFFFF"
HIGHLIGHT_COLOR = "#FF649A"
CARD_COLOR = "#FFFFFF"
CARD_TEXT_COLOR = "#191A1A"
DEFAULT_POINT_COLOR = [25, 26, 26, 200]  # #191A1A
SELECTED_POINT_COLOR = [255, 75, 75, 200]  # #FF4B4B
TEXT_FONT = "Inter"

# Загружаем стили из внешнего файла
with open("styles.html") as f:
    st.markdown(f.read(), unsafe_allow_html=True)

# Загружаем данные мечетей (координаты и периоды)
df = pd.read_csv("mosque_about.csv")
activity_df = pd.read_csv("mosques_years.csv")

opacity_map = {
    "Established": 1.0,
    "Renovated": 1.0,
    "Damaged": 0.7,
    "Changed function": 0.5,
    "Abandoned": 0.2,
    "Demolished": 0.0,
}

st.image("heading.png", use_container_width=True)
year = st.slider("", min_value=int(df['decade_built'].min()), max_value=2025, value=1700, step=10)

mask = (df['decade_built'] <= year) & ((df['decade_demolished'].isna()) | (df['decade_demolished'] >= year))
filtered_df = df[mask].copy()

if "selected_mosque" not in st.session_state:
    st.session_state.selected_mosque = None

selected_mosque = st.session_state.selected_mosque

filtered_df = pd.merge(
    filtered_df,
    activity_df[activity_df["decade"] == year][["mosque_name", "what_happend"]],
    on="mosque_name",
    how="left"
)

filtered_df["opacity"] = filtered_df["what_happend"].map(opacity_map).fillna(1.0)

filtered_df["color"] = filtered_df.apply(
    lambda row: SELECTED_POINT_COLOR if row.mosque_name == selected_mosque
    else [DEFAULT_POINT_COLOR[0], DEFAULT_POINT_COLOR[1], DEFAULT_POINT_COLOR[2], int(row.opacity * 255)],
    axis=1
)

filtered_df["what_happend"] = filtered_df["what_happend"].fillna("")

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v10',
    initial_view_state=pdk.ViewState(
        latitude=44.8185,
        longitude=20.4605,
        zoom=13.5,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=filtered_df,
            get_position='[longitude, latitude]',
            get_color='color',
            get_radius=50,
            pickable=True,
        ),
    ],
    tooltip={
        "html": """
        <div style='font-family: Inter; background-color: #191A1A; color: #FFFFFF; padding: 5px; font-size: 12px; max-width: 150px;'>
            <b>{mosque_name}</b><br>
            <span style='color: #FF4B4B'>{what_happend}</span>
        </div>
        """,
        "style": {
            "backgroundColor": "#191A1A",
            "color": "#FFFFFF",
            "fontFamily": "Inter",
            "fontSize": "12px"
        }
    }
))

# Галерея карточек мечетей
cols = st.columns(3)
for idx, row in filtered_df.iterrows():
    i = idx % 3
    selected_class = "selected" if row.mosque_name == selected_mosque else ""
    html = f"""
    <div class='card {selected_class}' style='cursor:pointer; position: relative;' onclick="window.location.href='/?mosque={row.mosque_name}'">
        <img src='{row.image_url}' style='width:100%; border-radius:8px;'>
        <div class='tooltip'>{row.description}</div>
        <div style='padding-top:5px;'><b>{row.mosque_name}</b></div>
    </div>
    """
    cols[i].markdown(html, unsafe_allow_html=True)

# Обработка клика по ссылке (грубо, на перезапуск страницы)
m_query = st.query_params.get("mosque")
if m_query:
    st.session_state.selected_mosque = m_query
