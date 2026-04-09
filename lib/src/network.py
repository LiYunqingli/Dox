import socket
import threading
import json
import time

UDP_PORT = 37020
TCP_PORT_START = 37021

# 全局状态
_device_name = None
_tcp_port = None
_run_server = False
_nodes_cache = {}  # {'node-1': ('192.168.1.100', 37021)}


def _get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _udp_listener():
    """监听广播的UDP请求"""
    global _device_name, _tcp_port, _run_server
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 对于 Windows，可能需要这么绑定
    try:
        sock.bind(("", UDP_PORT))
    except Exception as e:
        print(f"UDP Bind error: {e}")
        return

    while _run_server:
        try:
            sock.settimeout(1.0)
            data, addr = sock.recvfrom(1024)
            msg = data.decode("utf-8")
            if msg == "DOX_SCAN":
                # 收到扫描请求，回复自己的设备名和TCP端口
                reply = json.dumps({"name": _device_name, "port": _tcp_port})
                sock.sendto(reply.encode("utf-8"), addr)
        except socket.timeout:
            continue
        except Exception:
            pass
    sock.close()


def _tcp_listener():
    """监听TCP指令并执行"""
    global _run_server, _tcp_port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    port = TCP_PORT_START
    while port < TCP_PORT_START + 100:
        try:
            sock.bind(("", port))
            _tcp_port = port
            break
        except Exception:
            port += 1

    if _tcp_port is None:
        print("无法分配TCP端口进行监听。")
        _run_server = False
        return

    sock.listen(5)
    from lib.lib import _print

    _print(
        f"\n[Network] 本机服务已启动！设备名: '{_device_name}', IP: {_get_local_ip()}, 监听端口: {_tcp_port}\n",
        "green",
    )

    while _run_server:
        try:
            sock.settimeout(1.0)
            client, addr = sock.accept()
            # 开个线程处理
            threading.Thread(
                target=_handle_tcp_client, args=(client, addr), daemon=True
            ).start()
        except socket.timeout:
            continue
        except Exception:
            pass
    sock.close()


def _handle_tcp_client(client: socket.socket, addr):
    try:
        # 接收数据
        data = client.recv(4096).decode("utf-8")
        if not data:
            return

        cmd = data
        sync = True
        try:
            payload = json.loads(data)
            if isinstance(payload, dict):
                cmd = payload.get("cmd", data)
                sync = payload.get("sync", True)
        except Exception:
            pass

        if sync:
            from lib.lib import _print

            _print(f"\n[Remote Exec] {cmd}\n", "magenta")

        # 拦截stdout，执行命令
        import io
        from contextlib import redirect_stdout
        from lib.lib import command

        f = io.StringIO()
        with redirect_stdout(f):
            command(cmd)

        output = f.getvalue()

        if sync and output:
            print(output, end="")

        if not output.strip():
            output = "[OK] 执行完毕，无输出。"

        client.sendall(output.encode("utf-8"))
    except Exception as e:
        err = f"[Error] 远程执行遇到错误: {e}"
        client.sendall(err.encode("utf-8"))
    finally:
        client.close()


def serve(device_name):
    """启动服务端"""
    global _device_name, _run_server
    if _run_server:
        from lib.lib import _print

        _print("[Network] 错误：服务已在后台运行。\n", "red")
        return

    _device_name = device_name
    _run_server = True

    threading.Thread(target=_udp_listener, daemon=True).start()
    threading.Thread(target=_tcp_listener, daemon=True).start()


def scan():
    """扫描局域网内的其它Dox设备"""
    from lib.lib import _print

    _print("[Network] 正在扫描局域网中的 Dox 节点...\n", "yellow")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2.0)

    # 广播包
    sock.sendto("DOX_SCAN".encode("utf-8"), ("<broadcast>", UDP_PORT))

    global _nodes_cache
    _nodes_cache.clear()

    start_time = time.time()
    while time.time() - start_time < 2.0:
        try:
            data, addr = sock.recvfrom(1024)
            info = json.loads(data.decode("utf-8"))
            name = info.get("name")
            port = info.get("port")
            if name and port:
                _nodes_cache[name] = (addr[0], port)
                _print(f"找到节点: {name} ({addr[0]}:{port})\n", "green")
        except socket.timeout:
            break
        except Exception:
            pass

    sock.close()
    if not _nodes_cache:
        _print("[Network] 未找到任何节点。\n", "red")


