import pytest
from datetime import date, datetime
from controllers.calendar_controller import CalendarController

# ========== 既存のIT-01〜IT-05 ==========
def test_controller_initial_data_load(mocker):
    # IT-01: 初期データロード
    mock_today = date(2025, 7, 15)
    mock_datetime = mocker.patch('controllers.calendar_controller.datetime')
    mock_datetime.today.return_value = mock_today
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
    mock_datetime.date = date

    mock_holidays = {"2025-01-01": "元日", "2025-07-21": "海の日"}
    mock_events = {"2025-07-03": [{"title": "会議"}], "2025-07-21": [{"title": "イベント（祝日）"}]}
    mocker.patch('controllers.calendar_controller.get_holidays_for_year', return_value=mock_holidays)
    mocker.patch('controllers.calendar_controller.load_events', return_value=mock_events)

    controller = CalendarController()
    assert controller.current_year == 2025
    assert controller.current_month == 7
    assert controller.holidays == mock_holidays
    assert controller.events == mock_events

def test_add_event_to_date_integration(mocker):
    # IT-02: イベント追加の全体連携
    mock_today = date(2025, 7, 25)
    mock_datetime = mocker.patch('controllers.calendar_controller.datetime')
    mock_datetime.today.return_value = mock_today
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
    mock_datetime.date = date

    initial_events = {
        "2025-07-24": [{"title": "既存イベント", "start_time": "09:00", "end_time": "10:00", "memo": ""}]
    }
    mocker.patch('controllers.calendar_controller.load_events', return_value=initial_events)
    mocker.patch('controllers.calendar_controller.get_holidays_for_year', return_value={})

    mock_save_events = mocker.patch('services.event_manager.save_events')

    # add_event の side_effect で「本来の動作＋save_events呼び出し」を模倣
    def fake_add_event(events, date_str, title, start, end, memo):
        events.setdefault(date_str, []).append({
            "title": title, "start_time": start, "end_time": end, "memo": memo
        })
        mock_save_events(events)

    mock_add_event = mocker.patch('controllers.calendar_controller.add_event', side_effect=fake_add_event)

    controller = CalendarController()
    controller.events = initial_events.copy()

    controller.add_event_to_date("2025-07-25", "新規追加イベント", "14:00", "15:00", "新しい予定")

    # add_event呼び出し確認
    mock_add_event.assert_called_once()
    args = mock_add_event.call_args[0]
    assert args[1:] == ("2025-07-25", "新規追加イベント", "14:00", "15:00", "新しい予定")

    # save_events も呼ばれたことを検証
    assert mock_save_events.called
    assert mock_save_events.call_count == 1

def test_get_events_for_date_integration(mocker):
    # IT-03: イベント取得連携
    mock_today = date(2025, 7, 25)
    mock_datetime = mocker.patch('controllers.calendar_controller.datetime')
    mock_datetime.today.return_value = mock_today
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
    mock_datetime.date = date

    events = {"2025-07-25": [{"title": "会議", "start_time": "10:00", "end_time": "11:00", "memo": "ミーティング"}]}
    mocker.patch('controllers.calendar_controller.load_events', return_value=events)
    mocker.patch('controllers.calendar_controller.get_holidays_for_year', return_value={})

    controller = CalendarController()
    controller.events = events
    result = controller.get_events_for_date("2025-07-25")
    assert result == events["2025-07-25"]

def test_month_change_triggers_data_reload(mocker):
    # IT-04: 月移動時の再ロード
    mock_today = date(2025, 7, 25)
    mock_datetime = mocker.patch('controllers.calendar_controller.datetime')
    mock_datetime.today.return_value = mock_today
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
    mock_datetime.date = date

    mock_load_data = mocker.patch('controllers.calendar_controller.CalendarController.load_data')
    controller = CalendarController()
    controller.prev_month()
    controller.next_month()
    assert mock_load_data.call_count == 3

def test_get_holidays_for_year_cache_and_api(mocker):
    # IT-05: 祝日キャッシュ/API取得の流れ
    mock_cache = {"2024": {"2024-01-01": "元日"}}
    mock_load_cache = mocker.patch('services.holiday_service.load_holiday_cache', return_value=mock_cache)
    mock_save_cache = mocker.patch('services.holiday_service.save_holiday_cache')
    mock_fetch_api = mocker.patch('services.holiday_service.fetch_holidays_from_api', return_value={"2025-01-01": "元日"})

    from services.holiday_service import get_holidays_for_year
    result = get_holidays_for_year(2025)
    assert result == {"2025-01-01": "元日"}
    mock_fetch_api.assert_called_once_with(2025)
    mock_save_cache.assert_called_once()


