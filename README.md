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

```

## 📖 使用说明

### 交互模式

```bash
help
cd Documents
Documents >> ls -l
```

### 命令行参数模式

```bash
# 单命令模式
python main.py ls -l

# 批量命令模式
python main.py -r "cd /; ls; pwd"
```

## 📚 命令手册

| 命令 | 描述 | 使用示例 |
| --- | --- | --- |
| help | 显示帮助信息 | help ls |
| cd | 切换工作目录 | cd ../ |
| ls | 列出目录内容 | ls -l (详细模式) |
| ll | 同 ls -l | ll |
| pwd | 显示当前路径 | pwd |
| clear | 清空屏幕 | clear |
| version | 显示版本信息 | version |
| video | 播放视频 | video test (测试视频) |
| exit | 退出程序 | exit |

## 🌍 多语言支持

修改 config/config.json 中的语言设置：

```json
{
  "Config": {
    "Lang": "zh-CN"  // 可选 en-US
  }
}
```

## 🛠️ 开发与贡献

欢迎提交 Pull Request 或 Issue，共同改进项目。请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (git checkout -b feature/your-feature)
3. 提交修改 (git commit -m 'Add some feature')
4. 推送到分支 (git push origin feature/your-feature)
5. 创建 Pull Request

代码规范：

- 使用 Google Python 风格指南
- 新增功能需添加对应单元测试
- 修改语言文件需同步更新中英文版本

## 📜 许可证

本项目遵循 MIT 许可证。请查看 LICENSE 文件了解更多信息。

## 🎮 彩蛋功能

<!-- 输入 donghua 命令体验特殊动画效果（开发者预留惊喜） -->
<!-- 加粗donghua -->
输入 ```donghua``` 命令体验特殊动画效果（开发者预留惊喜）