import streamlit as st
import pandas as pd
import pydeck as pdk

# Загружаем данные
df = pd.read_csv("cleaned_mosques.csv")

# Заголовок
st.title("Мечети Белграда: Историческая карта")
st.markdown("Выберите год ниже, чтобы увидеть мечети, существовавшие в это время.")

# Ползунок времени
year = st.slider("Год", min_value=int(df['decade_built'].min()), max_value=int(df['decade_demolished'].max()), value=1700, step=10)

# Фильтрация мечетей по году существования
mask = (df['decade_built'] <= year) & ((df['decade_demolished'].isna()) | (df['decade_demolished'] >= year))
filtered_df = df[mask]

# Карта
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=44.82,
        longitude=20.46,
        zoom=12,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=filtered_df,
            get_position='[longitude, latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=100,
            pickable=True,
        ),
    ],
    tooltip={"text": "{mosque_name}"}
))

# Выбор мечети по клику (эмуляция через selectbox)
selected = st.selectbox(
    "Выберите мечеть из списка, чтобы увидеть подробности:",
    options=filtered_df['mosque_name'].tolist()
)

mosque_info = filtered_df[filtered_df['mosque_name'] == selected].iloc[0]

st.markdown(f"### {mosque_info['mosque_name']}")
st.markdown(f"*{mosque_info['original_name']}*")
st.markdown(f"**Годы:** {int(mosque_info['decade_built'])} - {int(mosque_info['decade_demolished']) if pd.notna(mosque_info['decade_demolished']) else 'настоящее время'}")

if pd.notna(mosque_info['image_url']):
    st.image(mosque_info['image_url'], use_column_width=True)

if pd.notna(mosque_info['about']):
    st.markdown(mosque_info['about'])
