# Claude Desktop 配置示例

本目录包含 DeepThinking MCP 与 Claude Desktop 集成的配置示例。

## 配置文件说明

| 配置文件 | 用途 | 适用场景 |
|---------|------|---------|
| `claude_desktop_config_stdio.json` | STDIO 模式配置 | **推荐**：日常使用，由 Claude Desktop 自动启动 |
| `claude_desktop_config_sse.json` | SSE 模式配置 | Web 应用、远程访问 |
| `claude_desktop_config_custom_storage.json` | 自定义存储目录 | 需要指定数据存储位置 |
| `claude_desktop_config_debug.json` | 调试模式配置 | 开发调试，启用详细日志 |

## 快速开始

### 安装 DeepThinking MCP

首先选择一种方式安装 DeepThinking MCP：

#### 使用 uv（推荐）⚡
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 DeepThinking MCP
uv pip install Deep-Thinking-MCP
```

#### 使用 pip
```bash
pip install Deep-Thinking-MCP
```

---

### 1. STDIO 模式（推荐）

这是最简单的配置方式，适用于大多数用户。

1. 复制配置内容到您的 Claude Desktop 配置文件：

**macOS 配置文件位置**：
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows 配置文件位置**：
```
%APPDATA%/Claude/claude_desktop_config.json
```

**Linux 配置文件位置**：
```
~/.config/Claude/claude_desktop_config.json
```

2. 将以下内容添加到配置文件中：

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": [
        "-m",
        "deep_thinking",
        "--mode",
        "stdio"
      ]
    }
  }
}
```

3. 重启 Claude Desktop

### 2. SSE 模式

适用于需要 Web 访问或远程访问的场景。

1. 启动 SSE 服务器：

```bash
python -m deep_thinking --mode sse --host 127.0.0.1 --port 8088
```

2. 复制 `claude_desktop_config_sse.json` 的内容到 Claude Desktop 配置文件

3. 重启 Claude Desktop

### 3. 自定义存储目录

如果您想将数据存储在特定位置：

1. 复制 `claude_desktop_config_custom_storage.json` 的内容

2. 修改 `--storage-dir` 参数为您想要的路径

3. 添加到 Claude Desktop 配置文件

## 配置验证

配置完成后，在 Claude Desktop 中测试：

```
列出所有可用的思考模板
```

如果返回模板列表，说明配置成功。

## 多服务器配置

您可以同时配置多个 MCP 服务器：

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": ["-m", "deep_thinking", "--mode", "stdio"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
    }
  }
}
```

## 环境变量配置

您也可以通过环境变量配置 DeepThinking MCP：

```bash
# 设置存储目录
export DEEP_THINKING_STORAGE_DIR="~/Documents/deep-thinking-data"

# 设置日志级别
export DEEP_THINKING_LOG_LEVEL="DEBUG"
```

然后在 Claude Desktop 配置中使用环境变量：

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": ["-m", "deep_thinking", "--mode", "stdio"],
      "env": {
        "DEEP_THINKING_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## 故障排除

### 问题：Claude Desktop 无法连接到 MCP 服务器

**解决方案**：

1. 确认配置文件路径正确
2. 确认 JSON 格式正确（使用 JSON 验证工具检查）
3. 重启 Claude Desktop
4. 查看日志：`~/Library/Logs/Claude/` (macOS)

### 问题：STDIO 模式无法启动

**解决方案**：

1. 确认 Python 已安装：`python --version`
2. 确认包已安装：
   - 使用 pip: `pip list | grep deep-thinking`
   - 使用 uv: `uv pip list | grep deep-thinking`
3. 尝试完整路径：将 `"python"` 改为 `"/usr/bin/python3"` 或完整 Python 路径

### 问题：SSE 模式连接失败

**解决方案**：

1. 确认 SSE 服务器已启动
2. 测试连接：`curl http://127.0.0.1:8088/health`
3. 检查防火墙设置

## 高级配置

### 使用 uv（推荐）⚡

如果您使用 uv 安装了 DeepThinking MCP：

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/DeepThinking",
        "run",
        "python",
        "-m",
        "deep_thinking",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

或使用全局安装：

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": ["-m", "deep_thinking", "--transport", "stdio"]
    }
  }
}
```

### 使用虚拟环境

如果您在虚拟环境中安装了 DeepThinking MCP：

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "deep_thinking", "--mode", "stdio"]
    }
  }
}
```

### Windows 路径示例

Windows 上使用反斜杠或正斜杠均可：

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": [
        "-m",
        "deep_thinking",
        "--mode",
        "stdio",
        "--storage-dir",
        "C:\\Users\\YourName\\Documents\\deep-thinking-data"
      ]
    }
  }
}
```

### Linux systemd 服务

为 SSE 模式创建系统服务：

创建 `/etc/systemd/system/deep-thinking.service`：

```ini
[Unit]
Description=DeepThinking MCP Server
After=network.target

[Service]
Type=simple
User=your-username
ExecStart=/usr/bin/python3 -m deep_thinking --mode sse --host 0.0.0.0 --port 8088
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable deep-thinking
sudo systemctl start deep-thinking
```

## 相关资源

- [安装与配置指南](../docs/installation.md)
- [用户指南](../docs/user_guide.md)
- [API 文档](../docs/api.md)
