# DeepThinking MCP 架构设计文档

> 项目: DeepThinking MCP
> 版本: 1.0.0
> 更新时间: 2026-01-01

---

## 一、架构概述

### 1.1 设计目标

1. **传输无关性**: 业务逻辑与传输层解耦，支持STDIO和SSE双模式
2. **可扩展性**: 模块化设计，便于添加新工具和功能
3. **类型安全**: 使用Pydantic进行数据验证
4. **持久化可靠**: 原子写入+自动备份机制
5. **可测试性**: 依赖注入+接口抽象

### 1.2 技术架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Claude / AI 应用                             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │   JSON-RPC 2.0 协议   │
                    └───────────┬───────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌────────────────┐     ┌───────────────┐
│  STDIO 传输   │     │   SSE 传输     │     │  (未来扩展)   │
│ (本地模式)    │     │   (远程模式)   │     │               │
└───────┬───────┘     └────────┬───────┘                 │
        │                      │                         │
        └──────────────────────┼─────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   FastMCP Server     │
                    │   (server.py)        │
                    └──────────┬───────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐     ┌────────────────┐     ┌───────────────┐
│   工具层      │     │   模型层       │     │  持久化层     │
│  (tools/)     │     │  (models/)     │     │ (storage/)    │
│               │     │                │     │               │
│ - 思考工具    │◄────┤ - 会话模型     │────►│ - JSON存储    │
│ - 会话管理    │     │ - 思考模型     │     │ - 存储管理器  │
│ - 导出工具    │     │ - 模板模型     │     │ - 任务清单存储│
│ - 任务管理    │     │ - 任务模型     │     │ - 原子写入    │
│ - 可视化      │     │                │     │ - 自动备份    │
└───────────────┘     └────────────────┘     └───────────────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    工具层 (utils/)    │
                    │                      │
                    │ - 日志配置(传输感知) │
                    │ - 参数验证          │
                    │ - 格式化工具        │
                    └──────────────────────┘
```

---

## 二、模块架构详解

### 2.1 传输层架构 (transports/)

#### 设计原则
- **传输无关**: 业务逻辑不关心使用何种传输方式
- **统一接口**: 两种传输方式对外提供相同的功能
- **日志分离**: STDIO模式日志必须输出到stderr，SSE模式可输出到stdout

#### 模块结构

```
transports/
├── __init__.py
├── stdio.py          # STDIO传输实现
└── sse.py            # SSE传输实现
```

#### STDIO传输 (stdio.py)

**职责**: 使用标准输入/输出流进行进程间通信

**关键实现**:
```python
def run_stdio(app: FastMCP) -> None:
    """
    使用STDIO传输运行MCP服务器

    适用于Claude Desktop本地集成
    """
    # 直接使用FastMCP的run方法，默认使用stdio
    app.run()
```

**特性**:
- 使用stdin接收JSON-RPC请求
- 使用stdout发送JSON-RPC响应
- 日志必须输出到stderr（严禁使用print）
- 最佳性能，无网络开销

#### SSE传输 (sse.py)

**职责**: 使用HTTP Server-Sent Events进行远程通信

**关键实现**:
```python
from aiohttp import web
import asyncio

async def run_sse(
    app: FastMCP,
    host: str = "localhost",
    port: int = 8000,
    auth_token: str | None = None
) -> None:
    """
    使用SSE传输运行MCP服务器

    适用于远程服务器部署
    支持Bearer Token认证
    """
    # 创建aiohttp应用
    web_app = web.Application()

    # 添加认证中间件（如果配置了auth_token）
    if auth_token:
        setup_auth(web_app, auth_token)

    # 添加SSE端点
    web_app.router.add_post('/sse', sse_handler(app))

    # 启动HTTP服务器
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    # 保持运行
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()
```

**特性**:
- HTTP POST + Server-Sent Events
- 支持Bearer Token认证
- 支持API Key认证
- 可通过网络从任何位置访问

### 2.2 工具层架构 (tools/)

#### 设计原则
- **单一职责**: 每个工具只负责一个特定功能
- **接口统一**: 所有工具都通过FastMCP的@app.tool()装饰器注册
- **异步优先**: 所有工具都是异步函数

#### 模块结构

```
tools/
├── __init__.py
├── sequential_thinking.py    # 核心思考工具
├── session_manager.py        # 会话管理工具
├── task_manager.py           # 任务管理工具
├── export.py                 # 导出工具
└── visualization.py          # 可视化工具
```

#### 顺序思考工具 (sequential_thinking.py)

**职责**: 实现核心的顺序思考功能

**工具定义**:
```python
from mcp.server import FastMCP

