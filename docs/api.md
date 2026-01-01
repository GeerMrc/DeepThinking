# DeepThinking-MCP API 文档

> 版本: 0.1.0
> 更新日期: 2026-01-01
>
> **重要更新** (2026-01-01):
> - 同步/异步设计统一：所有MCP工具函数均为同步函数，调用时无需使用 `await`
> - 代码已改为全同步设计（详见 `docs/ASYNC_SYNC_ANALYSIS.md`）
> - 示例代码已同步更新，移除了错误的 `await` 关键字

---

## 概述

DeepThinking-MCP 是一个基于 Model Context Protocol (MCP) 的深度思考服务器，提供顺序思考、会话管理、模板应用、导出和可视化等功能。

### MCP工具列表

| 工具名称 | 功能描述 | 分类 |
|---------|---------|------|
| `sequential_thinking` | 执行顺序思考步骤（支持动态调整） | 核心思考 |
| `resume_session` | 恢复已暂停的思考会话 | 会话管理 |
| `create_session` | 创建新会话 | 会话管理 |
| `get_session` | 获取会话详情 | 会话管理 |
| `list_sessions` | 列出所有会话 | 会话管理 |
| `delete_session` | 删除会话 | 会话管理 |
| `update_session_status` | 更新会话状态 | 会话管理 |
| `create_task` | 创建新任务 | 任务管理 |
| `list_tasks` | 列出任务 | 任务管理 |
| `update_task_status` | 更新任务状态 | 任务管理 |
| `get_next_task` | 获取下一个待执行任务 | 任务管理 |
| `get_task_stats` | 获取任务统计信息 | 任务管理 |
| `link_task_session` | 关联任务与思考会话 | 任务管理 |
| `apply_template` | 应用思考模板 | 模板系统 |
| `list_templates` | 列出可用模板 | 模板系统 |
| `export_session` | 导出会话 | 导出工具 |
| `visualize_session` | 可视化会话 | 可视化工具 |
| `visualize_session_simple` | 简化可视化 | 可视化工具 |

---

## 数据存储

### 存储位置

DeepThinking-MCP 将思考会话数据存储在本地文件系统中。

**默认存储路径（项目本地）**:
```
./.deep-thinking-mcp/
├── sessions/           # 会话数据目录
│   ├── .index.json    # 会话索引文件
│   └── *.json         # 各个会话的数据文件
├── .backups/          # 自动备份目录
└── .gitignore         # 防止数据提交到版本控制
```

### 存储路径配置

存储路径支持以下配置方式（按优先级排序）：

1. **环境变量**: `DEEP_THINKING_DATA_DIR`
   ```bash
   export DEEP_THINKING_DATA_DIR=/custom/path
   ```

2. **CLI参数**: `--data-dir`
   ```bash
   python -m deep_thinking --data-dir /custom/path
   ```

3. **默认值**: 项目本地目录 `.deep-thinking-mcp/`

### 数据迁移

**自动迁移**: 从旧版本（`~/.deep-thinking-mcp/`）升级时，系统会：
- 检测旧数据目录
- 自动创建备份
- 迁移数据到新位置
- 创建迁移标记文件

手动迁移或查看迁移状态，请参考 `MIGRATION.md`。

### 数据格式

所有数据以 JSON 格式存储，包含：
- 会话元数据（ID、名称、描述、状态）
- 思考步骤序列（内容、类型、时间戳）
- 索引信息（快速查找）

---

## 1. 核心思考工具

### 1.1 sequential_thinking

执行顺序思考步骤，支持常规思考、修订思考和分支思考三种类型。

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `thought` | string | ✅ | - | 当前思考内容 |
| `nextThoughtNeeded` | boolean | ✅ | - | 是否需要继续思考 |
| `thoughtNumber` | integer | ✅ | - | 当前思考步骤编号（从1开始） |
| `totalThoughts` | integer | ✅ | - | 预计总思考步骤数 |
| `session_id` | string | ❌ | "default" | 会话ID |
| `isRevision` | boolean | ❌ | false | 是否为修订思考 |
| `revisesThought` | integer\|null | ❌ | null | 修订的思考步骤编号 |
| `branchFromThought` | integer\|null | ❌ | null | 分支来源思考步骤编号 |
| `branchId` | string\|null | ❌ | null | 分支ID（格式如 "branch-0-1"） |
| `needsMoreThoughts` | boolean | ❌ | false | 是否需要增加总思考步骤数（每次增加10步，上限1000步） |

#### 返回值

