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
filtered_df = df[mask].copy()

# Выбор мечети (по умолчанию ни одна не выбрана)
selected_mosque = st.session_state.get("selected_mosque", None)

# Добавляем столбец цвета точек
filtered_df["color"] = filtered_df["mosque_name"].apply(
    lambda name: [0, 0, 255, 200] if name == selected_mosque else [200, 30, 0, 160]
)

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
            get_color='color',
            get_radius=150,
            pickable=True,
        ),
    ],
    tooltip={"text": "{mosque_name}"}
))

# Галерея карточек мечетей
st.markdown("### Мечети в выбранный период:")
columns = st.columns(3)

for idx, row in enumerate(filtered_df.itertuples()):
    col = columns[idx % 3]
    with col:
        if st.button(row.mosque_name, key=row.mosque_name):
            st.session_state.selected_mosque = row.mosque_name
            st.experimental_rerun()
        if pd.notna(row.image_url):
            st.image(row.image_url, use_column_width=True)
        st.markdown(f"**{row.original_name}**")
        st.markdown(f"{int(row.decade_built)} - {int(row.decade_demolished) if pd.notna(row.decade_demolished) else 'настоящее время'}")
        if row.mosque_name == selected_mosque:
            st.markdown("<div style='border:2px solid red; padding:4px;'>Выбрано</div>", unsafe_allow_html=True)
