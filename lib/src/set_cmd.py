"""set 命令实现：按“点分路径”修改配置文件中的键值。"""

from lib.lib import _print, get_config, get_run_path


# 修改配置文件
def set_config(input_str):
    import json
    import shlex

    # 将值格式化为可读文本用于展示
    def format_value(value):
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)

    # 尝试按 JSON 解析输入值，失败则按普通字符串处理
    def parse_value(value_str):
        value_str = value_str.strip()
        if value_str == "":
            return ""
        try:
            return json.loads(value_str)
        except Exception:
            return value_str

    # 判断用户输入是否为肯定答复
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

    key_path = (parts[1] or "").strip().strip(".")
    if not key_path:
        _print("_34_\n", "red")
        return

    value_str = " ".join(parts[2:])
    new_value = parse_value(value_str)

    config = get_config()
    config_root = config

    segments = [seg for seg in key_path.split(".") if seg]
    if not segments:
        _print("_34_\n", "red")
        return

    parent = config_root
    missing_path = None
    non_object_at = None

    # 逐级下钻，记录缺失路径或非字典节点
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

    # 目标键不存在（中间层级或最终键缺失）
    if missing_path is not None or not exists_final:
        _print("_39_\n", "yellow", [key_path])
        _print("_40_\n", items=[format_value(new_value)])
        _print("_41_", "yellow", [key_path])
        if not is_yes(input()):
            _print("_43_\n")
            return

        # 补全缺失的中间层级字典
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

    # 目标键已存在：展示新旧值并确认
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
