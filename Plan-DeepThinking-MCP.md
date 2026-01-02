# Python DeepThinking MCP 开发计划

> 项目名称: DeepThinking MCP
> 开发语言: Python 3.10+
> MCP框架: FastMCP
> 传输协议: STDIO + SSE (Streamable HTTP)
> 功能范围: 完整型（所有功能）
> Agent模式: 单一MCP服务器+工具
> 持久化方案: 纯JSON文件

---

## 一、项目概述

### 1.1 目标
使用Python重构现有Thinking MCP工具，实现功能完整、架构清晰、可扩展的深度思考MCP服务器。

### 1.2 核心功能

| 功能模块 | 说明 | 优先级 |
|---------|------|--------|
| 顺序思考 | 保留现有所有功能（常规/修订/分支） | P0 |
| 会话管理 | 创建/查询/删除思考会话 | P0 |
| 状态持久化 | JSON文件存储，支持恢复 | P0 |
| 多格式导出 | JSON/Markdown/HTML/Text | P1 |
| 可视化 | Mermaid流程图生成 | P1 |
| 模板系统 | 预设思考框架 | P2 |

### 1.3 技术栈

```
Python: 3.10+
MCP框架: FastMCP (mcp[cli])
传输层: STDIO (本地) + SSE/HTTP (远程)
HTTP框架: aiohttp (SSE服务器)
日志: logging模块（传输感知配置）
数据验证: Pydantic
异步: asyncio
测试: pytest + pytest-asyncio
```

### 1.4 传输协议说明

**STDIO传输**（本地模式）：
- 使用标准输入/输出流进行进程间通信
- 适用于Claude Desktop本地集成
- 日志必须输出到stderr（严禁使用print）
- 最佳性能，无网络开销

**SSE传输**（远程模式）：
- 使用HTTP POST + Server-Sent Events
- 适用于远程服务器部署
- 支持标准HTTP认证（Bearer Token、API Key）
- 可通过网络从任何位置访问

---

## 二、项目架构

### 2.1 目录结构

```
Deep-Thinking-MCP/
├── pyproject.toml                # 项目配置
├── README.md                     # 项目说明
├── .env.example                  # 环境变量示例
│
├── src/deep_thinking/
│   ├── __init__.py
│   ├── __main__.py               # CLI入口，支持传输模式选择
│   ├── server.py                 # FastMCP服务器实例（统一）
│   │
│   ├── transports/               # 传输层实现（新增）
│   │   ├── __init__.py
│   │   ├── stdio.py             # STDIO传输配置
│   │   └── sse.py               # SSE传输配置（aiohttp）
│   │
│   ├── tools/                    # MCP工具实现
│   │   ├── __init__.py
│   │   ├── sequential_thinking.py    # 核心思考工具
│   │   ├── session_manager.py        # 会话管理工具
│   │   ├── export.py                 # 导出工具
│   │   └── visualization.py          # 可视化工具
│   │
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   ├── thinking_session.py      # 会话模型
│   │   ├── thought.py               # 思考步骤模型
│   │   └── template.py              # 模板模型
│   │
│   ├── storage/                  # 持久化层
│   │   ├── __init__.py
│   │   ├── storage_manager.py       # 存储管理器
│   │   └── json_file_store.py       # JSON文件存储
│   │
│   ├── templates/                # 预设模板
│   │   ├── __init__.py
│   │   ├── problem_solving.py       # 问题求解模板
│   │   └── decision_making.py        # 决策模板
│   │
│   └── utils/                    # 工具函数
│       ├── __init__.py
│       ├── validators.py            # 参数验证
│       ├── formatters.py            # 格式化工具
│       └── logger.py                # 传输感知的日志配置
│
├── tests/                        # 测试目录
│   ├── conftest.py
│   ├── test_tools/
│   ├── test_models/
│   ├── test_storage/
│   └── test_transports/           # 传输层测试（新增）
│
└── docs/                         # 文档目录
    ├── api.md
    ├── architecture.md
    └── user_guide.md
```

