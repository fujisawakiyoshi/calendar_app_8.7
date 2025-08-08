# ui/event_dialog.py

import tkinter as tk
import sys
import os
from tkinter import messagebox
from services.event_manager import save_events
from ui.event_edit_dialog import EditDialog
from ui.theme import COLORS, FONTS
from services.theme_manager import ThemeManager
from ui.tooltip import ToolTip
from utils.resource import resource_path  # アイコン等のリソースパス解決用


class EventDialog(tk.Toplevel):
    """指定された日付のイベント一覧を表示・追加・編集・削除できるダイアログ"""

    def __init__(self, parent, date_key, events, on_update_callback):
        super().__init__(parent)
        self.parent = parent
        self.date_key = date_key
        self.events = events
        self.on_update_callback = on_update_callback

        # 初期設定
        self.withdraw()
        self.title(f"予定一覧 {self.date_key}")
        self.iconbitmap(resource_path("ui/icons/event_icon.ico"))
        self.configure(bg=ThemeManager.get('dialog_bg'))
        self.resizable(True, False)

        # 画面中央に配置
        self._place_relative_to_parent(width=380, height=260)

        # UI構築
        self.build_ui()

        # モーダル表示
        self.grab_set()
        self.deiconify()

    def _place_relative_to_parent(self, width, height):
        self.parent.update_idletasks()  # 親ウィンドウ位置の更新を反映

        # 親ウィンドウの左上座標とサイズを取得
        px = self.parent.winfo_x()
        py = self.parent.winfo_y()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()

        # 左右の余白を少しだけ確保して、左に寄せる
        # x = px + (pw * 0.1)  # 左端から10%の位置
        x = px + 10  # 例：左端から10ピクセル離す

        # 画面下部から少しだけ余白を確保して、下に配置
        # y = py + ph - height - (ph * 0.1) # 下端から10%の位置
        y = py + ph - height - 10 # 例：下端から10ピクセル離す

        self.geometry(f"{width}x{height}+{x}+{y}")

    def build_ui(self):
        """ヘッダー、リスト、ボタン、キーボードショートカットをまとめて生成"""
        self.create_header()
        self.create_listbox_area()
        self.create_button_area()
        self.bind_shortcuts()

    def create_header(self):
        """ウィンドウ上部に日付表示用ヘッダーを作成"""
        tk.Label(
            self,
            text=f"予定一覧（{self.date_key}）",
            font=(FONTS["base"][0], 13, "bold"),  # 少し大きめの太字フォント
            bg=ThemeManager.get('header_bg'),
            fg=ThemeManager.get('text'),
            pady=6
        ).pack(fill="x")

    def create_listbox_area(self):
        """イベント一覧の Listbox とスクロールバーを配置"""
        frame = tk.Frame(self, bg=ThemeManager.get('dialog_bg'))
        frame.pack(fill="both", expand=True, padx=12, pady=6)

        # イベント表示用 Listbox
        self.listbox = tk.Listbox(
            frame,
            font=FONTS["base"],
            bg=ThemeManager.get('bg'),
            fg=ThemeManager.get('text'),
            bd=0, relief="flat",
            selectbackground="#CCE8FF",  # 選択背景色
            selectforeground="#000000",  # 選択文字色
            activestyle="none",
            height=6, width=35,
            cursor="arrow"              # デフォルトカーソル
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        # ダブルクリックで編集
        self.listbox.bind("<Double-Button-1>", lambda e: self.edit_event())

        # 右側にスクロールバーを連携
        scrollbar = tk.Scrollbar(frame, command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.refresh_list()

    def create_button_area(self):
        """追加・編集・削除ボタンを作成して並べる"""
        frame = tk.Frame(self, bg=ThemeManager.get('dialog_bg'))
        frame.pack(fill="x", padx=14, pady=(0, 14))

        # ─── 1. 予定追加ボタン ────────────────────────────────
        self.add_icon = tk.PhotoImage(
            file=resource_path("ui/icons/plus_insert_icon.png")
        ).subsample(3,3)
        add_btn = tk.Button(
            frame,
            text="予定追加",
            image=self.add_icon,
            compound="right",          # テキスト右にアイコン
            command=self.add_event,
            font=FONTS["base_minus"],
            bg=ThemeManager.get('button_bg_add'),        # todayカラーで強調
            fg=ThemeManager.get('text'),
            relief="flat",
            padx=6, pady=2,
            cursor="hand2"
        )
        add_btn.pack(side="left")
        self.add_button_hover(add_btn, original_bg=ThemeManager.get('button_bg_add'))

        # ─── 2. 編集・削除ボタンを右側にまとめる ───────────────
        right_frame = tk.Frame(frame, bg=ThemeManager.get('dialog_bg'))
        right_frame.pack(side="right")

        # 編集ボタン
        self.edit_icon = tk.PhotoImage(
            file=resource_path("ui/icons/notes_edit_icon.png")
        ).subsample(3,3)
        edit_btn = tk.Button(
            right_frame,
            text="編集",
            image=self.edit_icon,
            compound="right",
            command=self.edit_event,
            font=FONTS['base_minus'],
            bg=ThemeManager.get('button_bg_edit'),    # パステルオレンジ
            fg=ThemeManager.get('text'),
            relief="flat",
            padx=6, pady=2,
            cursor="hand2"
        )
        edit_btn.pack(side="left", padx=4)
        self.add_button_hover(edit_btn, original_bg="#FFE7C1")

        # 削除ボタン
        self.delete_icon = tk.PhotoImage(
            file=resource_path("ui/icons/trash_icon.png")
        ).subsample(3,3)
        del_btn = tk.Button(
            right_frame,
            text="削除",
            image=self.delete_icon,
            compound="right",
            command=self.delete_event,
            font=FONTS["base_minus"],
            bg=ThemeManager.get('button_bg_delete'),    # パステルレッド
            activebackground="#F4B6B7",
            fg=ThemeManager.get('text'),
            relief="flat",
            padx=6, pady=2,
            cursor="hand2"
        )
        del_btn.pack(side="left", padx=4)
        self.add_button_hover(del_btn, original_bg="#F7C6C7")

    def bind_shortcuts(self):
        """Enter→編集、Delete→削除、Esc→閉じる のキーバインド設定"""
        self.listbox.bind("<Return>", lambda e: self.edit_event())
        self.listbox.bind("<Delete>", lambda e: self.delete_event())
        self.bind("<Escape>", lambda e: self.destroy())

    def refresh_list(self):
        """現在の events から Listbox を再描画"""
        self.listbox.delete(0, tk.END)
        for ev in self.events.get(self.date_key, []):
            text = f"{ev['start_time']}-{ev['end_time']}  {ev['title']}"
            if ev.get("memo"):
                text += f"  - {ev['memo']}"
            self.listbox.insert(tk.END, text)

    def add_event(self):
        """予定追加ダイアログを開き、新規予定を保存→再描画"""
        dialog = EditDialog(self, "予定の追加")
        dialog.wait_window()  # ダイアログ終了まで待機
        if dialog.result:
            title, st, et, memo = dialog.result
            self.events.setdefault(self.date_key, []).append({
                "title": title, "start_time": st, "end_time": et, "memo": memo
            })
            save_events(self.events)
            self.refresh_list()
            self.on_update_callback()

    def edit_event(self):
        """選択中の予定を編集ダイアログで更新→再描画"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("警告", "編集する予定を選択してください")
            return
        idx = sel[0]
        ev = self.events[self.date_key][idx]
        dialog = EditDialog(
            self, "予定の編集",
            default_title=ev["title"],
            default_start_time=ev["start_time"],
            default_end_time=ev["end_time"],
            default_content=ev.get("memo", "")
        )
        dialog.wait_window()
        if dialog.result:
            self.events[self.date_key][idx] = {
                "title": dialog.result[0],
                "start_time": dialog.result[1],
                "end_time": dialog.result[2],
                "memo": dialog.result[3]
            }
            save_events(self.events)
            self.refresh_list()
            self.on_update_callback()

    def delete_event(self):
        """選択中の予定を削除→再描画"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("警告", "削除する予定を選択してください")
            return
        idx = sel[0]
        del self.events[self.date_key][idx]
        if not self.events[self.date_key]:
            del self.events[self.date_key]
        save_events(self.events)
        self.refresh_list()
        self.on_update_callback()

    def add_button_hover(self, button, original_bg, hover_bg=None):
        """
        ボタンにマウスホバー時の背景色変化を設定。

        - original_bg: 元の背景色
        - hover_bg: ホバー時の色（未指定時は theme から取得）
        """
        if hover_bg is None:
            hover_bg = COLORS["button_hover"]

        button.bind("<Enter>", lambda e: button.config(bg=hover_bg))
        button.bind("<Leave>", lambda e: button.config(bg=original_bg))
        
