# DeepThinking-MCP

> 高级深度思考MCP服务器 - 使用Python构建的功能完整、架构清晰的MCP服务器

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
DEEP_THINKING_TRANSPORT=stdio
DEEP_THINKING_HOST=localhost
DEEP_THINKING_PORT=8000
DEEP_THINKING_LOG_LEVEL=INFO
DEEP_THINKING_AUTH_TOKEN=your-secret-token
DEEP_THINKING_API_KEY=your-api-key
```

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
└── docs/                     # 文档目录
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 作者

Maric
