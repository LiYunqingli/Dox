import json
import requests
from lib.lib import _print, get_config, get_run_path
from lib.src.agent_tool_selector import (
    parse_and_execute,
    build_tool_result_for_ai,
    extract_command_call,
    execute_dox_command,
)


# 如果config.json中没有关于AI的配置，将调用函数里补充AI配置
def _save_config(config):
    config_file_path = get_run_path() + "/../config/config.json"
    with open(config_file_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def chat_cmd(input_str):
    input_list = input_str.split(" ", 1)
    config = get_config()

    # 硬编码到程序中，如果没有相关配置直接覆写
    if "AI" not in config:
        config["AI"] = {
            "API_URL": "https://api.deepseek.com/chat/completions",
            "API_KEY": "",
            "Model": "deepseek-chat",
        }
        _save_config(config)

    ai_config = config["AI"]
    api_key = ai_config.get("API_KEY", "")

    if not api_key:
        _print(
            "_67_\n_68_\n",
            "red",
        )
        _print(
            "ps: set AI.API_KEY sk-xxxxx\nset AI.API_URL https://api.deepseek.com/chat/completions\nset AI.Model deepseek-chat\n",
            "yellow",
        )
        _print(
            "\n_69_\n",
            "yellow",
        )
        return

    api_url = ai_config.get("API_URL", "https://api.deepseek.com/chat/completions")
    model = ai_config.get("Model", "deepseek-chat")

    # 读取角色文件
    from lib.src.prompt import load_role_prompt

    # role = system 的意思是给ai设定角色背景信息以及行为准则
    messages = [
        {
            "role": "system",
            "content": load_role_prompt("dox"),
        }
    ]

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    def ask_ai(msgs, stream=False):
        try:
            payload = {"model": model, "messages": msgs, "stream": stream}
            response = requests.post(
                api_url, json=payload, headers=headers, timeout=30, stream=stream
            )
            if response.status_code == 200:
                if stream:
                    full_answer = ""
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode("utf-8")
                            if decoded_line.startswith("data: "):
                                data_str = decoded_line[6:]
                                if data_str == "[DONE]":
                                    break
                                try:
                                    data_json = json.loads(data_str)
                                    if (
                                        "choices" in data_json
                                        and len(data_json["choices"]) > 0
                                    ):
                                        delta = data_json["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            print(content, end="", flush=True)
                                            full_answer += content
                                except json.JSONDecodeError:
                                    pass
                    print()
                    return full_answer
                else:
                    answer = response.json()["choices"][0]["message"]["content"]
                    return answer
            else:
                return f"[HTTP {response.status_code}] 接口调用异常: {response.text}"
        except Exception as e:
            return f"[Error] 请求出错: {str(e)}"

    def chat_once(user_text: str):
        messages.append({"role": "user", "content": user_text})

        # 第一轮：先拿完整回复，判断是否触发工具调用
        first_answer = ask_ai(messages, stream=False)
        messages.append({"role": "assistant", "content": first_answer})

        tool_result = parse_and_execute(first_answer)
        if tool_result is None:
            # 无工具调用，直接输出AI首轮结果
            _print("[Dox AI] ", "green")
            print(first_answer)
            return

        # 有工具调用：把执行结果回注给AI，请它给最终自然语言答复
        tool_feedback = build_tool_result_for_ai(tool_result)
        messages.append({"role": "user", "content": tool_feedback})

        _print("[Dox AI] ", "green")
        final_answer = ask_ai(messages, stream=True)
        messages.append({"role": "assistant", "content": final_answer})

    # 如果输入时带了参数 (例如: chat 你好) 进行单次问答
    if len(input_list) > 1:
        question = input_list[1].strip()
        _print("Dox AI思考中...\n", "cyan")
        chat_once(question)
        print("\n")
    else:
        # 进入交互式闲聊模式
        _print(">> 已进入 Dox AI 对话模式 (输入 exit 退出) <<\n", "cyan")
        while True:
            try:
                user_input = input("[You] ")
                user_input = user_input.strip()
                if user_input.lower() in ("exit", "quit"):
                    break
                if not user_input:
                    continue
                chat_once(user_input)

            except (KeyboardInterrupt, EOFError):
                break
        _print("\n退出 Dox AI。\n", "yellow")


def ai_run_cmd(input_str):
    input_list = input_str.split(" ", 1)
    if len(input_list) < 2 or not input_list[1].strip():
        _print("请输入提示词，例如: ? 把语言切换为英文\n", "yellow")
        return

    user_prompt = input_list[1].strip()
    config = get_config()

    if "AI" not in config:
        config["AI"] = {
            "API_URL": "https://api.deepseek.com/chat/completions",
            "API_KEY": "",
            "Model": "deepseek-chat",
        }
        _save_config(config)

    ai_config = config["AI"]
    api_key = ai_config.get("API_KEY", "")
    if not api_key:
        _print("_67_\n_68_\n", "red")
        _print(
            "ps: set AI.API_KEY sk-xxxxx\nset AI.API_URL https://api.deepseek.com/chat/completions\nset AI.Model deepseek-chat\n",
            "yellow",
        )
        _print("\n_69_\n", "yellow")
        return

    api_url = ai_config.get("API_URL", "https://api.deepseek.com/chat/completions")
    model = ai_config.get("Model", "deepseek-chat")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    from lib.src.prompt import load_role_file, load_tool_prompt, load_help_prompt_for_ai

    role_desc = ""
    role_obj = load_role_file("dox")
    if isinstance(role_obj, dict):
        role_desc = str(role_obj.get("description", "")).strip()

    cmd_prompt = load_tool_prompt("global_cmd")
    help_doc = load_help_prompt_for_ai()

    system_prompt = (
        (role_desc + "\n\n" if role_desc else "")
        + (cmd_prompt + "\n\n" if cmd_prompt else "")
        + "以下是 Dox 帮助文档，请根据文档选择最合适的一条命令：\n"
        + help_doc
    ).strip()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        payload = {"model": model, "messages": messages, "stream": False}
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        if response.status_code != 200:
            _print(
                f"[HTTP {response.status_code}] 接口调用异常: {response.text}\n", "red"
            )
            return
        ai_text = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        _print(f"[Error] 请求出错: {str(e)}\n", "red")
        return

    cmd = extract_command_call(ai_text)
    if not cmd:
        _print("AI 未返回可执行命令，请检查提示词规范。\n", "yellow")
        print(ai_text)
        return

    _print("[AI CMD] ", "cyan")
    print(cmd)
    result = execute_dox_command(cmd)
    if result.get("output"):
        print(result["output"])
