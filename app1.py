
from flask import Flask, render_template, request, redirect, url_for
import requests
import random
import json
import re

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.jinja_env.globals.update(zip=zip)


GOOGLE_API_KEY = "AIzaSyBbTwYoF3iRq1ZVC41_BNNTkf5qED06oik"

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
    "新生教學館": "25.02294615,121.53356668",
    "普通教學館": "25.02328244,121.53303982",
    "舊總圖書館": "25.02366101,121.53253898",
    "醫學綜合大樓": "25.02403729,121.53210739",
    "護理學院": "25.02439865,121.53172511",
    "公衛學院": "25.02471848,121.53126752",
    "藥學院": "25.02503342,121.53088147",
    "生命科學院": "25.02539484,121.53050274",
    "獸醫學院": "25.02570649,121.53012676",
    "農業化學館": "25.02603441,121.52977913",
    "食品科技館": "25.02635412,121.52944178",
    "農場管理館": "25.02666099,121.52910115",
    "農業推廣館": "25.02699254,121.52876367",
    "植物病理館": "25.02733699,121.52844416",
    "昆蟲館新館": "25.02767095,121.52812636",
    "農機館": "25.02800281,121.52780079",
    "森林館": "25.02835011,121.52746551",
    "農業經濟館": "25.02867614,121.52714992",
    "農藝館": "25.02899738,121.52682533",
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
    "生物資源暨農學院": "25.03453094,121.52146571"
}
building_list = list(BUILDING_COORDS.keys())

Category_LIST = {
    "拉麵":"ramen",
    "咖啡":"cafe", 
    "麵包店":"bakery", 
    "甜點":"dessert",
    "韓式":"korean", 
    "火鍋":"hotpot", 
    "便當":"bento",
    "壽司":"sushi",
    "西式":"western", 
    "日式":"japanese", 
    "中式":"chinese" ,
    "速食":"fastfood",
    "海鮮":"seafood",
    "早餐":"breakfast",
    "麵食":"noodles",
    "飯類":"rice",
    "美式":"american", 
    "素食":"vegetarian",
    "燒烤":"bbq",
}
category_list = list(Category_LIST.keys())

def translate_price_level(level):
    mapping = {
        0: "免費",
        1: "$（0~150元）",
        2: "$$（150~300元）",
        3: "$$$（300~600元）",
        4: "$$$$（600元以上）"
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
        "vegetarian": "素食"
        # 不加入 point_of_interest，就不會顯示出來
    }
    if not types:
        return "無類別資訊"
    
    # 過濾掉未在 mapping 中的類別
    translated = [mapping[t] for t in types if t in mapping]
    
    if not translated:
        return "無類別資訊"
    
    return "、".join(translated[:3])


def translate_business_status(status):
    mapping = {
        "OPERATIONAL": "營業中",
        "CLOSED_TEMPORARILY": "暫停營業",
        "CLOSED_PERMANENTLY": "永久歇業"
    }
    return mapping.get(status, "未知")

def split_name(name):
    # 如果有中文字，就當作中文名，否則當作英文名
    if any('\u4e00' <= c <= '\u9fff' for c in name):
        return name, ""
    else:
        return "", name

