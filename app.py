import streamlit as st
import pandas as pd
import pydeck as pdk
import os

# Устанавливаем Mapbox Access Token
os.environ["MAPBOX_ACCESS_TOKEN"] = "вставь_сюда_свой_mapbox_token"

# === Цветовая схема и параметры ===
PAGE_BG_COLOR = "#CAD2D3"
PAGE_TEXT_COLOR = "#343332"
HIGHLIGHT_COLOR = "#FF649A"
CARD_COLOR = "#FFFFFF"
CARD_TEXT_COLOR = "#343332"
DEFAULT_POINT_COLOR = [255, 177, 100, 200]  # #FFB164
SELECTED_POINT_COLOR = [255, 100, 154, 200]  # #FF649A
TEXT_FONT = "Inter"

# Загружаем стили из внешнего файла
with open("styles.html") as f:
    st.markdown(f.read(), unsafe_allow_html=True)

# Загружаем данные
df = pd.read_csv("cleaned_mosques.csv")

# Заголовок
st.title("Мечети Белграда: Историческая карта")
st.markdown("Выберите год ниже, чтобы увидеть мечети, существовавшиеся в это время.")

# Ползунок времени
year = st.slider("Год", min_value=int(df['decade_built'].min()), max_value=int(df['decade_demolished'].max()), value=1700, step=10)

# Фильтрация мечетей по году существования
mask = (df['decade_built'] <= year) & ((df['decade_demolished'].isna()) | (df['decade_demolished'] >= year))
filtered_df = df[mask].copy()

# Выбор мечети (по умолчанию ни одна не выбрана)
if "selected_mosque" not in st.session_state:
    st.session_state.selected_mosque = None

selected_mosque = st.session_state.selected_mosque

# Добавляем столбец цвета точек
filtered_df["color"] = filtered_df["mosque_name"].apply(
    lambda name: SELECTED_POINT_COLOR if name == selected_mosque else DEFAULT_POINT_COLOR
)

# Карта с уменьшенными точками и кастомным tooltip
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/streets-v12',
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
            get_radius=50,  # уменьшено в 3 раза
            pickable=True,
        ),
    ],
    tooltip={
        "html": """
        <div style='font-family: Inter; background-color: #ECEEED; color: #343332; padding: 5px; font-size: 10px;'>
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

st.markdown("### Мечети в выбранный период:")
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
                <p><b>{row.original_name}</b><br>
                {int(row.decade_built)} - {int(row.decade_demolished) if pd.notna(row.decade_demolished) else 'настоящее время'}</p>
            </div>
            """
            st.markdown(mosque_block, unsafe_allow_html=True)
            if st.form_submit_button("double click", use_container_width=True):
                st.session_state.selected_mosque = row.mosque_name
