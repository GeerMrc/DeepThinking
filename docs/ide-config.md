# DeepThinking-MCP IDE 配置指南

> 版本: 0.3.0
> 更新日期: 2026-01-02
> 适用对象: Claude Desktop、Claude Code、Cursor、Continue.dev 等 MCP 客户端用户

---

## 概述

DeepThinking-MCP 支持通过 MCP (Model Context Protocol) 协议与各种 IDE 和代码编辑器集成。本文档提供主流 IDE 的配置示例，包括 Claude Code CLI 的详细配置指南。

### 支持的 IDE

| IDE / 编辑器 | 支持状态 | 传输模式 | 推荐度 |
|-------------|---------|----------|--------|
| Claude Desktop | ✅ 完全支持 | STDIO / SSE | ⭐⭐⭐⭐⭐ |
| Claude Code (VSCode) | ✅ 完全支持 | STDIO / SSE | ⭐⭐⭐⭐⭐ |
| Cursor | ✅ 完全支持 | STDIO / SSE | ⭐⭐⭐⭐⭐ |
| Continue.dev | ✅ 完全支持 | STDIO | ⭐⭐⭐⭐ |
| 其他 MCP 客户端 | ✅ 协议兼容 | STDIO / SSE | ⭐⭐⭐ |

### 文档结构

本文档包含以下配置章节：
1. **Claude Desktop 配置** - 桌面应用配置
2. **Claude Code (VSCode) 配置** - VSCode扩展配置
3. **Claude Code CLI 详细配置指南** - CLI命令行配置方式（推荐）、配置文件方式
4. **Cursor 配置** - Cursor编辑器配置
5. **Continue.dev 配置** - Continue.dev扩展配置

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

### Claude Code CLI 详细配置指南

Claude Code CLI 提供了灵活的配置方式，除了手动编辑配置文件外，还提供了更便捷的**命令行配置方式**。

#### 命令行配置方式（推荐）

Claude Code CLI 提供了 `claude mcp add` 命令系列，可以快速添加和管理 MCP 服务器，无需手动编辑配置文件。

**优势**：
- ⚡ 快速配置，一行命令完成
- 📝 自动生成/更新配置文件
- ✅ 内置配置验证
- 🔄 支持三种传输方式和三种配置范围

##### STDIO 服务器配置

**基础配置**（本地 Python）：
```bash
claude mcp add --transport stdio deep-thinking -- python -m deep_thinking
```

**带环境变量的配置**：
```bash
claude mcp add --transport stdio deep-thinking \
  --env DEEP_THINKING_MAX_THOUGHTS=50 \
  --env DEEP_THINKING_MIN_THOUGHTS=3 \
  --env DEEP_THINKING_LOG_LEVEL=INFO \
  -- python -m deep_thinking --transport stdio
```

**使用 uv 加速**（推荐）：
```bash
claude mcp add --transport stdio deep-thinking \
  --env DEEP_THINKING_MAX_THOUGHTS=100 \
  -- uv run --directory /path/to/Deep-Thinking-MCP python -m deep_thinking
```

**使用虚拟环境**：
```bash
claude mcp add --transport stdio deep-thinking \
  --env DEEP_THINKING_LOG_LEVEL=DEBUG \
  -- /path/to/venv/bin/python -m deep_thinking
```

##### SSE 服务器配置（远程部署）

**无认证连接**：
```bash
claude mcp add --transport sse deep-thinking-remote http://localhost:8088/sse
```

**Bearer Token 认证**：
```bash
claude mcp add --transport sse deep-thinking-remote \
  http://localhost:8088/sse \
  --header "Authorization: Bearer your-token-here"
```

**API Key 认证**：
```bash
claude mcp add --transport sse deep-thinking-remote \
  https://api.example.com/sse \
  --header "X-API-Key: your-api-key-here"
```

**自定义请求头**（多认证）：
```bash
claude mcp add --transport sse deep-thinking-remote \
  https://api.example.com/sse \
  --header "Authorization: Bearer token123" \
  --header "X-Client-ID: deep-thinking-client" \
  --header "X-Client-Version: 1.0.0"
```

##### HTTP 服务器配置

**基础 HTTP 连接**：
```bash
claude mcp add --transport http deep-thinking-http http://localhost:8088/mcp
```

**带认证的 HTTP 连接**：
```bash
claude mcp add --transport http deep-thinking-http \
  https://api.example.com/mcp \
  --header "X-API-Key: your-api-key"
```

##### 配置范围说明

Claude Code CLI 支持三种配置范围，决定了配置的存储位置和共享范围：

**本地范围**（默认）：
```bash
# 存储位置：项目特定用户设置
# 适用场景：个人开发、实验配置、敏感凭证
claude mcp add --transport stdio deep-thinking-local -- python -m deep_thinking

# 或显式指定
claude mcp add --transport stdio deep-thinking-local --scope local -- python -m deep_thinking
```

**项目范围**（团队协作推荐）：
```bash
# 存储位置：.mcp.json（可版本控制）
# 适用场景：团队共享、项目特定工具
claude mcp add --transport stdio deep-thinking \
  --scope project \
  --env DEEP_THINKING_MAX_THOUGHTS=50 \
  -- python -m deep_thinking
```

