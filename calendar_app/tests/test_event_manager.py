# tests/test_event_manager.py (修正箇所)

import pytest
from unittest.mock import patch, mock_open
import json
from services.event_manager import load_events, save_events

# Eventクラスのインポートを一時的にコメントアウトまたは削除
# from services.event_manager import Event # この行を削除、または先頭に # をつける

# UT-04: load_events() ファイルが存在しない場合、空の辞書 {} が返される
def test_load_events_file_not_found():
    """
    events.json ファイルが存在しない場合に load_events() が
    空の辞書を返すことを確認する。
    """
    # os.path.exists をモックして、常にファイルが存在しないと返すようにする
    # open() もモックし、FileNotFoundError を発生させるように設定する
    with patch('os.path.exists', return_value=False), \
         patch('builtins.open', side_effect=FileNotFoundError):
        events = load_events()
        assert events == {}


# UT-05: load_events() ファイルが空の場合、空の辞書 {} が返される
def test_load_events_empty_file():
    """
    events.json ファイルが存在し、中身が空の場合に load_events() が
    空の辞書を返すことを確認する。
    """
    mock_events_file_path = "mocked/data/events.json"

    m = mock_open(read_data="")
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', m), \
         patch('services.event_manager.EVENTS_FILE', new=mock_events_file_path):
        
        from services.event_manager import load_events 

        events = load_events()
        assert events == {}
            
        # ここを修正: 'r' モードを削除します。
        # load_events() 内の open() がモードを明示していないため、デフォルトの挙動と合わせる
        m.assert_called_once_with(mock_events_file_path, encoding="utf-8")
        

# UT-06: load_events() ファイルが不正なJSONの場合、空の辞書 {} が返される
def test_load_events_invalid_json():
    """
    events.json ファイルが存在し、中身が不正なJSON形式の場合に load_events() が
    空の辞書を返すことを確認する。
    """
    # 意図的に不正なJSON文字列
    invalid_json_data = "This is not a valid JSON string {"

    m = mock_open(read_data=invalid_json_data)
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', m), \
         patch('services.event_manager.EVENTS_FILE', new="mocked/data/events.json"):

        # load_eventsを呼び出す前にインポート
        from services.event_manager import load_events 

        events = load_events()
        assert events == {}

        # open() が正しく呼び出されたことを確認
        m.assert_called_once_with("mocked/data/events.json", encoding="utf-8")
        

# UT-07: load_events() 有効なイベントデータが正しく読み込まれることを確認
def test_load_events_valid_data():
    """
    events.json ファイルから有効なイベントデータが正しく読み込まれることを確認する。
    """
    # 有効なダミーのJSONデータ
    valid_json_data = """
    {
        "2025-07-25": [
            {
                "title": "会議",
                "start_time": "10:00",
                "end_time": "11:00",
                "memo": "プロジェクトミーティング"
            }
        ],
        "2025-07-26": [
            {
                "title": "セミナー",
                "start_time": "14:00",
                "end_time": "16:00",
                "memo": "新しい技術の学習"
            },
            {
                "title": "懇親会",
                "start_time": "18:00",
                "end_time": "",
                "memo": ""
            }
        ]
    }
    """
    # 期待されるパース後のPython辞書データ
    expected_events = {
        "2025-07-25": [
            {
                "title": "会議",
                "start_time": "10:00",
                "end_time": "11:00",
                "memo": "プロジェクトミーティング"
            }
        ],
        "2025-07-26": [
            {
                "title": "セミナー",
                "start_time": "14:00",
                "end_time": "16:00",
                "memo": "新しい技術の学習"
            },
            {
                "title": "懇親会",
                "start_time": "18:00",
                "end_time": "",
                "memo": ""
            }
        ]
    }

    mock_events_file_path = "mocked/data/events.json"

    m = mock_open(read_data=valid_json_data)
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', m), \
         patch('services.event_manager.EVENTS_FILE', new=mock_events_file_path):

        from services.event_manager import load_events 

        events = load_events()
        assert events == expected_events # 読み込まれたデータが期待値と一致するか検証

        m.assert_called_once_with(mock_events_file_path, encoding="utf-8")
        
    
    # tests/test_event_manager.py に追加

