import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

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

# Создаём карту
m = folium.Map(location=[44.82, 20.46], zoom_start=12, tiles="CartoDB positron")

# Добавляем мечети как маркеры с popup
for _, row in filtered_df.iterrows():
    html_popup = f"""
    <b>{row['mosque_name']}</b><br>
    <i>{row['original_name']}</i><br>
    <b>Годы:</b> {int(row['decade_built'])} - {int(row['decade_demolished']) if pd.notna(row['decade_demolished']) else 'настоящее время'}<br>
    {'<img src="' + row['image_url'] + '" width="200"><br>' if pd.notna(row['image_url']) else ''}
    {row['about'] if pd.notna(row['about']) else ''}
    """
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(html_popup, max_width=300),
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)

# Встраиваем карту в Streamlit
st_folium(m, width=700, height=500)
