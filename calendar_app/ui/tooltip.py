import tkinter as tk

class ToolTip:
    """
    ウィジェットにマウスホバー時のツールチップ（吹き出し）を付与するクラス。
    - widget: ツールチップを表示させたい Tkinter ウィジェット
    - text: ツールチップに表示する文字列
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None  # ツールチップ用 Toplevel

        # ウィジェットにマウスイベントをバインド
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        """マウスがウィジェットに入ったときにツールチップを表示"""
        # 既に表示中、またはテキストが空なら何もしない
        if self.tip_window or not self.text:
            return

        # ウィジェット内のキャレット位置を基準に座標を計算
        x, y, cx, cy = self.widget.bbox("insert")
        # 画面上の絶対座標に変換して少しオフセット
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + cy + 10

        # 枠なしの Toplevel を作成してラベルを配置
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        # ツールチップの見た目を設定
        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#ffffe0",  # 淡い黄色背景
            relief="solid",
            borderwidth=1,
            font=("Arial", 10)
        )
        label.pack(ipadx=4, ipady=2)

    def hide_tip(self, event=None):
        """マウスがウィジェットを離れたときにツールチップを閉じる"""
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
