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
| `sequential_thinking` | 执行顺序思考步骤 | 核心思考 |
| `create_session` | 创建新会话 | 会话管理 |
| `get_session` | 获取会话详情 | 会话管理 |
| `list_sessions` | 列出所有会话 | 会话管理 |
| `delete_session` | 删除会话 | 会话管理 |
| `update_session_status` | 更新会话状态 | 会话管理 |
| `apply_template` | 应用思考模板 | 模板系统 |
| `list_templates` | 列出可用模板 | 模板系统 |
| `export_session` | 导出会话 | 导出工具 |
| `visualize_session` | 可视化会话 | 可视化工具 |
| `visualize_session_simple` | 简化可视化 | 可视化工具 |

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
| `needsMoreThoughts` | boolean | ❌ | false | 是否需要增加总思考步骤数（预留参数） |

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

## 3. 模板系统

### 3.1 apply_template

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

### 3.2 list_templates

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

## 4. 导出工具

### 4.1 export_session

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

## 5. 可视化工具

### 5.1 visualize_session

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

### 5.2 visualize_session_simple

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
