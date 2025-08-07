# C:\work_202507\calendar_app\tests\test_holiday_service.py

import pytest
from unittest.mock import patch, mock_open
import json
import requests

# テスト対象の関数をインポート
# load_holiday_cache, save_holiday_cache, get_holidays_for_year は後でインポートする
# from services.holiday_service import get_holidays_for_year, load_holiday_cache, save_holiday_cache


# UT-13: get_holidays_for_year() 有効な祝日データが正しく読み込まれることを確認
def test_get_holidays_valid_data():
    """
    holidays.json ファイルから有効な祝日データが正しく読み込まれることを確認する。
    キャッシュが存在し、その年のデータがあるシナリオをテスト。
    """
    valid_json_cache_data = """
    {
        "2024": {
            "2024-01-01": "元日",
            "2024-01-08": "成人の日"
        },
        "2025": {
            "2025-01-01": "元日",
            "2025-07-21": "海の日"
        }
    }
    """
    expected_holidays_2025 = {
        "2025-01-01": "元日",
        "2025-07-21": "海の日"
    }

    mock_holidays_file_path = "mocked/data/holidays.json"

    mock_file_handle = mock_open(read_data=valid_json_cache_data)
    
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_file_handle), \
         patch('services.holiday_service.CACHE_FILE', new=mock_holidays_file_path), \
         patch('services.holiday_service.fetch_holidays_from_api') as mock_fetch_api:
        
        # モックが適用された状態で関数をインポート/参照する
         from services.holiday_service import get_holidays_for_year, load_holiday_cache, save_holiday_cache
        
         holidays = get_holidays_for_year(2025)

         assert holidays == expected_holidays_2025
         mock_fetch_api.assert_not_called()

         mock_file_handle.assert_called_once_with(mock_holidays_file_path, encoding="utf-8")