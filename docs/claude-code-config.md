# Claude Code 配置完整指南

> 版本: 1.0.0
> 更新日期: 2026-01-08
> 适用对象: Claude Code (VSCode) 用户

---

## 概述

Claude Code 是 Anthropic 官方的 VSCode 扩展，支持通过 MCP 协议集成 DeepThinking。

**快速开始**：
```bash
claude mcp add deepthinking stdio python -m deep_thinking
```

---

## 配置方式

### 方式1：CLI 命令（推荐）

使用 `claude mcp` 命令快速配置：

```bash
# STDIO 模式
claude mcp add deepthinking stdio python -m deep_thinking

# 带环境变量
claude mcp add deepthinking stdio python -m deep_thinking \
  --env DEEP_THINKING_LOG_LEVEL=DEBUG

# SSE 模式
claude mcp add deepthinking-remote sse python -m deep_thinking --transport sse
```

### 方式2：JSON 配置命令（add-json）

使用 `claude mcp add-json` 命令直接通过 JSON 配置添加 MCP 服务器。

**STDIO 模式（本地）- 完整参数配置**：
```bash
claude mcp add-json "deepthinking" '{
  "command": "python",
  "args": ["-m", "deep_thinking"],
  "env": {
    "DEEP_THINKING_LOG_LEVEL": "INFO",
    "DEEP_THINKING_DATA_DIR": "~/.deepthinking",
    "DEEP_THINKING_MAX_THOUGHTS": "50",
    "DEEP_THINKING_MIN_THOUGHTS": "3",
    "DEEP_THINKING_THOUGHTS_INCREMENT": "10",
    "DEEP_THINKING_BACKUP_COUNT": "10",
    "DEEP_THINKING_DESCRIPTION": "深度思考MCP服务器",
    "DEEP_THINKING_DEV": "false",
    "DEEP_THINKING_PROFILE": "false"
  }
}' --scope user
```

**SSE 模式（远程）- 完整参数配置**：
```bash
claude mcp add-json "deepthinking-remote" '{
  "command": "python",
  "args": ["-m", "deep_thinking", "--transport", "sse"],
  "env": {
    "DEEP_THINKING_LOG_LEVEL": "INFO",
    "DEEP_THINKING_DATA_DIR": "~/.deepthinking",
    "DEEP_THINKING_MAX_THOUGHTS": "50",
    "DEEP_THINKING_MIN_THOUGHTS": "3",
    "DEEP_THINKING_THOUGHTS_INCREMENT": "10",
    "DEEP_THINKING_BACKUP_COUNT": "10",
    "DEEP_THINKING_DESCRIPTION": "深度思考MCP服务器",
    "DEEP_THINKING_HOST": "localhost",
    "DEEP_THINKING_PORT": "8000",
    "DEEP_THINKING_AUTH_TOKEN": "your-secret-token"
  }
}' --scope user
```

**配置范围说明**：
- `--scope user`：全局配置，所有项目共享（推荐）
- `--scope project`：项目级配置，写入 `.mcp.json`
- `--scope local`：本地配置，默认选项

**参数分类说明**：

| 参数 | STDIO | SSE | 说明 |
|------|-------|-----|------|
| `DEEP_THINKING_LOG_LEVEL` | ✓ | ✓ | 日志级别 |
| `DEEP_THINKING_DATA_DIR` | ✓ | ✓ | 数据存储目录 |
| `DEEP_THINKING_MAX_THOUGHTS` | ✓ | ✓ | 最大思考步骤数 |
| `DEEP_THINKING_MIN_THOUGHTS` | ✓ | ✓ | 最小思考步骤数 |
| `DEEP_THINKING_THOUGHTS_INCREMENT` | ✓ | ✓ | 思考步骤增量 |
| `DEEP_THINKING_BACKUP_COUNT` | ✓ | ✓ | 自动备份保留数量 |
| `DEEP_THINKING_DESCRIPTION` | ✓ | ✓ | 自定义服务器描述 |
| `DEEP_THINKING_DEV` | ✓ | ✓ | 开发模式 |
| `DEEP_THINKING_PROFILE` | ✓ | ✓ | 性能分析 |
| `DEEP_THINKING_HOST` | - | ✓ | SSE服务器监听地址 |
| `DEEP_THINKING_PORT` | - | ✓ | SSE服务器监听端口 |
| `DEEP_THINKING_AUTH_TOKEN` | - | ✓ | Bearer Token认证 |
| `DEEP_THINKING_API_KEY` | - | ✓ | API Key认证 |

### 方式3：配置文件

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

---

## CLI 命令参考

### 基础命令语法

```bash
# 添加 MCP 服务器（STDIO）
claude mcp add <name> stdio <command> [args...]

# 添加 MCP 服务器（SSE）
claude mcp add <name> sse <command> [args...] --transport sse

# JSON 配置方式添加
claude mcp add-json <name> <json-config> [--scope {local|project|user}]

# 从文件导入 JSON 配置
claude mcp add-json <name> -f <config-file> [-s {local|project|user}]

# 列出所有服务器
claude mcp list

# 删除服务器
claude mcp remove <name>

# 查看帮助
claude mcp --help
```

### 使用虚拟环境

```bash
# 指定虚拟环境的 Python
claude mcp add deepthinking stdio /path/to/.venv/bin/python -m deep_thinking

# 或使用 uv
claude mcp add deepthinking stdio uv run python -m deep_thinking
```

---

## 配置文件详解

### 配置文件位置

- **macOS/Linux**: `~/.claude/settings.json`
- **Windows**: `%APPDATA%\claude\settings.json`

### 完整配置示例

