#!/bin/bash

# 第一步：获取脚本所在的绝对目录
# dirname "$0" 获取脚本所在目录，cd 进入后用 pwd 获取绝对路径
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# 拼接 main.py 的完整路径
MAIN_PY_PATH="${SCRIPT_DIR}/main.py"

# 第二步：检查 main.py 是否存在
if [ ! -f "${MAIN_PY_PATH}" ]; then
    echo "错误：在脚本目录 ${SCRIPT_DIR} 中未找到 main.py 文件！"
    exit 1
fi

# 第三步：定义包装脚本的路径（系统全局可执行目录）
DOX_BIN="/usr/local/bin/dox"

# 第四步：创建包装脚本（包含 python3 执行逻辑）
echo "正在创建全局命令 dox..."
cat > "${DOX_BIN}" << EOF
#!/bin/bash
python3 "${MAIN_PY_PATH}" "\$@"
EOF

# 第五步：添加可执行权限
chmod +x "${DOX_BIN}"

# 第六步：验证是否创建成功
if [ -x "${DOX_BIN}" ]; then
    echo "✅ 安装成功！"
    echo "👉 现在可以在任意位置输入 'dox' 来执行 ${MAIN_PY_PATH}"
    echo "💡 若需要传递参数，直接输入 dox 参数1 参数2 即可"
else
    echo "❌ 安装失败！请检查是否有 /usr/local/bin 的写入权限（建议用 sudo 运行脚本）"
    exit 1
fi