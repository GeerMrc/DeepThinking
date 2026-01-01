# DeepThinking-MCP IDE 配置指南

> 版本: 0.1.0
> 更新日期: 2026-01-01
> 适用对象: Claude Desktop、Claude Code、Cursor、Continue.dev 等 MCP 客户端用户

---

## 概述

DeepThinking-MCP 支持通过 MCP (Model Context Protocol) 协议与各种 IDE 和代码编辑器集成。本文档提供主流 IDE 的配置示例。

### 支持的 IDE

| IDE / 编辑器 | 支持状态 | 传输模式 | 推荐度 |
|-------------|---------|----------|--------|
| Claude Desktop | ✅ 完全支持 | STDIO / SSE | ⭐⭐⭐⭐⭐ |
| Claude Code (VSCode) | ✅ 完全支持 | STDIO / SSE | ⭐⭐⭐⭐⭐ |
| Cursor | ✅ 完全支持 | STDIO / SSE | ⭐⭐⭐⭐⭐ |
| Continue.dev | ✅ 完全支持 | STDIO | ⭐⭐⭐⭐ |
| 其他 MCP 客户端 | ✅ 协议兼容 | STDIO / SSE | ⭐⭐⭐ |

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
    "deep-thinking": {
      "command": "python",
      "args": [
        "-m",
        "deep_thinking",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

### STDIO + 配置参数

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": [
        "-m",
        "deep_thinking",
        "--transport",
        "stdio",
        "--max-thoughts",
        "50",
        "--min-thoughts",
        "3",
        "--thoughts-increment",
        "10"
      ]
    }
  }
}
```

### STDIO + 环境变量配置

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": ["-m", "deep_thinking", "--transport", "stdio"],
      "env": {
        "DEEP_THINKING_MAX_THOUGHTS": "50",
        "DEEP_THINKING_MIN_THOUGHTS": "3",
        "DEEP_THINKING_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### SSE 模式配置（远程服务器）

```json
{
  "mcpServers": {
    "deep-thinking-remote": {
      "url": "http://localhost:8088/sse",
      "headers": {
        "Authorization": "Bearer your-token-here"
      }
    }
  }
}
```

**API Key 认证**：
```json
{
  "mcpServers": {
    "deep-thinking-remote": {
      "url": "http://localhost:8088/sse",
      "headers": {
        "X-API-Key": "your-api-key-here"
      }
    }
  }
}
```

### 使用 uv 运行（推荐）

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/Deep-Thinking-MCP",
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

### 虚拟环境配置

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "deep_thinking", "--transport", "stdio"]
    }
  }
}
```

**Windows 虚拟环境**：
```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "C:\\path\\to\\venv\\Scripts\\python.exe",
      "args": ["-m", "deep_thinking", "--transport", "stdio"]
    }
  }
}
```

### 多配置示例（开发 + 生产）

```json
{
  "mcpServers": {
    "deep-thinking-local": {
      "command": "python",
      "args": ["-m", "deep_thinking", "--transport", "stdio"],
      "env": {
        "DEEP_THINKING_LOG_LEVEL": "DEBUG",
        "DEEP_THINKING_MAX_THOUGHTS": "100"
      }
    },
    "deep-thinking-prod": {
      "url": "https://api.example.com/sse",
      "headers": {
        "X-API-Key": "${PROD_API_KEY}"
      }
    }
  }
}
```

---

## Claude Code (VSCode) 配置

### 通过 Claude Code 配置

Claude Code 是 VSCode 的官方扩展，配置方式与 Claude Desktop 类似。

**配置文件**：`.claude/config.json`（项目级）或 `~/.claude/config.json`（用户级）

### 项目级配置示例

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": ["-m", "deep_thinking", "--transport", "stdio"],
      "env": {
        "DEEP_THINKING_MAX_THOUGHTS": "50",
        "DEEP_THINKING_MIN_THOUGHTS": "3"
      }
    }
  }
}
```

### 使用 .claude 目录

创建项目目录下的 `.claude/config.json`：

```
my-project/
├── .claude/
│   └── config.json
├── src/
└── README.md
```

**`.claude/config.json`**：
```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "uv",
      "args": [
        "--directory",
        "../../Deep-Thinking-MCP",
        "run",
        "python",
        "-m",
        "deep_thinking"
      ]
    }
  }
}
```

---

## Cursor 配置

Cursor 是基于 AI 的代码编辑器，完全支持 MCP 协议。

### 配置文件位置

**macOS**: `~/Library/Application Support/Cursor/User/globalStorage/mcp_servers_config.json`

**Windows**: `%APPDATA%/Cursor/User/globalStorage/mcp_servers_config.json`

**Linux**: `~/.config/Cursor/User/globalStorage/mcp_servers_config.json`

### 基础配置

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": ["-m", "deep_thinking", "--transport", "stdio"],
      "env": {
        "DEEP_THINKING_MAX_THOUGHTS": "50",
        "DEEP_THINKING_MIN_THOUGHTS": "3",
        "DEEP_THINKING_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 高级配置（带日志调试）

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": [
        "-m",
        "deep_thinking",
        "--transport",
        "stdio",
        "--log-level",
        "DEBUG"
      ],
      "env": {
        "DEEP_THINKING_DATA_DIR": "./.deep-thinking-debug"
      }
    }
  }
}
```

---

