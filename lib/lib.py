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
def _print(input_str="\n", color=None, items=[]):
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

        #现在格式化其中的%s，按照顺序讲items中的值替换进去
        output_str = output_str % tuple(items)

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

#清除屏幕内容
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
def video(input_str):
    """在终端播放视频（低分辨率渲染）

    用法：
        video [视频路径|test] [-w 宽度] [-h 高度] [--fps 15] [--loop] [--gray] [--no-color]
    """

    items = input_str.split()[1:]  # 去除命令本身
    if len(items) == 0:
        _print("_13_\n", "red")
        return

    # 兼容包含空格的路径：
    # - 可以不加引号：video D:\a b\c.mp4 -w 80
    # - 也可以使用单/双引号包裹：video "D:\a b\c.mp4" 或 video 'D:\a b\c.mp4'
    option_tokens = {
        "-w",
        "--width",
        "-h",
        "--height",
        "--fps",
        "--loop",
        "-l",
        "--gray",
        "--grey",
        "-g",
        "--no-color",
        "--ascii",
    }

    path_end = 0
    while path_end < len(items) and items[path_end] not in option_tokens:
        path_end += 1

    path = " ".join(items[:path_end]).strip()

    def _strip_wrapping_quotes(s: str) -> str:
        if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
            return s[1:-1]
        return s

    path = _strip_wrapping_quotes(path)

    items = items[path_end:]
    max_width = None
    max_height = None
    fps = None
    loop = False
    grayscale = False
    no_color = False

    i = 0
    while i < len(items):
        arg = items[i]
        if arg in ("-w", "--width"):
            if i + 1 >= len(items):
                _print("_13_\n", "red")
                return
            max_width = int(items[i + 1])
            i += 2
            continue
        if arg in ("-h", "--height"):
            if i + 1 >= len(items):
                _print("_13_\n", "red")
                return
            max_height = int(items[i + 1])
            i += 2
            continue
        if arg in ("--fps",):
            if i + 1 >= len(items):
                _print("_13_\n", "red")
                return
            fps = float(items[i + 1])
            i += 2
            continue
        if arg in ("--loop", "-l"):
            loop = True
            i += 1
            continue
        if arg in ("--gray", "--grey", "-g"):
            grayscale = True
            i += 1
            continue
        if arg in ("--no-color", "--ascii"):
            no_color = True
            i += 1
            continue

        _print("_13_\n", "red")
        return

    import os

    if path.lower() == "test":
        path = get_run_path() + "/../resources/video/kun.mp4"

    if not os.path.exists(path):
        _print("\n_7__5_\n\n")
        return

    try:
        from lib.src.video import video_in_cmd
        video_in_cmd(
            path,
            max_width=max_width,
            max_height=max_height,
            fps=fps,
            loop=loop,
            grayscale=grayscale,
            no_color=no_color,
            page_break=True,
        )
    except Exception as e:
        _print(f"\n_7_{str(e)}\n\n", "red")

# 指定一个路径在控制台显示图片（低分辨率）
def img(input_str):
    """在终端以较低分辨率查看图片

    用法：
        img [图片路径] [-w 宽度] [-h 高度] [--gray] [--no-color]
    """

    items = input_str.split()[1:]  # 去除命令本身
    if len(items) == 0:
        _print("_13_\n", "red")
        return

    # 兼容包含空格的路径（同 video 命令）：
    # img D:\a b\c.png -w 80
    # img "D:\a b\c.png" / img 'D:\a b\c.png'
    option_tokens = {
        "-w",
        "--width",
        "-h",
        "--height",
        "--gray",
        "--grey",
        "-g",
        "--no-color",
        "--ascii",
    }

    path_end = 0
    while path_end < len(items) and items[path_end] not in option_tokens:
        path_end += 1

    path = " ".join(items[:path_end]).strip()

    def _strip_wrapping_quotes(s: str) -> str:
        if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
            return s[1:-1]
        return s

    path = _strip_wrapping_quotes(path)

    items = items[path_end:]
    max_width = None
    max_height = None
    grayscale = False
    no_color = False

    i = 0
    while i < len(items):
        arg = items[i]
        if arg in ("-w", "--width"):
            if i + 1 >= len(items):
                _print("_13_\n", "red")
                return
            max_width = int(items[i + 1])
            i += 2
            continue
        if arg in ("-h", "--height"):
            if i + 1 >= len(items):
                _print("_13_\n", "red")
                return
            max_height = int(items[i + 1])
            i += 2
            continue
        if arg in ("--gray", "--grey", "-g"):
            grayscale = True
            i += 1
            continue
        if arg in ("--no-color", "--ascii"):
            no_color = True
            i += 1
            continue

        # 未识别参数
        _print("_13_\n", "red")
        return

    import os

    if path.lower() == "test":
        path = get_run_path() + "/../resources/img/test_img.png"

    if not os.path.exists(path):
        _print("\n_7__5_\n\n")
        return

    from lib.src.img import image_in_cmd
    image_in_cmd(path, max_width=max_width, max_height=max_height, grayscale=grayscale, no_color=no_color)