def get_google_restaurant(building, category, budget, distance_km=0.5):
    location = BUILDING_COORDS.get(building)
    if not location:
        return []

    keyword = category or "餐廳"

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": GOOGLE_API_KEY,
        "location": location,
        "radius": int(distance_km * 1000),
        "keyword": keyword,
        "type": "restaurant"
    }

    res = requests.get(url, params=params)
    data = res.json()

    if not data.get("results"):
        return []

    price_map = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
    max_price = price_map.get(budget, 4)

    # 條件符合 + 營業中
    open_filtered = [
        r for r in data["results"]
        if r.get("price_level", 1) <= max_price and
           r.get("business_status") == "OPERATIONAL" and
           r.get("opening_hours", {}).get("open_now", True)
    ]

    # 保底推薦（只營業中）
    fallback_candidates = [
        r for r in data["results"]
        if r.get("business_status") == "OPERATIONAL" and
           r.get("opening_hours", {}).get("open_now", True)
    ]

    candidates = open_filtered if open_filtered else fallback_candidates
    fallback = not open_filtered  # ✅ 沒有符合條件才標記 fallback 為 True

    if not candidates:
        return []

    # 隨機取最多三家
    selected_list = random.sample(candidates, min(3, len(candidates)))
    results = []

    for r in selected_list:
        name = r.get("name", "無名餐廳")
        match = re.match(r"(.+?)\s*[(（](.+?)[)）]", name)
        if match:
            name_zh = match.group(1).strip()
            name_en = match.group(2).strip()
        else:
            name_zh = name
            name_en = ""


        results.append({
            "name": name,
            "name_zh": name_zh,
            "name_en": name_en,
            "desc": r.get("vicinity", ""),
            "lat": r["geometry"]["location"]["lat"],
            "lon": r["geometry"]["location"]["lng"],
            "budget": translate_price_level(r.get("price_level")),
            "category": translate_type(r.get("types")),
            "rating": r.get("rating", "無評分"),
            "status": translate_business_status(r.get("business_status")),
            "fallback": fallback
        })

    return results






@app.route("/")
def index():
    return render_template("index.html")

# GET 請求：導向 tabs 的一餐分頁
@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    building_list = list(BUILDING_COORDS.keys())
    category_list = list(Category_LIST.keys())
    restaurant_list = []
    error = None

    if request.method == "POST":
        building = request.form.get("building")
        distance = float(request.form.get("distance") or 0.5)
        budget = request.form.get("budget")
        categories = request.form.getlist("category")
        category_keywords = [Category_LIST.get(c, "") for c in categories if Category_LIST.get(c)]
        category_keyword = " ".join(filter(None, category_keywords)) or "restaurant"

        restaurant_list = get_google_restaurant(building, category_keyword, budget, distance)

        if not restaurant_list:
            error = "找不到符合條件的餐廳，請換個建築或類別試試！"

    return render_template(
        "recommend_tabs.html",  # 傳回 tab 分頁頁面
        buildings=building_list,
        categories=category_list,
        restaurant_list=restaurant_list,  # ✅ 改為傳多筆結果
        error = error,
        multi_schedule={},
        zip=zip
    )



# POST 請求：處理表單結果（單日推薦）
@app.route("/recommend_result", methods=["POST"])
def recommend_result():
    building_list = list(BUILDING_COORDS.keys())
    category_list = list(Category_LIST.keys())
    restaurant = None
    error = None

    building = request.form.get("building")
    distance = float(request.form.get("distance") or 0.5)
    budget = request.form.get("budget")
    categories = request.form.getlist("category")
    category_keywords = [Category_LIST.get(c, "") for c in categories if Category_LIST.get(c)]
    category_keyword = " ".join(filter(None, category_keywords)) or "restaurant"

    restaurant = get_google_restaurant(building, category_keyword, budget, distance)

    if not restaurant:
        error = "找不到符合條件的餐廳，請換個建築或類別試試！"

    return render_template(
        "recommend_result.html",  # 新的結果頁模板
        restaurant=restaurant,
        error=error,
        buildings=building_list,
        categories=category_list
    )


@app.route("/recommend_multi")
def recommend_multi():
    category_list = list(Category_LIST.keys())
    building_list = list(BUILDING_COORDS.keys())
    return redirect(url_for("recommend_tabs") + "#multi")

def get_place_details_by_name(name, location="25.0175,121.541", radius=1000):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": GOOGLE_API_KEY,
        "location": location,
        "radius": radius,
        "keyword": name
    }
    res = requests.get(url, params=params)
    data = res.json()

    if data.get("results"):
        item = data["results"][0]
        return {
            "name": item.get("name", "未命名餐廳"),
            "desc": item.get("vicinity", ""),
            "lat": item["geometry"]["location"]["lat"],
            "lon": item["geometry"]["location"]["lng"],
            "rating": item.get("rating"),
            "budget": "$" * item.get("price_level", 1)
        }
    return None



from datetime import datetime, timedelta

