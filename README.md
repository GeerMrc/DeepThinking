# DeepThinking MCP

> 高级深度思考MCP服务器 - 使用Python构建的功能完整、架构清晰的MCP服务器

[![PyPI version](https://badge.fury.io/py/DeepThinking.svg)](https://badge.fury.io/py/DeepThinking)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📖 文档

### 快速导航

- **[文档索引](docs/README.md)** - 📚 完整的文档导航和快速开始指南
- **[配置参数参考](docs/configuration.md)** - ⚙️ 所有环境变量的完整参考

### 安装与配置

- **[安装指南](docs/installation.md)** - 安装步骤和配置指南
- **[IDE 配置示例](docs/ide-config.md)** - Claude Desktop/Cursor/Continue.dev 等配置
- **[Claude Code 配置指南](docs/claude-code-config.md)** - Claude Code CLI 完整配置
- **[SSE 配置指南](docs/sse-guide.md)** - SSE远程模式详细配置

### 使用指南

- **[用户指南](docs/user_guide.md)** - 详细的使用说明和示例
- **[API 文档](docs/api.md)** - 完整的MCP工具API参考

### 技术文档

- **[架构设计](ARCHITECTURE.md)** - 系统架构和技术设计
- **[数据迁移指南](docs/MIGRATION.md)** - 数据迁移和备份说明

## 项目概述

DeepThinking MCP是一个功能完整的MCP（Model Context Protocol）服务器，提供顺序思考工具，支持六种思考模式：常规思考、修订思考、分支思考、对比思考、逆向思考和假设思考。

### 核心特性

- **双传输模式**：支持STDIO（本地）和SSE（远程）两种传输协议
- **六种思考模式**：
  - 💭 **常规思考**：正常顺序思考步骤
  - 🔄 **修订思考**：修订之前的思考内容
  - 🌿 **分支思考**：从某点分出新思考分支
  - ⚖️ **对比思考**：比较多个选项或方案的优劣
  - 🔙 **逆向思考**：从结论反推前提条件
  - 🤔 **假设思考**：探索假设条件下的影响
- **会话管理**：创建/查询/删除思考会话
- **状态持久化**：JSON文件存储，支持恢复
- **多格式导出**：JSON/Markdown/HTML/Text
- **可视化**：Mermaid流程图生成
- **模板系统**：预设思考框架

## 安装

### 使用 uv 安装（推荐）⚡

[uv](https://github.com/astral-sh/uv) 是一个极速的 Python 包管理器。

```bash
# 安装 uv (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 DeepThinking
uv pip install DeepThinking
```

#### 重新安装（强制重装）

```bash
# 强制重新安装
uv pip install --force-reinstall DeepThinking
```

#### 升级到最新版本

```bash
# 从 PyPI 升级
uv pip install --upgrade DeepThinking

# 从 wheel 文件升级
uv pip install --force-reinstall dist/deepthinking-0.2.3-py3-none-any.whl
```

### 使用 pip 安装

```bash
pip install DeepThinking
```

### 从源码安装

**开发模式（推荐开发使用）**：
```bash
# 克隆仓库
git clone https://github.com/GeerMrc/DeepThinking.git
cd DeepThinking

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 以开发模式安装
pip install -e .
```

**生产模式（推荐部署使用）**：
```bash
# 克隆仓库
git clone https://github.com/GeerMrc/DeepThinking.git
cd DeepThinking

# 构建 Wheel 文件
uv build  # 或 python -m build

# 安装 Wheel 文件（不显示源代码路径）
uv pip install deepthinking-0.2.3-py3-none-any.whl
```

> 📘 **详细安装指南**: 请参阅 [安装与配置文档](docs/installation.md) 获取完整的安装说明，包括开发模式和生产模式Wheel安装的详细对比。

## 使用

### STDIO模式（本地）

```bash
python -m deep_thinking --transport stdio
```

### SSE模式（远程）

```bash
# 无认证
python -m deep_thinking --transport sse --host 0.0.0.0 --port 8000

# 带Bearer Token认证
python -m deep_thinking --transport sse --auth-token your-secret-token

# 带API Key认证
python -m deep_thinking --transport sse --api-key your-api-key
```

### 环境变量配置

```bash
# .env
# 服务器配置
# 自定义服务器描述（可选）
# 用于在MCP工具列表中显示自定义的服务器功能说明
# 默认描述："深度思考MCP服务器 - 高级思维编排引擎，提供顺序思考,适合处理多步骤、跨工具的复杂任务,会话管理和状态持久化功能"
# 如果不设置，将使用上述默认值
DEEP_THINKING_DESCRIPTION=我的AI助手服务器

# 传输配置
DEEP_THINKING_TRANSPORT=stdio
DEEP_THINKING_HOST=localhost
DEEP_THINKING_PORT=8000

# 认证配置（SSE模式）
DEEP_THINKING_AUTH_TOKEN=your-secret-token
DEEP_THINKING_API_KEY=your-api-key

# 存储配置
DEEP_THINKING_DATA_DIR=~/.deepthinking

# 思考配置
DEEP_THINKING_MAX_THOUGHTS=50           # 最大思考步骤数（推荐 50，支持 1-10000）
DEEP_THINKING_MIN_THOUGHTS=3            # 最小思考步骤数（推荐 3，支持 1-10000）
DEEP_THINKING_THOUGHTS_INCREMENT=10     # 思考步骤增量（默认 10，支持 1-100）

# 日志配置
DEEP_THINKING_LOG_LEVEL=INFO
```

**数据存储**: 默认存储在用户主目录 `~/.deepthinking/`，包含会话数据和索引文件。详见[数据迁移指南](docs/MIGRATION.md)。

## Claude Desktop配置

### STDIO模式配置

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/DeepThinking",
        "run", "python", "-m", "deep_thinking",
        "--transport", "stdio"
      ]
    }
  }
}
```

### SSE模式配置

```json
{
  "mcpServers": {
    "deep-thinking-remote": {
      "url": "http://localhost:8000/sse",
      "headers": {
        "Authorization": "Bearer your-token-here"
      }
    }
  }
}
```

## Claude Code 配置

Claude Code CLI 提供了多种配置方式，支持快速配置和 JSON 导入。

### 快速配置（使用 `claude mcp add`）

**STDIO 模式**（本地）：
```bash
# 基础配置
claude mcp add --transport stdio deep-thinking -- python -m deep_thinking