生成的 `.mcp.json` 文件：
```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": ["-m", "deep_thinking"],
      "env": {
        "DEEP_THINKING_MAX_THOUGHTS": "50"
      }
    }
  }
}
```

**用户范围**（全局配置）：
```bash
# 存储位置：用户级全局配置
# 适用场景：个人工具、跨项目使用
claude mcp add --transport stdio deep-thinking \
  --scope user \
  -- python -m deep_thinking
```

##### 管理命令

配置完成后，可以使用以下命令管理 MCP 服务器：

```bash
# 列出所有已配置的服务器
claude mcp list

# 获取特定服务器的详细信息
claude mcp get deep-thinking

# 删除服务器
claude mcp remove deep-thinking

# 在 Claude Code 中检查服务器状态
/mcp
```

##### 完整配置示例

**开发环境配置**（本地 + 调试）：
```bash
# 项目范围 - 团队共享
claude mcp add --transport stdio deep-thinking-dev \
  --scope project \
  --env DEEP_THINKING_MAX_THOUGHTS=100 \
  --env DEEP_THINKING_LOG_LEVEL=DEBUG \
  --env DEEP_THINKING_DATA_DIR=./.deep-thinking-dev \
  -- uv run --directory ../Deep-Thinking-MCP python -m deep_thinking
```

**生产环境配置**（远程 SSE）：
```bash
# 用户范围 - 个人使用
claude mcp add --transport sse deep-thinking-prod \
  --scope user \
  https://api.production.com/sse \
  --header "X-API-Key: ${DEEP_THINKING_API_KEY}"
```

**多环境配置**（开发 + 生产）：
```bash
# 开发环境（项目级）
claude mcp add --transport stdio deep-thinking-dev \
  --scope project \
  --env DEEP_THINKING_LOG_LEVEL=DEBUG \
  -- python -m deep_thinking

# 生产环境（用户级）
claude mcp add --transport sse deep-thinking-prod \
  --scope user \
  https://api.production.com/sse \
  --header "X-API-Key: ${PROD_API_KEY}"

# 查看所有配置
claude mcp list
```

##### 环境变量扩展

在命令行配置中支持环境变量扩展：

```bash
# 使用环境变量
claude mcp add --transport sse deep-thinking \
  https://${API_HOST:-localhost}:8088/sse \
  --header "X-API-Key: ${API_KEY}"

# 使用默认值语法
claude mcp add --transport stdio deep-thinking \
  --env DEEP_THINKING_MAX_THOUGHTS=${MAX_THOUGHTS:-50} \
  -- python -m deep_thinking
```

##### 故障排除

**问题 1：命令未找到**
```bash
# 确认 Claude Code CLI 已安装
claude --version

# 更新到最新版本
claude update
```

**问题 2：权限被拒绝**
```bash
# macOS/Linux
chmod +x /path/to/Deep-Thinking-MCP/src/deep_thinking/__main__.py

# 或使用 python -m 方式
claude mcp add --transport stdio deep-thinking -- python -m deep_thinking
```

**问题 3：配置未生效**
```bash
# 检查配置文件
cat .mcp.json          # 项目级
cat ~/.claude/config.json  # 用户级

# 验证配置
claude mcp get deep-thinking

# 重启 Claude Code
```

**问题 4：多配置冲突**
```bash
# 查看所有配置及优先级
claude mcp list

# 删除冲突的配置
claude mcp remove deep-thinking-local
```

##### 手动配置文件方式

除了命令行方式，您也可以手动编辑配置文件。Claude Code CLI 提供了灵活的配置方式，支持项目级和用户级配置。

#### 配置文件位置

| 配置级别 | 文件路径 | 优先级 | 适用场景 |
|---------|---------|--------|----------|
| **项目级** | `.claude/config.json` | 高 | 项目特定的MCP服务器配置 |
| **用户级** | `~/.claude/config.json` | 低 | 全局默认配置 |

**优先级规则**：项目级配置会覆盖用户级配置的相同服务器名称。

#### .claude/ 目录结构最佳实践

推荐的项目级配置结构：

```
my-project/
├── .claude/                    # Claude Code 项目配置
│   ├── config.json            # MCP服务器配置（必需）
│   ├── CLAUDE.md              # 项目特定指令（可选）
│   ├── prompts/               # 项目级系统提示（可选）
│   │   ├── code-reviewer.md   # 代码审查提示
│   │   └── api-designer.md    # API设计提示
│   └── output-styles/         # 输出样式配置（可选）
│       └── technical-docs.md  # 技术文档样式
├── src/
└── README.md
```

#### 基础配置示例

**全局配置（~/.claude/config.json）**：
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

#### 开发模式配置（本地源码）

当您正在开发 Deep-Thinking-MCP 本身时，使用开发模式配置：

