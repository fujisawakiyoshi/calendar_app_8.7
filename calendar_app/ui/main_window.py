# =============================================================
# ui/main_window.py 
# 目的:
#   - アプリケーションのエントリとなるメインウィンドウを構築
#   - カレンダー本体（CalendarView）とステータスバー（StatusBarWidget）を配置
#   - コントローラ（CalendarController）と連携して月移動・イベント編集・テーマ切替
# ポイント:
#   - Tkの起動時は一旦 withdraw() → UI準備 → after(0, deiconify) でチラつき低減
#   - resource_path() で実行形態（PyInstaller等）に依存しないアイコン解決
#   - ThemeManager から背景色を取得し、テーマ切替時は update_theme() を呼び出し
# =============================================================

import tkinter as tk
from datetime import datetime
import os

from controllers.calendar_controller import CalendarController
from ui.calendar_view import CalendarView
from ui.status_bar_widget import StatusBarWidget
from ui.theme import COLORS
from ui.event_dialog import EventDialog
from services.theme_manager import ThemeManager
from utils.resource import resource_path
from PIL import Image, ImageTk


class MainWindow:
    """アプリケーションのメインウィンドウを構成するクラス"""

    def __init__(self):
        # Tkインスタンス生成。初期表示は隠しておき、レイアウト完了後に表示する
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("Desktop Calendar")

        # タスクバーやウィンドウ左上に表示するアプリアイコンを設定
        ico_path = resource_path("ui/icons/event_icon.ico")
        if os.path.exists(ico_path):
            self.root.iconbitmap(ico_path)

        # 初期テーマの背景色を反映
        self.root.configure(bg=ThemeManager.get("header_bg"))
        self.root.resizable(True, True)          # ウィンドウのリサイズを許可
        self.root.attributes("-topmost", False) # 常に最前面にはしない

        # 画面中央付近（やや右上）に配置
        self._configure_window_position()

        # コントローラ（年月・祝日・イベント・天気の取得/更新を担う）
        self.controller = CalendarController()

        # 画面部品の構築（カレンダー本体とステータスバー）
        self._setup_ui()

        # レイアウト完了後にウィンドウを表示（チラつき抑制）
        self.root.after(0, self.root.deiconify)

    def _configure_window_position(self):
        # スクリーンサイズを取得し、ウィンドウの初期配置を計算
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        ww, wh = 560, 500
        # 画面中央からオフセット（+100, -80）した位置に出す
        x = (sw - ww)//2 + 100
        y = (sh - wh)//2 - 80
        self.root.geometry(f"{ww}x{wh}+{x}+{y}")

    def _setup_ui(self):
        # カレンダー本体を生成（クリック/前月/次月のコールバックはこのMainWindowのメソッド）
        self.calendar_view = CalendarView(
            self.root,
            self.controller.current_year,
            self.controller.current_month,
            self.controller.holidays,
            self.controller.events,
            on_date_click=self.open_event_dialog,
            on_prev=self.on_prev_month,
            on_next=self.on_next_month
        )

        # 画面下部にステータスバー（時計・天気・フラッシュメッセージ）をまとめる枠
        bottom_frame = tk.Frame(self.root, bg=ThemeManager.get('header_bg'))
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

        # 統合ウィジェット（テーマ切替は時計ボタン経由 → toggle_theme を呼ぶ）
        self.status_bar = StatusBarWidget(bottom_frame, on_theme_toggle=self.toggle_theme)

        # 初期の天気を表示（都度 controller から取得）
        self.status_bar.update_weather(self.controller.get_weather_info())

    def on_prev_month(self):
        # コントローラ側で年月を前月へ更新し、画面に反映
        self.controller.prev_month()
        self._refresh_calendar()

    def on_next_month(self):
        # コントローラ側で年月を次月へ更新し、画面に反映
        self.controller.next_month()
        self._refresh_calendar()

    def _refresh_calendar(self):
        # カレンダーへ最新の年月/祝日/イベントを流し込み、再描画
        self.calendar_view.update(
            self.controller.current_year,
            self.controller.current_month,
            self.controller.holidays,
            self.controller.events
        )
        # 天気も最新情報に更新
        self.status_bar.update_weather(self.controller.get_weather_info())

    def open_event_dialog(self, date_key):
        # 年月ラベルのダブルクリックによる特殊操作（"go_to_today"）に対応
        if date_key == "go_to_today":
            self.controller.go_to_today()
            self._refresh_calendar()
            return

        # それ以外はイベント編集ダイアログを開く
        try:
            from ui.event_dialog import EventDialog
            EventDialog(self.root, date_key, self.controller.events, self._refresh_calendar)
        except Exception as e:
            print(f"[ERROR] イベントダイアログでエラー発生: {e}")

    def toggle_theme(self):
        # テーマをトグル（ダーク↔ライト等）し、各UIに反映
        ThemeManager.toggle_theme()
        self.root.configure(bg=ThemeManager.get("header_bg"))
        # カレンダーUIのテーマ更新のみ（データ更新は行わない）
        self.calendar_view.update_theme()
        # ステータスバー（時計・天気）のテーマ更新
        self.status_bar.update_theme()

    def run(self):
        # Tk のメインループに入る
        self.root.mainloop()
