"""
Create at 2025.4.26 16:54:52 from Mr.LiHuarong
"""

from lib.lib import load, _print, command#,  clear
import os
import sys

if sys.platform == "linux":
    try:
        import readline
        
    except (ImportError, ModuleNotFoundError, Exception):
        # 捕获所有导入相关异常，静默跳过（也可添加日志提示）
        pass

if __name__ == '__main__':
    os.chdir(os.path.expanduser('~'))
    
    args = sys.argv[1:]

    # 检查是否存在 -r 参数
    if '-r' in args:
        try:
            r_index = args.index('-r')
            cmd_str = args[r_index + 1]
        except IndexError:
            _print("Dox _10_\n", )
            sys.exit(1)
        
        commands = cmd_str.split(';')
        for cmd in commands:
            cmd = cmd.strip()
            if cmd:  # 跳过空命令
                if cmd.lower() == "exit":
                    _print("_11_\n", "red")
                else:
                    command(cmd)
                # print(f"\n----end: {cmd}----\n")
        sys.exit()
    
    # 无 -r 参数时的逻辑
    if len(args) > 0:
        cmd = ' '.join(args)
        if cmd.lower() == "exit":
            _print("_11_\n", "red")
        else:
            command(cmd)
        sys.exit()
    
    # 交互模式（无参数时）
    
    # clear()
    load()
    try:
        while True:
            try:
                userPath = os.getcwd()
                base_name = os.path.basename(userPath) #只显示当前目录名
                if base_name == "":
                    base_name = "/" #如果当前目录为根目录，则显示为"/" 注意需要考虑windows下的兼容性（目前仅考虑Ubuntu）
                # _print("Dox:" + base_name + ">>")
                input_str = input("Dox:" + base_name + ">>")
                if input_str.lower() == "exit":
                    print("exit")
                    sys.exit()
                command(input_str)
            except KeyboardInterrupt:
                print("^C")  # 处理换行，使提示符出现在新行
                continue
    except Exception as e:
        _print(f"Error: {e}\n", "red")
        input("警告：程序出现错误，抱歉您的工作区无法恢复，按任意键退出程序...")