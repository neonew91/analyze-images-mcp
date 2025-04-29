# Gemini 2.5 Pro 图片理解工具

这是一个简单的Python脚本，用于调用Google Gemini 2.5 Pro API进行图片理解和分析。支持同时分析多张图片，并分析它们之间的关系。

## 准备工作

```
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install fastmcp
```

## 使用方法

### MCP配置

```
{
    "mcpServers": {
        "analyzeimage MCP": {
            "command": "/绝对路径/到/venv/bin/python3",
            "args": [
                "/绝对路径/到/gemini_vision.py",
                "--stdio"
            ]
        }
    }
}
```