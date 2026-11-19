# ============================================================
# GenRest app1.py 修正版片段
# 用法：
#   1. 刪掉原本的 get_google_restaurant() 與 get_place_details_by_name()
#   2. 把下面「A 區」整段貼在 translate_business_status() 之後
#   3. 用「B 區」的路由取代原本的 recommend / recommend_result /
#      generate_schedule / generate_map_schedule
#   4. requirements.txt 需有：flask, requests, gunicorn
#   5. Google Cloud 要啟用「Places API (New)」，並確認帳單與金鑰限制
# ============================================================

import math
import random
import re
import os
from datetime import datetime, timedelta

import requests
from flask import render_template, request

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# ------------------------------------------------------------
# A 區：Places API (New) 查詢
# ------------------------------------------------------------
PLACES_TEXT_URL = "https://places.googleapis.com/v1/places:searchText"

FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.location",
    "places.rating",
    "places.priceLevel",
    "places.businessStatus",
    "places.currentOpeningHours.openNow",
    "places.types",
])

PRICE_ENUM = {
    "PRICE_LEVEL_FREE": 0,
    "PRICE_LEVEL_INEXPENSIVE": 1,
    "PRICE_LEVEL_MODERATE": 2,
    "PRICE_LEVEL_EXPENSIVE": 3,
    "PRICE_LEVEL_VERY_EXPENSIVE": 4,
}
BUDGET_MAP = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}


class PlacesError(Exception):
    """Google API 呼叫失敗（金鑰、額度、網路等），不等於『沒有符合的餐廳』。"""


def _haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _search_text(query, lat, lng, radius_m):
    if not GOOGLE_API_KEY:
        raise PlacesError("伺服器沒有設定 GOOGLE_API_KEY")

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    body = {
        "textQuery": query,
        "languageCode": "zh-TW",
        "maxResultCount": 20,
        "locationBias": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": float(min(radius_m, 50000)),
            }
        },
    }
    try:
        res = requests.post(PLACES_TEXT_URL, json=body, headers=headers, timeout=10)
    except requests.RequestException as e:
        print("Places request failed:", e)
        raise PlacesError("連線 Google 失敗")

    if res.status_code != 200:
        try:
            msg = res.json().get("error", {}).get("message", "")
        except ValueError:
            msg = res.text[:200]
        print("Places API error:", res.status_code, msg)  # 會出現在 Render Logs
        raise PlacesError(f"Google API 錯誤 {res.status_code}：{msg}")

    return res.json().get("places", [])


def _to_result(p, fallback):
    name = (p.get("displayName") or {}).get("text", "無名餐廳")
    match = re.match(r"(.+?)\s*[(（](.+?)[)）]", name)
    name_zh, name_en = (match.group(1).strip(), match.group(2).strip()) if match else (name, "")
    price = PRICE_ENUM.get(p.get("priceLevel"))
    loc = p.get("location", {})
    return {
        "name": name,
        "name_zh": name_zh,
        "name_en": name_en,
        "desc": p.get("formattedAddress", ""),
        "lat": loc.get("latitude", 0),
        "lon": loc.get("longitude", 0),
        "budget": translate_price_level(price),
        "category": translate_type(p.get("types")),
        "rating": p.get("rating", "無評分"),
        "status": translate_business_status(p.get("businessStatus")),
        "fallback": fallback,
    }


def get_google_restaurant(building, category, budget, distance_km=0.5):
    """回傳最多 3 家餐廳 list；API 失敗時 raise PlacesError。"""
    location = BUILDING_COORDS.get(building)
    if not location:
        return []
    lat, lng = (float(x) for x in location.split(","))
    radius_m = int(distance_km * 1000)

    # 每個類別各查一次再合併（最多 3 個），避免關鍵字擠成一串導致結果過少
    keywords = [k for k in (category or "restaurant").split() if k][:3] or ["restaurant"]
    places = {}
    for kw in keywords:
        query = kw if kw == "restaurant" else f"{kw} restaurant"
        for p in _search_text(query, lat, lng, radius_m):
            pl = p.get("location", {})
            if "latitude" not in pl:
                continue
            if _haversine_m(lat, lng, pl["latitude"], pl["longitude"]) > radius_m:
                continue
            places[p.get("id", p.get("formattedAddress"))] = p
    all_places = list(places.values())

    max_price = BUDGET_MAP.get(budget, 4)

    def operational(p):
        return p.get("businessStatus", "OPERATIONAL") == "OPERATIONAL"

    def is_open(p):  # 沒有營業時間資料就視為可能營業
        return p.get("currentOpeningHours", {}).get("openNow", True)

    def in_budget(p):
        price = PRICE_ENUM.get(p.get("priceLevel"))
        return price is None or price <= max_price

    # 第 1 層：營業中 + 符合預算；第 2 層：營業中；第 3 層：只要沒歇業
    tiers = [
        [p for p in all_places if operational(p) and is_open(p) and in_budget(p)],
        [p for p in all_places if operational(p) and is_open(p)],
        [p for p in all_places if operational(p)],
    ]
    for i, tier in enumerate(tiers):
        if tier:
            chosen = random.sample(tier, min(3, len(tier)))
            return [_to_result(p, fallback=(i > 0)) for p in chosen]
    return []