app = FastMCP("deep-thinking")

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
    needsMoreThoughts: bool = False,
) -> str:
    """
    执行顺序思考步骤

    支持三种思考类型:
    - 常规思考 (regular): 正常的顺序思考
    - 修订思考 (revision): 修订之前的思考
    - 分支思考 (branch): 从某个思考点分出新分支
    """
```

**状态管理**:
- 每次思考自动关联到session_id指定的会话
- 思考步骤自动保存到持久化层
- 支持动态调整totalThoughts（通过needsMoreThoughts）

**动态思考步骤调整**:
- `needsMoreThoughts=true`: 每次增加10步，上限1000步
- 自动记录调整历史到会话元数据
- 防止无限循环的保护机制
- 支持断点续传恢复调整状态

**思考类型处理**:

| 类型 | isRevision | branchFromThought | branchId | 行为 |
|------|-----------|-------------------|----------|------|
| regular | false | null | null | 常规思考 |
| revision | true | thought编号 | null | 修订指定思考 |
| branch | false | thought编号 | 唯一标识 | 创建新分支 |

#### 会话管理工具 (session_manager.py)

**职责**: 管理思考会话的创建、查询、更新、删除

**工具列表**:
```python
@app.tool()
async def create_session(
    name: str,
    description: str = "",
    metadata: dict = {}
) -> str:
    """创建新的思考会话"""

@app.tool()
async def get_session(session_id: str) -> str:
    """获取指定会话的详细信息"""

@app.tool()
async def list_sessions(
    status: str | None = None,
    limit: int = 50
) -> str:
    """列出会话"""

@app.tool()
async def delete_session(session_id: str) -> str:
    """删除指定会话"""

@app.tool()
async def update_session_status(
    session_id: str,
    status: Literal["active", "completed", "archived"]
) -> str:
    """更新会话状态"""
```

#### 会话恢复工具

**职责**: 恢复已暂停的思考会话（断点续传功能）

**工具定义**:
```python
@app.tool()
def resume_session(session_id: str) -> str:
    """
    恢复已暂停的思考会话（断点续传）

    获取会话的最后一个思考步骤，返回可以继续思考的上下文信息。
    """
```

**核心功能**:
- 获取会话的最后一个思考步骤
- 显示思考进度和状态
- 提供继续思考的参数指导
- 支持查看思考步骤调整历史

#### 任务管理工具 (task_manager.py)

**职责**: 提供任务清单管理功能，支持优先级驱动的任务执行

**工具列表**:
```python
@app.tool(name="create_task")
def create_task(
    title: str,
    description: str = "",
    priority: str = "P2",
    task_id: str | None = None,
) -> str:
    """创建新任务"""

@app.tool(name="list_tasks")
def list_tasks(
    status: str | None = None,
    priority: str | None = None,
    limit: int = 100,
) -> str:
    """列出任务，支持按状态和优先级过滤"""

@app.tool(name="update_task_status")
def update_task_status(
    task_id: str,
    new_status: str,
) -> str:
    """更新任务状态"""

@app.tool(name="get_next_task")
def get_next_task() -> str:
    """获取下一个待执行任务（按优先级排序）"""

@app.tool(name="get_task_stats")
def get_task_stats() -> str:
    """获取任务统计信息"""

@app.tool(name="link_task_session")
def link_task_session(
    task_id: str,
    session_id: str,
) -> str:
    """关联任务与思考会话"""
```

**优先级机制**:
- P0: 最高优先级，立即处理
- P1: 高优先级，尽快处理
- P2: 普通优先级，按计划处理

**状态管理**:
- pending: 待执行
- in_progress: 进行中
- completed: 已完成
- failed: 失败
- blocked: 已阻塞

#### 导出工具 (export.py)

**职责**: 将思考会话导出为各种格式

**工具定义**:
```python
@app.tool()
async def export_session(
    session_id: str,
    format: Literal["json", "markdown", "html", "text"],
    output_path: str | None = None
) -> str:
    """
    导出会话为指定格式

    支持格式:
    - json: 完整的JSON数据
    - markdown: Markdown文档
    - html: HTML网页
    - text: 纯文本
    """