def daterange(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(n)

@app.route("/generate_schedule", methods=["POST"])
def generate_schedule():
    start = request.form.get("start_date")
    end = request.form.get("end_date")
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    dates = list(daterange(start_date, end_date))

    schedule = {"breakfast": [], "lunch": [], "dinner": []}

    selected_meals = []
    for meal in ["breakfast", "lunch", "dinner"]:
        if any(k.startswith(f"building_{meal}") for k in request.form):
            selected_meals.append(meal)

    for i, day in enumerate(dates):
        for meal in selected_meals:
            prefix = f"{meal}_{i}"
            building = request.form.get(f"building_{prefix}")

            if not building:
                schedule[meal].append(None)
                continue

            distance = float(request.form.get(f"distance_{prefix}", 0.5))
            budget = request.form.get(f"budget_{prefix}")
            categories = request.form.getlist(f"category_{prefix}")
            category_keywords = [Category_LIST.get(c, "") for c in categories if Category_LIST.get(c)]
            keyword = " ".join(filter(None, category_keywords)) or "restaurant"

            restaurant_list = get_google_restaurant(building, keyword, budget, distance)
            restaurant = random.choice(restaurant_list) if restaurant_list else None

            schedule[meal].append({
                "date": day.strftime("%Y-%m-%d"),
                **(restaurant or {
                    "name": "找不到",
                    "name_zh": "找不到",
                    "name_en": "",
                    "desc": "",
                    "lat": 0,
                    "lon": 0,
                    "budget": "",
                    "category": "",
                    "rating": "無評分",
                    "status": "",
                    "fallback": False
                })
            })

    return render_template(
        "recommend_tabs.html",
        buildings=building_list,
        categories=category_list,
        restaurant_list=[],        # ✅ 一餐不顯示
        error=None,
        multi_schedule=schedule, # ✅ 將多天結果傳給 template
        zip=zip  
    )


@app.route("/generate_map_schedule", methods=["POST"])
def generate_map_schedule():
    from datetime import date, timedelta

    start = request.form.get("start_date")
    end = request.form.get("end_date")
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    dates = list(daterange(start_date, end_date))

    schedule = {"breakfast": [], "lunch": [], "dinner": []}

    for i, day in enumerate(dates):
        for meal in ["breakfast", "lunch", "dinner"]:
            prefix = f"{meal}_{i}"
            building = request.form.get(f"building_{prefix}")

            if not building:
                schedule[meal].append(None)
                continue

            distance = float(request.form.get(f"distance_{prefix}", 0.5))
            budget = request.form.get(f"budget_{prefix}")
            categories = request.form.getlist(f"category_{prefix}")
            category_keywords = [Category_LIST.get(c, "") for c in categories if Category_LIST.get(c)]
            keyword = " ".join(filter(None, category_keywords)) or "restaurant"

            restaurant = get_google_restaurant(building, keyword, budget, distance)
            schedule[meal].append({
                "date": day.strftime("%Y-%m-%d"),
                **(restaurant or {"name": "找不到", "desc": "", "lat": 0, "lon": 0, "budget": "", "category": "", "rating": None})
            })


    return render_template(
        "recommend_tabs.html",
        buildings=building_list,
        categories=category_list,
        multi_schedule=schedule,  # ✅ 加入多天推薦結果
        restaurant_list=[],        # 避免一餐推薦區出錯
        error=None,
        zip=zip  # 👈 明確傳入 zip
    )

@app.route("/recommend_tabs", methods=["GET", "POST"])
def recommend_tabs():
    building_list = list(BUILDING_COORDS.keys())
    category_list = list(Category_LIST.keys())
    return render_template(
        "recommend_tabs.html",
        buildings=building_list,
        categories=category_list,
        restaurant_list=[],
        error=None,
        multi_schedule={},  # 空的 schedule
        zip=zip  # 👈 明確傳入 zip
    )


@app.route("/calendar")
def calendar():
    return render_template("calendar.html")

@app.route("/account")
def account():
    return render_template("account.html")


if __name__ == "__main__":
    app.run(debug=True)
