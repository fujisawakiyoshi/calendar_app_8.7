# C:\work_202507\calendar_app\tests\test_calendar_view.py

import pytest
import tkinter as tk # Tkinterウィジェットのテストのため
from unittest.mock import MagicMock, patch # モック機能のため

# テスト対象のクラスと、その依存関係にあるモジュールをインポート
from ui.calendar_view import CalendarView
from services.theme_manager import ThemeManager # ThemeManagerをモックするため
from ui.tooltip import ToolTip # ToolTipがインスタンス化されるため

# CalendarController をモックするためのダミークラス (必要であれば)
class MockCalendarController:
    def __init__(self, year, month):
        self.current_year = year
        self.current_month = month
        self.holidays = {}
        self.events = {}
    def load_data(self): pass
    def prev_month(self): pass
    def next_month(self): pass
    def get_calendar_days(self): return [] # ダミー

# CalendarViewのインスタンスを作成するためのフィクスチャ
@pytest.fixture
def calendar_view_fixture(mocker): # pytest-mock の mocker フィクスチャを使用
    # Tkinterのルートウィンドウをモック (テスト中にGUIウィンドウが開かないようにする)
    # MagicMock を使って Tk() と Frame() の呼び出しを記録し、実際のウィジェット生成を防ぐ
    mocker.patch('tkinter.Tk')
    mocker.patch('tkinter.Frame')
    mocker.patch('tkinter.Label')
    mocker.patch('tkinter.Button')
    mocker.patch('tkinter.Scrollbar')

    # CalendarView が依存する ThemeManager や ToolTip をモック
    mocker.patch('services.theme_manager.ThemeManager.get', return_value='mock_color')
    mocker.patch('services.theme_manager.ThemeManager.is_dark_mode', return_value=False)
    mocker.patch('ui.tooltip.ToolTip') # ToolTipのインスタンス化をモック

    # generate_calendar_matrix もモック (utils/calendar_utils.py)
    # test_get_calendar_days で成功した内容をベースにダミーデータを返すようにする
    mock_matrix = [
        [0, 0, 1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10, 11, 12],
        [13, 14, 15, 16, 17, 18, 19],
        [20, 21, 22, 23, 24, 25, 26],
        [27, 28, 29, 30, 31, 0, 0]
    ]
    mocker.patch('utils.calendar_utils.generate_calendar_matrix', return_value=mock_matrix)

    # PhotoImage をモック (存在しない画像ファイルへのアクセスを防ぐ)
    mocker.patch('tkinter.PhotoImage') # .subsample() もチェインでモックできるようにする

    # CalendarView のコールバック関数をモック
    mock_on_date_click = MagicMock()
    mock_on_prev = MagicMock()
    mock_on_next = MagicMock()

    # CalendarView のインスタンスを生成
    view = CalendarView(
        parent=MagicMock(), # 親ウィジェットもモック
        year=2025,
        month=7,
        holidays={"2025-07-21": "海の日"}, # ダミー祝日
        events={"2025-07-03": [
            {"title": "イベントA", "start_time": "10:00", "end_time": "11:00", "memo": "テストメモ"}
            ]},
        on_date_click=mock_on_date_click,
        on_prev=mock_on_prev,
        on_next=mock_on_next
    )
    return view, mock_on_date_click, mock_on_prev, mock_on_next

# UT-14: CalendarView が CalendarController のデータに基づき日付表示を正しく更新する
def test_calendar_view_update_display(calendar_view_fixture, mocker):
    """
    CalendarView が新しいデータに基づいてカレンダー表示を正しく更新することを確認する。
    """
    view, mock_on_date_click, mock_on_prev, mock_on_next = calendar_view_fixture

    # --- 準備 ---
    # update() メソッドに渡す新しいデータ
    new_year, new_month = 2026, 1
    new_holidays = {"2026-01-01": "元日"}
    new_events = {"2026-01-05": [{"title": "新年のイベント"}]}

    # _draw_header, _draw_weekday_labels, _draw_days が呼ばれることを検証するためにモック
    mocker.patch.object(view, '_draw_header')
    mocker.patch.object(view, '_draw_weekday_labels')
    mocker.patch.object(view, '_draw_days')
    mocker.patch.object(view, '_clear') # render()で呼ばれるため

    # --- テスト実行 ---
    view.update(new_year, new_month, new_holidays, new_events)

    # --- 検証 ---
    # 1. view の属性が更新されたか
    assert view.year == new_year
    assert view.month == new_month
    assert view.holidays == new_holidays
    assert view.events == new_events

    # 2. render() が呼ばれ、その中で描画メソッドが呼ばれたか
    # update() は render() を呼び出すので、render()の中のメソッドが呼ばれる
    view._clear.assert_called_once()
    view._draw_header.assert_called_once()
    view._draw_weekday_labels.assert_called_once()
    view._draw_days.assert_called_once()

    # 3. render() が呼ばれた後、月ラベルのテキストが更新されることを確認 (これは _draw_header の内部検証だが、ここではメソッド呼び出しで代替)
    # 実際のラベルオブジェクトはモックされているため、直接テキストを検証できない。
    # 代わりに、_draw_header が正しい引数で呼び出されたかを検証するか、
    # _draw_header のモックの引数を検証する。今回はメソッドが呼ばれたことだけ検証。

    # --- _draw_days の詳細な内部ロジックの検証 ---
    # _draw_days は日付セルを生成し、イベントや祝日によって色を変える
    # このテストは update() のテストなので、render() が正しく動くことを前提とするが、
    # _draw_days の中で tk.Label や ToolTip が呼ばれることを確認することも可能

    # 例: _draw_days の中で tk.Label が呼ばれたことを検証
    # (ただし、これは_draw_daysの責任であり、update()の直接の責任ではないため、別のテストで検証する方が良い)
    # mocker.patch('tkinter.Label') # もし CalendarView.__init__ で Label が呼ばれるなら、ここでモック
    # view._draw_days() の中で呼ばれる Label の呼び出しを検証
    # tkinter.Label.call_count は、各日のラベル生成でたくさん呼ばれるので注意

    # このテストは update() が render() を適切に呼び、属性が更新されることに焦点を当てています。
    # 実際のUI要素のテストは別途詳細なテストが必要です。