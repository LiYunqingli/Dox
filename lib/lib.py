"""
所有常用的方法封装的地方，如需添加新的方法，请注意规范且编写注释
"""

#初始化控制台，载入信息
def load():
    config = get_config()
    version = config["About"]["Version"]
    _print("_0_[v" + version + "]\n")
    _print("_1_\n")
    _print()

#获取配置文件的信息
def get_config():
    config_file_path = get_run_path() + "/../config/config.json"
    import json
    with open(config_file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

#获取main.py所在的路径
def get_run_path():
    import os
    return os.path.dirname(os.path.abspath(__file__))

# 获取当前语言设置
def get_lang():
    config = get_config()
    lang = config["Config"]["Lang"]
    return lang

#基于print的封装，根据本地语言设置输出对应语言的信息
def _print(input_str="\n", color=None):
    import json
    import re
    
    COLORS = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "reset": "\033[0m",  # 重置颜色
        "bold": "\033[1m",   # 加粗
        "underline": "\033[4m",
    }
    
    color_code = COLORS.get(color, "")
    reset_code = COLORS["reset"] if color else ""
    
    lang = get_lang()
    lang_file_path = f"{get_run_path()}/../resources/lang/src/{lang}.json"
    
    try:
        with open(lang_file_path, 'r', encoding='utf-8') as f:
            lang_data = json.load(f)["msg"]
        pattern = re.compile(r'_(\d+)_')
        def replace_match(match):
            key = match.group(1)
            return lang_data.get(key, match.group(0))
        output_str = pattern.sub(replace_match, input_str)
        print(f"{color_code}{output_str}{reset_code}", end='')
    except FileNotFoundError:
        print(f"Error: Language file not found at {lang_file_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in language file {lang_file_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

#获取关于信息
def get_about():
    config = get_config()
    about = config["About"]
    return str(about)

#加载动画
def donghua():
    """打印动画"""
    import time
    import random
    with open(get_run_path() + "/../resources/donghua/donghua", "r", encoding="utf-8") as f:
        for line in f:
            for char in line:
                print(f"\033[38;5;{random.randint(0, 255)}m{char}\033[0m", end="")
                time.sleep(0.001)
    print("\n")

#清楚屏幕内容
def clear():
    """清屏"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

#打印帮助信息（自动根据语言设置选择对应的语言包）
def help(input_str):
    """显示帮助信息"""
    items = input_str.split()
    items = items[1:]  # 去掉第一个元素（命令本身）

    def help_print(help_id):
        import json
        lang_file_path = f"{get_run_path()}/../resources/lang/src/{get_lang()}.json"
        with open(lang_file_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)["help"]
        if help_id == "ALL":
            _print("\n_12_\n\n")
            for help_item in help_data:
                # print(f"\n===============[{help_item["name"]}]===============\n")
                # print(help_item["msg"] + "\n")
                # for usage_item in help_item["usage"]:
                #     print(f"{usage_item}：{help_item['usage'][usage_item]}")
                # print("\n")
                
                # _print(f"{help_item['name']}","bold")#加粗命令
                print(f"{help_item['msg']}")
            print("\n")
        else:
            found = False
            for help_item in help_data:
                if help_item["name"] == help_id:
                    print(f"\n[{help_item['name']}]\n")
                    print(help_item["msg"] + "\n")
                    for usage_item in help_item["usage"]:
                        print(f"{usage_item}：{help_item['usage'][usage_item]}")
                    print("--------------------------------------------------------------------------------------\n")
                    found = True
                    break
            if not found:
                _print(f"_3_{help_id}\n", "red")

    if len(items) == 0:
        help_print("ALL")
    else:
        for item in items:
            # 将参数转换为大写以匹配JSON中的命令名称
            help_print(item.upper())

#进入一个新的目录
def cd(path):
    """改变当前工作目录"""
    import os
    try:
        os.chdir(path)
    except FileNotFoundError:
        _print("_4_\n")
    except NotADirectoryError:
        _print("_5_\n")
    except PermissionError:
        _print("_6_\n")
    except Exception as e:
        _print(f"_7_{str(e)}\n")

#列出目录内容（仿Linux）
def ls(detailed=False):
    """列出当前目录内容
    Args:
        detailed (bool): 是否显示详细信息（类似ls -l）
    """
    import os
    import time
    import stat
    import platform
    import sys

    try:
        items = os.listdir()
        if not detailed:
            # 简单模式
            for item in items:
                if os.path.isdir(item):
                    _print(f"\033[34m{item}/\033[0m ")  # 蓝色显示目录
                elif os.path.isfile(item):
                    _print(f"{item} ")
                else:
                    _print(f"\033[33m{item}\033[0m ")  # 黄色显示特殊文件
            _print("\n")
        else:
            # 详细模式（跨平台实现）
            for item in items:
                try:
                    stat_info = os.stat(item)
                    mode = stat_info.st_mode
                    file_type = 'd' if stat.S_ISDIR(mode) else '-' if stat.S_ISREG(mode) else '?'
                    permissions = [
                        'r' if mode & stat.S_IRUSR else '-',
                        'w' if mode & stat.S_IWUSR else '-',
                        'x' if mode & stat.S_IXUSR else '-',
                        'r' if mode & stat.S_IRGRP else '-',
                        'w' if mode & stat.S_IWGRP else '-',
                        'x' if mode & stat.S_IXGRP else '-',
                        'r' if mode & stat.S_IROTH else '-',
                        'w' if mode & stat.S_IWOTH else '-',
                        'x' if mode & stat.S_IXOTH else '-'
                    ]
                    
                    if platform.system() == 'Windows':
                        owner = str(stat_info.st_uid)
                        group = str(stat_info.st_gid)
                    else:
                        import pwd
                        import grp
                        owner = pwd.getpwuid(stat_info.st_uid).pw_name
                        group = grp.getgrgid(stat_info.st_gid).gr_name
                    
                    size = stat_info.st_size
                    mtime = time.strftime("%b %d %H:%M", time.localtime(stat_info.st_mtime))
                    
                    color_code = ""
                    reset_code = "\033[0m"
                    if stat.S_ISDIR(mode):
                        color_code = "\033[34m"  # 目录蓝色
                    elif stat.S_ISLNK(mode):
                        color_code = "\033[36m"  # 链接青色
                    elif mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
                        color_code = "\033[32m"  # 可执行文件绿色
                    
                    _print(f"{file_type}{''.join(permissions)} {stat_info.st_nlink} {owner} {group} "
                        f"{size:>8} {mtime} {color_code}{item}{reset_code}\n")
                except Exception as e:
                    _print(f"_9_{item}: {str(e)}\n")
    except Exception as e:
        _print(f"_7_{str(e)}\n")

#输出当前工作路径
def pwd():
    """返回当前路径"""
    import os
    _print("\n" + os.getcwd() + "\n\n")

#指定一个路径在控制台播放视频
def video(path):
    """播放指定视频，绝对路径"""
    if path.lower() == "test":
        path = get_run_path() + "/../resources/video/kun.mp4"
        print(path)
        from lib.src.video import video_in_cmd
        video_in_cmd(path)
    else:
        import os
        #判断文件是否存在
        if not os.path.exists(path):
            _print("\n_7__5_\n\n")
        else:
            from lib.src.video import video_in_cmd
            video_in_cmd(path)

#软件包管理器
def pck(input_str):
    items = input_str.split()[1:] # 去除命令本身
    if len(items) == 0:
        _print("pck需要携带参数\n")
    else:
        if items[0] == "install":
            items = items[1:]
            from lib.src.pck import pck_install
            if len(items) == 0:
                _print("pck install需要携带package\n")
            elif "-y" in items:
                items.remove("-y")
                pck_install(items, False)
            else:
                #询问安装
                pck_install(items, True)
        elif items[0] == "update":
            from lib.src.pck import pck_update
            items = items[1:]
            if len(items) != 0:
                _print("pck update不需要携带参数\n")
            else:
                pck_update()

#下载文件
def download(file_url, file_path):
    # 使用requests库下载文件，如果成功返回true，失败返回false
    _print("正在下载文件\n")
    import requests
    try:
        r = requests.get(file_url, stream=True)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        _print("下载完成\n")
        print("保存路径：" + file_path)
        return True
    except:
        _print("下载失败\n")
        return False

# 处理交互命令
def command(input_str):
    input_list = input_str.split()
    if len(input_list) == 0:
        return
    command = input_list[0]
    if command.lower() == "version":
        _print(get_about() + "\n")
    elif command.lower() == "clear":
        clear()
    elif command.lower() == "donghua":
        donghua() #属于彩蛋，在help文档中不应该记录关于此命令的信息及用法
    elif command.lower() == "cd":
        if len(input_list) > 1:
            cd(input_list[1])
        else:
            _print("_8_\n")
    elif command.lower() == "ls":
        if "-l" in input_list:
            ls(detailed=True)
        else:
            ls()
    elif command.lower() == "ll":
        ls(detailed=True)
    elif command.lower() == "pwd":
        pwd()
    elif command.lower() == "help":
        help(input_str)
    elif command.lower() == "video":
        if len(input_list) > 1:
            video(input_list[1])
        else:
            _print("_13_\n", "red")
    elif command.lower() == "pck":
        pck(input_str)
    else:
        _print("_2_" + command + "\n")