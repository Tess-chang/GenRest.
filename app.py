import streamlit as st
import geopy
from geopy.distance import geodesic
import json
import random
import geopandas as gpd

# 計算兩點間距離
def haversine(lon1, lat1, lon2, lat2):
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers

# 載入餐廳 GeoJSON 檔案
def load_restaurant_data(filename="restaurant-tpe.geojson"):
    with open(filename, encoding="utf-8") as f:
        data = json.load(f)
    return data

# 查詢附近餐廳
def find_nearby_restaurants(target_lat, target_lon, data, radius_km=0.5):
    nearby_restaurants = []
    for feature in data["features"]:
        lon, lat = feature["geometry"]["coordinates"]
        distance = haversine(target_lon, target_lat, lon, lat)
        if distance <= radius_km:
            opening = feature["properties"].get("opening_hours")
            if opening:  # 只選有營業時間的
                nearby_restaurants.append(feature)
    return nearby_restaurants

# 推薦餐廳
def recommend_random_restaurant(nearby_restaurants):
    if nearby_restaurants:
        selected = random.choice(nearby_restaurants)
        name = selected["properties"].get("name", "未命名餐廳")
        return f"建議餐廳：{name}"
    else:
        return "此地點方圓500公尺內沒有營業中的餐廳"

# Streamlit 主介面
st.title("台大附近餐廳推薦系統")

# 載入建築物資料
buildings = gpd.read_file("ntu_buildings.geojson")

# 讓使用者輸入建築物
building_name = st.text_input("請輸入台大建築物名稱（例如：綜合教學館）")

if building_name:
    matched = buildings[buildings['name'].str.contains(building_name, na=False)]
    if matched.empty:
        st.error("找不到這棟建築物")
    else:
        # 抓第一個符合建築物的中心座標
        target_geom = matched.iloc[0].geometry
        if target_geom.geom_type == "Polygon":
            target_point = target_geom.centroid
        else:
            target_point = target_geom

        target_lat = target_point.y
        target_lon = target_point.x

        # 載入餐廳並推薦
        data = load_restaurant_data()
        nearby = find_nearby_restaurants(target_lat, target_lon, data)
        st.success(recommend_random_restaurant(nearby))