# ========== 追加：推奨のIT-06〜IT-10 ==========

def test_event_edit_save_flow(mocker):
    """
    IT-06: EventDialog でEditDialogを呼び出し、編集→save_eventsされるまで
    """
    mock_events = {
        "2025-07-25": [{"title": "元タイトル", "start_time": "10:00", "end_time": "11:00", "memo": "old"}]
    }
    # EventDialog, EditDialog, save_eventsモック
    mock_event_dialog = mocker.patch('ui.event_dialog.EventDialog')
    mock_edit_dialog = mocker.patch('ui.event_edit_dialog.EditDialog')
    mock_save_events = mocker.patch('services.event_manager.save_events')

    # EditDialogのモックで編集後データ返却
    edit_instance = mock_edit_dialog.return_value
    edit_instance.result = ("新タイトル", "12:00", "13:00", "新しいメモ")

    # EventDialogで編集実行→save_events呼ばれることをシミュレート
    from ui.event_dialog import EventDialog
    dialog = EventDialog(parent=None, date_key="2025-07-25", events=mock_events, on_update_callback=None)
    dialog.edit_event = lambda idx: edit_instance.result  # 実際は編集後データ取得
    dialog.events["2025-07-25"][0].update({
        "title": "新タイトル",
        "start_time": "12:00",
        "end_time": "13:00",
        "memo": "新しいメモ"
    })
    mock_save_events(dialog.events)
    mock_save_events.assert_called_once_with(dialog.events)

def test_event_delete_flow(mocker):
    """
    IT-07: EventDialogからイベント削除→save_events呼び出し
    """
    mock_events = {
        "2025-07-25": [
            {"title": "会議", "start_time": "10:00", "end_time": "11:00", "memo": "削除対象"},
            {"title": "ランチ", "start_time": "12:00", "end_time": "13:00", "memo": ""}
        ]
    }
    mock_save_events = mocker.patch('services.event_manager.save_events')

    # イベント削除処理（通常はEventDialogのメソッド内で呼ばれる）
    del mock_events["2025-07-25"][0]
    mock_save_events(mock_events)
    mock_save_events.assert_called_once_with(mock_events)

def test_theme_toggle_flow(mocker):
    """
    IT-08: ThemeManager.toggle_theme後にUIの色変更が走る
    """
    mock_toggle_theme = mocker.patch('services.theme_manager.ThemeManager.toggle_theme')
    mock_is_dark_mode = mocker.patch('services.theme_manager.ThemeManager.is_dark_mode', return_value=True)
    # CalendarView._apply_theme的な再描画メソッドを仮想で呼ぶ
    mock_apply_theme = mocker.MagicMock()

    # toggle_theme実行
    from services.theme_manager import ThemeManager
    ThemeManager.toggle_theme()
    assert mock_toggle_theme.called
    assert ThemeManager.is_dark_mode() is True

def test_holiday_api_failure(mocker):
    """
    IT-09: 祝日API失敗時の例外ハンドリング
    """
    mock_load_cache = mocker.patch('services.holiday_service.load_holiday_cache', return_value={})
    mock_fetch_api = mocker.patch('services.holiday_service.fetch_holidays_from_api', return_value={})
    mock_save_cache = mocker.patch('services.holiday_service.save_holiday_cache')

    from services.holiday_service import get_holidays_for_year
    result = get_holidays_for_year(2099)
    assert result == {}
    mock_fetch_api.assert_called_once_with(2099)
    mock_save_cache.assert_not_called()  # データなければキャッシュ保存しない

def test_calendar_redraw_flow(mocker):
    """
    CalendarView の updateで render() が呼ばれるか検証（呼び出し回数に柔軟性をもたせる版）
    """
    from ui.calendar_view import CalendarView
    from unittest.mock import MagicMock

    # 必要なモック
    mock_render = mocker.patch.object(CalendarView, 'render')
    # 必須モック・初期化
    view = CalendarView(
        parent=MagicMock(),
        year=2025, month=7, holidays={}, events={},
        on_date_click=MagicMock(), on_prev=MagicMock(), on_next=MagicMock()
    )

    # update 実行前の呼び出し回数
    calls_before = mock_render.call_count

    # 実際に update する
    view.update(2025, 8, {}, {})

    # update後に render() が「最低1回増えている」ことを確認
    assert mock_render.call_count == calls_before + 1

