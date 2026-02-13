# DeepThinking MCP 使用示例

> 版本: 0.2.4
> 更新日期: 2026-02-14

本文档提供了 DeepThinking MCP 的详细使用示例，涵盖基本功能、Interleaved Thinking、资源控制等场景。

---

## 目录

1. [基本交错思考](#1-基本交错思考)
2. [工具调用追踪](#2-工具调用追踪)
3. [资源控制](#3-资源控制)
4. [六种思考类型](#4-六种思考类型)
5. [会话管理](#5-会话管理)
6. [导出和可视化](#6-导出和可视化)

---

## 1. 基本交错思考

### 1.1 三阶段工作流

Interleaved Thinking 支持三种执行阶段：`thinking`（思考）、`tool_call`（工具调用）、`analysis`（分析）。

```python
# 创建一个完整的交错思考会话
session_id = "interleaved-workflow-demo"

# Step 1: thinking 阶段 - 初始思考
result = sequential_thinking(
    thought="首先分析问题：需要获取用户订单数据进行分析",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=3,
    session_id=session_id,
)
# 输出: **阶段**: 思考 🧠

# Step 2: tool_call 阶段 - 调用工具获取数据
result = sequential_thinking(
    thought="调用数据库查询工具获取订单数据",
    nextThoughtNeeded=True,
    thoughtNumber=2,
    totalThoughts=3,
    session_id=session_id,
    toolCalls=[
        {"name": "query_database", "arguments": {"sql": "SELECT * FROM orders WHERE status = 'pending'"}},
    ],
)
# 输出: **阶段**: 工具调用 🔧
# 输出: 🔧 工具调用 (1个)

# Step 3: analysis 阶段 - 分析工具结果
result = sequential_thinking(
    thought="分析查询结果，发现有 25 条待处理订单",
    nextThoughtNeeded=False,
    thoughtNumber=3,
    totalThoughts=3,
    session_id=session_id,
    toolResults=[
        {"call_id": "...", "result": {"count": 25, "orders": [...]}, "success": True},
    ],
)
# 输出: **阶段**: 分析 📊
# 输出: ✅ 思考完成！
```

### 1.2 自动阶段推断

当 `phase` 参数为空时，系统会根据其他参数自动推断执行阶段：

```python
# 自动推断为 thinking（无 toolCalls 和 toolResults）
sequential_thinking(
    thought="纯思考内容",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=3,
    session_id="auto-infer-demo",
)
# 推断结果: thinking

# 自动推断为 tool_call（有 toolCalls）
sequential_thinking(
    thought="需要调用工具",
    nextThoughtNeeded=True,
    thoughtNumber=2,
    totalThoughts=3,
    session_id="auto-infer-demo",
    toolCalls=[{"name": "search", "arguments": {"q": "test"}}],
)
# 推断结果: tool_call

# 自动推断为 analysis（有 toolResults）
sequential_thinking(
    thought="分析结果",
    nextThoughtNeeded=False,
    thoughtNumber=3,
    totalThoughts=3,
    session_id="auto-infer-demo",
    toolResults=[{"call_id": "1", "result": "data", "success": True}],
)
# 推断结果: analysis（优先级最高）
```

### 1.3 显式指定阶段

可以显式指定 `phase` 参数覆盖自动推断：

```python
# 即使有 toolCalls，显式指定为 thinking
sequential_thinking(
    thought="这是计划阶段，工具调用只是计划",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=3,
    session_id="explicit-phase-demo",
    phase="thinking",  # 显式指定
    toolCalls=[{"name": "planned_tool", "arguments": {}}],
)
# 输出: **阶段**: 思考 🧠
```

---

## 2. 工具调用追踪

### 2.1 单工具调用

每个思考步骤可以关联一个工具调用：

```python
sequential_thinking(
    thought="调用搜索工具查找相关文档",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=3,
    session_id="single-tool-demo",
    toolCalls=[
        {"name": "search_docs", "arguments": {"query": "API 设计"}},
    ],
    toolResults=[
        {"call_id": "search-1", "result": "找到 10 篇相关文档", "success": True},
    ],
)
```

### 2.2 多工具调用（1:N 映射）

每个思考步骤可以关联多个工具调用，实现 1:N 映射：

```python
sequential_thinking(
    thought="并行获取用户信息、订单历史和产品数据",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=3,
    session_id="multi-tool-demo",
    toolCalls=[
        {"name": "get_user", "arguments": {"user_id": 123}, "call_id": "call-user"},
        {"name": "get_orders", "arguments": {"user_id": 123}, "call_id": "call-orders"},
        {"name": "get_products", "arguments": {"category": "electronics"}, "call_id": "call-products"},
    ],
    toolResults=[
        {"call_id": "call-user", "result": {"id": 123, "name": "Alice"}, "success": True},
        {"call_id": "call-orders", "result": [{"id": 1}, {"id": 2}], "success": True},
        {"call_id": "call-products", "result": [{"id": 101}, {"id": 102}], "success": True},
    ],
)
# 输出: 🔧 工具调用 (3个)
#   1. **get_user** - completed
#   2. **get_orders** - completed
#   3. **get_products** - completed
```

### 2.3 使用 call_id 匹配结果

使用 `call_id` 确保工具调用和结果正确匹配：

```python
sequential_thinking(
    thought="异步获取多个独立数据源",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=3,
    session_id="call-id-demo",
    toolCalls=[
        {"name": "api_a", "arguments": {}, "call_id": "id-a"},
        {"name": "api_b", "arguments": {}, "call_id": "id-b"},
        {"name": "api_c", "arguments": {}, "call_id": "id-c"},
    ],
    # 结果可以以任意顺序返回
    toolResults=[
        {"call_id": "id-c", "result": "c_result", "success": True},
        {"call_id": "id-a", "result": "a_result", "success": True},
        {"call_id": "id-b", "result": "b_result", "success": True},
    ],
)
# 每个结果会正确匹配到对应的工具调用
```

### 2.4 处理失败的工具调用

```python
sequential_thinking(
    thought="尝试调用可能失败的服务",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=3,
    session_id="failure-demo",
    toolCalls=[
        {"name": "reliable_service", "arguments": {}, "call_id": "call-1"},
        {"name": "unreliable_service", "arguments": {}, "call_id": "call-2"},
    ],
    toolResults=[
        {"call_id": "call-1", "result": "success_data", "success": True},
        {"call_id": "call-2", "result": null, "success": False, "error": "Connection timeout"},
    ],
)
# 输出: 🔧 工具调用 (2个)
#   1. **reliable_service** - completed
#      成功: 是
#   2. **unreliable_service** - completed
#      成功: 否
```

### 2.5 缓存命中标记

```python
sequential_thinking(
    thought="使用缓存加速重复查询",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=3,
    session_id="cache-demo",
    toolCalls=[
        {"name": "cached_query", "arguments": {"key": "frequent_data"}},
    ],
    toolResults=[
        {"call_id": "1", "result": "cached_result", "success": True, "from_cache": True},
    ],
)
# 统计信息会记录 cached_tool_calls += 1
```

---

## 3. 资源控制

### 3.1 配置资源限制

通过环境变量配置资源限制：

```bash
# 会话总工具调用次数上限
export DEEP_THINKING_MAX_TOOL_CALLS=100

# 每步骤工具调用次数上限
export DEEP_THINKING_MAX_TOOL_CALLS_PER_THOUGHT=10
```

### 3.2 超过总调用限制

当工具调用次数超过配置上限时，系统会拒绝新的调用：

```python
# 假设 DEEP_THINKING_MAX_TOOL_CALLS=5
# 已调用 5 次工具后...

result = sequential_thinking(
    thought="尝试第 6 次工具调用",
    nextThoughtNeeded=False,
    thoughtNumber=6,
    totalThoughts=10,
    session_id="limit-demo",
    toolCalls=[{"name": "test", "arguments": {}}],
)
# 输出: ⚠️ 警告：工具调用次数将超限，当前 5 + 新增 1 > 上限 5。
```

### 3.3 超过每步骤限制

当单步骤工具调用次数超过配置上限时：

```python
# 假设 DEEP_THINKING_MAX_TOOL_CALLS_PER_THOUGHT=3
# 尝试调用 4 个工具...

result = sequential_thinking(
    thought="尝试单步骤调用过多工具",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=3,
    session_id="per-thought-limit-demo",
    toolCalls=[
        {"name": "tool_1", "arguments": {}},
        {"name": "tool_2", "arguments": {}},
        {"name": "tool_3", "arguments": {}},
        {"name": "tool_4", "arguments": {}},  # 超过限制
    ],
)
# 输出: ⚠️ 警告：单步骤工具调用数超限，请求 4 > 每步骤上限 3。
```

### 3.4 查看统计信息

会话会自动统计工具调用信息：

```python
# 创建会话并执行工具调用
session_id = "stats-demo"

sequential_thinking(
    thought="调用工具",
    nextThoughtNeeded=False,
    thoughtNumber=1,
    totalThoughts=1,
    session_id=session_id,
    toolCalls=[
        {"name": "tool_a", "arguments": {}},
        {"name": "tool_b", "arguments": {}},
    ],
    toolResults=[
        {"call_id": "1", "result": "ok", "success": True},
        {"call_id": "2", "result": "error", "success": False},
    ],
)

# 获取会话查看统计信息
session = get_session(session_id)
print(session.statistics)
# 输出:
# total_tool_calls: 2
# successful_tool_calls: 1
# failed_tool_calls: 0  # 注：success=False 不等同于 status="failed"
# cached_tool_calls: 0
```

---

## 4. 六种思考类型

### 4.1 常规思考 (regular)

标准的顺序思考步骤：

```python
sequential_thinking(
    thought="分析问题的核心要素",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=5,
    session_id="types-demo",
)
```

### 4.2 修订思考 (revision)

修改之前某个思考步骤：

```python
sequential_thinking(
    thought="修正之前的分析，添加新的考虑因素",
    nextThoughtNeeded=True,
    thoughtNumber=3,
    totalThoughts=5,
    session_id="types-demo",
    isRevision=True,
    revisesThought=2,  # 修订第 2 步
)
```

### 4.3 分支思考 (branch)

从某个思考步骤创建新的分支：

```python
sequential_thinking(
    thought="探索另一种可能的解决方案",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=3,
    session_id="types-demo",
    branchFromThought=3,  # 从第 3 步分支
    branchId="branch-alt-solution",
)
```

### 4.4 对比思考 (comparison)

比较多个选项或方案的优劣：

```python
sequential_thinking(
    thought="经过综合对比，方案A在性能和成本上更优",
    nextThoughtNeeded=True,
    thoughtNumber=4,
    totalThoughts=5,
    session_id="types-demo",
    comparisonItems=[
        "方案A: 高性能低成本",
        "方案B: 易维护但成本高",
        "方案C: 折中方案",
    ],
    comparisonDimensions=["性能", "成本", "维护性"],
    comparisonResult="方案A综合得分最高，推荐采用",
)
```

### 4.5 逆向思考 (reverse)

从结论反推前提条件验证：

```python
sequential_thinking(
    thought="验证结论：采用微服务架构的前提条件已满足",
    nextThoughtNeeded=False,
    thoughtNumber=5,
    totalThoughts=5,
    session_id="types-demo",
    reverseTarget="验证'采用微服务架构'结论的前提条件",
    reverseSteps=[
        "前提1: 团队规模>20人 ✓",
        "前提2: 业务模块边界清晰 ✓",
        "前提3: 技术储备充足 ✓",
    ],
)
```

### 4.6 假设思考 (hypothetical)

探索假设条件下的影响：

```python
sequential_thinking(
    thought="用户量增长10倍将带来显著架构压力",
    nextThoughtNeeded=True,
    thoughtNumber=3,
    totalThoughts=4,
    session_id="types-demo",
    hypotheticalCondition="如果用户数量从10万增长到100万",
    hypotheticalImpact="服务器负载增加10倍，需要：1.数据库分库分表 2.引入缓存层 3.增加CDN节点",
    hypotheticalProbability="可能性：高",
)
```

---

## 5. 会话管理

### 5.1 创建会话

```python
# 创建新会话
session = create_session(
    name="技术方案分析",
    description="分析不同技术方案的优劣",
    metadata='{"project": "AI平台", "priority": "high"}'
)
print(f"会话ID: {session['session_id']}")
```

### 5.2 恢复会话

```python
# 恢复已暂停的会话
session = resume_session("existing-session-id")
print(f"上一步思考: {session['latest_thought']}")
print(f"总思考数: {session['thought_count']}")
```

### 5.3 列出会话

```python
# 列出所有活跃会话
sessions = list_sessions(status="active", limit=10)
for s in sessions:
    print(f"- {s['name']} ({s['session_id'][:8]}...)")
```

### 5.4 更新会话状态

```python
# 标记会话为已完成
update_session_status("session-id", "completed")

# 归档会话
update_session_status("session-id", "archived")
```

---

## 6. 导出和可视化

### 6.1 导出会话

```python
# 导出为 JSON
export_session("session-id", "json", "~/exports/session.json")

# 导出为 Markdown
export_session("session-id", "markdown", "~/exports/session.md")

# 导出为 HTML
export_session("session-id", "html", "~/exports/session.html")

# 导出为纯文本
export_session("session-id", "text", "~/exports/session.txt")
```

### 6.2 可视化会话

```python
# Mermaid 流程图（可在 Markdown 中渲染）
mermaid_code = visualize_session("session-id", "mermaid")

# ASCII 流程图（适合终端显示）
ascii_art = visualize_session("session-id", "ascii")

# 树状结构
tree_structure = visualize_session("session-id", "tree")
```

### 6.3 简化可视化

```python
# 直接获取可视化内容（无额外说明）
mermaid_code = visualize_session_simple("session-id", "mermaid")
tree_structure = visualize_session_simple("session-id", "tree")
```

---

## 完整示例

### 端到端工作流

```python
# 1. 创建会话
session = create_session(
    name="产品分析",
    description="分析产品数据并生成报告"
)
session_id = session["session_id"]

# 2. 执行交错思考工作流
# Step 1: thinking
sequential_thinking(
    thought="需要分析产品销售数据",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=5,
    session_id=session_id,
)

# Step 2: tool_call
sequential_thinking(
    thought="查询销售数据库",
    nextThoughtNeeded=True,
    thoughtNumber=2,
    totalThoughts=5,
    session_id=session_id,
    toolCalls=[
        {"name": "query_sales", "arguments": {"month": "2026-01"}},
    ],
)

# Step 3: analysis
sequential_thinking(
    thought="分析销售数据趋势",
    nextThoughtNeeded=True,
    thoughtNumber=3,
    totalThoughts=5,
    session_id=session_id,
    toolResults=[
        {"call_id": "...", "result": {"total": 1000000, "growth": 0.15}, "success": True},
    ],
)

# Step 4: thinking (继续思考)
sequential_thinking(
    thought="根据分析结果制定营销策略",
    nextThoughtNeeded=True,
    thoughtNumber=4,
    totalThoughts=5,
    session_id=session_id,
)

# Step 5: 完成
sequential_thinking(
    thought="策略已制定完成",
    nextThoughtNeeded=False,
    thoughtNumber=5,
    totalThoughts=5,
    session_id=session_id,
)

# 3. 查看统计信息
session = get_session(session_id)
print(f"工具调用次数: {session['statistics']['total_tool_calls']}")

# 4. 导出报告
export_session(session_id, "markdown", "~/exports/product-analysis.md")

# 5. 可视化思考流程
visualize_session(session_id, "mermaid")
```

---

## 参考文档

- [API 文档](./api.md) - 完整 API 参考
- [配置文档](./configuration.md) - 环境变量配置
- [架构文档](../ARCHITECTURE.md) - 系统架构设计
