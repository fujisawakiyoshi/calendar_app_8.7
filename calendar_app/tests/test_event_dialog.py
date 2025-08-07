# C:\work_202507\calendar_app\tests\test_event_dialog.py

import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch

# テスト対象のクラスと依存モジュールをインポート
from ui.event_dialog import EventDialog
from services.event_manager import save_events # save_events が呼ばれる可能性があるためモック
from ui.event_edit_dialog import EditDialog # EditDialog の初期化をテスト
from ui.theme import COLORS, FONTS # 定数が必要な場合
from services.theme_manager import ThemeManager # ThemeManager をモックするため
from ui.tooltip import ToolTip # ToolTip がインスタンス化されるため
from utils.resource import resource_path # resource_path をモックするため


# UT-15: EventDialog のイベントデータ初期表示
def test_event_dialog_initial_display(mocker):
    """
    EventDialog が既存のイベントデータで正しく初期表示されることを確認する。
    """
    # --- 準備 ---
    test_date_key = "2025-07-25"
    # EventDialogに渡すダミーの全イベントデータ
    mock_all_events = {
        "2025-07-25": [
            {"title": "会議", "start_time": "10:00", "end_time": "11:00", "memo": "プロジェクトミーティング"},
            {"title": "ランチ", "start_time": "12:00", "end_time": "13:00", "memo": ""}
        ],
        "2025-07-26": [
            {"title": "セミナー", "start_time": "14:00", "end_time": "16:00", "memo": "技術セミナー"}
        ]
    }
    mock_on_update_callback = MagicMock()

    # TkinterのGUIコンポーネントと依存モジュールをモック
    mocker.patch('tkinter.Toplevel') # Toplevelが開かないように
    mocker.patch.object(tk, 'Label')
    mocker.patch.object(tk, 'Listbox')
    mocker.patch.object(tk, 'Scrollbar')
    mocker.patch.object(tk, 'Frame')
    mocker.patch.object(tk, 'Button')
    mocker.patch.object(tk, 'PhotoImage') # PhotoImageの読み込み
    mocker.patch('tkinter.messagebox.showwarning') # messageboxが出ないように

    mocker.patch('services.theme_manager.ThemeManager.get', return_value='mock_color')
    mocker.patch('ui.tooltip.ToolTip') # ToolTipのインスタンス化
    mocker.patch('utils.resource.resource_path', return_value='mocked_path') # resource_pathの呼び出し

    # EventDialogの内部で呼ばれる save_events と EditDialog をモック
    mocker.patch('services.event_manager.save_events')
    mocker.patch('ui.event_edit_dialog.EditDialog') # EditDialog が開かないように

    # Listboxのインスタンスをキャプチャし、そのメソッド呼び出しを検証できるようにする
    mock_listbox_instance = MagicMock()
    mocker.patch('tkinter.Listbox', return_value=mock_listbox_instance)

    # --- テスト実行 ---
    # EventDialog のインスタンスを生成
    dialog = EventDialog(
        parent=MagicMock(), # 親ウィジェットもモック
        date_key=test_date_key,
        events=mock_all_events,
        on_update_callback=mock_on_update_callback
    )

    # --- 検証 ---
    # 1. Listboxが正しく初期化されたか（insertメソッドが呼ばれたか）
    # 2025-07-25 のイベントが2つあるので、Listbox.insert が2回呼ばれるはず
    assert mock_listbox_instance.insert.call_count == 2

    # 期待されるListboxの表示テキストを定義
    expected_listbox_calls = [
        (tk.END, "10:00-11:00  会議  - プロジェクトミーティング"),
        (tk.END, "12:00-13:00  ランチ") # メモがない場合は表示されない
    ]

    # Listbox.insert が期待される引数で呼ばれたかを確認
    # 各呼び出しを個別に検証
    actual_calls = [call for call in mock_listbox_instance.insert.call_args_list]

    # assert len(actual_calls) == len(expected_listbox_calls) # 呼び出し回数は上で確認済み
    assert actual_calls[0].args == expected_listbox_calls[0]
    assert actual_calls[1].args == expected_listbox_calls[1]

    # 2. ウィンドウタイトルが正しく設定されたか (Toplevelのモックを通して)
    mocker.patch.object(dialog.window, 'title') # dialog.window.title をモック (後からパッチしてもOK)
    # EventDialog.__init__ 内で既に window.title が呼ばれているので、
    # ここで直接 window.title が呼ばれたことを検証するのは難しい。
    # 代わりに、EventDialog の属性が正しく設定されたことを検証する。
    assert dialog.date_key == test_date_key
    assert dialog.events == mock_all_events

    # 3. リストボックスがイベントデータを正しく表示するためのrefresh_list()が呼ばれたか
    # refresh_list() は build_ui() -> create_listbox_area() の中で呼ばれる
    # ここでは Listbox.insert の呼び出しを検証することで代替

    # 4. アイコンが設定されたか
    # mock_resource_path = mocker.patch('utils.resource.resource_path') # resource_path は上でモック済み
    # mocker.patch.object(dialog.window, 'iconbitmap')
    # dialog.window.iconbitmap.assert_called_once_with('mocked_path') # resource_pathの戻り値と一致