返回思考结果描述，包含：
- 当前思考信息和类型
- 会话状态（会话ID、总思考数、预计总数）
- 下一步提示或完成标记

#### 思考类型

1. **常规思考 (regular)**: 标准的顺序思考步骤
2. **修订思考 (revision)**: 修改之前某个思考步骤
3. **分支思考 (branch)**: 从某个思考步骤创建新的分支

#### 使用示例

```python
# 常规思考
sequential_thinking(
    thought="首先分析问题的核心要素",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=5,
    session_id="my-session"
)

# 修订思考
sequential_thinking(
    thought="修正之前的分析，添加新的考虑因素",
    nextThoughtNeeded=True,
    thoughtNumber=4,
    totalThoughts=6,
    session_id="my-session",
    isRevision=True,
    revisesThought=2
)

# 分支思考
sequential_thinking(
    thought="探索另一种可能的解决方案",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=3,
    session_id="my-session",
    branchFromThought=3,
    branchId="branch-0-1"
)
```

#### 错误处理

- `ValueError`: 参数验证失败
- `RuntimeError`: 会话丢失

---

## 2. 会话管理工具

### 2.1 create_session

创建新的思考会话。

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `name` | string | ✅ | - | 会话名称 |
| `description` | string | ❌ | "" | 会话描述 |
| `metadata` | string\|null | ❌ | null | 元数据JSON字符串 |

#### 返回值

返回创建的会话信息：
- 会话ID
- 名称
- 描述
- 创建时间
- 状态

#### 使用示例

```python
create_session(
    name="技术方案分析",
    description="分析不同技术方案的优劣",
    metadata='{"project": "AI平台", "priority": "high"}'
)
```

---

### 2.2 get_session

获取会话详情。

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `session_id` | string | ✅ | - | 会话ID |

#### 返回值

返回会话详细信息：
- 会话ID、名称、描述
- 状态
- 创建/更新时间
- 思考步骤数
- 所有思考步骤列表

#### 使用示例

```python
get_session("abc-123-def")
```

#### 错误处理

- `ValueError`: 会话不存在

---

### 2.3 list_sessions

列出所有会话。

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `status` | string\|null | ❌ | null | 过滤状态（active/completed/archived） |
| `limit` | integer | ❌ | 20 | 最大返回数量 |

#### 返回值

返回会话列表，每个会话包含：
- 名称
- 会话ID
- 状态
- 思考数
- 更新时间

#### 使用示例

```python
# 列出所有会话
list_sessions()

# 只列出活跃会话
list_sessions(status="active", limit=10)
```

#### 状态值

- `active`: 活跃中
- `completed`: 已完成
- `archived`: 已归档

---

### 2.4 delete_session

删除会话。

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `session_id` | string | ✅ | - | 会话ID |

#### 返回值

返回删除结果（成功/失败信息）

#### 使用示例

```python
delete_session("abc-123-def")
```

---

### 2.5 update_session_status

更新会话状态。

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `session_id` | string | ✅ | - | 会话ID |
| `status` | string | ✅ | - | 新状态（active/completed/archived） |

#### 返回值

返回更新结果

#### 使用示例

```python
update_session_status("abc-123-def", "completed")
```

#### 错误处理

- `ValueError`: 会话不存在或状态值无效

---

### 2.6 resume_session

恢复已暂停的思考会话（断点续传功能）。

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `session_id` | string | ✅ | - | 要恢复的会话ID |

#### 返回值

返回会话恢复信息，包含：
- 会话ID、名称、状态
- 总思考数
- 上一个思考步骤内容
- 思考步骤调整历史（如有）
- 继续思考的指导

#### 使用示例

```python
# 恢复会话，获取上次思考进度
resume_session("my-session-id")
```

#### 断点续传功能

- 获取会话的最后一个思考步骤
- 显示当前思考进度和状态
- 提供继续思考的参数指导
- 支持查看历史调整记录

#### 错误处理

- `ValueError`: 会话不存在

---

## 3. 任务管理工具

任务管理工具提供任务清单管理功能，支持优先级驱动的任务执行。

### 3.1 create_task

创建新任务。

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `title` | string | ✅ | - | 任务标题 |
| `description` | string | ❌ | "" | 任务描述 |
| `priority` | string | ❌ | "P2" | 任务优先级（P0/P1/P2） |
| `task_id` | string\|null | ❌ | null | 任务ID（不提供则自动生成） |

#### 返回值

返回创建的任务信息：
- 任务ID
- 标题
- 优先级
- 状态

#### 使用示例

