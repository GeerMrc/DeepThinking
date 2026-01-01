# DeepThinking-MCP

> 高级深度思考MCP服务器 - 使用Python构建的功能完整、架构清晰的MCP服务器

[![PyPI version](https://badge.fury.io/py/deep-thinking-mcp.svg)](https://badge.fury.io/py/deep-thinking-mcp)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📖 文档

- **[API 文档](docs/api.md)** - 完整的MCP工具API参考
- **[用户指南](docs/user_guide.md)** - 详细的使用说明和示例
- **[安装与配置](docs/installation.md)** - 安装步骤和配置指南
- **[架构设计](ARCHITECTURE.md)** - 系统架构和技术设计

## 项目概述

DeepThinking-MCP是一个功能完整的MCP（Model Context Protocol）服务器，提供顺序思考工具，支持常规思考、修订思考和分支思考三种模式。

### 核心特性

- **双传输模式**：支持STDIO（本地）和SSE（远程）两种传输协议
- **顺序思考**：保留所有现有功能（常规/修订/分支）
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

# 安装 DeepThinking-MCP
uv pip install deep-thinking-mcp
```

### 使用 pip 安装

```bash
pip install deep-thinking-mcp
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/deep-thinking-mcp.git
cd deep-thinking-mcp

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .
```

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
# 传输配置
DEEP_THINKING_TRANSPORT=stdio
DEEP_THINKING_HOST=localhost
DEEP_THINKING_PORT=8000

# 认证配置（SSE模式）
DEEP_THINKING_AUTH_TOKEN=your-secret-token
DEEP_THINKING_API_KEY=your-api-key

# 存储配置
DEEP_THINKING_DATA_DIR=./.deep-thinking-mcp

# 思考配置
DEEP_THINKING_MAX_THOUGHTS=50           # 最大思考步骤数（推荐 50，支持 1-10000）
DEEP_THINKING_MIN_THOUGHTS=3            # 最小思考步骤数（推荐 3，支持 1-10000）
DEEP_THINKING_THOUGHTS_INCREMENT=10     # 思考步骤增量（默认 10，支持 1-100）

# 日志配置
DEEP_THINKING_LOG_LEVEL=INFO
```

**数据存储**: 默认存储在项目本地目录 `.deep-thinking-mcp/`，包含会话数据和索引文件。详见[数据迁移指南](docs/MIGRATION.md)。

## Claude Desktop配置

### STDIO模式配置

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/deep-thinking-mcp",
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

## 项目结构

```
deep-thinking-mcp/
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