```

**格式映射**:

| 格式 | 输出特点 |
|------|---------|
| JSON | 完整数据，可重新导入 |
| Markdown | 易读，支持代码高亮 |
| HTML | 可在浏览器中查看 |
| Text | 纯文本，兼容性最好 |

#### 可视化工具 (visualization.py)

**职责**: 生成思考流程的可视化图表

**工具定义**:
```python
@app.tool()
async def visualize_session(
    session_id: str,
    format: Literal["mermaid", "ascii"]
) -> str:
    """
    生成思考流程图

    支持格式:
    - mermaid: Mermaid流程图语法
    - ascii: ASCII字符流程图
    """
```

**可视化处理**:

| 思考类型 | Mermaid表示 | ASCII表示 |
|---------|------------|-----------|
| regular | 标准节点 | [1] |
| revision | 虚线箭头 | [1] ←→ [1'] |
| branch | 分支路径 | [1] ↦ [branch-1] |

### 2.3 模型层架构 (models/)

#### 设计原则
- **类型安全**: 使用Pydantic BaseModel进行数据验证
- **序列化友好**: 支持model_dump_json()直接序列化
- **不可变性**: 创建后不应修改（使用frozen=True）

#### 模块结构

```
models/
├── __init__.py
├── thought.py               # 思考步骤模型
├── thinking_session.py      # 思考会话模型
├── task.py                  # 任务模型
└── template.py              # 模板模型
```

#### 思考步骤模型 (thought.py)

```python
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

# 定义思考类型的联合类型
ThoughtType = Literal["regular", "revision", "branch", "comparison", "reverse", "hypothetical"]

class Thought(BaseModel):
    """单个思考步骤"""
    thought_number: int = Field(..., description="思考步骤编号")
    content: str = Field(..., description="思考内容")
    type: ThoughtType = Field(
        default="regular",
        description="思考类型"
    )
    is_revision: bool = Field(default=False, description="是否为修订")
    revises_thought: int | None = Field(
        default=None,
        description="修订的思考步骤编号"
    )
    branch_from_thought: int | None = Field(
        default=None,
        description="分支起始思考步骤编号"
    )
    branch_id: str | None = Field(
        default=None,
        description="分支标识符"
    )

    # Comparison类型专属字段
    comparison_items: list[str] | None = Field(
        default=None,
        description="对比思考的比较项列表，至少2个"
    )
    comparison_dimensions: list[str] | None = Field(
        default=None,
        description="对比思考的比较维度列表，最多10个"
    )
    comparison_result: str | None = Field(
        default=None,
        description="对比思考的比较结论，最多10000字符"
    )

    # Reverse类型专属字段
    reverse_from: int | None = Field(
        default=None,
        description="逆向思考的反推起点思考编号"
    )
    reverse_target: str | None = Field(
        default=None,
        description="逆向思考的反推目标描述，最多2000字符"
    )
    reverse_steps: list[str] | None = Field(
        default=None,
        description="逆向思考的反推步骤列表，最多20个"
    )

    # Hypothetical类型专属字段
    hypothetical_condition: str | None = Field(
        default=None,
        description="假设思考的假设条件描述，最多2000字符"
    )
    hypothetical_impact: str | None = Field(
        default=None,
        description="假设思考的影响分析，最多10000字符"
    )
    hypothetical_probability: str | None = Field(
        default=None,
        description="假设思考的可能性评估"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间"
    )

    class Config:
        frozen = True  # 不可变
