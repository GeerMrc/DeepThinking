# DeepThinking MCP IDE 配置指南

> 版本: 1.0.0
> 更新日期: 2026-01-08
> 适用对象: Claude Desktop、Cursor、Continue.dev 等 MCP 客户端用户

---

## 概述

DeepThinking MCP 支持通过 MCP (Model Context Protocol) 协议与各种 IDE 和代码编辑器集成。

**环境变量配置**：请参考 [配置参数参考](./configuration.md)

### 支持的 IDE

| IDE / 编辑器 | 支持状态 | 传输模式 |
|-------------|---------|----------|
| Claude Desktop | ✅ 完全支持 | STDIO / SSE |
| Claude Code (VSCode) | ✅ 完全支持 | STDIO / SSE |
| Cursor | ✅ 完全支持 | STDIO / SSE |
| Continue.dev | ✅ 完全支持 | STDIO |

---

## Claude Desktop 配置

### 配置文件位置

| 操作系统 | 配置文件路径 |
|---------|-------------|
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Windows** | `%APPDATA%/Claude/claude_desktop_config.json` |
| **Linux** | `~/.config/Claude/claude_desktop_config.json` |

### 基础 STDIO 配置

```json
{
  "mcpServers": {
    "deepthinking": {
      "command": "python",
      "args": ["-m", "deep_thinking"],
      "env": {
        "DEEP_THINKING_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### SSE 远程模式配置

```json
{
  "mcpServers": {
    "deepthinking-remote": {
      "command": "python",
      "args": ["-m", "deep_thinking", "--transport", "sse"],
      "env": {
        "DEEP_THINKING_HOST": "localhost",
        "DEEP_THINKING_PORT": "8000",
        "DEEP_THINKING_AUTH_TOKEN": "your-token-here"
      }
    }
  }
}
```

### 使用虚拟环境

```json
{
  "mcpServers": {
    "deepthinking": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "deep_thinking"]
    }
  }
}
```

---

## Claude Code (VSCode) 配置

> 💡 **详细配置**：请参考 [Claude Code 配置完整指南](./claude-code-config.md)

### 快速开始

```bash
# 添加 MCP 服务器
claude mcp add deepthinking stdio python -m deep_thinking

# 查看配置
claude mcp list
```

### 配置文件方式

编辑 `~/.claude/settings.json`：

```json
{
  "mcpServers": {
    "deepthinking": {
      "command": "python",
      "args": ["-m", "deep_thinking"],
      "env": {
        "DEEP_THINKING_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### SSE 模式配置

```bash
claude mcp add deepthinking-remote sse python -m deep_thinking --transport sse \
  --env DEEP_THINKING_HOST=localhost \
  --env DEEP_THINKING_PORT=8000
```

---

## Cursor 配置

### 配置文件位置

| 操作系统 | 配置文件路径 |
|---------|-------------|
| **macOS** | `~/Library/Application Support/Cursor/User/globalStorage/mcp_servers_config.json` |
| **Windows** | `%APPDATA%/Cursor/User/globalStorage/mcp_servers_config.json` |
| **Linux** | `~/.config/Cursor/User/globalStorage/mcp_servers_config.json` |

### STDIO 模式配置

```json
{
  "mcpServers": {
    "deepthinking": {
      "command": "python",
      "args": ["-m", "deep_thinking"],
      "env": {
        "DEEP_THINKING_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### SSE 远程模式配置

```json
{
  "mcpServers": {
    "deepthinking-remote": {
      "command": "python",
      "args": ["-m", "deep_thinking", "--transport", "sse"],
      "env": {
        "DEEP_THINKING_HOST": "your-server.com",
        "DEEP_THINKING_PORT": "8000",
        "DEEP_THINKING_AUTH_TOKEN": "your-token-here"
      }
    }
  }
}
```

---

## Continue.dev 配置

### 配置文件位置

`~/.continue/config.json`

### STDIO 模式配置

```json
{
  "mcpServers": {
    "deepthinking": {
      "command": "python",
      "args": ["-m", "deep_thinking"],
      "env": {
        "DEEP_THINKING_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

---

## 通用配置选项

### 环境变量

所有 IDE 都支持通过 `env` 字段传递环境变量：

```json
{
  "env": {
    "DEEP_THINKING_LOG_LEVEL": "DEBUG",
    "DEEP_THINKING_DATA_DIR": "~/.deepthinking",
    "DEEP_THINKING_MAX_THOUGHTS": "100"
  }
}
```

**常用环境变量**：
- `DEEP_THINKING_LOG_LEVEL` - 日志级别（DEBUG/INFO/WARNING/ERROR）
- `DEEP_THINKING_DATA_DIR` - 数据存储目录
- `DEEP_THINKING_MAX_THOUGHTS` - 最大思考步骤数

详细的环境变量配置请参考：[配置参数参考](./configuration.md)

### 使用虚拟环境

确保使用正确的 Python 解释器：

```json
{
  "command": "/path/to/.venv/bin/python"
}
```

或

```json
{
  "command": "python",
  "args": ["-m", "deep_thinking"],
  "cwd": "/path/to/project"
}
```

---

## 验证配置

### 检查 MCP 连接

1. 重启 IDE
2. 查看 MCP 日志
3. 验证工具列表

### 常见问题

**问题：找不到模块**
```bash
# 确认安装
pip install deep-thinking-mcp

# 或使用开发模式
pip install -e /path/to/Deep-Thinking-MCP
```

**问题：权限错误**
```bash
# 使用用户安装
pip install --user deep-thinking-mcp
```

---

## 相关文档

- [配置参数参考](./configuration.md) - 完整的环境变量配置
- [Claude Code 配置完整指南](./claude-code-config.md) - Claude Code 详细配置
- [SSE 配置指南](./sse-guide.md) - SSE 远程模式详细配置
- [安装指南](./installation.md) - 安装和验证