### 2.2 数据存储结构

```
~/.Deep-Thinking-MCP/
├── sessions/
│   ├── {session_id}.json       # 单个会话文件
│   └── .index.json            # 会话索引
├── templates/
│   └── {template_id}.json
├── exports/
└── backups/
    └── sessions/
```

---

## 三、开发阶段

### 阶段1: 基础框架搭建

**任务清单**:
- [ ] 创建项目目录结构
- [ ] 配置pyproject.toml（依赖、入口点）
- [ ] 设置开发环境（虚拟环境、依赖安装）
- [ ] 实现传输层模块（transports/stdio.py, transports/sse.py）
- [ ] 实现双模式CLI入口（__main__.py）
- [ ] 实现传输感知的日志配置（utils/logger.py）
- [ ] 实现参数验证工具（utils/validators.py）
- [ ] 编写基础测试框架（tests/conftest.py）

**关键文件**:
- `src/deep_thinking/__main__.py` - CLI入口，支持--transport参数
- `src/deep_thinking/transports/stdio.py` - STDIO传输实现
- `src/deep_thinking/transports/sse.py` - SSE传输实现（aiohttp）
- `src/deep_thinking/utils/logger.py` - 传输感知的日志配置
- `src/deep_thinking/utils/validators.py` - Pydantic模型验证
- `pyproject.toml` - 项目依赖和配置

**完成标准**:
- STDIO模式：日志正确输出到stderr，严禁使用print()
- SSE模式：HTTP端点可访问，SSE连接正常
- 基础测试可运行
- 依赖安装无错误

**CLI使用示例**:
```bash
# STDIO模式（本地）
python -m deep_thinking --transport stdio

# SSE模式（远程）
python -m deep_thinking --transport sse --port 8000 --host 0.0.0.0
```

---

### 阶段2: 数据模型实现

**任务清单**:
- [ ] 实现思考步骤模型（models/thought.py）
- [ ] 实现思考会话模型（models/thinking_session.py）
- [ ] 实现模板模型（models/template.py）
- [ ] 编写模型单元测试

**关键文件**:
- `src/deep_thinking/models/thought.py`
```python
class Thought(BaseModel):
    thought_number: int
    content: str
    type: Literal["regular", "revision", "branch"]
    is_revision: bool = False
    revises_thought: int | None = None
    branch_from_thought: int | None = None
    branch_id: str | None = None
    timestamp: datetime
```

- `src/deep_thinking/models/thinking_session.py`
```python
class ThinkingSession(BaseModel):
    session_id: str
    name: str
    description: str = ""
    created_at: datetime
    updated_at: datetime
    status: Literal["active", "completed", "archived"]
    thoughts: list[Thought] = []
    metadata: dict = {}
```

**完成标准**:
- 所有模型通过Pydantic验证
- 单元测试覆盖率>80%
- 序列化/反序列化正确

---

### 阶段3: 持久化层实现

**任务清单**:
- [ ] 实现JSON文件存储（storage/json_file_store.py）
- [ ] 实现存储管理器（storage/storage_manager.py）
- [ ] 实现原子写入机制
- [ ] 实现自动备份功能
- [ ] 编写存储层单元测试

**关键文件**:
- `src/deep_thinking/storage/json_file_store.py`
  - 原子写入：临时文件+重命名
  - 并发控制：文件锁
  - 自动备份：每次修改前备份

- `src/deep_thinking/storage/storage_manager.py`
  - 会话CRUD操作
  - 索引管理
  - 备份恢复

**完成标准**:
- 原子写入测试通过
- 并发安全测试通过
- 备份恢复功能验证

---

### 阶段4: 核心工具实现

**任务清单**:
- [ ] 实现FastMCP服务器（server.py）
- [ ] 实现顺序思考工具（tools/sequential_thinking.py）
- [ ] 实现会话管理工具（tools/session_manager.py）
- [ ] 编写工具集成测试

