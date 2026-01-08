# Claude Code 配置完整指南

> 版本: 1.0.0
> 更新日期: 2026-01-02
> 适用对象: Claude Code CLI 用户、VSCode 开发者

---

## 概述

Claude Code 是 Anthropic 官方的 VSCode AI 助手，支持通过 MCP (Model Context Protocol) 协议集成 DeepThinking MCP 服务器。

### 配置方式对比

Claude Code 提供两种配置方式：

| 方式 | 优势 | 适用场景 |
|------|------|----------|
| **CLI 命令行** | ⚡ 快速、自动验证、一键配置 | 快速上手、日常使用 |
| **配置文件** | 🔧 灵活、可版本控制、团队共享 | 项目配置、深度定制 |

### 文档结构

本文档包含以下配置章节：
1. **CLI 命令行配置方式**（推荐）- 快速配置指南
2. **配置文件方式** - 手动配置和高级选项
3. **故障排除** - 常见问题和解决方案

---

## CLI 命令行配置方式（推荐）

Claude Code CLI 提供了 `claude mcp add` 命令系列，可以快速添加和管理 MCP 服务器，无需手动编辑配置文件。

**优势**：
- ⚡ 快速配置，一行命令完成
- 📝 自动生成/更新配置文件
- ✅ 内置配置验证
- 🔄 支持三种传输方式和三种配置范围

### STDIO 服务器配置

**基础配置**（本地 Python）：
```bash
claude mcp add --transport stdio deep-thinking -- python -m deep_thinking
```

**带环境变量的配置**：
```bash
claude mcp add --transport stdio deep-thinking \
  --env DEEP_THINKING_DESCRIPTION="我的AI助手服务器" \
  --env DEEP_THINKING_MAX_THOUGHTS=50 \
  --env DEEP_THINKING_MIN_THOUGHTS=3 \
  --env DEEP_THINKING_LOG_LEVEL=INFO \
  -- python -m deep_thinking --transport stdio
```

**使用 uv 加速**（推荐）：
```bash
claude mcp add --transport stdio deep-thinking \
  --env DEEP_THINKING_MAX_THOUGHTS=100 \
  -- uv run --directory /path/to/DeepThinking python -m deep_thinking
```

**使用虚拟环境**：
```bash
claude mcp add --transport stdio deep-thinking \
  --env DEEP_THINKING_LOG_LEVEL=DEBUG \
  -- /path/to/venv/bin/python -m deep_thinking
```

### SSE 服务器配置（远程部署）

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

### HTTP 服务器配置

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

### 配置范围说明

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
  --env DEEP_THINKING_DESCRIPTION="项目AI助手 - 专用工具" \
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

### JSON 配置导入方式

除了逐参数配置，Claude Code CLI 还提供了 `claude mcp add-json` 命令，可以直接使用 JSON 配置导入 MCP 服务器。

**优势**：
- 📦 从现有 JSON 配置快速导入
- 🔄 适合配置迁移和批量操作
- 📝 支持从文件或标准输入读取
- ✅ 自动验证 JSON 格式

**适用场景**：
- 从 Claude Desktop 或其他 MCP 客户端迁移配置
- 脚本化批量配置多个服务器
- 使用版本控制的配置文件

#### 基本用法

> ⚠️ **重要提示**：`claude mcp add-json` 命令需要将 JSON 作为单个参数传递。heredoc 方式在某些 shell 中可能无法正确工作。

**方式1：直接传递 JSON 字符串**（推荐）
```bash
claude mcp add-json deep-thinking '{"command":"python","args":["-m","deep_thinking"]}'
```

**方式2：使用 echo 和管道**（适用于复杂配置）
```bash
echo '{
  "command": "python",
  "args": ["-m", "deep_thinking"],
  "env": {
    "DEEP_THINKING_MAX_THOUGHTS": "50"
  }
}' | claude mcp add-json deep-thinking -
```

**方式3：从文件读取**
```bash
claude mcp add-json deep-thinking < config.json
```

**方式4：使用 claude mcp add 命令**（最灵活，推荐用于复杂配置）
```bash
claude mcp add --transport stdio deep-thinking -- python -m deep_thinking
```

> 💡 **建议**：对于复杂配置（如多个环境变量），推荐使用 `claude mcp add` 命令，它支持：
> - Shell 环境变量扩展（`${VAR}`）
> - 更好的可读性
> - 逐参数配置

#### STDIO 配置示例

