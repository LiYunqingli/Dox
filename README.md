# Dox Terminal Tool

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.7%2B-green.svg)

一个跨平台的命令行工具，提供类Linux操作体验，支持视频播放、多语言交互和丰富的扩展功能。

## 🌟 功能特性

- **类Linux命令** - 支持常用命令如 `ls`, `cd`, `pwd`, `clear` 等
- **多语言支持** - 中英文双语切换（默认中文）
- **彩色终端输出** - 支持多种颜色和高亮显示
- **视频播放** - 直接在控制台播放视频（测试视频彩蛋）
- **批处理模式** - 支持通过参数批量执行命令
- **扩展框架** - 模块化设计，易于功能扩展

## 📥 安装与运行

### 前置要求
- Python 3.7+
- 推荐终端：
  - Windows: Windows Terminal / PowerShell
  - Linux/macOS: 默认终端

```bash
# 克隆仓库
git clone https://github.com/yourusername/dox-terminal.git
cd dox-terminal

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py