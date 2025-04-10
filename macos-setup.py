import sys
import os
from setuptools import setup
from cx_Freeze import Executable, setup  # Windows需安装cx_Freeze

# 自动获取tkinterdnd2库路径
def get_tkinterdnd2_path():
    try:
        import tkinterdnd2
        return os.path.dirname(tkinterdnd2.__file__)
    except ImportError:
        return ""

# 基础配置
APP_NAME = "中文统计工具"
VERSION = "1.0"
MAIN_SCRIPT = "main.py"
ICON_PATH = "assets/app.ico"

# 自动包含资源文件和tkinterdnd2
include_files = []
if os.path.exists("assets"):
    include_files.append(("assets", "assets"))

tkdnd_path = get_tkinterdnd2_path()
if tkdnd_path:
    include_files.append((tkdnd_path, "tkinterdnd2"))

# Windows打包配置
build_exe_options = {
    "include_files": include_files,
    "excludes": ["tkinter"],  # 避免重复包含
    "optimize": 2
}

# macOS打包配置（需py2app）
if sys.platform == "darwin":
    extra_options = {
        "setup_requires": ["py2app"],
        "app": [MAIN_SCRIPT],
        "options": {
            "py2app": {
                "iconfile": ICON_PATH,
                "includes": ["tkinterdnd2"],
                "resources": ["assets/"]
            }
        }
    }
else:
    extra_options = {
        "options": {"build_exe": build_exe_options},
        "executables": [
            Executable(
                MAIN_SCRIPT,
                base="Win32GUI" if sys.platform == "win32" else None,
                icon=ICON_PATH
            )
        ]
    }

setup(
    name=APP_NAME,
    version=VERSION,
    description="带拖放功能的中文统计工具",
    **extra_options
)