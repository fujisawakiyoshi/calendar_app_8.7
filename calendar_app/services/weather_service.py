# services/weather_service.py
import requests
import sys
import json
from datetime import datetime

# 気象庁の予報概況JSONデータのURL
# 140000 は神奈川県の地域コード
JSON_URL = "https://www.jma.go.jp/bosai/forecast/data/overview_forecast/140000.json"

def get_weather_for_today() -> dict | None:
    """
    気象庁APIから横浜市の今日の天気概況を取得
    :return: 天気情報（辞書）。取得失敗時は None を返す
    """
    try:
        # print(f"URLにアクセス中: {JSON_URL}")
        res = requests.get(JSON_URL)
        res.raise_for_status() # HTTPエラーチェック
        
        data = res.json()
        
        weather_text = data.get("text", "")
        
        kanagawa_weather = _extract_kanagawa_weather(weather_text)
        
        if not kanagawa_weather:
             return None
        
        icons = _get_weather_icon_from_text(kanagawa_weather)
        
        # 修正: publishing_officeを返さない
        return {
            "icon": icons,
            "description": kanagawa_weather
        }

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] HTTPリクエストエラー: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSONデコードエラー: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[ERROR] 天気情報取得で不明なエラー: {e}", file=sys.stderr)
        return None

def _get_weather_icon_from_text(text: str) -> list[str]:
    """
    天気概況のテキストから対応するアイコンのファイル名を返す
    """
    icons = []
    if "晴れ" in text:
        icons.append("sun_icon.png")
    if "曇り" in text:
        icons.append("cloudy_icon.png")
    if "雨" in text:
        icons.append("rain_icon.png")
    if "雪" in text:
        icons.append("snow_icon.png")
    if "雷" in text or "稲妻" in text:
        icons.append("thunder_icon.png")
    if "風" in text:
        icons.append("wind_icon.png")
    
    if not icons:
        # どの条件にも当てはまらない場合、デフォルトアイコンを設定
        icons.append("sun_icon.png")
        
    return icons

def _extract_kanagawa_weather(text: str) -> str | None:
    """
    概況文から「神奈川県は、...」の行か、今日の日付の予報を抽出する
    """
    today_num_str = str(datetime.now().day)
    search_str = f"{today_num_str}日は"

    lines = text.split("。")
    
    # 複数行に分かれている場合があるので、行ごとに検索
    for line in lines:
        if "神奈川県は、" in line:
            return line.strip()
        if search_str in line:
            return line.strip()
    return None