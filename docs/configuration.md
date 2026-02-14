# 配置参数参考

> 本文档由 `scripts/generate_config_docs.py` 自动生成，请勿手动编辑。

本文档提供所有环境变量的完整参考，确保配置参数与代码实现100%一致。

## 📋 目录

- [环境变量完整参考](#环境变量完整参考)
  - [传输模式配置](#传输模式配置)
  - [SSE模式配置](#sse模式配置)
  - [日志配置](#日志配置)
  - [存储配置](#存储配置)
  - [思考配置](#思考配置)
  - [服务器配置](#服务器配置)
  - [开发选项](#开发选项)
- [配置文件位置](#配置文件位置)
- [传输模式配置](#传输模式配置-1)
- [高级配置](#高级配置)

## 环境变量完整参考

### 传输模式配置

| 环境变量 | 默认值 | 描述 |
|---------|--------|------|
| `DEEP_THINKING_TRANSPORT` | stdio | 从代码自动提取 |

### 日志配置

| 环境变量 | 默认值 | 描述 |
|---------|--------|------|
| `DEEP_THINKING_LOG_LEVEL` | INFO | 从代码自动提取 |

### 存储配置

| 环境变量 | 默认值 | 描述 |
|---------|--------|------|
| `DEEP_THINKING_DATA_DIR` | 未设置 | 从代码自动提取 |

### 思考配置

| 环境变量 | 默认值 | 描述 |
|---------|--------|------|
| `DEEP_THINKING_MAX_THOUGHTS` | 50 | 从代码自动提取 |
| `DEEP_THINKING_MIN_THOUGHTS` | 3 | 从代码自动提取 |
| `DEEP_THINKING_THOUGHTS_INCREMENT` | 10 | 从代码自动提取 |
| `DEEP_THINKING_MAX_TOOL_CALLS` | 100 | 从代码自动提取 |
| `DEEP_THINKING_MAX_TOOL_CALLS_PER_THOUGHT` | 10 | 从代码自动提取 |

### 服务器配置

| 环境变量 | 默认值 | 描述 |
|---------|--------|------|
| `DEEP_THINKING_HOST` | localhost | 从代码自动提取 |
| `DEEP_THINKING_AUTH_TOKEN` | 未设置 | 从代码自动提取 |
| `DEEP_THINKING_API_KEY` | 未设置 | 从代码自动提取 |
| `DEEP_THINKING_PORT` | 8000 | 从代码自动提取 |
| `DEEP_THINKING_DESCRIPTION` | 未设置 | 从代码自动提取 |

## 配置文件位置

### 默认存储路径

数据存储目录：`~/.deepthinking/`

目录结构：
```
~/.deepthinking/
├── sessions/              # 会话数据目录
│   ├── .index.json       # 会话索引文件
│   └── *.json            # 各个会话的数据文件
├── .backups/             # 自动备份目录
│   └── sessions/         # 会话备份
├── .gitignore            # 防止数据提交到版本控制
└── tasks.json            # 任务列表存储
```

### 环境变量配置方式

**方式1：使用 .env 文件**（推荐）

在项目根目录创建 `.env` 文件：
```bash
# 复制示例配置
cp .env.example .env

# 编辑配置
nano .env
```

**方式2：使用系统环境变量**

在 `~/.bashrc` 或 `~/.zshrc` 中添加：
```bash
export DEEP_THINKING_DATA_DIR=/custom/path
export DEEP_THINKING_LOG_LEVEL=DEBUG
```

**方式3：使用 CLI 参数**

```bash
python -m deep_thinking --data-dir /custom/path --log-level DEBUG
```

### 配置优先级

``CLI 参数 > 环境变量 > 默认值```

## 传输模式配置

### STDIO 模式（本地）

适用于本地开发场景，通过标准输入输出进行通信。

**配置示例**：

在 `.env` 文件中：
```bash
DEEP_THINKING_TRANSPORT=stdio
```

### SSE 模式（远程）

适用于远程服务器部署，通过 HTTP Server-Sent Events 进行通信。

**配置示例**：

在 `.env` 文件中：
```bash
DEEP_THINKING_TRANSPORT=sse
DEEP_THINKING_HOST=localhost
DEEP_THINKING_PORT=8000
```

**认证配置**（可选）：

```bash
# Bearer Token 认证
DEEP_THINKING_AUTH_TOKEN=your-secret-token-here

# API Key 认证
DEEP_THINKING_API_KEY=your-api-key-here
```

详细的 SSE 配置指南请参考：[SSE 配置指南](./sse-guide.md)

## 高级配置

### 思考参数配置

DeepThinking MCP 支持配置思考步骤的限制范围，防止无限循环：

| 参数 | 默认值 | 范围 | 推荐值 | 说明 |
|------|--------|------|--------|------|
| `DEEP_THINKING_MAX_THOUGHTS` | 50 | 1-10000 | 50 | 最大思考步骤数 |
| `DEEP_THINKING_MIN_THOUGHTS` | 3 | 1-10000 | 3 | 最小思考步骤数 |
| `DEEP_THINKING_THOUGHTS_INCREMENT` | 10 | 1-100 | 10 | 思考步骤增量 |

**配置建议**：

- **简单任务**：使用默认值即可
- **复杂任务**：适当增加 `MAX_THOUGHTS` 到 100-200
- **防止失控**：设置合理的 `MAX_THOUGHTS` 上限
- **增量思考**：使用 `THOUGHTS_INCREMENT` 控制思考步骤的增量

### 日志配置

日志级别控制输出的详细程度：

| 级别 | 输出内容 | 使用场景 |
|------|---------|----------|
| `DEBUG` | 所有调试信息 | 开发调试 |
| `INFO` | 一般信息（默认） | 正常运行 |
| `WARNING` | 警告信息 | 生产环境 |
| `ERROR` | 仅错误信息 | 生产环境 |

**配置示例**：

```bash
# 开发环境
DEEP_THINKING_LOG_LEVEL=DEBUG

# 生产环境
DEEP_THINKING_LOG_LEVEL=INFO
```

### 存储配置

自定义数据存储目录：

```bash
# 使用绝对路径
DEEP_THINKING_DATA_DIR=/opt/deepthinking

# 使用相对路径
DEEP_THINKING_DATA_DIR=./data

# 使用 ~ 路径（自动扩展）
DEEP_THINKING_DATA_DIR=~/custom-deepthinking

# 使用环境变量
DEEP_THINKING_DATA_DIR=$HOME/data
```

**路径扩展支持**：

- `~` 自动扩展为用户主目录
- `$HOME` 等环境变量自动扩展
- 相对路径相对于当前工作目录

### 服务器描述配置

自定义 MCP 服务器的描述（在 MCP 工具列表中显示）：

```bash
DEEP_THINKING_DESCRIPTION="我的 AI 助手服务器"
```

**说明**：
- 如果不设置，使用默认描述
- 默认值：`深度思考MCP服务器 - 高级思维编排引擎，提供顺序思考,适合处理多步骤、跨工具的复杂任务,会话管理和状态持久化功能`

### 开发选项

**启用开发模式**（暂未实现）：

```bash
DEEP_THINKING_DEV=true
```

**启用性能分析**（暂未实现）：

```bash
DEEP_THINKING_PROFILE=true
```

---

## 相关文档

- [安装指南](./installation.md) - 快速安装和配置
- [IDE 集成配置](./ide-config.md) - 各种 IDE 的配置示例
- [用户指南](./user_guide.md) - 使用指南和最佳实践
- [API 参考](./api.md) - 完整的 API 文档

---

> **提示**：本文档由 `scripts/generate_config_docs.py` 自动生成，
> 如需更新配置参数，请修改源代码中的 docstring 或 `.env.example` 文件，
> 然后重新运行脚本生成文档。
