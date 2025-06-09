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
df = pd.read_csv("cleaned_mosques.csv")

# Загружаем помесячную активность мечетей
activity_df = pd.read_csv("Ghost Town. Belgrade Mosques - mosques_years.csv")

# Сопоставление событий и прозрачности
opacity_map = {
    "Established": 1.0,
    "Renovated": 1.0,
    "Damaged": 0.7,
    "Changed function": 0.5,
    "Abandoned": 0.2,
    "Demolished": 0.0,
}

# Заголовок
st.title("Belgrade Mosques: Historical Map")
st.markdown("Select a year below to see which mosques existed at that time.")

# Ползунок времени
year = st.slider("Year", min_value=int(df['decade_built'].min()), max_value=int(df['decade_demolished'].max()), value=1700, step=10)

# Фильтрация мечетей по году существования
mask = (df['decade_built'] <= year) & ((df['decade_demolished'].isna()) | (df['decade_demolished'] >= year))
filtered_df = df[mask].copy()

# Выбор мечети (по умолчанию ни одна не выбрана)
if "selected_mosque" not in st.session_state:
    st.session_state.selected_mosque = None

selected_mosque = st.session_state.selected_mosque

# Назначаем прозрачность на основе события в конкретный год
filtered_df = pd.merge(
    filtered_df,
    activity_df[activity_df["decade"] == year][["mosque_name", "what_happend"]],
    on="mosque_name",
    how="left"
)

filtered_df["opacity"] = filtered_df["what_happend"].map(opacity_map).fillna(1.0)

# Назначаем цвет с учётом прозрачности
filtered_df["color"] = filtered_df.apply(
    lambda row: SELECTED_POINT_COLOR if row.mosque_name == selected_mosque
    else [DEFAULT_POINT_COLOR[0], DEFAULT_POINT_COLOR[1], DEFAULT_POINT_COLOR[2], int(row.opacity * 255)],
    axis=1
)


# Карта с уменьшенными точками и кастомным tooltip
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v10',
    initial_view_state=pdk.ViewState(
        latitude=44.8185,
        longitude=20.4605,
        zoom=12,
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
        <div style='font-family: Inter; background-color: #ECEEED; color: #343332; padding: 5px; font-size: 8px; max-width: 150px;'>
            <b>{mosque_name}</b>
        </div>
        """,
        "style": {
            "backgroundColor": "#ECEEED",
            "color": "#343332",
            "fontFamily": "Inter",
            "fontSize": "10px"
        }
    }
))

st.markdown("### Mosques in the selected period:")
columns = st.columns(3)

for idx, row in enumerate(filtered_df.itertuples()):
    col = columns[idx % 3]
    is_selected = row.mosque_name == selected_mosque
    css_class = "card selected" if is_selected else "card"

    with col:
        with st.form(key=f"form_{row.mosque_name}"):
            mosque_block = f"""
            <div class='{css_class}'>
                <h4>{row.mosque_name}</h4>
                {'<img src="' + row.image_url + '" width="100%">' if pd.notna(row.image_url) else ''}
                <p><b>{row.original_name}</b><br>{int(row.decade_built)} - {int(row.decade_demolished) if pd.notna(row.decade_demolished) else 'present'}</p>
            </div>
            """
            st.markdown(mosque_block, unsafe_allow_html=True)
            if st.form_submit_button("double click", use_container_width=True):
                st.session_state.selected_mosque = row.mosque_name
