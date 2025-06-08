import streamlit as st
import pandas as pd
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static

# Загружаем данные
df = pd.read_csv("cleaned_mosques.csv")

# Заголовок
st.title("Мечети Белграда: Историческая карта (Kepler.gl)")
st.markdown("Выберите год ниже, чтобы увидеть мечети, существовавшие в это время.")

# Ползунок времени
year = st.slider("Год", min_value=int(df['decade_built'].min()), max_value=int(df['decade_demolished'].max()), value=1700, step=10)

# Фильтрация мечетей по году существования
mask = (df['decade_built'] <= year) & ((df['decade_demolished'].isna()) | (df['decade_demolished'] >= year))
filtered_df = df[mask].copy()

# Добавляем нужные поля для отображения
def format_popup(row):
    img = f'<img src="{row["image_url"]}" width="200"><br>' if pd.notna(row['image_url']) else ''
    about = row['about'] if pd.notna(row['about']) else ''
    return f"""
    <b>{row['mosque_name']}</b><br>
    <i>{row['original_name']}</i><br>
    <b>Годы:</b> {int(row['decade_built'])} - {int(row['decade_demolished']) if pd.notna(row['decade_demolished']) else 'настоящее время'}<br>
    {img}
    {about}
    """

filtered_df['popup'] = filtered_df.apply(format_popup, axis=1)

# Переименовываем в формат Kepler
filtered_df.rename(columns={"longitude": "lng", "latitude": "lat"}, inplace=True)

# Создаём карту Kepler
config = {
    "version": "v1",
    "config": {
        "visState": {
            "layers": [
                {
                    "type": "point",
                    "config": {
                        "dataId": "mosques",
                        "label": "Mosques",
                        "color": [30, 144, 255],
                        "columns": {"lat": "lat", "lng": "lng", "altitude": None},
                        "isVisible": True,
                        "visConfig": {"radius": 15, "opacity": 0.8},
                        "tooltip": ["popup"]
                    },
                }
            ]
        }
    }
}

map_1 = KeplerGl(height=600, data={"mosques": filtered_df}, config=config)
keplergl_static(map_1)
