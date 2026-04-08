# 2026.4.8 19:58
# by LiHuaRong, I want to make a ai agent function to manage the dox ai
# good!

import json
import os


# 读取角色的信息，返回提示词
def load_role_prompt(role_name):
    role_data = load_role_file(role_name)
    if role_data is None:
        return None
    # 拼接角色身份 + 工具协议提示，便于AI在需要时按规范触发工具调用
    prompt = role_data.get("description", "")
    tool_prompt = load_tool_prompt("ls_ll")
    if tool_prompt:
        prompt = (prompt + "\n\n" + tool_prompt).strip()
    return prompt


# 读取对应的agent角色文件，返回角色的对象
def load_role_file(role_name):
    from lib.lib import _print, get_run_path

    role_file_path = get_run_path() + "/../resources/prompt/role/" + role_name + ".json"
    if not os.path.exists(role_file_path):
        _print("Dox chat 执行异常，缺少角色文件", color="yellow")
        return None
    with open(role_file_path, "r", encoding="utf-8") as f:
        role_data = json.load(f)
    return role_data


def load_tool_prompt(prompt_name):
    from lib.lib import _print, get_run_path

    prompt_file_path = (
        get_run_path() + "/../resources/prompt/tool/" + prompt_name + ".json"
    )
    if not os.path.exists(prompt_file_path):
        _print("Dox chat 警告：缺少工具提示词文件\n", color="yellow")
        return ""

    try:
        with open(prompt_file_path, "r", encoding="utf-8") as f:
            prompt_data = json.load(f)
        return str(prompt_data.get("content", "")).strip()
    except Exception as e:
        _print(f"Dox chat 警告：工具提示词加载失败: {str(e)}\n", color="yellow")
        return ""