def safe_search(building, keyword, budget, distance):
    """回傳 (餐廳 list, 錯誤訊息)。API 壞掉和沒結果會顯示不同訊息。"""
    try:
        results = get_google_restaurant(building, keyword, budget, distance)
    except PlacesError as e:
        return [], f"餐廳資料暫時無法取得（{e}）"
    if not results:
        return [], "找不到符合條件的餐廳，請換個建築或類別試試！"
    return results, None


def parse_filters(suffix=""):
    """從表單讀取條件。suffix 例如 '_lunch_0'；單餐表單則為空字串。"""
    building = request.form.get(f"building{suffix}")
    try:
        distance = float(request.form.get(f"distance{suffix}") or 0.5)
    except ValueError:
        distance = 0.5
    budget = request.form.get(f"budget{suffix}")
    cats = request.form.getlist(f"category{suffix}")
    kws = [Category_LIST[c] for c in cats if c in Category_LIST]
    return building, distance, budget, " ".join(kws) or "restaurant"


# ------------------------------------------------------------
# B 區：路由（取代原本同名函式）
# ------------------------------------------------------------
@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    restaurant_list, error = [], None
    if request.method == "POST":
        building, distance, budget, keyword = parse_filters()
        restaurant_list, error = safe_search(building, keyword, budget, distance)
    return render_template(
        "recommend_tabs.html",
        buildings=list(BUILDING_COORDS.keys()),
        categories=list(Category_LIST.keys()),
        restaurant_list=restaurant_list,
        error=error,
        multi_schedule={},
        zip=zip,
    )


@app.route("/recommend_result", methods=["POST"])
def recommend_result():
    building, distance, budget, keyword = parse_filters()
    restaurant, error = safe_search(building, keyword, budget, distance)
    return render_template(
        "recommend_result.html",
        restaurant=restaurant,
        error=error,
        buildings=list(BUILDING_COORDS.keys()),
        categories=list(Category_LIST.keys()),
    )


def daterange(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(n)


EMPTY_MEAL = {
    "name": "找不到", "name_zh": "找不到", "name_en": "", "desc": "",
    "lat": 0, "lon": 0, "budget": "", "category": "",
    "rating": "無評分", "status": "", "fallback": False,
}


def _build_schedule(only_selected_meals):
    start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
    end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")
    dates = list(daterange(start_date, end_date))

    meals = ["breakfast", "lunch", "dinner"]
    if only_selected_meals:
        meals = [m for m in meals if any(k.startswith(f"building_{m}") for k in request.form)]

    schedule = {"breakfast": [], "lunch": [], "dinner": []}
    for i, day in enumerate(dates):
        for meal in meals:
            building, distance, budget, keyword = parse_filters(f"_{meal}_{i}")
            if not building:
                schedule[meal].append(None)
                continue
            results, _ = safe_search(building, keyword, budget, distance)
            pick = random.choice(results) if results else EMPTY_MEAL
            schedule[meal].append({"date": day.strftime("%Y-%m-%d"), **pick})
    return schedule


def _render_schedule(schedule):
    return render_template(
        "recommend_tabs.html",
        buildings=list(BUILDING_COORDS.keys()),
        categories=list(Category_LIST.keys()),
        restaurant_list=[],
        error=None,
        multi_schedule=schedule,
        zip=zip,
    )


@app.route("/generate_schedule", methods=["POST"])
def generate_schedule():
    return _render_schedule(_build_schedule(only_selected_meals=True))


@app.route("/generate_map_schedule", methods=["POST"])
def generate_map_schedule():
    # 原版這裡對 list 使用 **，會 TypeError；現在改成先 random.choice
    return _render_schedule(_build_schedule(only_selected_meals=False))