# calendar_app/services/event_manager.py

import json
import os
import sys
from threading import Lock
from utils.resource import resource_path

# 書き込み対応のファイルパス
EVENTS_FILE = resource_path("data/events.json", writable=True)

# 複数スレッドから同時に書き込むのを防ぐためロックを用意
_FILE_LOCK = Lock()


def load_events() -> dict:
    """
    イベントデータを JSON ファイルから読み込んで返します。
    ファイルがなければ空の dict、JSON が壊れていれば警告のうえ空の dict を返します。
    """
    try:
        with open(EVENTS_FILE, encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            # 形式が dict でない場合も空にフォールバック
            return {}
    except FileNotFoundError:
        # ファイル未作成時は空データ
        return {}
    except json.JSONDecodeError:
        # JSON 故障時の警告
        print(f"[warning] イベントファイルの読み込みに失敗しました: {EVENTS_FILE}", file=sys.stderr)
        return {}


def save_events(events: dict) -> None:
    """
    イベントデータを JSON ファイルに書き込みます。
    必要に応じてディレクトリを作成し、 thread-safe に動作します。
    """
    os.makedirs(os.path.dirname(EVENTS_FILE), exist_ok=True)
    with _FILE_LOCK:
        with open(EVENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=2)


def add_event(events: dict,
              date_str: str,
              title: str,
              start_time: str = "",
              end_time: str = "",
              memo: str = "") -> None:
    """
    新しい予定を events に追加して保存します。

    - date_str: "YYYY-MM-DD" 形式の日付キー
    - title: イベントタイトル
    - start_time, end_time: "HH:MM" 形式
    - memo: 任意のメモ文字列
    """
    # 同じキーのリストに追加
    events.setdefault(date_str, []).append({
        "title":       title,
        "start_time":  start_time,
        "end_time":    end_time,
        "memo":        memo
    })
    save_events(events)


def delete_event(events: dict, date_str: str, index: int) -> None:
    """
    指定の日(date_str)のイベントリストから index 番目を削除し、空になればキーごと削除して保存します。
    """
    if date_str in events and 0 <= index < len(events[date_str]):
        events[date_str].pop(index)
        if not events[date_str]:
            del events[date_str]
        save_events(events)

        
# calendar_app/services/event_manager.py (抜粋 - 追加する可能性のある関数)
# ...既存の import と関数...

def update_event(events: dict,
                 date_str: str,
                 index: int,
                 title: str,
                 start_time: str = "",
                 end_time: str = "",
                 memo: str = "") -> None:
    """
    既存のイベントを更新し、保存します。

    - events: 現在のイベントデータ辞書
    - date_str: "YYYY-MM-DD" 形式の日付キー
    - index: その日付のイベントリスト内でのインデックス
    - title: 新しいイベントタイトル
    - start_time, end_time: "HH:MM" 形式
    - memo: 任意のメモ文字列
    """
    if date_str in events and 0 <= index < len(events[date_str]):
        # イベントデータを更新
        events[date_str][index] = {
            "title":      title,
            "start_time": start_time,
            "end_time":   end_time,
            "memo":       memo
        }
        save_events(events)
    else:
        # 存在しないイベントを更新しようとした場合の処理（エラーログなど）
        print(f"[warning] イベントの更新に失敗しました: 日付 {date_str}, インデックス {index} が見つかりません。", file=sys.stderr)