```

**思考类型说明**：

| 类型 | 说明 | 显示符号 | 必需字段 |
|------|------|---------|---------|
| regular | 常规思考 | 💭 | content |
| revision | 修订思考 | 🔄 | content, revises_thought |
| branch | 分支思考 | 🌿 | content, branch_from_thought, branch_id |
| comparison | 对比思考 | ⚖️ | content, comparison_items |
| reverse | 逆向思考 | 🔙 | content, reverse_target |
| hypothetical | 假设思考 | 🤔 | content, hypothetical_condition |

#### 思考会话模型 (thinking_session.py)

```python
class ThinkingSession(BaseModel):
    """思考会话"""
    session_id: str = Field(..., description="会话唯一标识")
    name: str = Field(..., description="会话名称")
    description: str = Field(default="", description="会话描述")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="最后更新时间"
    )
    status: Literal["active", "completed", "archived"] = Field(
        default="active",
        description="会话状态"
    )
    thoughts: list[Thought] = Field(
        default_factory=list,
        description="思考步骤列表"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="元数据"
    )

    class Config:
        frozen = True
```

#### 任务模型 (task.py)

```python
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class TaskPriority(str, Enum):
    """任务优先级枚举"""
    P0 = "P0"  # 最高优先级
    P1 = "P1"  # 高优先级
    P2 = "P2"  # 普通优先级

class ThinkingTask(BaseModel):
    """任务清单模型"""
    task_id: str = Field(..., description="任务唯一标识")
    title: str = Field(..., description="任务标题")
    description: str = Field(default="", description="任务描述")
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="任务状态"
    )
    priority: TaskPriority = Field(
        default=TaskPriority.P2,
        description="任务优先级"
    )
    linked_session_id: str | None = Field(
        default=None,
        description="关联的思考会话ID"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="更新时间"
    )

    class Config:
        frozen = True

    def update_status(self, new_status: TaskStatus) -> None:
        """更新任务状态"""
        object.__setattr__(self, 'status', new_status)
        object.__setattr__(self, 'updated_at', datetime.utcnow())

    def link_session(self, session_id: str) -> None:
        """关联思考会话"""
        object.__setattr__(self, 'linked_session_id', session_id)
        object.__setattr__(self, 'updated_at', datetime.utcnow())
```

**任务与思考会话关联**:
- 一个任务可以关联到一个思考会话
- 通过`linked_session_id`字段关联
- 支持任务执行时记录思考过程

#### 模板模型 (template.py)

```python
class Template(BaseModel):
    """思考模板"""
    template_id: str = Field(..., description="模板唯一标识")
    name: str = Field(..., description="模板名称")
    description: str = Field(default="", description="模板描述")
    structure: dict = Field(..., description="模板结构")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间"
    )

    class Config:
        frozen = True
```

### 2.4 持久化层架构 (storage/)

#### 设计原则
- **原子写入**: 使用临时文件+重命名确保数据完整性
- **并发安全**: 使用文件锁避免竞态条件
- **自动备份**: 每次修改前自动备份
- **简单可靠**: 使用纯JSON文件，无需额外依赖

#### 模块结构

```
storage/
├── __init__.py
├── json_file_store.py       # JSON文件存储
└── storage_manager.py       # 存储管理器
```

#### JSON文件存储 (json_file_store.py)

**职责**: 提供原子写入、并发安全的JSON文件存储

**核心功能**:
```python
import json
import tempfile
import os
from pathlib import Path

