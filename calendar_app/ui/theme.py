# ui/theme.py

# ────────────────────────────────────────────────────────────
# カラー定義（COLORS）
# ────────────────────────────────────────────────────────────
COLORS = {
    # ◾ 背景色
    "bg":           "#FAFAFA",  # メイン背景
    "dialog_bg":    "#FFFFFF",  # ダイアログ背景
    "header_bg":    "#FAFAFA",  # ヘッダー（ナビゲーション部）背景

    # ◾ テキスト色
    "text":         "#333333",  # 標準テキスト

    # ◾ 日付セルの特殊背景
    "weekend":      "#FFC1DA",
    "sunday":       "#FADCD9",  # 日曜セル
    "saturday":     "#DCEEF9",  # 土曜セル
    "holiday":      "#F6CACA",  # 祝日セル（未使用ならaccentと統合可能）
    "today":        "#B7DCF5",  # 今日セルの強調
    "highlight":    "#FFF4CC",  # イベントありセル
    "accent":       "#EA92A0",  # 祝日セル用アクセント

    # ◾ ボタン共通
    "button_bg":    "#FFFFFF",  # ボタン標準背景
    "button_fg":    "#444444",  # ボタンテキスト
    "button_hover": "#F0F0F0",  # ボタンホバー時背景
}
# ────────────────────────────────────────────────────────────
# カラー定義（COLORS）
# ────────────────────────────────────────────────────────────
LIGHT_THEME = {
    "bg": "#FFFFFF",
    "dialog_bg": "#FFFFFF",
    "header_bg": "#FAFAFA",
    "text": "#333333",
    "weekend": "#FFC1DA",
    "today": "#B7DCF5",
    "highlight": "#FFF4CC",
    "accent": "#F1AEB9",
    
    "hover": "#D0EBFF",  # LIGHT_THEME
    
    # ボタン
    "button_bg": "#FFFFFF",
    "button_fg": "#444444",
    "button_hover": "#F0F0F0",
    "button_bg_add": "#B7DCF5",     
    "button_bg_edit": "#FFE7C1",     
    "button_bg_delete": "#F7C6C7", 
    
    "clock_fg": "#555555",    
    "footer_fg": "#888888",
    "holiday_label_fg": "#888888", # 新規追加
    "clock_hover": "#AA77AA",
    "today_fg":"#3F68D8"  #今日の文字を強調
}

DARK_THEME = {
    # 背景・ベース
    "bg": "#FFF7F9",              # ミルキーピンク系
    "header_bg": "#FEEEF3",       # ヘッダーは少し濃いピンクベージュ
    "dialog_bg": "#FFF7F9",

    # テキスト
    "text": "#7D4B6C",            # 落ち着いたローズブラウン

    # 特殊背景
    "weekend": "#FADAE1",         # 土日：ふんわりピンク
    "sunday": "#FFD1DC",          # 日曜：さくら色
    "saturday": "#D5F5F6",        # 土曜：ミントブルー
    "holiday": "#FFD3E0",         # 祝日：淡ピンク
    "today": "#D3E9FD",           # 今日：やさしいサクラピンク
    "highlight": "#FFF4CC",       # イベントあり：レモン色
    "accent": "#FFC1E3",          # 強調ピンク

    "hover": "#D5F5F6",             # DARK_THEME 例

    # ボタン
    "button_bg": "#FFF0F5",         # ライトラベンダー
    "button_fg": "#7D4B6C",         # ローズブラウン
    "button_hover": "#FFE4EC",      # ホバー：やわらかピンク
    
    "button_bg_add": "#FFD6F0",     # かわいいピンク（追加ボタン）
    "button_bg_edit": "#FFECB3",    # パステルイエロー（編集ボタン）
    "button_bg_delete": "#FFCDD2",  # パステルレッド（削除ボタン）
    
    "clock_fg": "#AA77AA",  # 時計の文字色
    "footer_fg": "#AA77AA",
    "holiday_label_fg": "#CA67B5", # 新規追加
    "clock_hover": "#AA77AA",
    "today_fg":"#da3e87"

}

# 初期テーマはライト
COLORS = LIGHT_THEME

# ────────────────────────────────────────────────────────────
# フォント定義（FONTS）
# ────────────────────────────────────────────────────────────
# フォント種類とサイズをここで一元管理します。
FONTS = {
    "base":         ("Helvetica", 13),            # 標準テキスト
    "base_minus":   ("Helvetica", 11),            # 予定一覧画面の文字
    "bold":         ("Helvetica", 13, "bold"),    # 太字
    "small":        ("Helvetica", 11),            # 補助テキスト・ラベル
    "small_holiday": ("Helvetica", 10),          # 祝日名
    "weather_emoji":   ("Helvetica", 12, "bold"),    # 天気のEmoji
    "weather_text": ("Helvetica", 9),      # 天気のテキスト
    "header":       ("Helvetica", 15, "bold"),    # カレンダー見出し
    "dialog_title": ("Helvetica", 14, "bold"),    # ダイアログタイトル
    "button":       ("Helvetica", 12),            # ボタンテキスト
}

# ────────────────────────────────────────────────────────────
# 選択肢リスト
# ────────────────────────────────────────────────────────────
# コンボボックス等で利用する選択肢を定義
TITLE_CHOICES = [
    "会議/打合せ",
    "来客",
    "外出",
    "出張",
    "休暇",
    "私用",
    "その他"
]

# 時刻選択肢：07:00～21:30 まで 30 分刻み
TIME_CHOICES = [
    f"{h:02d}:{m:02d}"
    for h in range(7, 22)    # 07時～21時
    for m in (0, 30)         # on the hour / half past
]
