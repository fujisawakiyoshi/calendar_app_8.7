import json
import os
import requests
from utils.resource import resource_path

CACHE_FILE = resource_path("data/holidays.json")

def fetch_holidays_from_api(year):
    """祝日APIから取得"""
    url = f"https://holidays-jp.github.io/api/v1/{year}/date.json"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        return data
    except Exception as e:
        print(f"API取得失敗({year}):", e)
        return {}

def load_holiday_cache():
    """キャッシュファイル読み込み"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_holiday_cache(data):
    """キャッシュファイル保存"""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_holidays_for_year(year):
    """
    この関数をMainWindowで使うイメージ
    - キャッシュを読み込む
    - 欲しい年がなければAPIから取得
    - キャッシュに保存
    - その年のデータを返す
    """
    holidays_cache = load_holiday_cache()
    
    if str(year) in holidays_cache:
        return holidays_cache[str(year)]
    
    print(f"キャッシュに{year}年がないのでAPIから取得します")
    data = fetch_holidays_from_api(year)
    if data:
        holidays_cache[str(year)] = data
        save_holiday_cache(holidays_cache)
    return data

#if __name__ == "__main__":
    """API取得するための確認"""
    target_year = 2025
    holidays = fetch_holidays_from_api(target_year)
    if holidays:
        save_holiday_cache(holidays)
        print(f"{target_year}年の祝日を保存しました")
    else:
        print("祝日データ取得に失敗しました")