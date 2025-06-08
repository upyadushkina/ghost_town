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
        ),
    ],
))

# Дополнительная информация
if not filtered_df.empty:
    for _, row in filtered_df.iterrows():
        with st.expander(f"{row['mosque_name']} ({int(row['decade_built'])})"):
            st.write(row['original_name'])
            if pd.notna(row['image_url']):
                st.image(row['image_url'], use_column_width=True)
            if pd.notna(row['about']):
                st.write(row['about'])
else:
    st.info("В этом году не было зарегистрированных мечетей.")