class JsonFileStore:
    """JSON文件存储"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.lock = asyncio.Lock()

    async def read(self, key: str) -> dict | None:
        """读取JSON文件"""

    async def write(self, key: str, data: dict) -> None:
        """原子写入JSON文件"""

    async def delete(self, key: str) -> None:
        """删除JSON文件"""

    async def exists(self, key: str) -> bool:
        """检查文件是否存在"""

    async def _backup(self, key: str) -> None:
        """备份文件"""
```

**原子写入机制**:
1. 数据写入临时文件
2. 临时文件重命名为目标文件
3. 重命名是原子操作，确保数据完整性

**并发控制**:
- 使用asyncio.Lock确保同一时间只有一个写操作
- 文件锁作为额外保护

**自动备份**:
- 每次write()前自动备份到backups/目录
- 保留最近10个备份版本

#### 存储管理器 (storage_manager.py)

**职责**: 提供会话CRUD操作和索引管理

**核心功能**:
```python
class StorageManager:
    """存储管理器"""

    def __init__(self, base_dir: Path):
        self.store = JsonFileStore(base_dir / "sessions")
        self.index_path = base_dir / "sessions" / ".index.json"

    async def create_session(self, session: ThinkingSession) -> None:
        """创建会话"""

    async def get_session(self, session_id: str) -> ThinkingSession | None:
        """获取会话"""

    async def update_session(self, session: ThinkingSession) -> None:
        """更新会话"""

    async def delete_session(self, session_id: str) -> None:
        """删除会话"""

    async def list_sessions(
        self,
        status: str | None = None,
        limit: int = 50
    ) -> list[ThinkingSession]:
        """列出会话"""

    async def _update_index(self, session: ThinkingSession) -> None:
        """更新索引"""
```

**索引设计**:
```json
{
  "sessions": {
    "session-123": {
      "name": "问题分析",
      "status": "active",
      "created_at": "2025-12-31T00:00:00Z",
      "thought_count": 5
    }
  },
  "updated_at": "2025-12-31T00:00:00Z"
}
```

### 2.5 工具层架构 (utils/)

#### 设计原则
- **传输感知**: 日志配置根据传输模式调整
- **可复用**: 工具函数独立、无状态
- **类型安全**: 使用类型注解

#### 模块结构

```
utils/
├── __init__.py
├── logger.py               # 传输感知的日志配置
├── validators.py           # 参数验证
└── formatters.py           # 格式化工具
```

#### 日志配置 (logger.py)

**职责**: 根据传输模式配置日志系统

```python
import logging
import sys

def setup_logging(transport_mode: str = "stdio") -> logging.Logger:
    """
    配置传输感知的日志系统

    Args:
        transport_mode: "stdio" 或 "sse"

    Returns:
        配置好的logger实例
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    if transport_mode == "stdio":
        # STDIO模式：强制输出到stderr（严禁使用print）
        handler = logging.StreamHandler(sys.stderr)
    else:
        # SSE模式：可以使用stdout或文件
        handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
```

#### 参数验证 (validators.py)

**职责**: 提供Pydantic模型和验证函数

```python
from pydantic import BaseModel, Field, field_validator

class ThoughtInput(BaseModel):
    """思考步骤输入验证"""
    thought: str = Field(..., min_length=1, max_length=10000)
    nextThoughtNeeded: bool
    thoughtNumber: int = Field(..., ge=1)
    totalThoughts: int = Field(..., ge=1)
    session_id: str = Field(default="default")
    isRevision: bool = False
    revisesThought: int | None = None
    branchFromThought: int | None = None
    branchId: str | None = None

    @field_validator('thoughtNumber')
    @classmethod
    def validate_thought_number(cls, v, info):
        if 'totalThoughts' in info.data and v > info.data['totalThoughts']:
            raise ValueError('thoughtNumber cannot exceed totalThoughts')
        return v
```

#### 格式化工具 (formatters.py)

**职责**: 提供各种格式化函数

```python
def format_markdown(session: ThinkingSession) -> str:
    """格式化为Markdown"""

def format_html(session: ThinkingSession) -> str:
    """格式化为HTML"""

def format_mermaid(session: ThinkingSession) -> str:
    """格式化为Mermaid流程图"""
```

---

## 三、数据流设计

### 3.1 顺序思考数据流

```
┌─────────────────┐
│  Claude / AI    │
└────────┬────────┘
         │
         │ 1. 调用sequential_thinking工具
         │    参数: thought, thoughtNumber, ...
         ▼
┌─────────────────────────────┐
│   FastMCP Server            │
│   (接收工具调用)             │
└────────┬────────────────────┘
         │
         │ 2. 验证参数
         ▼
┌─────────────────────────────┐
│   validators.py             │
│   (Pydantic验证)             │
└────────┬────────────────────┘
         │
         │ 3. 创建Thought对象
         ▼
┌─────────────────────────────┐
│   models.Thought            │
│   (数据模型)                 │
└────────┬────────────────────┘
         │
         │ 4. 保存到存储
         ▼
┌─────────────────────────────┐
│   storage.StorageManager    │
│   (持久化)                   │
└────────┬────────────────────┘
         │
         │ 5. 原子写入JSON文件
         ▼
┌─────────────────────────────┐
│   ./.deepthinking/          │
│   sessions/{session_id}.json│
└────────┬────────────────────┘
         │
         │ 6. 更新索引
         ▼
┌─────────────────────────────┐
│   .index.json               │
└────────┬────────────────────┘
         │
         │ 7. 返回结果
         ▼
