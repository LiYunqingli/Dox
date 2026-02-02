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
    import json
    import shlex

    def format_value(value):
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)

    def parse_value(value_str):
        value_str = value_str.strip()
        if value_str == "":
            return ""
        try:
            return json.loads(value_str)
        except Exception:
            return value_str

    def is_yes(s: str) -> bool:
        s = (s or "").strip().lower()
        return s in {"y", "yes", "true", "1", "是", "好", "ok"}

    try:
        parts = shlex.split(input_str, posix=False)
    except Exception:
        parts = input_str.split()

    if len(parts) < 3:
        _print("_34_\n", "red")
        return

    raw_key_path = (parts[1] or "").strip()
    if raw_key_path.lower().startswith("config."):
        raw_key_path = raw_key_path[7:]
    key_path = raw_key_path.strip(".")
    if not key_path:
        _print("_34_\n", "red")
        return

    value_str = " ".join(parts[2:])
    new_value = parse_value(value_str)

    config = get_config()
    if not isinstance(config.get("Config"), dict):
        _print("_45_\n", "red")
        return
    config_root = config["Config"]

    segments = [seg for seg in key_path.split(".") if seg]
    if not segments:
        _print("_34_\n", "red")
        return

    parent = config_root
    missing_path = None
    non_object_at = None

    for i, seg in enumerate(segments[:-1]):
        if seg not in parent:
            missing_path = ".".join(segments[: i + 1])
            break
        if not isinstance(parent[seg], dict):
            non_object_at = ".".join(segments[: i + 1])
            break
        parent = parent[seg]

    if non_object_at is not None:
        _print("_44_\n", "red", [non_object_at])
        return

    final_key = segments[-1]
    exists_final = missing_path is None and final_key in parent

    # Key missing (either intermediate path or final key)
    if missing_path is not None or not exists_final:
        _print("_39_\n", "yellow", [key_path])
        _print("_40_\n", items=[format_value(new_value)])
        _print("_41_", "yellow", [key_path])
        if not is_yes(input()):
            _print("_43_\n")
            return

        # Create missing intermediate dicts
        parent = config_root
        for seg in segments[:-1]:
            if seg not in parent:
                parent[seg] = {}
            elif not isinstance(parent[seg], dict):
                _print("_44_\n", "red", [seg])
                return
            parent = parent[seg]

        parent[final_key] = new_value
        try:
            config_file_path = get_run_path() + "/../config/config.json"
            with open(config_file_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
                f.write("\n")
            _print("_42_\n", items=[key_path])
        except Exception as e:
            _print("_46_\n", "red", [str(e)])
        return

    # Key exists; show old/new and confirm
    old_value = parent.get(final_key)
    _print("_35_\n", items=[key_path])
    _print("_36_\n", items=[format_value(old_value)])
    _print("_37_\n", items=[format_value(new_value)])
    _print("_38_", "yellow", [key_path])
    if not is_yes(input()):
        _print("_43_\n")
        return

    parent[final_key] = new_value
    try:
        config_file_path = get_run_path() + "/../config/config.json"
        with open(config_file_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
            f.write("\n")
        _print("_42_\n", items=[key_path])
    except Exception as e:
        _print("_46_\n", "red", [str(e)])

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
    elif command.lower() == "path":
        path_cmd(input_str)
    elif command.lower() == "env":
        env_cmd(input_str)
    elif command.lower() == "set":
        set_config(input_str)
    else:
        _print("_2_" + command + "\n")


_TEMP_ENV = {
    "PATH": [],
}


def _path_json_path():
    return get_run_path() + "/../config/path.json"


def _load_persistent_env():
    import json
    import os

    path = _path_json_path()
    if not os.path.exists(path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"PATH": []}, f, ensure_ascii=False, indent=4)
                f.write("\n")
        except Exception:
            return {"PATH": []}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {}
        if "PATH" not in data or not isinstance(data.get("PATH"), list):
            data["PATH"] = []
        return data
    except Exception as e:
        _print("_63_\n", "red", [str(e)])
        return {"PATH": []}


def _save_persistent_env(data):
    import json
    try:
        with open(_path_json_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.write("\n")
        return True
    except Exception as e:
        _print("_64_\n", "red", [str(e)])
        return False


def _normalize_path_entry(p: str) -> str:
    import os
    p = (p or "").strip().strip('"').strip("'")
    if p == "":
        return ""
    p = os.path.expanduser(p)
    return os.path.normpath(p)


def _path_key(p: str) -> str:
    import os
    return os.path.normcase(os.path.normpath(p))


def _effective_path_list(persistent_list, temp_list):
    seen = set()
    result = []
    for item in temp_list + persistent_list:
        norm = _normalize_path_entry(item)
        if not norm:
            continue
        k = _path_key(norm)
        if k in seen:
            continue
        seen.add(k)
        result.append(norm)
    return result


def path_cmd(input_str):
    import os
    import shlex

    try:
        parts = shlex.split(input_str, posix=False)
    except Exception:
        parts = input_str.split()

    args = parts[1:]
    sub = (args[0].lower() if args else "show")

    persistent = _load_persistent_env()
    persistent_path_list = persistent.get("PATH", [])
    temp_path_list = _TEMP_ENV.get("PATH", [])

    if sub in {"show", "get"}:
        effective_list = _effective_path_list(persistent_path_list, temp_path_list)
        _print("_47_\n", items=[os.pathsep.join(effective_list)])
        _print("_48_\n", items=[str(len(persistent_path_list))])
        _print("_49_\n", items=[str(len(temp_path_list))])
        return

    if sub == "list":
        _print("_50_\n", items=[str(len(persistent_path_list))])
        for idx, entry in enumerate(persistent_path_list, start=1):
            _print("_51_\n", items=[str(idx), str(entry)])
        _print("_52_\n", items=[str(len(temp_path_list))])
        for idx, entry in enumerate(temp_path_list, start=1):
            _print("_51_\n", items=[str(idx), str(entry)])
        return

    if sub in {"add", "rm", "remove"}:
        if len(args) < 2:
            _print("_60_\n", "red")
            return

        raw_value = args[1]
        value = _normalize_path_entry(raw_value)
        if not value:
            _print("_60_\n", "red")
            return

        flags = set(a.lower() for a in args[2:])
        use_temp = ("-t" in flags) or ("--temp" in flags)
        use_persist = ("-p" in flags) or ("--persist" in flags) or ("--permanent" in flags)
        use_all = ("--all" in flags) or ("-a" in flags)
        if not (use_temp or use_persist or use_all):
            use_persist = True
        if use_all:
            use_temp = True
            use_persist = True

        if sub == "add":
            added_any = False
            if use_persist:
                if _path_key(value) in {_path_key(_normalize_path_entry(p)) for p in persistent_path_list}:
                    _print("_55_\n", "yellow", [value])
                else:
                    persistent_path_list.append(value)
                    persistent["PATH"] = persistent_path_list
                    if _save_persistent_env(persistent):
                        _print("_53_\n", items=[value])
                        added_any = True
            if use_temp:
                if _path_key(value) in {_path_key(_normalize_path_entry(p)) for p in temp_path_list}:
                    _print("_55_\n", "yellow", [value])
                else:
                    temp_path_list.append(value)
                    _TEMP_ENV["PATH"] = temp_path_list
                    _print("_54_\n", items=[value])
                    added_any = True

            if not added_any:
                return
            return

        # rm/remove
        removed_any = False
        if use_persist:
            before = list(persistent_path_list)
            persistent_path_list = [p for p in persistent_path_list if _path_key(_normalize_path_entry(p)) != _path_key(value)]
            if len(before) != len(persistent_path_list):
                persistent["PATH"] = persistent_path_list
                if _save_persistent_env(persistent):
                    _print("_56_\n", items=[value])
                    removed_any = True
        if use_temp:
            before = list(temp_path_list)
            temp_path_list = [p for p in temp_path_list if _path_key(_normalize_path_entry(p)) != _path_key(value)]
            if len(before) != len(temp_path_list):
                _TEMP_ENV["PATH"] = temp_path_list
                _print("_57_\n", items=[value])
                removed_any = True

        if not removed_any:
            _print("_58_\n", "yellow", [value])
        return

    if sub == "clear":
        flags = set(a.lower() for a in args[1:])
        use_temp = ("-t" in flags) or ("--temp" in flags)
        use_persist = ("-p" in flags) or ("--persist" in flags) or ("--permanent" in flags)
        use_all = ("--all" in flags) or ("-a" in flags)
        if use_all:
            use_temp = True
            use_persist = True
        if not (use_temp or use_persist):
            _print("_61_\n", "red")
            return

        if use_persist:
            persistent["PATH"] = []
            if _save_persistent_env(persistent):
                _print("_59_\n")
        if use_temp:
            _TEMP_ENV["PATH"] = []
            _print("_62_\n")
        return

    _print("_65_\n", "red", [sub])


def env_cmd(input_str):
    import os
    import shlex

    try:
        parts = shlex.split(input_str, posix=False)
    except Exception:
        parts = input_str.split()

    args = parts[1:]
    var = (args[0].upper() if args else "PATH")
    if var != "PATH":
        # fallback to actual process env for other vars
        _print("_66_\n", items=[var, os.environ.get(var, "")])
        return

    persistent = _load_persistent_env()
    persistent_path_list = persistent.get("PATH", [])
    temp_path_list = _TEMP_ENV.get("PATH", [])
    effective_list = _effective_path_list(persistent_path_list, temp_path_list)
    _print("_66_\n", items=["PATH", os.pathsep.join(effective_list)])