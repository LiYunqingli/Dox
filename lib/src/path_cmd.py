"""path / env 命令实现：PATH 条目的查看、增删与清空（临时 + 持久化）。

持久化数据存放在 config/path.json，临时数据仅保存在进程内（_TEMP_ENV）。
"""

from lib.lib import _print, get_run_path

# 进程内的临时环境变量（不落盘）
_TEMP_ENV = {
    "PATH": [],
}


def _path_json_path():
    return get_run_path() + "/../config/path.json"


def _load_persistent_env():
    """读取持久化的环境变量配置，文件不存在时自动初始化。"""
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
    """写回持久化的环境变量配置。"""
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
    """去掉引号与首尾空白，展开 ~ 并规范化路径。"""
    import os

    p = (p or "").strip().strip('"').strip("'")
    if p == "":
        return ""
    p = os.path.expanduser(p)
    return os.path.normpath(p)


def _path_key(p: str) -> str:
    """生成用于去重比较的路径键（大小写与分隔符归一）。"""
    import os

    return os.path.normcase(os.path.normpath(p))


def _effective_path_list(persistent_list, temp_list):
    """临时条目优先，合并去重后返回生效的 PATH 列表。"""
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
    """path 子命令：show/get、list、add、rm/remove、clear。"""
    import os
    import shlex

    try:
        parts = shlex.split(input_str, posix=False)
    except Exception:
        parts = input_str.split()

    args = parts[1:]
    sub = args[0].lower() if args else "show"

    persistent = _load_persistent_env()
    persistent_path_list = persistent.get("PATH", [])
    temp_path_list = _TEMP_ENV.get("PATH", [])

    # show/get：输出合并后的生效 PATH 与条目统计
    if sub in {"show", "get"}:
        effective_list = _effective_path_list(persistent_path_list, temp_path_list)
        _print("_47_\n", items=[os.pathsep.join(effective_list)])
        _print("_48_\n", items=[str(len(persistent_path_list))])
        _print("_49_\n", items=[str(len(temp_path_list))])
        return

    # list：分别列出持久化与临时条目
    if sub == "list":
        _print("_50_\n", items=[str(len(persistent_path_list))])
        for idx, entry in enumerate(persistent_path_list, start=1):
            _print("_51_\n", items=[str(idx), str(entry)])
        _print("_52_\n", items=[str(len(temp_path_list))])
        for idx, entry in enumerate(temp_path_list, start=1):
            _print("_51_\n", items=[str(idx), str(entry)])
        return

    # add / rm / remove：解析 -t(--temp)、-p(--persist)、--all(-a) 作用域
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
        use_persist = (
            ("-p" in flags) or ("--persist" in flags) or ("--permanent" in flags)
        )
        use_all = ("--all" in flags) or ("-a" in flags)
        # 未指定作用域时默认持久化
        if not (use_temp or use_persist or use_all):
            use_persist = True
        if use_all:
            use_temp = True
            use_persist = True

        if sub == "add":
            added_any = False
            if use_persist:
                if _path_key(value) in {
                    _path_key(_normalize_path_entry(p)) for p in persistent_path_list
                }:
                    _print("_55_\n", "yellow", [value])
                else:
                    persistent_path_list.append(value)
                    persistent["PATH"] = persistent_path_list
                    if _save_persistent_env(persistent):
                        _print("_53_\n", items=[value])
                        added_any = True
            if use_temp:
                if _path_key(value) in {
                    _path_key(_normalize_path_entry(p)) for p in temp_path_list
                }:
                    _print("_55_\n", "yellow", [value])
                else:
                    temp_path_list.append(value)
                    _TEMP_ENV["PATH"] = temp_path_list
                    _print("_54_\n", items=[value])
                    added_any = True

            if not added_any:
                return
            return

        # rm/remove：分别在两个作用域中剔除匹配条目
        removed_any = False
        if use_persist:
            before = list(persistent_path_list)
            persistent_path_list = [
                p
                for p in persistent_path_list
                if _path_key(_normalize_path_entry(p)) != _path_key(value)
            ]
            if len(before) != len(persistent_path_list):
                persistent["PATH"] = persistent_path_list
                if _save_persistent_env(persistent):
                    _print("_56_\n", items=[value])
                    removed_any = True
        if use_temp:
            before = list(temp_path_list)
            temp_path_list = [
                p
                for p in temp_path_list
                if _path_key(_normalize_path_entry(p)) != _path_key(value)
            ]
            if len(before) != len(temp_path_list):
                _TEMP_ENV["PATH"] = temp_path_list
                _print("_57_\n", items=[value])
                removed_any = True

        if not removed_any:
            _print("_58_\n", "yellow", [value])
        return

    # clear：必须显式指定作用域，避免误清空
    if sub == "clear":
        flags = set(a.lower() for a in args[1:])
        use_temp = ("-t" in flags) or ("--temp" in flags)
        use_persist = (
            ("-p" in flags) or ("--persist" in flags) or ("--permanent" in flags)
        )
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
    """env 命令：输出指定环境变量，PATH 走合并后的生效值。"""
    import os
    import shlex

    try:
        parts = shlex.split(input_str, posix=False)
    except Exception:
        parts = input_str.split()

    args = parts[1:]
    var = args[0].upper() if args else "PATH"
    if var != "PATH":
        # 其它变量回退到进程真实环境变量
        _print("_66_\n", items=[var, os.environ.get(var, "")])
        return

    persistent = _load_persistent_env()
    persistent_path_list = persistent.get("PATH", [])
    temp_path_list = _TEMP_ENV.get("PATH", [])
    effective_list = _effective_path_list(persistent_path_list, temp_path_list)
    _print("_66_\n", items=["PATH", os.pathsep.join(effective_list)])
