# 脚本执行
from lib.lib import _print


def script_cmd(arg):
    if not arg:
        _print("请输入脚本文件路径\n")
        return
    args = arg.split(" ")
    script_path = args[1]
    script_path = check_and_format_script_path(script_path)  # 格式化脚本路径
    if not script_path:
        _print("脚本文件路径无效\n", "red")
        return
    _print("正在执行脚本文件: " + script_path + "\n")


def check_script_is_dox(script_content):
    first_line = script_content.split("\n")[0].strip()
    if first_line != "#!dox":
        _print("脚本文件必须以#!dox开头，非法的dox脚本", "red")


def check_and_format_script_path(path):
    import os
    from lib.lib import pwd

    if not os.path.exists(path):
        if not os.path.exists(pwd() + "/" + path):
            _print("脚本文件不存在: " + path + "\n", "red")
            return None

    _print("脚本文件路径: " + path + "\n")
    return path


def format_script(path):
    with open(path, "r", encoding="utf-8") as f:
        script_content = f.read()