**关键文件**:

**server.py** - MCP服务器入口
```python
from mcp.server import FastMCP
from contextlib import asynccontextmanager

@asynccontextmanager
async def server_lifespan():
    # 初始化存储管理器
    yield
    # 清理资源

app = FastMCP("deep-thinking", lifespan=server_lifespan)

@app.tool()
async def sequential_thinking(
    thought: str,
    nextThoughtNeeded: bool,
    thoughtNumber: int,
    totalThoughts: int,
    session_id: str = "default",
    isRevision: bool = False,
    revisesThought: int | None = None,
    branchFromThought: int | None = None,
    branchId: str | None = None,
) -> str:
    """执行顺序思考步骤"""
    # 实现核心逻辑
```

**sequential_thinking.py** - 核心思考工具
- 保留所有现有参数
- 支持session_id关联
- 自动保存状态
- 三种思考类型（常规/修订/分支）

**完成标准**:
- MCP Inspector测试通过（STDIO模式）
- HTTP端点可访问，SSE连接正常（SSE模式）
- 两种模式功能完全一致
- 状态正确持久化
- 日志在两种模式下都正确输出

---

### 阶段5: 增强功能实现

**任务清单**:
- [ ] 实现导出工具（tools/export.py）
- [ ] 实现可视化工具（tools/visualization.py）
- [ ] 实现模板系统（templates/）
- [ ] 编写功能测试

**关键文件**:

**export.py** - 多格式导出
```python
@app.tool()
async def export_session(
    session_id: str,
    format: Literal["json", "markdown", "html", "text"],
    output_path: str | None = None
) -> str:
    """导出会话为指定格式"""
```

**visualization.py** - 可视化
```python
@app.tool()
async def visualize_session(
    session_id: str,
    format: Literal["mermaid", "ascii"]
) -> str:
    """生成思考流程图"""
```

**完成标准**:
- 支持JSON/Markdown/HTML/Text导出
- 生成Mermaid流程图
- 至少3个预设模板
- 两种传输模式下功能完全一致

---

### 阶段6: 质量保证

**任务清单**:
- [ ] 完整测试套件执行
- [ ] 代码质量检查（ruff、mypy）
- [ ] 性能测试（1000+思考步骤）
- [ ] 压力测试（并发会话）
- [ ] 安全审计（输入验证、文件路径）

**完成标准**:
- 单元测试覆盖率>80%
- 集成测试全部通过
- 无已知安全漏洞
- 性能符合要求

---

### 阶段7: 文档与发布

**任务清单**:
- [ ] 编写API文档（docs/api.md）
- [ ] 编写架构文档（docs/architecture.md）
- [ ] 编写用户指南（docs/user_guide.md）
- [ ] 准备PyPI发布
- [ ] 创建Claude Desktop配置示例

**完成标准**:
- 文档完整且准确
- 配置示例可直接使用
- PyPI包可正常安装

---

## 四、规范开发流程

### 4.1 标准开发流程（必须严格遵守）

```
需求分析 → 技术调研 → 方案设计 → 任务拆解 →
代码实现 → 单元测试 → 自我验证 →
代码审查 → 集成测试 → 性能测试 → 安全检查 →
预发布验证 → 文档更新 → Git提交
```

### 4.2 每次开发推进前的必申明内容

**1. 重申规范开发流程**（每次开始前必须声明）
- 明确当前所处阶段
- 明确当前阶段的进入条件
- 明确当前阶段的完成标准
- 明确下一阶段的准入要求

**2. 回顾前一阶段任务完成情况**
- 检查TASKS.md中前一阶段所有任务状态
- 确认所有任务都已标记为completed
- 确认所有测试都已通过
- 确认所有代码审查已完成

**3. 明确当前开发任务**
- 基于TASKS.md读取当前阶段任务列表
- 创建当前阶段的TODO清单
- 明确任务优先级和依赖关系