**基础配置**（本地 Python）：
```bash
# 推荐：使用 claude mcp add 命令
claude mcp add --transport stdio deep-thinking \
  --env DEEP_THINKING_DESCRIPTION="我的AI助手" \
  --env DEEP_THINKING_MAX_THOUGHTS=50 \
  --env DEEP_THINKING_MIN_THOUGHTS=3 \
  -- python -m deep_thinking

# 或使用 add-json 直接传递 JSON 字符串
claude mcp add-json deep-thinking '{"command":"python","args":["-m","deep_thinking"],"env":{"DEEP_THINKING_MAX_THOUGHTS":"50","DEEP_THINKING_MIN_THOUGHTS":"3"}}'
```

**带环境变量的配置**：
```bash
# 推荐：使用 claude mcp add 命令
claude mcp add --transport stdio deep-thinking \
  --env DEEP_THINKING_MAX_THOUGHTS=100 \
  --env DEEP_THINKING_LOG_LEVEL=DEBUG \
  --env DEEP_THINKING_DATA_DIR="./.deep-thinking-data" \
  -- python -m deep_thinking --transport stdio

# 或使用 echo 和管道
echo '{
  "command": "python",
  "args": ["-m", "deep_thinking", "--transport", "stdio"],
  "env": {
    "DEEP_THINKING_MAX_THOUGHTS": "100",
    "DEEP_THINKING_LOG_LEVEL": "DEBUG",
    "DEEP_THINKING_DATA_DIR": "./.deep-thinking-data"
  }
}' | claude mcp add-json deep-thinking -
```

**使用 uv 加速**（推荐）：
```bash
# 推荐：使用 claude mcp add 命令
claude mcp add --transport stdio deep-thinking \
  --env DEEP_THINKING_MAX_THOUGHTS=100 \
  -- uv run --directory /path/to/DeepThinking python -m deep_thinking

# 或使用 add-json 直接传递 JSON 字符串
claude mcp add-json deep-thinking '{"command":"uv","args":["--directory","/path/to/DeepThinking","run","python","-m","deep_thinking"],"env":{"DEEP_THINKING_MAX_THOUGHTS":"100"}}'
```

#### 从现有配置迁移

**从 Claude Desktop 迁移**：

Claude Desktop 配置（`~/.claude/desktop_config.json`）：
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

迁移命令：
```bash
# 1. 提取单个服务器配置
jq '.mcpServers.deep-thinking' ~/.claude/desktop_config.json | \
  claude mcp add-json deep-thinking

# 2. 批量迁移所有服务器
jq -r '.mcpServers | to_entries[] | "\(.key) \(.value | @json)"' \
  ~/.claude/desktop_config.json | while read -r name config; do
  echo "$config" | claude mcp add-json "$name"
done
```

**从其他 MCP 客户端迁移**：

如果其他客户端使用相同的 JSON 格式，可以直接使用其配置文件：
```bash
claude mcp add-json deep-thinking < /path/to/other-client-config.json
```

#### 批量配置脚本

**Shell 脚本示例**（批量配置多个服务器）：
```bash
#!/bin/bash
# configure-mcps.sh

# 配置数组（名称:配置文件路径）
declare -A configs=(
  ["deep-thinking"]="configs/deep-thinking.json"
  ["deep-thinking-dev"]="configs/deep-thinking-dev.json"
)

# 批量添加配置
for name in "${!configs[@]}"; do
  config_file="${configs[$name]}"
  echo "正在配置 $name..."
  claude mcp add-json "$name" < "$config_file"
  if [ $? -eq 0 ]; then
    echo "✅ $name 配置成功"
  else
    echo "❌ $name 配置失败"
  fi
done

echo "完成！列出所有配置："
claude mcp list
```

**Python 脚本示例**（动态生成配置）：
```python
#!/usr/bin/env python3
import json
import subprocess

# 定义多个服务器配置
servers = {
    "deep-thinking-prod": {
        "command": "python",
        "args": ["-m", "deep_thinking"],
        "env": {
            "DEEP_THINKING_MAX_THOUGHTS": "50",
            "DEEP_THINKING_LOG_LEVEL": "INFO"
        }
    },
    "deep-thinking-dev": {
        "command": "uv",
        "args": [
            "--directory",
            "../Deep-Thinking-MCP",
            "run",
            "python",
            "-m",
            "deep_thinking"
        ],
        "env": {
            "DEEP_THINKING_LOG_LEVEL": "DEBUG",
            "DEEP_THINKING_MAX_THOUGHTS": "100"
        }
    }
}

# 批量添加配置
for name, config in servers.items():
    config_json = json.dumps(config)
    result = subprocess.run(
        ["claude", "mcp", "add-json", name],
        input=config_json,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"✅ {name} 配置成功")
    else:
        print(f"❌ {name} 配置失败: {result.stderr}")
```