def _send_command(node_name, cmd, sync=True) -> str:
    """向目标发送命令并获取结果"""
    if node_name not in _nodes_cache:
        # 如果缓存没有，先扫描一次
        scan()
        if node_name not in _nodes_cache:
            return f"[Error] 未找到名为 '{node_name}' 的节点。"

    ip, port = _nodes_cache[node_name]
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((ip, port))

        payload = json.dumps({"cmd": cmd, "sync": sync})
        sock.sendall(payload.encode("utf-8"))

        # 接收结果
        result = []
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            result.append(chunk.decode("utf-8"))

        sock.close()
        return "".join(result)
    except Exception as e:
        return f"[Error] 连接节点 '{node_name}' 失败: {e}"


def send(node_name, cmd, sync=True):
    from lib.lib import _print

    if not cmd.strip():
        _print("发送的命令不能为空。\n", "red")
        return

    _print(f"\n[发送至 {node_name}] -> {cmd}\n", "blue")
    res = _send_command(node_name, cmd, sync)
    print(res)


def connect(node_name, sync=True):
    from lib.lib import _print

    if node_name not in _nodes_cache:
        scan()
        if node_name not in _nodes_cache:
            _print(f"[Error] 未找到名为 '{node_name}' 的节点。\n", "red")
            return

    _print(
        f"\n=== 连接到 '{node_name}' (同步输出: {sync}) (输入 'exit' 退出) ===\n",
        "green",
    )

    while True:
        try:
            cmd = input(f"Dox({node_name})&> ")
            if cmd.strip() == "":
                continue
            if cmd.lower() in ("exit", "& disconnect"):
                _print("\n已断开连接。\n", "yellow")
                break

            res = _send_command(node_name, cmd, sync)
            print(res)
        except KeyboardInterrupt:
            _print("\n已断开连接。\n", "yellow")
            break


def stop():
    """停止服务端监听"""
    global _run_server
    from lib.lib import _print

    if not _run_server:
        _print("[Network] 服务未在运行。\n", "yellow")
        return
    _run_server = False
    _print("[Network] 本机服务已关闭。\n", "green")


def network_cmd(input_str: str):
    """处理所有的 & 命令"""
    from lib.lib import _print

    parts = input_str.split(maxsplit=2)
    if len(parts) < 2:
        _print(
            "用法: & serve <name> | & stop | & scan | & send <name> [-q] <cmd> | & connect <name> [-q]\n",
            "yellow",
        )
        return

    action = parts[1].lower()

    if action == "serve":
        name = parts[2].split()[0] if len(parts) > 2 and parts[2].split() else "node"
        serve(name)
    elif action == "stop":
        stop()
    elif action == "scan":
        scan()
    elif action == "send":
        if len(parts) < 3:
            _print("用法: & send <name> [-q] <cmd>\n", "red")
            return

        args = parts[2].split(maxsplit=1)
        if not args:
            _print("请输入目标节点和命令。\n", "red")
            return

        node_name = args[0]
        rem_cmd = args[1] if len(args) > 1 else ""

        sync = True
        if rem_cmd.startswith("-q "):
            sync = False
            rem_cmd = rem_cmd[3:].strip()

        if not rem_cmd:
            _print("请输入要执行的命令。\n", "red")
            return

        send(node_name, rem_cmd, sync)
    elif action == "connect":
        rem = parts[2].split() if len(parts) > 2 else []
        name = rem[0] if rem else ""
        sync = True
        if "-q" in rem:
            sync = False

        if not name:
            _print("用法: & connect <name> [-q]\n", "red")
            return
        connect(name, sync)
    else:
        _print(f"未知的 & 指令: {action}\n", "red")
