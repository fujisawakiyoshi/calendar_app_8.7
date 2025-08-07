# C:\work_202507\calendar_app\tests\test_theme_manager.py

import pytest
from unittest.mock import patch # ThemeManager が依存する ui.theme をモックするため

# テスト対象のクラスをインポート
from services.theme_manager import ThemeManager
# ThemeManager が ui.theme から LIGHT_THEME と DARK_THEME をインポートするため、ここでも利用可能にする
from ui.theme import LIGHT_THEME, DARK_THEME
from datetime import datetime


# UT-18: ThemeManager の toggle_theme()
def test_toggle_theme(mocker):
    """
    ThemeManager.toggle_theme() がライトモードとダークモードを正しく切り替えることを確認する。
    """
    # --- 準備 ---
    # ThemeManager が ui.theme からインポートする LIGHT_THEME と DARK_THEME をモック
    # ThemeManager の内部状態 _is_dark と _theme もリセット可能であればリセットする
    # fixture を使わない場合、クラス変数の状態をテスト間でリセットする必要がある

    # ThemeManager クラス変数にアクセスして初期化
    ThemeManager._is_dark = False
    ThemeManager._theme = LIGHT_THEME

    # --- テスト実行 & 検証 ---

    # 1回目トグル: ライト -> ダーク
    ThemeManager.toggle_theme()
    assert ThemeManager.is_dark_mode() is True
    assert ThemeManager._theme == DARK_THEME

    # 2回目トグル: ダーク -> ライト
    ThemeManager.toggle_theme()
    assert ThemeManager.is_dark_mode() is False
    assert ThemeManager._theme == LIGHT_THEME

    # さらにトグルして、再びダーク -> ライトを確認
    ThemeManager.toggle_theme()
    assert ThemeManager.is_dark_mode() is True
    assert ThemeManager._theme == DARK_THEME
    ThemeManager.toggle_theme()
    assert ThemeManager.is_dark_mode() is False
    assert ThemeManager._theme == LIGHT_THEME
    
