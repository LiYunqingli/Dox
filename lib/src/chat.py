import json
import requests
from lib.lib import _print, get_config, get_run_path
from lib.src.agent_tool_selector import (
    parse_and_execute,
    build_tool_result_for_ai,
    extract_command_call,
    execute_dox_commands,
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

    def ask_ai_stream_with_tool_probe(msgs):
        """单次流式请求：在流式接收时探测是否为工具调用标签。

        - 如果是工具调用标签：不输出流式文本，仅返回完整内容。
        - 如果是普通回答文本：实时流式输出并返回完整内容。
        """
        tool_prefix = "<DOX_TOOL_CALL>"
        try:
            payload = {"model": model, "messages": msgs, "stream": True}
            response = requests.post(
                api_url, json=payload, headers=headers, timeout=30, stream=True
            )
            if response.status_code != 200:
                return (
                    f"[HTTP {response.status_code}] 接口调用异常: {response.text}",
                    False,
                )

            full_answer = ""
            probe_buf = ""
            mode = "unknown"  # unknown | tool | text
            printed_prefix = False

            for line in response.iter_lines():
                if not line:
                    continue
                decoded_line = line.decode("utf-8")
                if not decoded_line.startswith("data: "):
                    continue

                data_str = decoded_line[6:]
                if data_str == "[DONE]":
                    break

                try:
                    data_json = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                if "choices" not in data_json or len(data_json["choices"]) == 0:
                    continue

                delta = data_json["choices"][0].get("delta", {})
                content = delta.get("content", "")
                if not content:
                    continue

                full_answer += content

                if mode == "unknown":
                    probe_buf += content
                    probe = probe_buf.lstrip()

                    if not probe:
                        continue

                    # 前缀仍可能匹配工具标签，继续等待更多字符
                    if tool_prefix.startswith(probe):
                        continue

                    # 明确是工具调用
                    if probe.startswith(tool_prefix):
                        mode = "tool"
                        continue

                    # 非工具调用，切换到文本流式输出
                    mode = "text"
                    if not printed_prefix:
                        _print("[Dox AI] ", "green")
                        printed_prefix = True
                    print(probe_buf, end="", flush=True)
                    probe_buf = ""
                    continue

                if mode == "text":
                    print(content, end="", flush=True)

            if mode == "unknown":
                # 流结束仍未判定：按最终文本决定
                probe = probe_buf.lstrip()
                if probe.startswith(tool_prefix):
                    mode = "tool"
                else:
                    mode = "text"
                    if probe_buf:
                        _print("[Dox AI] ", "green")
                        print(probe_buf, end="", flush=True)

            if mode == "text":
                print()

            return full_answer, (mode == "tool")
        except Exception as e:
            return f"[Error] 请求出错: {str(e)}", False

    def chat_once(user_text: str):
        messages.append({"role": "user", "content": user_text})

        # 支持多轮工具链：AI可连续调用工具，直到返回最终自然语言答案
        max_tool_steps = 8
        step = 0

        while step < max_tool_steps:
            step += 1
            answer, is_tool = ask_ai_stream_with_tool_probe(messages)
            messages.append({"role": "assistant", "content": answer})

            if not is_tool:
                return

            tool_result = parse_and_execute(answer)
            if tool_result is None:
                # 兜底：若探测为工具但解析失败，按普通文本输出，避免吞消息
                _print("[Dox AI] ", "green")
                print(answer)
                return

            tool_feedback = build_tool_result_for_ai(tool_result)
            messages.append({"role": "user", "content": tool_feedback})

        # 超出最大工具调用轮次时，避免死循环
        _print("[Dox AI] ", "green")
        print("工具调用次数过多，已中止本轮。请缩小问题范围后重试。")

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
    result = execute_dox_commands(cmd)
    if result.get("output"):
        print(result["output"])