## Continue.dev 配置

Continue.dev 是 VSCode 的 AI 编程助手扩展。

### 配置文件位置

`~/.continue/config.json`

### 基础配置

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

### 使用 uv 加速启动

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/Deep-Thinking-MCP",
        "run",
        "python",
        "-m",
        "deep_thinking"
      ]
    }
  }
}
```

---

## Cline (VSCode扩展) 配置

Cline 是另一个流行的 VSCode AI 助手。

### 配置文件

`~/.cline/config.json`

### 配置示例

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": ["-m", "deep_thinking", "--transport", "stdio"],
      "env": {
        "DEEP_THINKING_MAX_THOUGHTS": "50",
        "DEEP_THINKING_MIN_THOUGHTS": "3",
        "DEEP_THINKING_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

---

## 通用配置模式

### 使用环境变量传递配置

所有 MCP 客户端都支持通过 `env` 字段传递环境变量：

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": ["-m", "deep_thinking"],
      "env": {
        "DEEP_THINKING_TRANSPORT": "stdio",
        "DEEP_THINKING_MAX_THOUGHTS": "50",
        "DEEP_THINKING_MIN_THOUGHTS": "3",
        "DEEP_THINKING_THOUGHTS_INCREMENT": "10",
        "DEEP_THINKING_LOG_LEVEL": "INFO",
        "DEEP_THINKING_DATA_DIR": "./.deep-thinking-data"
      }
    }
  }
}
```

### 混合配置（CLI 参数 + 环境变量）

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": [
        "-m",
        "deep_thinking",
        "--transport",
        "stdio",
        "--max-thoughts",
        "100"
      ],
      "env": {
        "DEEP_THINKING_MIN_THOUGHTS": "5",
        "DEEP_THINKING_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

**配置优先级**：CLI 参数 > 环境变量 > 代码默认值

---

## 多服务器配置

### 同时使用本地和远程服务器

```json
{
  "mcpServers": {
    "deep-thinking-local": {
      "command": "python",
      "args": ["-m", "deep_thinking", "--transport", "stdio"],
      "env": {
        "DEEP_THINKING_LOG_LEVEL": "DEBUG"
      }
    },
    "deep-thinking-prod": {
      "url": "https://api.example.com/sse",
      "headers": {
        "X-API-Key": "${PROD_API_KEY}"
      }
    }
  }
}
```

### 多实例配置（不同配置）

```json
{
  "mcpServers": {
    "deep-thinking-fast": {
      "command": "python",
      "args": ["-m", "deep_thinking", "--max-thoughts", "20"],
      "env": {
        "DEEP_THINKING_MIN_THOUGHTS": "1"
      }
    },
    "deep-thinking-deep": {
      "command": "python",
      "args": ["-m", "deep_thinking", "--max-thoughts", "200"],
      "env": {
        "DEEP_THINKING_MIN_THOUGHTS": "10"
      }
    }
  }
}
```

---

## 配置验证

### 验证步骤

1. **检查配置文件语法**：
   ```bash
   # 验证 JSON 格式
   cat ~/.claude/config.json | python -m json.tool
   ```

2. **检查 Python 可用性**：
   ```bash
   # 验证 Python 和 deep_thinking 可用
   python -c "import deep_thinking; print('OK')"
   ```

3. **查看日志**：
   - **Claude Desktop**: `~/Library/Logs/Claude/` (macOS)
   - **Claude Code**: VSCode 输出面板
   - **Cursor**: Help -> Toggle Developer Tools

### 常见问题排查

**问题1: MCP 服务器未连接**

- 检查配置文件路径是否正确
- 验证 `command` 和 `args` 是否正确
- 查看 IDE 日志获取详细错误信息

**问题2: 导入错误**

```bash
# 确保 deep_thinking 已安装
pip install -e /path/to/Deep-Thinking-MCP

# 或使用 uv
uv pip install -e /path/to/Deep-Thinking-MCP
```

**问题3: 权限错误**

```bash
# 确保数据目录可写
mkdir -p .deep-thinking-mcp
chmod 755 .deep-thinking-mcp
```

---

## 高级配置

### 使用自定义 Python 解释器

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "/custom/path/python3.11",
      "args": ["-m", "deep_thinking", "--transport", "stdio"]
    }
  }
}
```

### 使用 conda 环境

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "/opt/anaconda3/envs/deep-thinking/bin/python",
      "args": ["-m", "deep_thinking", "--transport", "stdio"]
    }
  }
}
```

### Docker 容器部署（高级）

**启动容器**：
```bash
docker run -d \
  --name deep-thinking-mcp \
  -p 8088:8088 \
  -e DEEP_THINKING_API_KEY="your-key" \
  -v /data:/app/.deep-thinking-mcp \
  your-registry/deep-thinking-mcp:latest \
  python -m deep_thinking --transport sse --host 0.0.0.0
```

**IDE 连接到容器**：
```json
{
  "mcpServers": {
    "deep-thinking-docker": {
      "url": "http://localhost:8088/sse",
      "headers": {
        "X-API-Key": "your-key"
      }
    }
  }
}
```

---

## 相关资源

- [SSE 配置指南](./sse-guide.md) - SSE 模式详细配置
- [安装指南](./installation.md) - 安装和部署说明
- [API 文档](./api.md) - MCP 工具 API 参考

---

## 许可证

MIT License
