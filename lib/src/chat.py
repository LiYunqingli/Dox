import os
import json
import requests
from lib.lib import _print, get_config, get_run_path

def _save_config(config):
    config_file_path = get_run_path() + "/../config/config.json"
    with open(config_file_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def chat_cmd(input_str):
    input_list = input_str.split(" ", 1)
    
    config = get_config()
    # 如果 config.json 中没有 AI 配置，默认补充 DeepSeek / OpenAI 兼容格式
    if "AI" not in config:
        config["AI"] = {
            "API_URL": "https://api.deepseek.com/chat/completions",
            "API_KEY": "",
            "Model": "deepseek-chat"
        }
        _save_config(config)
    
    ai_config = config["AI"]
    api_key = ai_config.get("API_KEY", "")
    
    if not api_key:
        _print("未找到 API_KEY。\n请在 'config/config.json' 中配置 AI 节点的 'API_KEY'！\n", "red")
        _print("例如设置免费的 DeepSeek、Kimi 或者本地 Ollama 的 API 信息。\n", "yellow")
        return
        
    api_url = ai_config.get("API_URL", "https://api.deepseek.com/chat/completions")
    model = ai_config.get("Model", "deepseek-chat")
    
    messages = [
        {"role": "system", "content": "你是由 Dox 项目嵌入的本地终端 AI 助手，回答应该简短、准确，并在可能的情况下返回可以被直接执行的命令行指令。"}
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    def ask_ai(msgs):
        try:
            payload = {
                "model": model,
                "messages": msgs
            }
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                answer = response.json()["choices"][0]["message"]["content"]
                return answer
            else:
                return f"[HTTP {response.status_code}] 接口调用异常: {response.text}"
        except Exception as e:
            return f"[Error] 请求出错: {str(e)}"

    # 如果输入时带了参数 (例如: chat 你好) 进行单次问答
    if len(input_list) > 1:
        question = input_list[1].strip()
        messages.append({"role": "user", "content": question})
        _print("Dox AI思考中...\n", "cyan")
        ans = ask_ai(messages)
        _print(f"\nDox AI:\n{ans}\n\n", "green")
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
                messages.append({"role": "user", "content": user_input})
                ans = ask_ai(messages)
                _print(f"[Dox AI] {ans}\n", "green")
                messages.append({"role": "assistant", "content": ans})
                
            except (KeyboardInterrupt, EOFError):
                break
        _print("\n退出 Dox AI。\n", "yellow")