#软件包管理器
def pck(input_str):
    items = input_str.split()[1:] # 去除命令本身
    if len(items) == 0:
        _print("_16_\n")#至少需要一个参数
    else:
        if items[0] == "install":
            items = items[1:]
            from lib.src.pck import pck_install
            if len(items) == 0:
                _print("_17_\n")#最少需要一个包名
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
                _print("_18_\n")#pck update 用法错误（携带参数非法）
            else:
                pck_update()
        elif items[0] == "list":
            from lib.src.pck import pck_list
            items = items[1:]
            if len(items) != 0:
                _print("_18_\n")
            else:
                pck_list()
        elif items[0] == "search":
            items = items[1:]
            if len(items) == 0:
                _print("_33_\n")
            else:
                from lib.src.pck import pck_search
                pck_search(items[0], isOutPut=True)
        else:
            _print("_19_" + items[0] + "\n") #非法的pck参数

# 修改配置文件
def set_config(input_str):
    _print("设置配置文件\n")
    pass

# rm 删除文件或者目录
def rm(paths, recursive=False, force=False):
    """删除文件或目录
    Args:
        paths (list): 要删除的文件/目录路径列表
        recursive (bool): 是否递归删除目录
        force (bool): 是否强制删除（无确认）
    """
    import os
    import shutil
    for path in paths:
        # 检查路径是否存在
        if not os.path.exists(path):
            if not force:
                _print("_20_\n", "red", [path])  # 文件或目录不存在
            continue  # 强制模式下忽略不存在的文件
        # 删除文件
        if os.path.isfile(path):
            try:
                if not force:
                    _print("_22_\n", "yellow", [path])  # 确认删除文件
                    confirm = input().strip().lower()
                    if confirm != 'y':
                        _print("_24_\n")  # 取消删除
                        continue
                os.remove(path)
                _print("_21_\n", items=[path])  # 成功删除文件
            except Exception as e:
                _print(f"_29_: {str(e)}\n", "red", [path])  # 删除失败
        # 删除目录
        elif os.path.isdir(path):
            if not recursive:
                _print("_25_\n", "red")  # 需要-r参数
                continue
            try:
                if not force:
                    _print("_27_\n","yellow",[path])  # 确认删除目录
                    confirm = input().strip().lower()
                    if confirm != 'y':
                        _print("_24_\n")
                        continue
                shutil.rmtree(path, ignore_errors=force)  # 强制模式下忽略错误
                _print("_26_\n", items=[path])  # 成功删除目录
            except Exception as e:
                if not force:
                    _print(f"_29_: {str(e)}\n", "red", [path])
        else:
            _print("_28_\n", "red", [path])  # 未知类型

#下载文件(高级版本，支持动态显示下载过程，不支持断点续传)
def download(file_url, file_path):
    import requests
    import os
    import time

    COLORS = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "reset": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
    }

    def human_readable_size(size_bytes):
        if size_bytes <= 0:
            return "0B"
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = size_bytes
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        return f"{size:.2f} {units[unit_index]}"

    def format_time(seconds):
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    try:
        r = requests.get(file_url, stream=True)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        total_size = int(r.headers.get('Content-Length', 0))
        downloaded = 0
        start_time = time.time()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    elapsed_time = time.time() - start_time
                    speed = downloaded / elapsed_time if elapsed_time > 0 else 0
                    human_downloaded = human_readable_size(downloaded)
                    speed_h = human_readable_size(speed) + "/s"
                    time_str = format_time(elapsed_time)
                    if total_size > 0:
                        percent = downloaded / total_size * 100
                        progress_width = 20
                        filled = int(progress_width * percent / 100)
                        bar = '=' * filled + '>' + ' ' * (progress_width - filled - 1) if filled < progress_width else '=' * progress_width
                        human_total = human_readable_size(total_size)
                        remaining_time = (total_size - downloaded) / speed if speed > 0 else 0
                        eta_str = format_time(remaining_time) if speed > 0 else '--:--'
                        progress_line = f"\r{percent:.1f}% [{bar}] {human_downloaded}/{human_total} {speed_h} Time: {time_str} ETA: {eta_str}"
                    else:
                        progress_line = f"\rDownloaded: {human_downloaded} at {speed_h} Time: {time_str}"
                    color_code = COLORS['green']
                    reset_code = COLORS['reset']
                    print(f"{color_code}{progress_line}{reset_code}", end='', flush=True)
            print(f"{COLORS['reset']}\n", end='')
        return True
    except Exception as e:
        _print(f"download() : {str(e)}\n", color="red")
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
        video(input_str)
    elif command.lower() == "img":
        img(input_str)
    elif command.lower() == "pck":
        pck(input_str)
    elif command.lower() == "download":
        file_url = input_list[1]
        file_path = input_list[2]
        download(file_url, file_path)
    elif command.lower() == "rm":
        items = input_list[1:]  # 去除命令本身
        if not items:
            _print("_30_\n", "red")  # 缺少参数
            return
        recursive = False
        force = False
        paths = []
        # 解析参数
        for item in items:
            if item.startswith('-'):
                if 'r' in item or 'R' in item:
                    recursive = True
                if 'f' in item:
                    force = True
            else:
                paths.append(item)
        if not paths:
            _print("_31_\n", "red")  # 未指定文件或目录
            return
        # 调用rm函数
        rm(paths, recursive, force)
    elif command.lower() == "bookmark":
        bookmark(input_str)
    elif command.lower() == "set":
        set_config(input_str)
    else:
        _print("_2_" + command + "\n")
        
# 书签（变量）
def bookmark(input_str):
    items = input_str.split()[1:] # 去除命令本身
    if len(items) == 0:
        _print("至少需要一个参数来操作书签\n")
    else:
        print(items[0])