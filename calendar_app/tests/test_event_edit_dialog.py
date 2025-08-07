# C:\work_202507\calendar_app\tests\test_event_edit_dialog.py (抜粋)

import pytest
import tkinter as tk
from tkinter import ttk
from unittest.mock import MagicMock, patch

# テスト対象のクラスと依存モジュールをインポート
from ui.event_edit_dialog import EditDialog
from ui.theme import COLORS, FONTS, TITLE_CHOICES, TIME_CHOICES
from services.theme_manager import ThemeManager
from utils.resource import resource_path


# UT-16: EditDialog のデータ取得 (OKシナリオ)
def test_edit_dialog_data_acquisition_ok(mocker): # 関数名を変更 (UT-17のOKシナリオ用)
    """
    EditDialog がユーザー入力（タイトル、時間、内容）を正しく取得し、
    result 属性に格納することを確認する。
    """
    mocker.patch('tkinter.Toplevel')
    mocker.patch.object(tk, 'Label')
    mocker.patch.object(tk, 'Frame')
    mocker.patch.object(tk, 'Button')
    mocker.patch.object(ttk, 'Combobox')
    mocker.patch.object(tk, 'Entry')
    
    # ★ここを修正: tk.StringVar をモックする際に、__init__ の引数を受け取れるようにする ★
    # MagicMock はデフォルトで引数を受け取れるので、side_effect だけ調整します
    mock_title_var = MagicMock(spec=tk.StringVar) # spec=tk.StringVar は引数チェックを厳密にする
    mock_start_var = MagicMock(spec=tk.StringVar)
    mock_end_var = MagicMock(spec=tk.StringVar)
    mock_content_var = MagicMock(spec=tk.StringVar)
    
    # tkinter.StringVar をモックし、呼び出し時にこれらのモックインスタンスを返す
    # StringVar の __init__ は master 引数を受け取るので、MagicMock.side_effect が
    # それを正しく処理できるようにする必要があります。
    # MagicMock(return_value=...).master = ... のように、モックされたインスタンスの属性を直接設定します。
    # あるいは、_default_root をパッチします。
    
    # 最もシンプルな解決策: tkinter._get_default_root を直接モックしてエラーを回避する
    mocker.patch('tkinter._get_default_root', return_value=MagicMock())


    mocker.patch('tkinter.StringVar', side_effect=[
        mock_title_var, mock_start_var, mock_end_var, mock_content_var
    ])


    mocker.patch('services.theme_manager.ThemeManager.get', return_value='mock_color')
    mocker.patch('utils.resource.resource_path', return_value='mocked_icon_path')

    dialog = EditDialog(
        parent=MagicMock(),
        title="テストダイアログ",
        default_title="デフォルトタイトル",
        default_start_time="09:00",
        default_end_time="10:00",
        default_content="デフォルト内容"
    )

    # on_ok がこれらの .get() を呼び出すときに返される値を設定する
    mock_title_var.get.return_value = "新しいタイトル"
    mock_start_var.get.return_value = "11:00"
    mock_end_var.get.return_value = "12:00"
    mock_content_var.get.return_value = "新しい内容"

    mock_window_destroy = mocker.patch.object(dialog.window, 'destroy')
    
    # --- テスト実行 ---
    dialog.on_ok()

    # --- 検証 ---
    expected_result = (
        "新しいタイトル",
        "11:00",
        "12:00",
        "新しい内容"
    )
    
    assert dialog.result == expected_result
    mock_window_destroy.assert_called_once()


# UT-17: EditDialog のデータ取得 (キャンセルシナリオ)
def test_edit_dialog_data_acquisition_cancel(mocker):
    """
    EditDialog がキャンセルされたときに result 属性が None になることを確認する。
    """
    mocker.patch('tkinter.Toplevel')
    mocker.patch.object(tk, 'Label')
    mocker.patch.object(tk, 'Frame')
    mocker.patch.object(tk, 'Button')
    mocker.patch.object(ttk, 'Combobox')
    mocker.patch.object(tk, 'Entry')
    
    # ★ここも修正: tk._get_default_root をモックする ★
    mocker.patch('tkinter._get_default_root', return_value=MagicMock())
    
    mocker.patch('tkinter.StringVar') # StringVarの内部値はここでは不要
    mocker.patch('services.theme_manager.ThemeManager.get', return_value='mock_color')
    mocker.patch('utils.resource.resource_path', return_value='mocked_icon_path')

    dialog_cancel = EditDialog(parent=MagicMock(), title="キャンセルテスト")
    mock_window_destroy_cancel = mocker.patch.object(dialog_cancel.window, 'destroy')
    
    dialog_cancel.on_cancel()
    assert dialog_cancel.result is None
    mock_window_destroy_cancel.assert_called_once()