**4. 有序规范推进**
- 严格按照TODO清单顺序执行
- 每完成一个任务立即更新TASKS.md
- 每完成一个任务进行自我验证

**5. 当前阶段完成后**
- 对TODO所有开发内容进行代码审核
- 进行代码测试验证
- 进行交叉验证确认真实有效
- 审核TASKS.md更新所有任务进展
- 正确的git commit当前项目代码
- 回复用户当前阶段开发任务已完成

### 4.3 禁止行为（严格遵守）

**禁止随意创建文档**
- 只创建3个核心文档：PYTHON-DeepThinking MCP-开发计划.md、TASKS.md、ARCHITECTURE.md
- 其他文档创建必须经过审批
- 文档创建前检查是否已有相关文档

**禁止随意进度开发推进**
- 必须通过当前阶段所有检查点
- 未通过检查不得进入下一阶段
- 检查结果记录到TASKS.md

**禁止无申明的无序开发**
- 每次开发前必须申明规范流程
- 每次开发前必须回顾前一阶段
- 每次开发前必须明确当前任务

**禁止虚假开发/虚假审核/虚假测试**
- 代码必须真实实现功能
- 测试必须真实验证功能
- 审核必须真实检查代码质量
- 交叉验证机制确保真实性

**禁止批量化操作**
- 除非有完整回滚方案
- 除非经过充分测试
- 除非获得明确授权

### 4.4 阶段门控机制

**每个阶段结束前的强制检查**：

| 检查项 | 检查方式 | 通过标准 | 记录位置 |
|--------|---------|---------|---------|
| 代码质量 | ruff check + mypy | 无错误无警告 | TASKS.md |
| 单元测试 | pytest --cov | 覆盖率>80% | TASKS.md |
| 集成测试 | pytest tests/test_integration/ | 全部通过 | TASKS.md |
| STDIO传输测试 | MCP Inspector | 工具可调用，日志在stderr | TASKS.md |
| SSE传输测试 | curl/HTTP客户端 | 端点可访问，SSE连接 | TASKS.md |
| 功能验证 | 手动测试MCP工具 | 所有工具可用 | TASKS.md |
| 文档同步 | 检查代码与文档 | 一致性确认 | TASKS.md |
| Git状态 | git status | 正确分支+无未提交 | TASKS.md |

**未通过检查的处理**：
1. 记录问题到TASKS.md
2. 修复问题
3. 重新检查
4. 重复直到通过

### 4.5 交叉验证机制

**验证1：代码真实性验证**
- 检查代码是否真实实现功能
- 检查是否有占位符或TODO
- 检查是否有虚假实现

**验证2：测试真实性验证**
- 检查测试是否真实验证功能
- 检查是否有跳过测试的代码
- 检查测试覆盖率是否真实

**验证3：功能完整性验证**
- 对照需求逐一验证功能
- 检查所有功能点是否实现
- 检查边界条件是否处理

**验证4：文档一致性验证**
- 检查代码与文档是否一致
- 检查API文档是否准确
- 检查用户指南是否完整

### 4.6 代码规范

**日志规范（传输感知配置）**

```python
# utils/logger.py - 传输感知的日志配置
import logging
import sys

def setup_logging(transport_mode: str = "stdio"):
    """
    配置传输感知的日志系统

    Args:
        transport_mode: "stdio" 或 "sse"
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 清除现有handlers
    logger.handlers.clear()

    if transport_mode == "stdio":
        # STDIO模式：强制输出到stderr（严禁使用print）
        handler = logging.StreamHandler(sys.stderr)
        logger.info("Initialized in STDIO mode - logs to stderr")
    else:
        # SSE模式：可以使用stdout或文件
        handler = logging.StreamHandler(sys.stdout)
        logger.info("Initialized in SSE mode - logs to stdout")

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

# 使用示例
import logging

logger = logging.getLogger(__name__)

async def process_thought(thought: str, transport_mode: str = "stdio") -> None:
    """处理思考 - 支持双传输模式"""
    if transport_mode == "stdio":
        # STDIO模式：严禁使用print()
        # print(f"Processing: {thought}")  # 禁止！会破坏JSON-RPC
        logger.info(f"Processing thought: {thought[:50]}...")
    else:
        # SSE模式：同样推荐使用logging
        logger.info(f"Processing thought: {thought[:50]}...")

    # 处理逻辑...
```