```python
# 创建高优先级任务
create_task(
    title="修复登录bug",
    description="用户无法正常登录",
    priority="P0"
)

# 创建中等优先级任务
create_task(
    title="优化数据库查询",
    priority="P1"
)
```

#### 优先级说明

- `P0`: 最高优先级，立即处理
- `P1`: 高优先级，尽快处理
- `P2`: 普通优先级，按计划处理

---

### 3.2 list_tasks

列出任务，支持按状态和优先级过滤。

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `status` | string\|null | ❌ | null | 过滤状态（pending/in_progress/completed/failed/blocked） |
| `priority` | string\|null | ❌ | null | 过滤优先级（P0/P1/P2） |
| `limit` | integer | ❌ | 100 | 最大返回数量 |

#### 返回值

返回任务列表，每个任务包含：
- 状态图标
- 优先级
- 标题
- 任务ID
- 状态
- 更新时间

#### 使用示例

```python
# 列出所有任务
list_tasks()

# 只列出待执行的高优先级任务
list_tasks(status="pending", priority="P0")

# 列出进行中的任务
list_tasks(status="in_progress")
```

#### 状态值

- `pending`: 待执行
- `in_progress`: 进行中
- `completed`: 已完成
- `failed`: 失败
- `blocked`: 已阻塞

---

### 3.3 update_task_status

更新任务状态。

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `task_id` | string | ✅ | - | 任务ID |
| `new_status` | string | ✅ | - | 新状态（pending/in_progress/completed/failed/blocked） |

#### 返回值

返回更新结果，包含：
- 任务ID
- 旧状态 → 新状态

#### 使用示例

```python
# 开始执行任务
update_task_status("task-123", "in_progress")

# 标记任务完成
update_task_status("task-123", "completed")

# 标记任务失败
update_task_status("task-123", "failed")
```

---

### 3.4 get_next_task

获取下一个待执行任务（按优先级排序）。

#### 参数

无参数

#### 返回值

返回下一个待执行任务信息：
- 任务ID
- 标题
- 描述
- 优先级
- 创建时间

如果没有待执行任务，返回提示信息。

#### 使用示例

```python
# 获取下一个待执行任务
next_task = get_next_task()
```

#### 优先级排序

- P0 任务优先
- P1 任务次之
- P2 任务最后
- 同优先级按创建时间排序

---

### 3.5 get_task_stats

获取任务统计信息。

#### 参数

无参数

#### 返回值

返回任务统计信息：
- 总任务数
- 状态分布（各状态任务数）
- 优先级分布（各优先级任务数）

#### 使用示例

```python
# 获取任务统计
stats = get_task_stats()
```

---

### 3.6 link_task_session

关联任务与思考会话。

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `task_id` | string | ✅ | - | 任务ID |
| `session_id` | string | ✅ | - | 思考会话ID |

#### 返回值

返回关联结果，包含：
- 任务ID
- 关联的会话ID

#### 使用示例

```python
# 将任务与思考会话关联
link_task_session("task-123", "session-abc")
```

#### 使用场景

- 跟踪任务相关的思考过程
- 在任务执行时记录思考步骤
- 任务完成后回顾思考历程

---

## 4. 模板系统

### 4.1 apply_template

应用思考模板创建新会话。

#### 内置模板

| 模板ID | 名称 | 描述 |
|-------|------|------|
| `problem_solving` | 问题求解模板 | 系统地分析和解决问题 |
| `decision_making` | 决策模板 | 帮助做出理性决策 |
| `analysis` | 分析模板 | 深入分析复杂问题 |

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `template_id` | string | ✅ | - | 模板ID |
| `context` | string | ❌ | "" | 当前问题或任务的上下文描述 |
| `session_name` | string\|null | ❌ | null | 会话名称（默认使用模板名称） |

#### 返回值

返回：
- 创建的会话信息
- 模板引导步骤列表

#### 使用示例

```python
# 应用问题求解模板
apply_template(
    template_id="problem_solving",
    context="如何优化团队协作效率"
)

# 应用决策模板
apply_template(
    template_id="decision_making",
    context="选择哪个技术方案：方案A vs 方案B"
)
```

#### 错误处理

- `ValueError`: 模板不存在或参数无效

---

### 4.2 list_templates

列出所有可用的思考模板。

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `category` | string\|null | ❌ | null | 过滤类别（problem_solving/decision/analysis） |

#### 返回值

返回模板列表，每个模板包含：
- 名称
- ID
- 描述
- 标签

#### 使用示例