┌─────────────────────────────┐
│   FastMCP响应               │
│   (JSON格式)                 │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────┐
│  Claude / AI    │
└─────────────────┘
```

### 3.2 会话管理数据流

```
┌─────────────────┐
│  Claude / AI    │
└────────┬────────┘
         │
         │ 调用create_session
         ▼
┌─────────────────────────────┐
│   session_manager.create    │
└────────┬────────────────────┘
         │
         │ 创建ThinkingSession对象
         ▼
┌─────────────────────────────┐
│   models.ThinkingSession    │
└────────┬────────────────────┘
         │
         │ 保存到存储
         ▼
┌─────────────────────────────┐
│   storage.StorageManager    │
└────────┬────────────────────┘
         │
         │ 原子写入
         ▼
┌─────────────────────────────┐
│   sessions/{session_id}.json│
└────────┬────────────────────┘
         │
         │ 返回session_id
         ▼
┌─────────────────┐
│  Claude / AI    │
└─────────────────┘
```

---

## 四、接口定义

### 4.1 MCP工具接口

#### sequential_thinking

```json
{
  "name": "sequential_thinking",
  "description": "执行顺序思考步骤，支持常规/修订/分支三种模式",
  "inputSchema": {
    "type": "object",
    "properties": {
      "thought": {
        "type": "string",
        "description": "思考内容"
      },
      "nextThoughtNeeded": {
        "type": "boolean",
        "description": "是否需要更多思考"
      },
      "thoughtNumber": {
        "type": "integer",
        "minimum": 1,
        "description": "当前思考步骤编号"
      },
      "totalThoughts": {
        "type": "integer",
        "minimum": 1,
        "description": "总思考步骤数（可动态调整）"
      },
      "session_id": {
        "type": "string",
        "default": "default",
        "description": "会话标识"
      },
      "isRevision": {
        "type": "boolean",
        "default": false,
        "description": "是否为修订思考"
      },
      "revisesThought": {
        "type": "integer",
        "description": "修订的思考步骤编号"
      },
      "branchFromThought": {
        "type": "integer",
        "description": "分支起始思考步骤编号"
      },
      "branchId": {
        "type": "string",
        "description": "分支标识符"
      },
      "needsMoreThoughts": {
        "type": "boolean",
        "default": false,
        "description": "需要扩展totalThoughts"
      }
    },
    "required": ["thought", "nextThoughtNeeded", "thoughtNumber", "totalThoughts"]
  }
}
```

#### create_session

```json
{
  "name": "create_session",
  "description": "创建新的思考会话",
  "inputSchema": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "会话名称"
      },
      "description": {
        "type": "string",
        "default": "",
        "description": "会话描述"
      },
      "metadata": {
        "type": "object",
        "default": {},
        "description": "元数据"
      }
    },
    "required": ["name"]
  }
}
```

### 4.2 数据模型接口

#### Thought

```json
{
  "thought_number": "integer",
  "content": "string",
  "type": "regular|revision|branch",
  "is_revision": "boolean",
  "revises_thought": "integer|null",
  "branch_from_thought": "integer|null",
  "branch_id": "string|null",
  "timestamp": "datetime (ISO 8601)"
}
```

#### ThinkingSession

```json
{
  "session_id": "string (UUID)",
  "name": "string",
  "description": "string",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)",
  "status": "active|completed|archived",
  "thoughts": ["Thought"],
  "metadata": "object"
}
```

---

## 五、技术选型理由

| 技术选择 | 理由 |
|---------|------|
| FastMCP | 官方高层MCP框架，简化开发 |
| Pydantic | 类型安全，自动验证，序列化友好 |
| aiohttp | 异步HTTP服务器，支持SSE |
| asyncio | 异步IO，高性能 |
| pytest | 成熟的Python测试框架 |
| JSON文件 | 简单可靠，无需额外依赖 |

---

## 六、安全考虑

### 6.1 输入验证
- 所有输入使用Pydantic验证
- 字符串长度限制
- 数值范围检查

### 6.2 文件路径安全
- 限制文件操作在base_dir内
- 防止路径遍历攻击

### 6.3 并发控制
- 文件锁防止竞态条件
- asyncio.Lock保证原子操作

### 6.4 认证（SSE模式）
- Bearer Token认证
- API Key认证支持