# 带环境变量
claude mcp add --transport stdio deep-thinking \
  --env DEEP_THINKING_MAX_THOUGHTS=50 \
  --env DEEP_THINKING_LOG_LEVEL=DEBUG \
  -- python -m deep_thinking
```

### JSON 配置导入（使用 `claude mcp add-json`）

**从 JSON 配置导入**：
```bash
claude mcp add-json deep-thinking <<'EOF'
{
  "command": "python",
  "args": ["-m", "deep_thinking"],
  "env": {
    "DEEP_THINKING_MAX_THOUGHTS": "50",
    "DEEP_THINKING_MIN_THOUGHTS": "3"
  }
}
EOF
```

**从文件导入**：
```bash
claude mcp add-json deep-thinking < config.json
```

### 配置范围说明

Claude Code 支持三种配置范围，决定了配置的存储位置和共享范围：

| 范围 | 存储位置 | 适用场景 | 命令示例 |
|------|---------|---------|---------|
| **local** | 项目用户设置 | 个人开发、实验配置 | `--scope local`（默认） |
| **project** | `.mcp.json` | 团队共享、项目特定 | `--scope project` |
| **user** | 全局配置 | 跨项目使用 | `--scope user` |

**项目级配置示例**（团队共享）：
```bash
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

> 📘 **详细配置指南**: 请参阅 [Claude Code 配置指南](docs/claude-code-config.md) 获取完整的配置说明，包括 CLI 命令、JSON 导入、配置范围和故障排除。

---

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=deep_thinking

# 运行特定测试
pytest tests/test_tools/test_sequential_thinking.py
```

### 代码质量检查

```bash
# Ruff代码检查
ruff check src/ tests/

# Ruff格式化
ruff format src/ tests/

# Mypy类型检查
mypy src/deep_thinking/
```

## 字段限制说明

为确保系统稳定性和性能，各思考类型字段有相应的长度和数量限制：

### 思考内容字段

| 字段 | 类型 | 限制 | 说明 |
|------|------|------|------|
| `content` | str | 1-10000字符 | 主思考内容字段 |
| `branch_id` | str | 1-50字符 | 分支标识符 |

### 对比思考字段

| 字段 | 类型 | 限制 | 说明 |
|------|------|------|------|
| `comparison_items` | list[str] | 最少2个，每项1-500字符 | 比较项应为简短描述 |
| `comparison_dimensions` | list[str] | 最多10个，每项1-50字符 | 比较维度列表 |
| `comparison_result` | str | 1-10000字符 | 比较结论，支持详细分析 |

### 逆向思考字段

| 字段 | 类型 | 限制 | 说明 |
|------|------|------|------|
| `reverse_target` | str | 1-2000字符 | 反推目标描述 |
| `reverse_steps` | list[str] | 最多20个，每项1-500字符 | 反推步骤，每步简洁描述 |

### 假设思考字段

| 字段 | 类型 | 限制 | 说明 |
|------|------|------|------|
| `hypothetical_condition` | str | 1-2000字符 | 假设条件描述 |
| `hypothetical_impact` | str | 1-10000字符 | 影响分析，支持详细描述 |
| `hypothetical_probability` | str | 1-50字符 | 可能性评估 |

### 会话和模板字段

| 字段 | 类型 | 限制 | 说明 |
|------|------|------|------|
| `name` | str | 1-100字符 | 会话/模板名称 |
| `description` | str | 0-2000字符 | 会话/模板描述 |

### 思考配置

| 配置项 | 默认值 | 范围 | 说明 |
|--------|--------|------|------|
| `max_thoughts` | 50 | 1-10000 | 最大思考步骤数 |
| `min_thoughts` | 3 | 1-10000 | 最小思考步骤数 |
| `thoughts_increment` | 10 | 1-100 | 每次增加的步骤数 |

> 💡 **设计说明**: 限制值基于实际使用场景设定，平衡了灵活性和系统性能。如需调整限制，请确保充分测试。

## 项目结构

```
DeepThinking/
├── src/deep_thinking/
│   ├── __main__.py           # CLI入口
│   ├── transports/            # 传输层实现
│   │   ├── stdio.py          # STDIO传输
│   │   └── sse.py            # SSE传输
│   ├── tools/                # MCP工具实现
│   ├── models/               # 数据模型
│   ├── storage/              # 持久化层
│   └── utils/                # 工具函数
├── tests/                    # 测试目录
├── docs/                     # 文档目录
│   ├── api.md                # API文档
│   ├── user_guide.md         # 用户指南
│   └── installation.md       # 安装指南
├── examples/                 # 配置示例
│   └── *.json                # Claude Desktop配置示例
├── ARCHITECTURE.md           # 架构文档
├── README.md                 # 项目说明
└── LICENSE                   # MIT许可证
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 作者

Maric
