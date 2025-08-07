# utils/resource.py
import os
import sys
import shutil

def resource_path(relative_path: str, writable: bool = False) -> str:
    """
    リソースファイルのパスを解決する。
    
    Args:
        relative_path (str): プロジェクトのルートディレクトリからの相対パス。
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstallerでパッケージ化されている場合
        base_path = sys._MEIPASS
    else:
        # 開発環境の場合
        # os.path.dirname(os.path.abspath(sys.argv[0])) は
        # 実行ファイル(main.py)のディレクトリを返す
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))

    full_path = os.path.join(base_path, relative_path)
    
    # 書き込み可能ファイルは、ユーザーのホームディレクトリにコピーしてパスを返す
    if writable:
        user_dir = os.path.join(os.path.expanduser("~"), ".calendar_app")
        os.makedirs(user_dir, exist_ok=True)
        dest_path = os.path.join(user_dir, os.path.basename(relative_path))
        
        if not os.path.exists(dest_path):
            try:
                shutil.copy(full_path, dest_path)
            except FileNotFoundError:
                with open(dest_path, "w", encoding="utf-8") as f:
                    f.write("[]")
        return dest_path
    
    return full_path