**方案1：使用绝对路径指向本地源码**
```json
{
  "mcpServers": {
    "deep-thinking-dev": {
      "command": "python",
      "args": ["-m", "deep_thinking", "--transport", "stdio"],
      "cwd": "/Volumes/DISK/Claude-code-glm/Deep-Thinking-MCP",
      "env": {
        "PYTHONPATH": "/Volumes/DISK/Claude-code-glm/Deep-Thinking-MCP/src",
        "DEEP_THINKING_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

**方案2：使用相对路径（推荐）**
```json
{
  "mcpServers": {
    "deep-thinking-dev": {
      "command": "uv",
      "args": [
        "--directory",
        "../Deep-Thinking-MCP",
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

**方案3：使用虚拟环境**
```json
{
  "mcpServers": {
    "deep-thinking-dev": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "deep_thinking", "--transport", "stdio"],
      "cwd": "/Volumes/DISK/Claude-code-glm/Deep-Thinking-MCP"
    }
  }
}
```

#### uv 加速配置

使用 uv 包管理器可以大幅提升启动速度：

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
      ],
      "env": {
        "UV_INDEX": "https://pypi.org/simple"
      }
    }
  }
}
```

**uv 优势**：
- 🚀 极快启动（比pip快10-100倍）
- 🔒 自动依赖解析
- 📦 集成虚拟环境管理

#### 环境变量配置

所有支持的环境变量：

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": ["-m", "deep_thinking"],
      "env": {
        "传输配置": "stdio",
        "DEEP_THINKING_TRANSPORT": "stdio",
        "DEEP_THINKING_HOST": "localhost",
        "DEEP_THINKING_PORT": "8000",
        "思考配置": "50",
        "DEEP_THINKING_MAX_THOUGHTS": "50",
        "DEEP_THINKING_MIN_THOUGHTS": "3",
        "DEEP_THINKING_THOUGHTS_INCREMENT": "10",
        "存储配置": "./.deep-thinking-data",
        "DEEP_THINKING_DATA_DIR": "./.deep-thinking-data",
        "日志配置": "INFO",
        "DEEP_THINKING_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### 多项目配置管理

**场景1：同时使用生产和开发版本**

```json
{
  "mcpServers": {
    "deep-thinking-prod": {
      "command": "python",
      "args": ["-m", "deep_thinking"],
      "env": {
        "DEEP_THINKING_LOG_LEVEL": "WARN"
      }
    },
    "deep-thinking-dev": {
      "command": "uv",
      "args": ["--directory", "../Deep-Thinking-MCP", "run", "python", "-m", "deep_thinking"],
      "env": {
        "DEEP_THINKING_LOG_LEVEL": "DEBUG",
        "DEEP_THINKING_DATA_DIR": "./.deep-thinking-dev"
      }
    }
  }
}
```

**场景2：不同项目使用不同配置**

项目A的 `.claude/config.json`：
```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": ["-m", "deep_thinking"],
      "env": {
        "DEEP_THINKING_MAX_THOUGHTS": "100"
      }
    }
  }
}
```

项目B的 `.claude/config.json`：
```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": ["-m", "deep_thinking"],
      "env": {
        "DEEP_THINKING_MAX_THOUGHTS": "20"
      }
    }
  }
}
```

#### 验证和调试

**1. 验证配置文件语法**

```bash
# 检查JSON格式
cat .claude/config.json | python -m json.tool
```

**2. 检查Python模块可用性**

```bash
# 验证deep_thinking可导入
python -c "import deep_thinking; print('OK')"
```

**3. 查看Claude Code日志**

VSCode输出面板会显示MCP服务器连接状态：
- ✅ 成功：`Connected to MCP server: deep-thinking`
- ❌ 失败：显示具体错误信息

**4. 测试MCP工具**

在VSCode中打开聊天窗口，输入：
```
请使用deep-thinking工具进行顺序思考
```

**5. 常见问题排查**

| 问题 | 解决方案 |
|------|---------|
| `ModuleNotFoundError: No module named 'deep_thinking'` | 运行 `pip install -e /path/to/Deep-Thinking-MCP` |
| `Permission denied` | 检查数据目录权限，或使用 `--data-dir` 指定其他位置 |
| `Command not found: uv` | 安装uv：`curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| 配置不生效 | 确认配置文件位置正确（项目级 vs 用户级） |
| 启动缓慢 | 使用uv加速，或检查网络连接 |

#### 高级配置示例

**完整的生产环境配置**

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "uv",
      "args": [
        "--directory",
        "/opt/Deep-Thinking-MCP",
        "run",
        "python",
        "-m",
        "deep_thinking",
        "--transport",
        "stdio"
      ],
      "env": {
        "DEEP_THINKING_MAX_THOUGHTS": "50",
        "DEEP_THINKING_MIN_THOUGHTS": "3",
        "DEEP_THINKING_THOUGHTS_INCREMENT": "10",
        "DEEP_THINKING_LOG_LEVEL": "INFO",
        "DEEP_THINKING_DATA_DIR": "/var/data/deep-thinking"
      }
    }
  },
  "systemPrompt": {
    "append": "使用deep-thinking工具进行复杂问题分析时，请遵循思考步骤的最佳实践。"
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
