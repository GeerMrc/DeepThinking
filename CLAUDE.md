# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

DeepThinking MCP 是一个高级深度思考 MCP (Model Context Protocol) 服务器，支持六种思考模式（常规、修订、分支、对比、逆向、假设），提供会话管理、任务跟踪、多格式导出和可视化功能。

## 开发环境

### 环境架构

```
┌─────────────────────────────────────────────────────────────┐
│                    开发环境架构                              │
├─────────────────────────────────────────────────────────────┤
│  终端默认: conda base (miniconda3) → Python 3.13.11        │
│  项目虚拟环境: .venv (由 uv 创建)                           │
│  包管理器: uv 0.10.2                                        │
│  LSP: pyright (已配置)                                      │
└─────────────────────────────────────────────────────────────┘
```

### 环境使用规范

| 场景 | 命令 | 说明 |
|------|------|------|
| **运行测试** | `pytest` | 使用 conda base 环境（已安装完整测试工具） |
| **安装依赖** | `uv pip install -e ".[dev]"` | 安装到 .venv |
| **同步到 conda** | `pip install -e ".[dev]"` | 安装到 conda base |
| **构建打包** | `uv build` | 使用 uv 环境 |

### 重要说明

1. **测试运行环境**: 直接使用 `pytest` 命令，它会在 conda base 环境中运行
2. **不要使用 `uv run pytest`**: .venv 中缺少 pytest-cov 等插件
3. **新增依赖后**: 需要同时安装到 conda base 环境以运行测试

### 初始化开发环境

```bash
# 1. 确保 conda base 环境有完整开发依赖
pip install -e ".[dev]"

# 2. 同步到 uv 虚拟环境（可选，用于构建）
uv pip install -e ".[dev]"

# 3. 验证环境
pytest --version  # 应显示 pytest 9.0.2+
python -c "import pytest_asyncio"  # 验证 pytest-asyncio
```

### 运行服务器

```bash
# STDIO模式（本地MCP）
python -m deep_thinking --transport stdio

# SSE模式（远程MCP）
python -m deep_thinking --transport sse --host 0.0.0.0 --port 8000
```

## 常用命令

### 测试

```bash
# 运行所有测试（使用 conda base 环境）
pytest

# 运行测试并生成覆盖率报告
pytest --cov=deep_thinking

# 运行特定测试文件
pytest tests/test_tools/test_sequential_thinking.py

# 运行特定标记的测试
pytest -m unit
pytest -m integration

# 运行核心测试（Phase 3.5/3.6 验证）
pytest tests/test_tools/test_phase_inference.py \
        tests/test_integration/test_sequential_thinking.py \
        tests/test_models/test_config.py -v
```

### 代码质量

```bash
# Ruff 代码检查
ruff check src/ tests/

# Ruff 格式化
ruff format src/ tests/

# Mypy 类型检查
mypy src/deep_thinking/
```

### 构建

```bash
# 构建 Wheel 包
uv build

# 或使用
python -m build
```

## 架构

### 模块结构

```
src/deep_thinking/
├── __main__.py         # CLI 入口
├── server.py           # FastMCP 服务器实例和生命周期管理
├── transports/         # 传输层实现
│   ├── stdio.py       # STDIO 传输 (本地模式)
│   └── sse.py         # SSE 传输 (远程模式)
├── tools/              # MCP 工具实现
│   ├── sequential_thinking.py  # 核心思考工具
│   ├── session_manager.py      # 会话管理
│   ├── task_manager.py         # 任务管理
│   ├── export.py               # 导出工具
│   ├── visualization.py        # 可视化
│   └── template.py             # 模板系统
├── models/             # Pydantic 数据模型
├── storage/            # 持久化层 (JSON 存储)
└── utils/              # 工具函数 (日志、格式化)
```

### 核心设计原则

1. **传输无关性**: 业务逻辑与传输层解耦，支持 STDIO 和 SSE 双模式
2. **装饰器注册模式**: 所有 MCP 工具必须使用 `@app.tool()` 装饰器
3. **类型安全**: 使用 Pydantic 进行数据验证
4. **原子写入**: 临时文件 + 重命名确保数据完整性

### 工具注册机制

工具通过导入 `server.py` 中的 `app` 实例自动注册：

```python
# 在 tools/your_tool.py 中
from deep_thinking.server import app, get_storage_manager

@app.tool()
def your_tool_function(param: str) -> str:
    """工具功能描述"""
    return "结果"
```