```python
# 列出所有模板
list_templates()

# 只列决策类模板
list_templates(category="decision")
```

---

## 5. 导出工具

### 5.1 export_session

导出思考会话为指定格式。

#### 支持的格式

| 格式 | 扩展名 | 描述 |
|------|-------|------|
| `json` | .json | JSON格式，包含完整的会话数据 |
| `markdown` / `md` | .md | Markdown格式，适合文档查看 |
| `html` | .html | HTML格式，带有样式，适合浏览器查看 |
| `text` / `txt` | .txt | 纯文本格式，兼容性最好 |

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `session_id` | string | ✅ | - | 会话ID |
| `format_type` | string | ❌ | "markdown" | 导出格式 |
| `output_path` | string | ❌ | "" | 输出文件路径（可选） |

#### output_path 参数说明

- 如果为空：自动生成文件名到 `~/exports/` 目录
- 如果指定路径：使用指定路径
- 支持相对路径和绝对路径
- 支持波浪号(~)展开

#### 返回值

返回导出结果，包含：
- 会话名称、ID
- 导出格式
- 文件路径
- 思考步骤数

#### 使用示例

```python
# 使用默认格式和路径
export_session("abc-123")

# 导出为JSON格式
export_session("abc-123", "json")

# 指定输出路径
export_session("abc-123", "html", "~/my-session.html")

# 使用相对路径
export_session("abc-123", "markdown", "./exports/session.md")
```

#### 错误处理

- `ValueError`: 会话不存在、格式不支持

---

## 6. 可视化工具

### 6.1 visualize_session

可视化思考会话。

#### 支持的格式

| 格式 | 描述 |
|------|------|
| `mermaid` | Mermaid 流程图代码（可用于 Markdown 文档或 Mermaid 编辑器） |
| `ascii` | ASCII 流程图（纯文本，适合终端显示） |
| `tree` | 树状结构（简化的层次显示） |

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `session_id` | string | ✅ | - | 会话ID |
| `format_type` | string | ❌ | "mermaid" | 可视化格式 |

#### 返回值

返回可视化结果，包含：
- 会话信息
- 可视化内容
- 使用提示

#### 使用示例

```python
# 使用默认 Mermaid 格式
visualize_session("abc-123")

# 使用 ASCII 格式
visualize_session("abc-123", "ascii")

# 使用树状结构
visualize_session("abc-123", "tree")
```

#### 错误处理

- `ValueError`: 会话不存在、格式不支持

---

### 6.2 visualize_session_simple

简化的会话可视化（直接返回可视化内容，不包含额外说明）。

#### 参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|-------|------|-----|-------|------|
| `session_id` | string | ✅ | - | 会话ID |
| `format_type` | string | ❌ | "tree" | 可视化格式 |

#### 返回值

直接返回纯可视化内容（无额外说明）

#### 使用示例

```python
# 直接获取 Mermaid 代码
mermaid_code = visualize_session_simple("abc-123", "mermaid")

# 获取树状结构
tree_structure = visualize_session_simple("abc-123", "tree")
```

---

## 数据模型

### Thought（思考步骤）

```typescript
{
  thought_number: number;      // 思考步骤编号
  content: string;             // 思考内容
  type: "regular" | "revision" | "branch";  // 思考类型
  is_revision: boolean;        // 是否为修订
  revises_thought: number | null;  // 修订的思考步骤编号
  branch_from_thought: number | null;  // 分支来源
  branch_id: string | null;    // 分支ID
  timestamp: string;           // 时间戳（ISO 8601）
}
```

### ThinkingSession（思考会话）

```typescript
{
  session_id: string;          // 会话ID（UUID）
  name: string;                // 会话名称
  description: string;         // 会话描述
  status: "active" | "completed" | "archived";  // 状态
  created_at: string;          // 创建时间
  updated_at: string;          // 更新时间
  thoughts: Thought[];         // 思考步骤列表
  metadata: Record<string, any>;  // 元数据
}
```

---

## 错误处理

所有工具在遇到错误时会抛出 `ValueError`，包含详细的错误信息。

常见错误：
- 会话不存在
- 参数验证失败
- 格式不支持
- 元数据JSON格式错误

---

## 传输模式

DeepThinking-MCP 支持两种传输模式：

### STDIO 模式
- 适用于命令行和本地应用
- 通过标准输入/输出通信

### SSE 模式
- 适用于Web应用和远程访问
- 通过HTTP Server-Sent Events通信

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 0.1.0 | 2025-12-31 | 初始版本 |

---

## 许可证

MIT License