# UT-08: add_event() 新しいイベントが正しく追加され、ファイルに保存される
def test_add_event():
    """
    add_event() が新しいイベントを既存のデータに追加し、
    save_events() を呼び出して保存することを確認する。
    """
    # 初期イベントデータ（空でもOKですが、追加されることを明確にするため既存データを用意）
    initial_events = {
        "2025-07-25": [
            {
                "title": "既存会議",
                "start_time": "09:00",
                "end_time": "10:00",
                "memo": "既存のイベント"
            }
        ]
    }

    # add_event が呼び出された後に期待されるイベントデータ
    expected_events_after_add = {
        "2025-07-25": [
            {
                "title": "既存会議",
                "start_time": "09:00",
                "end_time": "10:00",
                "memo": "既存のイベント"
            },
            {
                "title": "新しい会議",
                "start_time": "11:00",
                "end_time": "12:00",
                "memo": "新規追加イベント"
            }
        ],
        "2025-07-26": [ # 新しい日付のイベントも追加されるケースを想定
            {
                "title": "別日のイベント",
                "start_time": "09:00",
                "end_time": "10:00",
                "memo": "別日のイベント"
            }
        ]
    }

    # save_events をモックして、実際にファイルに書き込まれないようにする
    with patch('services.event_manager.save_events') as mock_save_events:
        # add_event を呼び出すための準備
        from services.event_manager import add_event

        # 既存のイベント辞書を渡してイベントを追加
        events_data = initial_events.copy() # オリジナルを保持するためコピー

        add_event(events_data, "2025-07-25", "新しい会議", "11:00", "12:00", "新規追加イベント")

        # 別日のイベントも追加して、setdefaultの動作も確認
        add_event(events_data, "2025-07-26", "別日のイベント", "09:00", "10:00", "別日のイベント")

        # 検証 1: events_data が正しく更新されたか
        assert events_data == expected_events_after_add

        # 検証 2: save_events がイベントが追加されるたびに呼び出されたか
        # add_eventが2回呼ばれているので、save_eventsも2回呼ばれるはず
        assert mock_save_events.call_count == 2

        # 検証 3: save_events が期待されるデータで呼び出されたか (最後の呼び出しをチェック)
        # 最後の save_events の呼び出しは expected_events_after_add と同じはず
        mock_save_events.assert_called_with(expected_events_after_add)


# UT-09: update_event() 既存イベントが正しく更新され、ファイルに保存される
def test_update_event():
    """
    update_event() が既存のイベントを更新し、
    save_events() を呼び出して保存することを確認する。
    """
    # 初期イベントデータ
    initial_events = {
        "2025-07-25": [
            {
                "title": "元のタイトル",
                "start_time": "09:00",
                "end_time": "10:00",
                "memo": "元のメモ"
            },
            {
                "title": "別のイベント",
                "start_time": "14:00",
                "end_time": "15:00",
                "memo": "変更されないイベント"
            }
        ]
    }

    # update_event が呼び出された後に期待されるイベントデータ
    expected_events_after_update = {
        "2025-07-25": [
            {
                "title": "更新されたタイトル", # ここが変更される
                "start_time": "09:30",        # ここも変更される
                "end_time": "10:30",          # ここも変更される
                "memo": "更新されたメモ"      # ここも変更される
            },
            {
                "title": "別のイベント",
                "start_time": "14:00",
                "end_time": "15:00",
                "memo": "変更されないイベント"
            }
        ]
    }

    # save_events をモックして、実際にファイルに書き込まれないようにする
    with patch('services.event_manager.save_events') as mock_save_events:
        # update_event を呼び出すための準備
        from services.event_manager import update_event # update_eventをインポート

        events_data = initial_events.copy() # オリジナルを保持するためコピー

        # イベントを更新 (インデックス0のイベント)
        update_event(events_data, "2025-07-25", 0, 
                     "更新されたタイトル", "09:30", "10:30", "更新されたメモ")

        # 検証 1: events_data が正しく更新されたか
        assert events_data == expected_events_after_update

        # 検証 2: save_events が呼び出されたか
        assert mock_save_events.called
        assert mock_save_events.call_count == 1 # 1回呼び出されるはず

        # 検証 3: save_events が期待されるデータで呼び出されたか
        mock_save_events.assert_called_with(expected_events_after_update)

        # --- 存在しないインデックスを更新しようとした場合のテスト ---
        events_data_no_change = initial_events.copy()
        initial_call_count = mock_save_events.call_count # ここまでの呼び出し回数を記録

        # 存在しないインデックスを更新しようとする
        update_event(events_data_no_change, "2025-07-25", 99, 
                     "存在しない更新", "", "", "")

        # 検証 4: イベントデータが変更されていないこと
        assert events_data_no_change == initial_events

        # 検証 5: save_events が追加で呼び出されていないこと
        assert mock_save_events.call_count == initial_call_count

        # --- 存在しない日付のイベントを更新しようとした場合のテスト ---
        events_data_no_change_date = initial_events.copy()
        initial_call_count_date = mock_save_events.call_count

        # 存在しない日付を更新しようとする
        update_event(events_data_no_change_date, "2025-08-01", 0, 
                     "存在しない日付", "", "", "")

        # 検証 6: イベントデータが変更されていないこと
        assert events_data_no_change_date == initial_events

        # 検証 7: save_events が追加で呼び出されていないこと
        assert mock_save_events.call_count == initial_call_count_date
        