```json
{
  "mcpServers": {
    "deepthinking": {
      "command": "python",
      "args": ["-m", "deep_thinking"],
      "env": {
        "DEEP_THINKING_LOG_LEVEL": "INFO",
        "DEEP_THINKING_DATA_DIR": "~/.deepthinking",
        "DEEP_THINKING_MAX_THOUGHTS": "50"
      }
    },
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

---

## 环境变量配置

### 常用环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEEP_THINKING_LOG_LEVEL` | INFO | 日志级别 |
| `DEEP_THINKING_DATA_DIR` | ~/.deepthinking/ | 数据目录 |
| `DEEP_THINKING_MAX_THOUGHTS` | 50 | 最大思考步骤 |
| `DEEP_THINKING_MIN_THOUGHTS` | 3 | 最小思考步骤 |

详细的环境变量配置请参考：[配置参数参考](./configuration.md)

---

## 常用配置场景

### 场景1：本地开发

```bash
claude mcp add deepthinking stdio python -m deep_thinking \
  --env DEEP_THINKING_LOG_LEVEL=DEBUG \
  --env DEEP_THINKING_MAX_THOUGHTS=100
```

### 场景2：生产环境

```bash
claude mcp add deepthinking stdio python -m deep_thinking \
  --env DEEP_THINKING_LOG_LEVEL=INFO \
  --env DEEP_THINKING_DATA_DIR=/opt/deepthinking
```

### 场景3：远程服务器

```bash
claude mcp add deepthinking-remote sse python -m deep_thinking --transport sse \
  --env DEEP_THINKING_HOST=server.example.com \
  --env DEEP_THINKING_PORT=8000 \
  --env DEEP_THINKING_AUTH_TOKEN=your-secret-token
```

### 场景4：使用虚拟环境

```bash
claude mcp add deepthinking stdio /path/to/.venv/bin/python -m deep_thinking
```

### 场景5：开发模式

```bash
# 在项目目录中以开发模式运行
cd /path/to/Deep-Thinking-MCP
claude mcp add deepthinking stdio python -m deep_thinking \
  --env DEEP_THINKING_DEV=true
```

---

## 验证配置

### 检查连接

```bash
# 列出所有 MCP 服务器
claude mcp list

# 应该看到 deepthinking 在列表中
```

### 测试工具

在 Claude Code 中：

1. 打开命令面板 (`Cmd/Ctrl + Shift + P`)
2. 输入 "MCP"
3. 选择 "DeepThinking" 相关工具
4. 验证工具可用

---

## 故障排除

### 常见问题

**问题：服务器未找到**
```bash
# 检查配置
claude mcp list

# 重新添加
claude mcp remove deepthinking
claude mcp add deepthinking stdio python -m deep_thinking
```

**问题：模块导入失败**
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

## 开发模式配置

### 编辑模式配置

对于开发 DeepThinking 本身：

```bash
# 以开发模式安装
cd /path/to/Deep-Thinking-MCP
pip install -e .

# 配置 Claude Code
claude mcp add deepthinking stdio python -m deep_thinking \
  --env DEEP_THINKING_LOG_LEVEL=DEBUG \
  --env DEEP_THINKING_DEV=true
```

### 热重载

代码修改后自动重载（需要 DEEP_THINKING_DEV=true）：

```bash
claude mcp add deepthinking stdio python -m deep_thinking \
  --env DEEP_THINKING_DEV=true
```

---

## 完整配置快速参考

### 所有支持的环境变量

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| **传输配置** |
| `DEEP_THINKING_TRANSPORT` | stdio | 传输模式（stdio/sse） |
| `DEEP_THINKING_HOST` | localhost | SSE服务器监听地址 |
| `DEEP_THINKING_PORT` | 8000 | SSE服务器监听端口 |
| **认证配置** |
| `DEEP_THINKING_AUTH_TOKEN` | 无 | Bearer Token认证 |
| `DEEP_THINKING_API_KEY` | 无 | API Key认证 |
| **服务器配置** |
| `DEEP_THINKING_DESCRIPTION` | 深度思考MCP服务器 - 高级思维编排引擎，提供顺序思考,适合处理多步骤、跨工具的复杂任务,会话管理和状态持久化功能 | 自定义服务器描述 |
| **日志配置** |
| `DEEP_THINKING_LOG_LEVEL` | INFO | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| **存储配置** |
| `DEEP_THINKING_DATA_DIR` | ~/.deep-thinking/ | 数据存储目录 |
| `DEEP_THINKING_BACKUP_COUNT` | 10 | 自动备份保留数量 |
| **思考配置** |
| `DEEP_THINKING_MAX_THOUGHTS` | 50 | 最大思考步骤数（1-10000） |
| `DEEP_THINKING_MIN_THOUGHTS` | 3 | 最小思考步骤数（1-10000） |
| `DEEP_THINKING_THOUGHTS_INCREMENT` | 10 | 思考步骤增量（1-100） |
| **开发选项** |
| `DEEP_THINKING_DEV` | false | 启用开发模式（暂未实现） |
| `DEEP_THINKING_PROFILE` | false | 启用性能分析（暂未实现） |

> 💡 **提示**：完整的配置说明请参考 [配置参数参考](./configuration.md)

---

## 相关文档

- [配置参数参考](./configuration.md) - 完整的环境变量配置
- [安装指南](./installation.md) - 安装和验证
- [SSE 配置指南](./sse-guide.md) - SSE 远程模式详细配置
- [IDE 集成配置](./ide-config.md) - 其他 IDE 配置示例
- [用户指南](./user_guide.md) - 使用指南和最佳实践
