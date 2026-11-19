import math
import os
import random
import re
from datetime import datetime, timedelta

import requests
from flask import Flask, render_template, request, redirect, url_for

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.jinja_env.globals.update(zip=zip)

BUILDING_COORDS = {
    "傅鐘": "25.0173,121.5417",
    "綜合教學館": "25.0186,121.5376",
    "總圖書館": "25.0171,121.5399",
    "湖心亭": "25.02042032,121.53761439",
    "綜合體育館": "25.02161972,121.53518091",
    "小福": "25.01858512,121.53732402",
    "農業陳列館": "25.0181421,121.53419815",
    "新月台": "25.01854917,121.53401429",
    "管理學院二號館": "25.01312146,121.53687679",
    "資訊工程館": "25.01952974,121.54161874",
    "社會科學院大樓": "25.020759,121.54230763",
    "普通教學館": "25.01651768,121.5380872",
    "化學館": "25.01615468,121.53978546",
    "行政大樓": "25.01663323,121.54220518",
    "文學院": "25.01543326,121.54229838",
    "新生教學館": "25.01736283,121.53431376",
    "應力館": "25.01798987,121.53269006",
    "工綜館": "25.01712503,121.53225511",
    "博雅教學館": "25.01643138,121.5332693",
    "電機系館": "25.0175525,121.53261623",
    "思亮館": "25.01594806,121.53191138",
    "食品科技館": "25.02044796,121.53341193",
    "農化館": "25.02039558,121.53388518",
    "生農學院": "25.02067291,121.5344446",
    "植物科學研究中心": "25.02128938,121.53411517",
    "畜產館": "25.02148725,121.53366568",
    "森林館": "25.0212382,121.53296318",
    "農藝館": "25.02118565,121.53215712",
    "獸醫館": "25.02168694,121.53167466",
    "生物技術館": "25.02211373,121.53168489",
    "農業綜合館": "25.02222366,121.53257218",
    "園藝系溫室": "25.02145748,121.53205442",
    "植物教學館": "25.02174382,121.53118365",
    "昆蟲館": "25.02203216,121.53136593",
    "農業試驗館": "25.02223277,121.53097942",
    "獸醫臨床教學大樓": "25.02268367,121.53085266",
    "化工館": "25.01912368,121.53335867",
    "土木館": "25.01864818,121.53324378",
    "環工館": "25.01816433,121.53310588",
    "應力與材料館": "25.01779938,121.53294784",
    "生機系館": "25.01737383,121.53288645",
    "電資綜合大樓": "25.01720423,121.53198996",
    "電資大樓北棟": "25.01702918,121.53132647",
    "計算機及資訊網路中心": "25.01650593,121.53149734",
    "基礎實驗大樓": "25.01608037,121.53180446",
    "應用力學研究所": "25.01653322,121.53268036",
    "天文數學館": "25.01534945,121.53364069",
    "物理館": "25.0155792,121.53432058",
    "天文台": "25.01594576,121.53471166",
    "地質館": "25.01634652,121.53501447",
    "心理系館": "25.01666791,121.53556296",
    "生命科學館": "25.01653986,121.53595007",
    "教學大樓": "25.0189287,121.53736027",
    "綜合大樓": "25.01932345,121.53743558",
    "資訊系館": "25.01964263,121.53727388",
    "第二活動中心": "25.02017782,121.5370955",
    "一號館": "25.02069594,121.53682115",
    "總務處": "25.02097598,121.53654333",
    "文學院大樓": "25.02139662,121.53623813",
    "外語教學暨資源中心": "25.02175066,121.53587968",
    "外文系館": "25.02187734,121.53535897",
    "教學資源中心": "25.02207265,121.53488857",
    "外語學院": "25.02231249,121.53447113",
    "圖書資訊學系": "25.02270292,121.53405026",
    # 注意：以下從「新生教學館」到「農藝館」在上方已定義過，
    # 後面的座標會覆蓋前面的，而且看起來不像真實位置，建議對照 ntu_buildings.geojson 修正。
    "動物科學技術館": "25.02932541,121.52648912",
    "畜產館": "25.02964817,121.52617236",
    "畜產試驗場": "25.02998032,121.52584743",
    "農化館": "25.03031055,121.52551984",
    "植物科學館": "25.03064843,121.52519182",
    "作物科學館": "25.03096475,121.52488359",
    "水產養殖館": "25.03128974,121.52457119",
    "實驗林館": "25.03161743,121.52426484",
    "農藝試驗館": "25.03193722,121.52395728",
    "生物技術館": "25.03225088,121.52364211",
    "農業資源與環境學系": "25.03258067,121.52333327",
    "農業與自然資源學院": "25.03290011,121.52302984",
    "實驗農場教學大樓": "25.03322531,121.52271006",
    "景觀暨都市計劃系": "25.03354374,121.52239879",
    "土地管理館": "25.03387243,121.52208431",
    "實驗農場管理中心": "25.03420086,121.52177556",
    "生物資源暨農學院": "25.03453094,121.52146571",
}