**类型注解规范**
```python
from typing import Literal
from pydantic import BaseModel

class Thought(BaseModel):
    thought_number: int
    content: str
    type: Literal["regular", "revision", "branch"]
```

### 4.7 测试规范

```python
# tests/test_models/test_thought.py
import pytest
from deep_thinking.models.thought import Thought

def test_thought_creation():
    """测试思考对象创建"""
    thought = Thought(
        thought_number=1,
        content="测试思考",
        type="regular"
    )
    assert thought.thought_number == 1
    assert thought.type == "regular"

def test_thought_serialization():
    """测试序列化"""
    thought = Thought(thought_number=1, content="测试", type="regular")
    data = thought.model_dump_json()
    assert isinstance(data, str)

@pytest.mark.asyncio
async def test_thought_async_validation():
    """测试异步验证"""
    # 异步测试示例
    pass
```

### 4.8 Git提交规范

```
feat(tools): 添加会话管理工具
- 实现create_session工具
- 实现list_sessions工具
- 实现get_session工具
- 测试覆盖率85%

fix(storage): 修复并发写入问题
- 添加文件锁机制
- 实现原子写入
- 修复测试用例

docs(readme): 更新安装说明
- 添加虚拟环境创建步骤
- 更新依赖版本

test(models): 添加思考模型测试
- 测试创建、序列化、验证
- 覆盖率提升到90%
```

### 4.9 分支管理规范

```
main          - 生产环境代码（不接受直接提交）
develop       - 开发环境集成代码
feature/阶段1 - 基础框架搭建
feature/阶段2 - 数据模型实现
feature/阶段3 - 持久化层实现
feature/阶段4 - 核心工具实现
feature/阶段5 - 增强功能实现
feature/阶段6 - 质量保证
feature/阶段7 - 文档与发布
```

---

## 五、项目文档组织

### 5.1 三大核心文档职责分离

**PYTHON-DeepThinking MCP-开发计划.md**（本文件）
- 项目概述和目标
- 开发阶段划分
- 规范开发流程
- 禁止行为声明
- 完成标准定义

**TASKS.md**（项目级唯一任务追踪文档）
- 所有任务的详细分解
- 任务状态实时追踪（pending/in_progress/completed）
- 任务依赖关系
- 完成标准和验证方式
- 检查结果记录

**ARCHITECTURE.md**（架构设计文档）
- 详细架构设计说明
- 模块间的交互关系
- 数据流图
- 接口定义
- 技术选型理由

### 5.2 文档创建规范

**创建前检查清单**：
- [ ] 搜索现有文档，确认不存在相关内容
- [ ] 确定文档类型（计划/任务/架构）
- [ ] 选择正确的文档文件
- [ ] 确认内容属于该文档的职责范围

**禁止行为**：
- 禁止随意创建新的md文档
- 禁止在多个文档中重复相同内容
- 禁止将任务分解放在开发计划中（应在TASKS.md）
- 禁止将架构细节放在开发计划中（应在ARCHITECTURE.md）

---

## 六、关键文件清单

### 需要创建的核心文件

| 文件 | 行数估算 | 优先级 |
|------|---------|--------|
| src/deep_thinking/__main__.py | ~80 | P0 |
| src/deep_thinking/transports/stdio.py | ~50 | P0 |
| src/deep_thinking/transports/sse.py | ~100 | P0 |
| src/deep_thinking/server.py | ~150 | P0 |
| src/deep_thinking/tools/sequential_thinking.py | ~300 | P0 |
| src/deep_thinking/storage/storage_manager.py | ~400 | P0 |
| src/deep_thinking/models/thinking_session.py | ~200 | P0 |
| src/deep_thinking/utils/logger.py | ~80 | P0 |
| src/deep_thinking/tools/export.py | ~200 | P1 |
| src/deep_thinking/tools/visualization.py | ~150 | P1 |