# UT-10: delete_event() イベントが正しく削除され、ファイルに保存される
def test_delete_event():
    """
    delete_event() がイベントを正しく削除し、
    save_events() を呼び出して保存することを確認する。
    また、日付の全てのイベントが削除された場合に日付キーも削除されることを確認する。
    """
    # 初期イベントデータ
    initial_events = {
        "2025-07-25": [
            {
                "title": "イベントA",
                "start_time": "09:00",
                "end_time": "10:00",
                "memo": "メモA"
            },
            {
                "title": "イベントB",
                "start_time": "11:00",
                "end_time": "12:00",
                "memo": "メモB"
            }
        ],
        "2025-07-26": [
            {
                "title": "イベントC",
                "start_time": "14:00",
                "end_time": "15:00",
                "memo": "メモC"
            }
        ]
    }

    # 検証 1: 特定のイベントを削除した場合
    events_data_case1 = initial_events.copy()
    expected_events_case1 = {
        "2025-07-25": [
            {
                "title": "イベントB",
                "start_time": "11:00",
                "end_time": "12:00",
                "memo": "メモB"
            }
        ],
        "2025-07-26": [
            {
                "title": "イベントC",
                "start_time": "14:00",
                "end_time": "15:00",
                "memo": "メモC"
            }
        ]
    }
    with patch('services.event_manager.save_events') as mock_save_events:
        from services.event_manager import delete_event

        delete_event(events_data_case1, "2025-07-25", 0) # イベントAを削除

        assert events_data_case1 == expected_events_case1
        assert mock_save_events.called
        assert mock_save_events.call_count == 1
        mock_save_events.assert_called_with(expected_events_case1)

    # 検証 2: 日付の全てのイベントを削除した場合、日付キーも削除される
    events_data_case2 = {
        "2025-07-25": [
            {
                "title": "イベントD",
                "start_time": "09:00",
                "end_time": "10:00",
                "memo": "メモD"
            }
        ]
    }
    expected_events_case2 = {} # 空の辞書になるはず
    with patch('services.event_manager.save_events') as mock_save_events:
        from services.event_manager import delete_event

        delete_event(events_data_case2, "2025-07-25", 0) # イベントDを削除

        assert events_data_case2 == expected_events_case2
        assert mock_save_events.called
        assert mock_save_events.call_count == 1
        mock_save_events.assert_called_with(expected_events_case2)

    # 検証 3: 存在しないインデックスを削除しようとした場合（変更なし、save_eventsも呼ばれない）
    events_data_case3 = initial_events.copy()
    initial_call_count_case3 = 0 # 初期のsave_events呼び出しを0とする（新しいpatchブロックなので）
    with patch('services.event_manager.save_events') as mock_save_events:
        from services.event_manager import delete_event

        delete_event(events_data_case3, "2025-07-25", 99) # 存在しないインデックス

        assert events_data_case3 == initial_events # 変更されていないこと
        assert mock_save_events.call_count == initial_call_count_case3 # save_eventsが呼ばれていないこと

    # 検証 4: 存在しない日付のイベントを削除しようとした場合（変更なし、save_eventsも呼ばれない）
    events_data_case4 = initial_events.copy()
    initial_call_count_case4 = 0 # 初期のsave_events呼び出しを0とする
    with patch('services.event_manager.save_events') as mock_save_events:
        from services.event_manager import delete_event

        delete_event(events_data_case4, "2025-08-01", 0) # 存在しない日付

        assert events_data_case4 == initial_events # 変更されていないこと
        assert mock_save_events.call_count == initial_call_count_case4 # save_eventsが呼ばれていないこと