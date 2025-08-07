# ui/main_window.py

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
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("Desktop Calendar")

        ico_path = resource_path("ui/icons/event_icon.ico")
        if os.path.exists(ico_path):
            self.root.iconbitmap(ico_path)

        self.root.configure(bg=ThemeManager.get("header_bg"))
        self.root.resizable(True, True)
        self.root.attributes("-topmost", False)

        self._configure_window_position()
        self.controller = CalendarController()
        self._setup_ui()
        self.root.after(0, self.root.deiconify)

    def _configure_window_position(self):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        ww, wh = 560, 500
        x = (sw - ww)//2 + 100
        y = (sh - wh)//2 - 80
        self.root.geometry(f"{ww}x{wh}+{x}+{y}")

    def _setup_ui(self):
        # カレンダー
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

        # 時計と天気をまとめるためのフレーム
        bottom_frame = tk.Frame(self.root, bg=ThemeManager.get('header_bg'))
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

        # 統合ウィジェット（時計＋天気＋メッセージ）
        self.status_bar = StatusBarWidget(bottom_frame, on_theme_toggle=self.toggle_theme)

        # 天気を初期表示
        self.status_bar.update_weather(self.controller.get_weather_info())

    def on_prev_month(self):
        self.controller.prev_month()
        self._refresh_calendar()

    def on_next_month(self):
        self.controller.next_month()
        self._refresh_calendar()

    def _refresh_calendar(self):
        self.calendar_view.update(
            self.controller.current_year,
            self.controller.current_month,
            self.controller.holidays,
            self.controller.events
        )
        # 天気も更新
        self.status_bar.update_weather(self.controller.get_weather_info())

    def open_event_dialog(self, date_key):
        if date_key == "go_to_today":
            self.controller.go_to_today()
            self._refresh_calendar()
            return

        try:
            from ui.event_dialog import EventDialog
            EventDialog(self.root, date_key, self.controller.events, self._refresh_calendar)
        except Exception as e:
            print(f"[ERROR] イベントダイアログでエラー発生: {e}")

    def toggle_theme(self):
        ThemeManager.toggle_theme()
        self.root.configure(bg=ThemeManager.get("header_bg"))
        # カレンダーUIのテーマ更新のみ（データ更新は行わない）
        self.calendar_view.update_theme()
        # 時計・天気ウィジェットのテーマ更新
        self.status_bar.update_theme()

    def run(self):
        self.root.mainloop()
