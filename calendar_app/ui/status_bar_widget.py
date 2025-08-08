# =============================================================
# StatusBarWidget
# 目的:
#   左側に天気（アイコン＋テキスト）、右側にフラッシュメッセージと時計を表示。
#   時計はクリックでテーマ切替（on_theme_toggle）を呼び出す想定。
# 要点:
#   - ThemeManager から配色を取得し、update_theme() で一括更新
#   - Pillow で天気アイコンを読み込み（PhotoImageの参照を保持）
#   - after(1000, ...) で1秒ごとに時計を更新（スレッド不要／安全）
#   - flash_message_for_seconds() で一定時間だけメッセージを表示
# =============================================================

# --- 標準/外部/アプリ内 import ---
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk
import os
import sys

from ui.theme import FONTS
from services.theme_manager import ThemeManager
from utils.resource import resource_path


class StatusBarWidget:
    def __init__(self, parent, on_theme_toggle=None):
        # 親ウィジェットへの参照と、テーマ切替時に呼ばれるコールバックを保持
        self.parent = parent
        self.on_theme_toggle = on_theme_toggle

        # 現在のテーマから配色を取得（ヘッダ背景／通常テキスト／時計テキスト色）
        bg = ThemeManager.get("header_bg")
        fg = ThemeManager.get("text")
        clock_fg = ThemeManager.get("clock_fg")

        # === メインフレーム ===
        self.frame = tk.Frame(parent, bg=bg)
        self.frame.pack(fill="x", padx=0, pady=(0))  # 最上段に横いっぱいで配置

        # === 左側: 天気表示 ===
        # 画面左端に詰まりすぎないよう、左に余白（30px）を追加
        self.left_frame = tk.Frame(self.frame, bg=bg)
        self.left_frame.pack(side="left", anchor="w", padx=(30, 0))

        # 画像（PhotoImage）は参照を保持しないとGCで消えるためdictで保持
        self.icon_images = {}
        # 実際に画面に載せるアイコン用Labelを保持（更新時に一括破棄）
        self.icon_widgets = []
        self.icon_frame = tk.Frame(self.left_frame, bg=bg)
        # アイコンとテキストの間に少し余白をつけて視認性を上げる
        self.icon_frame.pack(side="left", padx=(0, 5), anchor="center")

        # 天気の説明テキスト。wraplengthはピクセル指定で自動改行。
        self.weather_label = tk.Label(
            self.left_frame,
            text="",
            font=FONTS["weather_text"],
            bg=bg,
            fg=clock_fg,
            anchor="w",
            justify="left",
            wraplength=160
        )
        self.weather_label.pack(side="left", anchor="center", pady=(2, 0)) 

        # 利用しそうな天気アイコンをあらかじめ読み込む（存在しない場合は後述のフォールバック）
        self._load_icons()

        # === 右側: 時計 + メッセージ ===
        self.right_frame = tk.Frame(self.frame, bg=bg)
        self.right_frame.pack(side="right", anchor="e", padx=(0, 20))

        # 一時的なお知らせメッセージ。3秒表示→自動クリアなどに使用
        self.flash_label = tk.Label(
            self.right_frame,
            text="",
            font=("Segoe UI Emoji", 10, "italic"),
            bg=bg,
            fg=clock_fg,
            anchor="e",
            justify="right",
            wraplength=200
        )
        # 時計との間隔を少し空ける（pady=(0, 4)）
        self.flash_label.pack(side="top", anchor="e", pady=(0, 4))

        # 時計はボタンにしてクリックを受け付ける（テーマ切替のトリガ）
        self.clock_btn = tk.Button(
            self.right_frame,
            text=self._get_time_str(),
            font=FONTS["small"],
            bg=bg,
            fg=clock_fg,
            cursor="hand2",
            relief="flat",
            bd=0,
            command=self._on_toggle_clicked
        )
        self.clock_btn.pack(side="top", anchor="e", pady=(0, 1))

        # 1秒ごとに時刻を更新。afterを使うことでメインスレッドだけで安全に更新可能
        self._update_clock()

        # ホバー効果（色とカーソル変更）。操作可能であることを視覚的に示す
        def _on_enter(e):
            hover_color = ThemeManager.get("clock_hover")
            self.clock_btn.config(fg=hover_color, cursor="hand2")

        def _on_leave(e):
            self.clock_btn.config(fg=ThemeManager.get("clock_fg"))

        self.clock_btn.bind("<Enter>", _on_enter)
        self.clock_btn.bind("<Leave>", _on_leave)

        # ここでもう一度呼んでいるが、上の呼び出しだけでも動作する（動作影響なし）
        self._update_clock()

    def _load_icons(self):
        # 事前に用意した想定アイコン名。必要に応じて増減可能。
        icon_names = [
            "sun_icon.png", "cloudy_icon.png", "rain_icon.png",
            "snow_icon.png", "thunder_icon.png", "wind_icon.png"
        ]
        for name in icon_names:
            try:
                # resource_pathでPyInstallerの実行パス差異にも対応
                img_path = resource_path(os.path.join("ui", "icons", name))
                img = Image.open(img_path).resize((24, 24), Image.LANCZOS)
                self.icon_images[name] = ImageTk.PhotoImage(img)
            except Exception as e:
                # 読み込み失敗時は標準エラー出力にロギング（運用時はloggingモジュールも検討）
                print(f"[ERROR] アイコン読み込み失敗: {name} - {e}", file=sys.stderr)

        # 一つも読み込めなかった場合に備えて、透明のプレースホルダを用意
        if not self.icon_images:
            self.icon_images["default"] = ImageTk.PhotoImage(
                Image.new("RGBA", (24, 24), (0, 0, 0, 0))
            )

    def _get_time_str(self):
        # 時計表示用の文字列を生成（先頭に絵文字付き）
        return "🕒 " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _update_clock(self):
        # 時刻ラベルを更新し、1秒後に自分自身を再度スケジュールする
        self.clock_btn.config(text=self._get_time_str())
        self.clock_btn.after(1000, self._update_clock)

    def _on_toggle_clicked(self, event=None):
        # 時計ボタン押下時の処理：テーマ切替（コールバック任意）＋短いフラッシュ表示
        if self.on_theme_toggle:
            self.on_theme_toggle()
        self.flash_message_for_seconds("₊✩‧₊かわいくなったよ〜💖₊✩‧₊", 3)

    def update_weather(self, weather_info: dict | None):
        # まず既存のアイコンWidgetを破棄し、クリアしてから再配置する
        for widget in self.icon_widgets:
            widget.destroy()
        self.icon_widgets.clear()

        if weather_info:
            # weather_infoは {"icon": [ファイル名...], "description": 文字列} を想定
            icon_files = weather_info.get("icon", [])
            for icon_file in icon_files:
                img = self.icon_images.get(icon_file, self.icon_images.get("default"))
                # 背景色はテーマのヘッダ背景に合わせる
                lbl = tk.Label(self.icon_frame, image=img, bg=ThemeManager.get('header_bg'))
                lbl.pack(side="left", padx=2)
                self.icon_widgets.append(lbl)

            # テキストは空文字だと見栄えしないため、デフォルトで「情報なし」を表示
            self.weather_label.config(text=weather_info.get("description", "情報なし"))
        else:
            # Noneが来た場合は一旦テキストを空に（非表示の意図）
            self.weather_label.config(text="")

    def set_flash_message(self, text):
        # 右上の一時メッセージを即時表示。空文字を渡すと非表示になる
        self.flash_label.config(text=text)

    def update_theme(self):
        # テーマ（配色）が変わった際に呼び出し、背景色や文字色を更新
        bg = ThemeManager.get("header_bg")
        fg = ThemeManager.get("text")
        clock_fg = ThemeManager.get("clock_fg")

        # 関連ウィジェットの背景色を一括で更新
        for widget in [
            self.frame, self.left_frame, self.right_frame,
            self.icon_frame, self.weather_label,
            self.flash_label, self.clock_btn
        ]:
            widget.config(bg=bg)

        # テキスト色の更新（時計とフラッシュは同系色に揃える）
        self.weather_label.config(fg=clock_fg)
        self.flash_label.config(fg=clock_fg)
        self.clock_btn.config(
            fg=clock_fg, 
            activebackground=bg,
            activeforeground=clock_fg
        )

        # 表示済みのアイコン背景もテーマに合わせて更新
        for icon_widget in self.icon_widgets:
            icon_widget.config(bg=bg)
    
    def flash_message_for_seconds(self, message: str, seconds: int = 3):
        # 指定秒数だけメッセージを表示し、その後自動で消す（非同期・非ブロッキング）
        self.set_flash_message(message)
        self.frame.after(seconds * 1000, lambda: self.set_flash_message(""))