building_list = list(BUILDING_COORDS.keys())

Category_LIST = {
    "拉麵": "ramen",
    "咖啡": "cafe",
    "麵包店": "bakery",
    "甜點": "dessert",
    "韓式": "korean",
    "火鍋": "hotpot",
    "便當": "bento",
    "壽司": "sushi",
    "西式": "western",
    "日式": "japanese",
    "中式": "chinese",
    "速食": "fastfood",
    "海鮮": "seafood",
    "早餐": "breakfast",
    "麵食": "noodles",
    "飯類": "rice",
    "美式": "american",
    "素食": "vegetarian",
    "燒烤": "bbq",
}

category_list = list(Category_LIST.keys())


def translate_price_level(level):
    mapping = {
        0: "免費",
        1: "$（0~150元）",
        2: "$$（150~300元）",
        3: "$$$（300~600元）",
        4: "$$$$（600元以上）",
    }
    return mapping.get(level, "未知")


def translate_type(types):
    mapping = {
        "cafe": "咖啡廳",
        "restaurant": "餐廳",
        "bakery": "麵包店",
        "bar": "酒吧",
        "meal_delivery": "外送",
        "meal_takeaway": "外帶",
        "food": "食品",
        "fast_food": "速食",
        "japanese": "日式",
        "korean": "韓式",
        "chinese": "中式",
        "thai": "泰式",
        "hotpot": "火鍋",
        "vegetarian": "素食",
        # 不加入 point_of_interest，就不會顯示出來
    }
    if not types:
        return "無類別資訊"
    translated = [mapping[t] for t in types if t in mapping]
    if not translated:
        return "無類別資訊"
    return "、".join(translated[:3])


def translate_business_status(status):
    mapping = {
        "OPERATIONAL": "營業中",
        "CLOSED_TEMPORARILY": "暫停營業",
        "CLOSED_PERMANENTLY": "永久歇業",
    }
    return mapping.get(status, "未知")


def split_name(name):
    # 如果有中文字，就當作中文名，否則當作英文名
    if any('\u4e00' <= c <= '\u9fff' for c in name):
        return name, ""
    else:
        return "", name


# ------------------------------------------------------------
# Places API (New) 查詢
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
        print("Places request failed:", e, flush=True)
        raise PlacesError("連線 Google 失敗")

    if res.status_code != 200:
        try:
            msg = res.json().get("error", {}).get("message", "")
        except ValueError:
            msg = res.text[:200]
        print("Places API error:", res.status_code, msg, flush=True)  # 會出現在 Render Logs
        raise PlacesError(f"Google API 錯誤 {res.status_code}：{msg}")

    return res.json().get("places", [])


def _to_result(p, fallback):
    name = (p.get("displayName") or {}).get("text", "無名餐廳")
    match = re.match(r"(.+?)\s*[(（](.+?)[)）]", name)
    if match:
        name_zh, name_en = match.group(1).strip(), match.group(2).strip()
    else:
        name_zh, name_en = name, ""
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
    print(f"[search] building={building!r} in_coords={building in BUILDING_COORDS} "
          f"keyword={keyword!r} budget={budget!r} distance={distance}", flush=True)
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
# 路由
# ------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


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


@app.route("/recommend_multi")
def recommend_multi():
    return redirect(url_for("recommend_tabs") + "#multi")


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


@app.route("/recommend_tabs", methods=["GET", "POST"])
def recommend_tabs():
    return render_template(
        "recommend_tabs.html",
        buildings=list(BUILDING_COORDS.keys()),
        categories=list(Category_LIST.keys()),
        restaurant_list=[],
        error=None,
        multi_schedule={},
        zip=zip,
    )


@app.route("/calendar")
def calendar():
    return render_template("calendar.html")


@app.route("/account")
def account():
    return render_template("account.html")




if __name__ == "__main__":
    app.run(debug=True)