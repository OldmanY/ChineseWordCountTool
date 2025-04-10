import sys
import os
from cx_Freeze import setup, Executable

# 自动获取 tkinterdnd2 路径
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

# 包含资源文件
include_files = []
if os.path.exists("assets"):
    include_files.append(("assets", "assets"))

# 包含 tkinterdnd2
tkdnd_path = get_tkinterdnd2_path()
if tkdnd_path:
    include_files.append((tkdnd_path, "tkinterdnd2"))

# Windows 专属配置
build_options = {
    "include_files": include_files,
    "excludes": ["tkinter", "py2app"],  # 显式排除 py2app
    "optimize": 2
}

executables = [
    Executable(
        MAIN_SCRIPT,
        base="Win32GUI",
        icon=ICON_PATH,
        target_name="ChineseWordCounter.exe"
    )
]

setup(
    name=APP_NAME,
    version=VERSION,
    description="中文文本统计工具",
    options={"build_exe": build_options},
    executables=executables
)