**注意**: 禁止使用 `register_xxx(app)` 函数模式，必须使用装饰器模式。

## 六种思考类型

| 类型 | 符号 | 必需参数 | 说明 |
|------|------|---------|------|
| regular | 💭 | thought | 常规顺序思考 |
| revision | 🔄 | thought, revisesThought | 修订之前的思考 |
| branch | 🌿 | thought, branchFromThought, branchId | 创建思考分支 |
| comparison | ⚖️ | thought, comparisonItems | 对比多个选项 |
| reverse | 🔙 | thought, reverseTarget | 从结论反推前提 |
| hypothetical | 🤔 | thought, hypotheticalCondition | 探索假设影响 |

## 数据存储

- **默认目录**: `~/.deepthinking/`
- **环境变量覆盖**: `DEEP_THINKING_DATA_DIR`
- **存储内容**: 会话数据 (sessions/)、索引 (.index.json)、备份 (.backups/)

## 环境变量配置

关键配置项（详见 `.env.example`）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEEP_THINKING_TRANSPORT` | stdio | 传输模式 |
| `DEEP_THINKING_DATA_DIR` | ~/.deepthinking | 数据存储目录 |
| `DEEP_THINKING_MAX_THOUGHTS` | 50 | 最大思考步骤数 |
| `DEEP_THINKING_MIN_THOUGHTS` | 3 | 最小思考步骤数 |
| `DEEP_THINKING_LOG_LEVEL` | INFO | 日志级别 |
| `DEEP_THINKING_AUTH_TOKEN` | - | SSE 认证 Token |
| `DEEP_THINKING_MAX_TOOL_CALLS` | 100 | 最大工具调用总数 |
| `DEEP_THINKING_MAX_TOOL_CALLS_PER_THOUGHT` | 10 | 每步骤最大工具调用数 |
| `DEEP_THINKING_THOUGHTS_INCREMENT` | 10 | 思考步骤增量（needsMoreThoughts功能） |

## LSP 配置 (Pyright)

项目使用 pyright 作为类型检查 LSP，配置通过 `pyproject.toml` 中的 `[tool.mypy]` 部分。

### 类型检查兼容性

- mypy 和 pyright 共用相同配置
- Python 版本: 3.10+
- 严格模式启用

### 常见类型问题解决

```python
# 使用 TYPE_CHECKING 避免循环导入
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deep_thinking.models.thought import Thought

# 使用类型别名提高可读性
ToolCallsList = list[dict[str, Any]] | None
```

## 开发规范

### 新增工具模块检查清单

1. 使用 `@app.tool()` 装饰器
2. 添加完整类型注解和 docstring
3. 实现 `__all__` 导出列表
4. 添加单元测试和集成测试
5. 更新 `docs/api.md` 文档

### 提交前检查

```bash
ruff check src/
ruff format src/
mypy src/
pytest tests/ -v
```

### 提交信息规范

```
type(scope): description

# 类型: feat/fix/docs/refactor/test/chore
# 示例: feat(thinking): 添加假设思考模式
```

## 禁止事项

- 禁止批量化操作（必须逐一验证）
- 禁止跳过测试直接提交
- 禁止伪造测试结果
- 禁止在 STDIO 模式使用 print() 输出（必须用 stderr）
- 禁止使用 `uv run pytest`（缺少 pytest-cov 插件）

## 常见问题

### 测试运行报错: `unrecognized arguments: --cov`

**原因**: 使用了 `uv run pytest`，但 .venv 中没有 pytest-cov
**解决**: 直接使用 `pytest` 命令（使用 conda base 环境）

### 测试报错: `async def functions are not natively supported`

**原因**: pytest-asyncio 未安装
**解决**: `pip install pytest-asyncio`

### 警告: `Unknown config option: asyncio_mode`

**原因**: pytest-asyncio 版本不兼容
**解决**: 升级到 pytest-asyncio>=1.0.0 或移除 pyproject.toml 中的 asyncio_mode 配置

### 类型检查失败

**原因**: pyright/mypy 配置不一致
**解决**: 确保 `pyproject.toml` 中 `[tool.mypy]` 配置正确

## 相关文档

- `ARCHITECTURE.md` - 详细架构设计
- `docs/api.md` - 完整 API 参考
- `docs/DEVELOPMENT_STANDARDS.md` - 开发规范
- `docs/configuration.md` - 配置参数参考