#### 与配置范围结合

**项目级配置**（团队共享）：
```bash
claude mcp add-json deep-thinking --scope project < team-config.json
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

**用户级配置**（个人使用）：
```bash
claude mcp add-json deep-thinking --scope user < personal-config.json
```

#### JSON 配置格式规范

**必需字段**：
- `command` (string): 启动命令
- `args` (array): 命令参数数组

**可选字段**：
- `env` (object): 环境变量键值对
- `cwd` (string): 工作目录

**完整示例**：
```json
{
  "command": "python",
  "args": ["-m", "deep_thinking"],
  "cwd": "/path/to/project",
  "env": {
    "DEEP_THINKING_MAX_THOUGHTS": "50",
    "DEEP_THINKING_MIN_THOUGHTS": "3",
    "DEEP_THINKING_LOG_LEVEL": "INFO",
    "DEEP_THINKING_DATA_DIR": "./.deep-thinking-data"
  }
}
```

#### 限制和注意事项

**适用范围**：
- ✅ **STDIO 传输**: 完全支持，这是主要使用场景
- ❌ **SSE/HTTP 传输**: 不支持，请使用 `claude mcp add --transport sse/http`

**JSON 验证**：
- 命令会自动验证 JSON 格式
- 如果 JSON 格式错误，会显示详细的错误信息
- 缺少必需字段（`command` 或 `args`）会报错

**配置覆盖**：
- 如果服务器名称已存在，会提示覆盖确认
- 使用 `--force` 参数可以强制覆盖（如支持）

**环境变量扩展**：
- JSON 配置中的环境变量会按字面值处理
- 不支持 shell 风格的变量扩展（如 `${VAR}`）
- 如需动态环境变量，建议使用 `claude mcp add --env` 方式

**示例对比**：

```bash
# ❌ JSON 方式不支持环境变量扩展
claude mcp add-json deep-thinking '{"env":{"API_KEY":"${MY_API_KEY}"}}'
# 会被当作字面值 "${MY_API_KEY}"

# ✅ 使用 claude mcp add 方式支持环境变量扩展
claude mcp add --transport stdio deep-thinking \
  --env API_KEY=${MY_API_KEY} \
  -- python -m deep_thinking
```

#### 故障排除

**问题1：JSON 格式错误**
```bash
# 错误示例：缺少引号
claude mcp add-json deep-thinking '{command: "python"}'
# 错误信息：Invalid JSON format

# 正确示例
claude mcp add-json deep-thinking '{"command":"python"}'
```

**问题2：缺少必需字段**
```bash
# 错误示例：缺少 args 字段
claude mcp add-json deep-thinking '{"command":"python"}'
# 错误信息：Missing required field: args

# 正确示例
claude mcp add-json deep-thinking '{"command":"python","args":["-m","deep_thinking"]}'
```

**问题3：特殊字符转义**
```bash
# JSON 中的特殊字符需要正确转义
claude mcp add-json deep-thinking '{"command":"python","args":["-m","deep_thinking"],"env":{"PATH_WITH_SPACES":"/path/with spaces/to/bin"}}'

# 或使用 claude mcp add 命令（更简单）
claude mcp add --transport stdio deep-thinking \
  --env PATH_WITH_SPACES="/path/with spaces/to/bin" \
  -- python -m deep_thinking
