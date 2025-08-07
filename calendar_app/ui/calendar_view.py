import tkinter as tk
from datetime import datetime
from utils.calendar_utils import generate_calendar_matrix
from ui.theme import COLORS, FONTS
from services.theme_manager import ThemeManager
from ui.tooltip import ToolTip

class CalendarView:
    """カレンダー表示用の UI コンポーネント"""

    def __init__(
        self,
        parent,
        year: int,
        month: int,
        holidays: dict,
        events: dict,
        on_date_click,  # 日付クリック時コールバック
        on_prev,        # 前月ボタンコールバック
        on_next         # 次月ボタンコールバック
    ):
        self.parent = parent
        self.year = year
        self.month = month
        self.holidays = holidays
        self.events = events
        self.on_date_click = on_date_click
        self.on_prev = on_prev
        self.on_next = on_next
        self.footer_frame = None
        self.holiday_label = None

        # カレンダー全体を入れるフレームを作成
        self.frame = tk.Frame(self.parent, bg=ThemeManager.get('bg'))
        self.frame.pack(padx=15, pady=15)

        # 初回描画
        self.render()

    def update(self, year, month, holidays, events):
        """
        外部から年月・祝日・イベントを更新したいときに呼ぶ。
        再描画を行う。
        """
        self.year = year
        self.month = month
        self.holidays = holidays
        self.events = events
        self.render()
    
    def _draw_footer(self):
        """
        カレンダーの最下部にフッターを描画する関数。
        左端にその月の祝日名、右端に時計を表示します。
        """
        # 既存のフッターフレームがあれば、破棄して再描画に備える
        if self.footer_frame:
            self.footer_frame.destroy()

        # 新しいフッターフレームを作成し、カレンダー下部に配置
        # gridのrow=8, column=0はカレンダーのセル（7行分）の次の行を想定
        self.footer_frame = tk.Frame(self.frame, bg=ThemeManager.get('header_bg'))
        self.footer_frame.grid(row=8, column=0, columnspan=7, sticky="we", pady=(8, 0))

        # ---- 左端：祝日名を表示する部分 ----
        # `self.holidays`から、現在表示している月（self.month）の祝日を抽出
        holidays_this_month = [
            (d, name)
            for d, name in self.holidays.items()
            if int(d[5:7]) == self.month
        ]

        # 祝日があれば「日付 祝日名」の形式で文字列を作成
        if holidays_this_month:
            holiday_strs = [f"{int(d[8:]):d}日 {name}" for d, name in holidays_this_month]
            text = " | ".join(holiday_strs)
        else:
            # 祝日がなければ空の文字列を設定
            text = "今月は祝日ありません"

        # 祝日名を表示するラベルを作成し、フッターの左側に配置
        self.holiday_label = tk.Label(
            self.footer_frame,
            text=text,
            font=FONTS['small_holiday'],
            bg=ThemeManager.get('header_bg'),
            fg=ThemeManager.get('holiday_label_fg'),
            anchor="w",
            justify="left",
            wraplength=280      
        )
        self.holiday_label.pack(side="left", padx=(5, 0)) 

    def render(self):
        """ヘッダー／曜日ラベル／日付セルを再構築"""
        self._clear()
        self._draw_header()
        self._draw_weekday_labels()
        self._draw_days()
        self._draw_footer()

    def _clear(self):
        """前回描画したウィジェットをすべて破棄"""
        for widget in self.frame.winfo_children():
            widget.destroy()

    def _draw_header(self):
        """年・月と前後移動ボタンを表示するヘッダーを作成"""
        header = tk.Frame(self.frame, bg=ThemeManager.get('header_bg'))
        header.grid(row=0, column=0, columnspan=7, sticky='nsew')

        # 両ボタンの間にスペース
        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(3, weight=1)

        # 前月ボタン
        prev_btn = tk.Button(
            header,
            text='＜',
            command=self.on_prev,
            bg=ThemeManager.get('header_bg'),
            fg=ThemeManager.get('text'),
            relief='flat',
            font=FONTS['header'],
            width=3,
            cursor='hand2'
        )
        prev_btn.grid(row=0, column=0, padx=6, pady=6)
        self._add_button_hover(prev_btn, ThemeManager.get('header_bg'))

        # 年月ラベル（ダブルクリックで今月へ）
        self.month_label = tk.Label(
            header,
            text=f"{self.year}年 {self.month}月",
            font=FONTS['header'],
            bg=ThemeManager.get('header_bg'),
            fg=ThemeManager.get('text'),
            padx=12,
            pady=6
        )
        self.month_label.grid(row=0, column=2, padx=6, pady=6)
        
        # ダブルクリックイベントをバインド
        self.month_label.bind("<Double-1>", self._go_to_today)

        # 次月ボタン
        next_btn = tk.Button(
            header,
            text='＞',
            command=self.on_next,
            bg=ThemeManager.get('header_bg'),
            fg=ThemeManager.get('text'),
            relief='flat',
            font=FONTS['header'],
            width=3,
            cursor='hand2'
        )
        next_btn.grid(row=0, column=4, padx=6, pady=6)
        self._add_button_hover(next_btn, ThemeManager.get('header_bg'))

    def _draw_weekday_labels(self):
        """日～土の曜日ラベルを表示"""
        days = ['日', '月', '火', '水', '木', '金', '土']
        for idx, wd in enumerate(days):
            fg = ThemeManager.get('text')
            if wd in ('日', '土'):
                fg = '#9D5C64'  

            tk.Label(
                self.frame,
                text=wd,
                font=FONTS['base'],
                bg=ThemeManager.get('header_bg'),
                fg=fg,
                width=6,
                pady=4
            ).grid(row=1, column=idx, padx=1, pady=4)

    def _draw_days(self):
        """各日付セルを生成し、イベントや祝日を反映"""
        matrix = generate_calendar_matrix(self.year, self.month)

        for row_index, week in enumerate(matrix, start=2):
                for col_index, day in enumerate(week):
                    if not day:
                        text, key = '', None
                        fg_color = ThemeManager.get('text') 
                    else:
                        key = f"{self.year}-{self.month:02d}-{day:02d}"
                        text = str(day)
                        # 今日だけ色を変える
                        fg_color = ThemeManager.get('today_fg') if self._is_today(day) else ThemeManager.get('text')
                    
                    bg = self._get_day_bg(day, col_index, key)

                    lbl = tk.Label(
                        self.frame,
                        text=text,
                        font=FONTS['base'],
                        bg=bg,
                        fg=fg_color,
                        width=6,
                        height=2,
                        bd=1,
                        padx=2,  # 左右の余白を増やす
                        pady=2,  # 上下の余白を減らす
                        relief='ridge'
                    )
                    lbl.grid(row=row_index, column=col_index, padx=1, pady=1)

                    # ↓この下に追加！祝日セルに㊗マークバッジを右上に表示
                    badge = None
                    if key in self.holidays:
                        badge = tk.Label(
                            self.frame,
                            text="㊗",
                            font=("Meiryo", 12, "bold"),
                            fg=ThemeManager.get('badge_fg', ThemeManager.get('bg')),
                            bg=ThemeManager.get('badge_bg', bg),
                            bd=0
                        )
                        # セルの中で右上に配置（relx=1.0で右端、y=+4で少し下げる）
                        badge.place(in_=lbl, relx=1.0, rely=0.0, anchor="ne", x=-2, y=2)
                    
                    # --- ホバー効果（祝日バッジがあれば連動） ---
                    self._add_hover_effect(lbl, bg, badge=badge)
                    
                    if day:
                        # クリック時の挙動設定
                        lbl.bind('<Button-1>', lambda e, d=key: self.on_date_click(d))
                        # イベントがある日はツールチップ表示
                        if key in self.events:
                            tip_text = self._make_event_summary(self.events[key])
                            ToolTip(lbl, tip_text)

    def _get_day_bg(self, day, col, key) -> str:
        """
        日付セルの背景色を決定。
        優先度：空セル → イベント → 祝日 → 今日 → 日曜 → 土曜 → 通常
        """
        if not day:
            return ThemeManager.get('bg')
        if key in self.events:
            return ThemeManager.get('highlight')
        if key in self.holidays:
            return ThemeManager.get('accent')
        if self._is_today(day):
            return ThemeManager.get('today')
        if col in (0, 6):  # 土日どちらも
            return ThemeManager.get('weekend')
        return ThemeManager.get('bg')

    def _is_today(self, day) -> bool:
        """指定した日付が「今日」であるかを判定"""
        now = datetime.today()
        return (
            now.year == self.year and
            now.month == self.month and
            now.day == day
        )

    def _add_hover_effect(self, widget, orig_bg, badge=None):
        """日付セルと㊗バッジのホバー効果"""
        hover_bg = ThemeManager.get("hover", "#D0EBFF")

        def on_enter(e):
            widget.config(bg=hover_bg)
            if badge:
                badge.config(bg=hover_bg)

        def on_leave(e):
            widget.config(bg=orig_bg)
            if badge:
                badge.config(bg=orig_bg)

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    def _add_button_hover(self, button, orig_bg, hover_bg='#F0F0F0'):
        """ナビゲーションボタンにホバー効果を追加"""
        button.bind('<Enter>', lambda e: button.config(bg=hover_bg))
        button.bind('<Leave>', lambda e: button.config(bg=orig_bg))
        
    def _go_to_today(self, event):
        """年月ラベルをダブルクリック → 今月に戻る"""
        self.on_date_click("go_to_today")

    def _make_event_summary(self, events_list) -> str:
        """
        ツールチップ用に、複数イベントを「時刻〜タイトル（メモ）」形式で整形
        改行区切りで返す
        """
        lines = []
        for ev in events_list:
            times = f"{ev['start_time']}〜{ev['end_time']}"
            line = f"{times} {ev['title']}"
            if ev.get('memo'):
                line += f" - {ev['memo']}"
            lines.append(line)
        return '\n'.join(lines)
    
    def update_theme(self):
        """テーマ切り替え時に呼び出され、カレンダー全体を再描画する"""
        self.frame.config(bg=ThemeManager.get('bg'))
        self.render()  # テーマに基づき再描画（色もすべて更新される）
