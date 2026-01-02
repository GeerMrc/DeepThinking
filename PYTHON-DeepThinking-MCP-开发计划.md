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
│   ├── transports/               # 传输层实现
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
│   └── test_transports/
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

---

### 阶段2: 数据模型实现

**任务清单**:
- [ ] 实现思考步骤模型（models/thought.py）
- [ ] 实现思考会话模型（models/thinking_session.py）
- [ ] 实现模板模型（models/template.py）
- [ ] 编写模型单元测试

**关键文件**:
- `src/deep_thinking/models/thought.py`
- `src/deep_thinking/models/thinking_session.py`

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

---

## 六、下一步

确认计划后，开始**阶段1: 基础框架搭建**。