```

---

### 管理命令

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

### 完整配置示例

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

### 环境变量扩展

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

### 故障排除

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
chmod +x /path/to/DeepThinking/src/deep_thinking/__main__.py

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

---

## 配置文件方式

除了命令行方式，您也可以手动编辑配置文件。Claude Code CLI 提供了灵活的配置方式，支持项目级和用户级配置。

### 配置文件位置

| 配置级别 | 文件路径 | 优先级 | 适用场景 |
|---------|---------|--------|----------|
| **项目级** | `.claude/config.json` | 高 | 项目特定的MCP服务器配置 |
| **用户级** | `~/.claude/config.json` | 低 | 全局默认配置 |

**优先级规则**：项目级配置会覆盖用户级配置的相同服务器名称。

### .claude/ 目录结构最佳实践

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

### 基础配置示例

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

**带描述字段的完整配置**：
```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": ["-m", "deep_thinking"],
      "description": "深度思考MCP服务器 - 高级思维编排引擎，适合处理多步骤、跨工具的复杂任务",
      "env": {
        "DEEP_THINKING_MAX_THOUGHTS": "50",
        "DEEP_THINKING_MIN_THOUGHTS": "3",
        "DEEP_THINKING_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

> 💡 **说明**：`description` 字段是可选的，用于在 Claude Code 中显示服务器的描述信息，帮助用户更好地理解每个 MCP 服务器的用途。

### 开发模式配置（本地源码）

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

### uv 加速配置

使用 uv 包管理器可以大幅提升启动速度：

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

### 环境变量配置

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

> ⚠️ **重要提示 - 环境变量路径扩展**：
>
> **关于 `DEEP_THINKING_DATA_DIR` 的特殊说明**：
>
> - ✅ **支持的路径格式**：
>   - 相对路径：`"./.deep-thinking-data"` 或 `".deep-thinking-data"`
>   - 绝对路径：`"/Users/yourname/.deep-thinking-data"` 或 `"/home/user/.deep-thinking-data"`
>   - **~ 路径**：`"~/.deep-thinking-data"` - 自动扩展为用户主目录
>   - **环境变量**：`"$HOME/.deep-thinking-data"` - 自动展开 $HOME 变量
>
> **使用示例**：
>
> 1. **使用 ~ 路径**（推荐）：
> ```json
> {
>   "env": {
>     "DEEP_THINKING_DATA_DIR": "~/.deep-thinking-data"
>   }
> }
> ```
>
> 2. **使用环境变量**：
> ```json
> {
>   "env": {
>     "DEEP_THINKING_DATA_DIR": "$HOME/.deep-thinking-data"
>   }
> }
> ```
>
> 3. **使用相对路径**：
> ```json
> {
>   "env": {
>     "DEEP_THINKING_DATA_DIR": "./.deep-thinking-data"
>   }
> }
> ```
>
> 4. **使用 claude mcp add 命令**（支持 shell 扩展）：
> ```bash
> claude mcp add --transport stdio deep-thinking \
>   --env DEEP_THINKING_DATA_DIR=~/.deep-thinking-data \
>   -- python -m deep_thinking
> ```

### 多项目配置管理

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

### 安装方式说明

在使用 DeepThinking MCP 之前，需要先安装它。支持以下安装方式：

#### 开发模式安装（推荐用于本地开发）

**使用 pip**：
```bash
# 克隆仓库
git clone https://github.com/GeerMrc/DeepThinking.git
cd DeepThinking

# 以开发模式安装
pip install -e .
```

**使用 uv**（更快）：
```bash
# 克隆仓库
git clone https://github.com/GeerMrc/DeepThinking.git
cd DeepThinking

# 以开发模式安装
uv pip install -e .
```

#### 生产模式安装（推荐用于部署）

**从 PyPI 安装**（已发布版本）：
```bash
# 使用 pip
pip install DeepThinking

# 使用 uv
uv pip install DeepThinking
```

**从 wheel 文件安装**：
```bash
# 下载 wheel 文件后
pip install dist/DeepThinking-0.2.2-py3-none-any.whl

# 或使用 uv
uv pip install dist/DeepThinking-0.2.2-py3-none-any.whl
```

#### 关于 uvx 的说明

> ⚠️ **重要提示**：`uvx` 命令仅在 PyPI 发布后可用。
>
> - ❌ **当前不可用**：`uvx DeepThinking`（尚未发布到 PyPI）
> - ✅ **替代方案**：使用开发模式安装
>   ```bash
>   # 开发模式安装后，可以直接使用
>   pip install -e .
>   python -m deep_thinking --help
>   ```

### 配置方式

安装完成后，使用以下方式配置 DeepThinking MCP：

**方式1：使用 claude mcp add 命令**（推荐）：
```bash
claude mcp add --transport stdio deep-thinking \
  --env DEEP_THINKING_MAX_THOUGHTS=50 \
  -- python -m deep_thinking
```

**方式2：使用 claude mcp add-json 命令**：
```bash
claude mcp add-json deep-thinking '{"command":"python","args":["-m","deep_thinking"]}'
```

### 验证和调试

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
| `ModuleNotFoundError: No module named 'deep_thinking'` | 运行 `pip install -e /path/to/DeepThinking` |
| `Permission denied` | 检查数据目录权限，或使用 `--data-dir` 指定其他位置 |
| `Command not found: uv` | 安装uv：`curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| 配置不生效 | 确认配置文件位置正确（项目级 vs 用户级） |
| 启动缓慢 | 使用uv加速，或检查网络连接 |

### 高级配置示例

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

## 相关资源

- [IDE 配置总览](./ide-config.md) - 其他 IDE（Claude Desktop、Cursor、Continue.dev）配置
- [SSE 配置指南](./sse-guide.md) - SSE 模式详细配置
- [安装指南](./installation.md) - 安装和部署说明
- [API 文档](./api.md) - MCP 工具 API 参考

---

## 许可证

MIT License