### 参考文件

| 文件 | 用途 |
|------|------|
| autonomous-coding/agent.py | 会话生命周期管理 |
| autonomous-coding/progress.py | 进度追踪模式 |
| autonomous-coding/security.py | 安全验证模式 |
| MCP-架构概述.md | MCP传输层架构理解 |
| MCP-连接到本地.md | STDIO传输配置 |
| MCP-连接到远端.md | SSE传输配置 |

### Claude Desktop 配置示例

**STDIO模式配置**（本地）：
```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/Deep-Thinking-MCP",
        "run", "python", "-m", "deep_thinking",
        "--transport", "stdio"
      ]
    }
  }
}
```

**SSE模式配置**（远程）：
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

**环境变量配置**：
```bash
# .env
DEEP_THINKING_TRANSPORT=stdio
# 或
DEEP_THINKING_TRANSPORT=sse
DEEP_THINKING_PORT=8000
DEEP_THINKING_HOST=0.0.0.0
```

---

## 七、风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| STDIO传输调试困难 | 使用单元测试+日志 |
| JSON解析异常 | 多层异常处理 |
| 并发写入冲突 | 文件锁+原子写入 |
| 测试覆盖不足 | 强制覆盖率要求 |

---

## 八、最终可交付性验证

### 8.1 功能完整性验证

**现有Thinking MCP功能对照**：
| 功能 | 状态 | 验证方式 |
|------|------|---------|
| sequential_thinking工具 | ✓ 规划中 | MCP Inspector测试 |
| 常规思考(💭) | ✓ 规划中 | 单元测试 |
| 修订思考(🔄) | ✓ 规划中 | 单元测试 |
| 分支思考(🌿) | ✓ 规划中 | 单元测试 |
| 思考历史追踪 | ✓ 规划中 | 集成测试 |
| 动态调整总数 | ✓ 规划中 | 功能测试 |

**功能增强对照**：
| 功能 | 状态 | 验证方式 |
|------|------|---------|
| 状态持久化 | ✓ 规划中 | 重启测试 |
| 多格式导出 | ✓ 规划中 | 导出测试 |
| 可视化 | ✓ 规划中 | 生成测试 |
| 模板系统 | ✓ 规划中 | 应用测试 |

### 8.2 可交付物清单

**代码交付物**：
- [ ] 完整的源代码（src/deep_thinking/）
- [ ] 单元测试套件（tests/）
- [ ] 集成测试套件（tests/test_integration/）
- [ ] 测试覆盖率报告（>80%）

**文档交付物**：
- [ ] README.md（项目说明）
- [ ] docs/api.md（API文档）
- [ ] docs/architecture.md（架构文档）
- [ ] docs/user_guide.md（用户指南）
- [ ] PYTHON-DeepThinking MCP-开发计划.md（本文件）
- [ ] TASKS.md（任务追踪）
- [ ] ARCHITECTURE.md（架构设计）

**配置交付物**：
- [ ] pyproject.toml（项目配置）
- [ ] .env.example（环境变量示例）
- [ ] Claude Desktop配置示例

### 8.3 质量标准验证

| 质量维度 | 标准 | 验证方式 |
|---------|------|---------|
| 代码质量 | 无警告 | ruff check + mypy |
| 测试覆盖 | >80% | pytest --cov |
| 功能完整 | 100% | 需求对照 |
| 文档完整 | 100% | 文档检查清单 |
| 性能 | 符合要求 | 性能测试 |
| 安全 | 无已知漏洞 | 安全审计 |

---

## 九、下一步

确认计划后，开始**阶段1: 基础框架搭建**：
1. 创建项目目录结构
2. 配置pyproject.toml
3. 实现日志配置模块
4. 设置测试框架
