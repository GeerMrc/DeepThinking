# DeepThinking MCP CLI对话测试指南

> 版本: v0.2.2
> 更新时间: 2026-01-03
> 测试环境: Claude Code CLI

本文档提供在Claude Code CLI环境中，通过对话交互测试DeepThinking MCP所有功能的完整指南。

---

## 快速开始

### 前置条件

1. **MCP服务器已配置**：
   在Claude Code配置文件中已添加DeepThinking MCP服务器

2. **工具可用性检查**：
   > 在Claude Code CLI中输入：
   > "请列出所有可用的MCP工具"

   预期AI应列出DeepThinking相关工具：
   - `sequential_thinking_sequential_thinking` - 顺序思考
   - `create_session` - 创建会话
   - `get_session` - 获取会话
   - `list_sessions` - 列出会话
   - `update_session_status` - 更新会话状态
   - `resume_session` - 恢复会话
   - `create_task` - 创建任务
   - `list_tasks` - 列出任务
   - `update_task_status` - 更新任务状态
   - `get_next_task` - 获取下一个任务
   - `link_task_session` - 关联任务和会话
   - `task_statistics` - 任务统计
   - `export_session` - 导出会话
   - `visualize_session` - 可视化会话

---

## 一、六种思考类型对话测试

### 1.1 常规思考（Regular）💭

**测试目的**: 验证AI能使用 DeepThinking MCP 的 sequential_thinking 工具进行常规思考

**对话提示词**:
> "使用 DeepThinking MCP 的 sequential_thinking 工具，分析Python中列表和元组的区别。请进行3步思考。"

**预期AI行为**:
- AI调用 `sequential_thinking_sequential_thinking` 工具
- 参数包含:
  - `thought`: 思考内容
  - `thoughtNumber`: 1
  - `totalThoughts`: 3
  - `nextThoughtNeeded`: true

**通过标准**:
- [ ] AI正确调用了 DeepThinking MCP 的 sequential_thinking 工具
- [ ] 返回结果显示"常规思考 💭"
- [ ] 显示思考步骤编号（如"步骤 1/3"）
- [ ] 思考内容与列表和元组相关

---

### 1.2 修订思考（Revision）🔄

**测试目的**: 验证AI能对之前的思考进行修订

**对话提示词**:
> "使用 DeepThinking MCP 的 sequential_thinking 工具进行思考。第一步：假设MySQL是最优数据库选择。第二步：修订你的第一步思考，考虑PostgreSQL可能在ACID合规性上更好。"

**预期AI行为**:
- 第一步调用: 常规思考
- 第二步调用:
  - `isRevision`: true
  - `revisesThought`: 1
  - `thought`: 修订后的思考内容

**通过标准**:
- [ ] 第二次调用显示"修订思考 🔄"
- [ ] 显示"修订思考步骤 1"
- [ ] 内容体现对第一步的修订

---

### 1.3 分支思考（Branch）🌿

**测试目的**: 验证AI能创建分支思考路径

**对话提示词**:
> "使用 DeepThinking MCP 的 sequential_thinking 工具分析微服务架构。第一步：分析优势。第二步：从第一步分支，专门分析数据一致性的挑战。"

**预期AI行为**:
- 第一步调用: 常规思考
- 第二步调用:
  - `branchFromThought`: 1
  - `branchId`: 如"branch-0-1"
  - `thought`: 分支思考内容

**通过标准**:
- [ ] 第二次调用显示"分支思考 🌿"
- [ ] 显示"从步骤 1 分支"
- [ ] 内容聚焦于数据一致性挑战

---

### 1.4 对比思考（Comparison）⚖️

**测试目的**: 验证AI能进行多方案对比分析

**对话提示词**:
> "使用 DeepThinking MCP 的 sequential_thinking 工具，对比React、Vue、Angular三个前端框架在性能、学习曲线、生态系统三个维度的优劣。请提供comparisonItems参数列出对比项，comparisonDimensions参数列出比较维度。"

**预期AI行为**:
- 调用 DeepThinking MCP 的 sequential_thinking 工具
- 参数包含:
  - `comparisonItems`: ["React: 社区大生态成熟", "Vue: 学习曲线平缓", "Angular: 企业级框架"]
  - `comparisonDimensions`: ["性能", "学习曲线", "生态系统"]
  - `comparisonResult`: 对比结论
- **注意**: 无需传递type参数，系统会根据comparisonItems自动识别为对比思考

**通过标准**:
- [ ] 显示"对比思考 ⚖️"
- [ ] 列出3个对比项
- [ ] 显示3个比较维度
- [ ] 给出对比结论

---

### 1.5 逆向思考（Reverse）🔙

**测试目的**: 验证AI能反向推理验证结论

**对话提示词**:
> "使用 DeepThinking MCP 的 sequential_thinking 工具的逆向思考功能。你已经得出结论'应该采用微服务架构'，现在请反推验证这个结论的前提条件是否成立。请提供reverseTarget参数描述反推目标，reverseSteps参数列出验证步骤。"

**预期AI行为**:
- 调用 DeepThinking MCP 的 sequential_thinking 工具
- 参数包含:
  - `reverseTarget`: "验证'采用微服务架构'结论的前提条件"
  - `reverseSteps`: ["团队规模>20人", "业务模块边界清晰", "技术储备充足"]
  - `reverseFrom`: (可选) 反推起点的思考编号
- **注意**: 无需传递type参数，系统会根据reverseTarget自动识别为逆向思考

**通过标准**:
- [ ] 显示"逆向思考 🔙"
- [ ] 显示反推目标
- [ ] 列出多个前提条件
- [ ] 验证每个前提是否成立

---

### 1.6 假设思考（Hypothetical）🤔

**测试目的**: 验证AI能进行假设性分析

**对话提示词**:
> "使用 DeepThinking MCP 的 sequential_thinking 工具的假设思考功能。假设用户数量从10万增长到100万，分析这对服务器架构的影响。请提供hypotheticalCondition参数描述假设条件，hypotheticalImpact参数分析影响。"

**预期AI行为**:
- 调用 DeepThinking MCP 的 sequential_thinking 工具
- 参数包含:
  - `hypotheticalCondition`: "如果用户数量从10万增长到100万"
  - `hypotheticalImpact`: "服务器负载增加10倍，需要：1.数据库分库分表 2.引入缓存层"
  - `hypotheticalProbability`: "可能性：高"
- **注意**: 无需传递type参数，系统会根据hypotheticalCondition自动识别为假设思考

**通过标准**:
- [ ] 显示"假设思考 🤔"
- [ ] 明确描述假设条件
- [ ] 分析具体影响
- [ ] 评估可能性

---

## 二、会话管理功能对话测试

### 2.1 创建会话

**对话提示词**:
> "创建一个新的思考会话，名称为'架构设计讨论'，描述为'设计电商系统架构'。"

**预期AI行为**:
- 调用 `create_session` 工具
- 参数:
  - `name`: "架构设计讨论"
  - `description`: "设计电商系统架构"

**通过标准**:
- [ ] 返回"会话已创建"
- [ ] 显示会话ID（UUID格式）
- [ ] 显示会话名称和描述

---

### 2.2 查询会话

**对话提示词**:
> "获取会话ID为[上一步创建的会话ID]的详细信息。"

**预期AI行为**:
- 调用 `get_session` 工具
- 参数: `session_id`: [会话ID]

**通过标准**:
- [ ] 返回完整会话信息
- [ ] 包含会话ID、名称、描述
- [ ] 包含思考步骤列表

---

### 2.3 列出所有会话

**对话提示词**:
> "列出所有思考会话。"

**预期AI行为**:
- 调用 `list_sessions` 工具

**通过标准**:
- [ ] 显示会话列表
- [ ] 包含会话数量统计
- [ ] 每个会话显示基本信息

---

### 2.4 更新会话状态

**对话提示词**:
> "将会话[会话ID]的状态更新为'已完成'。"

**预期AI行为**:
- 调用 `update_session_status` 工具
- 参数:
  - `session_id`: [会话ID]
  - `status`: "completed"

**通过标准**:
- [ ] 返回"会话状态已更新"
- [ ] 显示新状态为"completed"

---

### 2.5 恢复会话

**对话提示词**:
> "恢复会话[会话ID]，总共需要5个思考步骤。"

**预期AI行为**:
- 调用 `resume_session` 工具
- 参数:
  - `session_id`: [会话ID]
  - `total_thoughts`: 5

**通过标准**:
- [ ] 返回会话历史信息
- [ ] 显示之前的思考步骤
- [ ] 提示可以继续思考

---

## 三、任务管理功能对话测试

### 3.1 创建任务

**对话提示词**:
> "创建一个新任务，标题是'设计数据库Schema'，优先级为P1，描述是'设计用户和订单表结构'。"

**预期AI行为**:
- 调用 `create_task` 工具
- 参数:
  - `title`: "设计数据库Schema"
  - `priority`: "P1"
  - `description`: "设计用户和订单表结构"

**通过标准**:
- [ ] 返回"任务已创建"
- [ ] 显示任务ID（格式：task-xxx）
- [ ] 显示优先级P1

---

### 3.2 列出任务

**对话提示词**:
> "列出所有任务。"

**预期AI行为**:
- 调用 `list_tasks` 工具

**通过标准**:
- [ ] 显示任务列表
- [ ] 包含任务数量统计
- [ ] 显示每个任务的基本信息

---

### 3.3 更新任务状态

**对话提示词**:
> "将任务[任务ID]的状态更新为'in_progress'。"

**预期AI行为**:
- 调用 `update_task_status` 工具
- 参数:
  - `task_id`: [任务ID]
  - `status`: "in_progress"

**通过标准**:
- [ ] 返回"任务状态已更新"
- [ ] 显示新状态

---

### 3.4 获取下一个任务

**对话提示词**:
> "获取下一个待执行的任务。"

**预期AI行为**:
- 调用 `get_next_task` 工具

**通过标准**:
- [ ] 返回优先级最高的待执行任务
- [ ] P0 > P1 > P2优先级顺序正确

---

### 3.5 关联任务与会话

**对话提示词**:
> "将任务[任务ID]关联到会话[会话ID]。"

**预期AI行为**:
- 调用 `link_task_session` 工具
- 参数:
  - `task_id`: [任务ID]
  - `session_id`: [会话ID]

**通过标准**:
- [ ] 返回"任务已关联到思考会话"
- [ ] 显示关联的会话ID

---

### 3.6 任务统计

**对话提示词**:
> "显示任务统计信息。"

**预期AI行为**:
- 调用 `task_statistics` 工具

**通过标准**:
- [ ] 显示各状态任务数量
- [ ] 显示各优先级任务数量
- [ ] 显示完成率等统计指标

---

## 四、导出功能对话测试

### 4.1 JSON格式导出

**对话提示词**:
> "将会话[会话ID]导出为JSON格式，保存到exports/session.json。"

**预期AI行为**:
- 调用 `export_session` 工具
- 参数:
  - `session_id`: [会话ID]
  - `format`: "json"
  - `output_path`: "exports/session.json"

**通过标准**:
- [ ] 返回"会话已导出"
- [ ] 显示文件路径
- [ ] JSON格式正确

---

### 4.2 Markdown格式导出

**对话提示词**:
> "将会话[会话ID]导出为Markdown格式，保存到exports/session.md。"

**预期AI行为**:
- 调用 `export_session` 工具
- 参数:
  - `session_id`: [会话ID]
  - `format`: "markdown"
  - `output_path`: "exports/session.md"

**通过标准**:
- [ ] Markdown格式正确
- [ ] 标题层级正确
- [ ] 思考类型符号显示（💭/🔄/🌿/⚖️/🔙/🤔）

---

### 4.3 HTML格式导出

**对话提示词**:
> "将会话[会话ID]导出为HTML格式，保存到exports/session.html。"

**预期AI行为**:
- 调用 `export_session` 工具
- 参数:
  - `format`: "html"
  - `output_path`: "exports/session.html"

**通过标准**:
- [ ] HTML结构完整
- [ ] 包含样式
- [ ] 可在浏览器中打开

---

### 4.4 Text格式导出

**对话提示词**:
> "将会话[会话ID]导出为纯文本格式，保存到exports/session.txt。"

**预期AI行为**:
- 调用 `export_session` 工具
- 参数:
  - `format`: "text"
  - `output_path`: "exports/session.txt"

**通过标准**:
- [ ] 纯文本格式正确
- [ ] 易于阅读

---

## 五、可视化功能对话测试

### 5.1 Mermaid流程图

**对话提示词**:
> "将会话[会话ID]可视化为Mermaid流程图。"

**预期AI行为**:
- 调用 `visualize_session` 工具
- 参数:
  - `session_id`: [会话ID]
  - `format`: "mermaid"

**通过标准**:
- [ ] 返回Mermaid语法
- [ ] 显示思考步骤节点
- [ ] 显示类型关系（revision/branch）

---

### 5.2 ASCII流程图

**对话提示词**:
> "将会话[会话ID]可视化为ASCII流程图。"

**预期AI行为**:
- 调用 `visualize_session` 工具
- 参数:
  - `format`: "ascii"

**通过标准**:
- [ ] ASCII图正确显示
- [ ] 树状结构清晰
- [ ] 思考类型符号显示

---

## 六、综合场景测试

### 6.1 完整思考流程

**对话提示词**:
> "请帮我完成一个完整的思考流程：1.创建一个名为'技术选型'的会话；2.使用 DeepThinking MCP 的 sequential_thinking 工具分析选择PostgreSQL还是MySQL；3.考虑修订你的分析；4.最后将会话导出为Markdown格式。"

**预期AI行为**:
1. 调用 `create_session`
2. 调用 DeepThinking MCP 的 `sequential_thinking`（常规思考）
3. 调用 DeepThinking MCP 的 `sequential_thinking`（修订思考）
4. 调用 `export_session`

**通过标准**:
- [ ] 4个工具按顺序调用
- [ ] 每个工具参数正确
- [ ] 最终生成Markdown文件

---

### 6.2 任务驱动思考

**对话提示词**:
> "创建一个P1任务'设计API接口'，然后创建一个思考会话来完成这个任务，将任务和会话关联，最后将思考过程导出。"

**预期AI行为**:
1. 调用 `create_task`
2. 调用 `create_session`
3. 调用 DeepThinking MCP 的 `sequential_thinking`（一次或多次）
4. 调用 `link_task_session`
5. 调用 `export_session`

**通过标准**:
- [ ] 任务创建成功
- [ ] 会话创建成功
- [ ] 思考过程记录
- [ ] 关联成功
- [ ] 导出成功

---

## 七、快速验证清单

### 7.1 功能覆盖检查

使用以下对话一次性验证所有功能：

> "请帮我完成以下测试：
> 1. 列出所有可用的DeepThinking工具
> 2. 创建一个测试会话
> 3. 使用6种思考类型各进行一次思考（常规/修订/分支/对比/逆向/假设）
> 4. 创建一个测试任务并关联到会话
> 5. 将会话导出为JSON和Markdown格式
> 6. 生成Mermaid可视化
> 7. 显示任务统计"

**验证清单**:
- [ ] 列出工具（13个工具）
- [ ] 常规思考 💭
- [ ] 修订思考 🔄
- [ ] 分支思考 🌿
- [ ] 对比思考 ⚖️
- [ ] 逆向思考 🔙
- [ ] 假设思考 🤔
- [ ] 任务创建和关联
- [ ] JSON导出
- [ ] Markdown导出
- [ ] Mermaid可视化
- [ ] 任务统计

---

### 7.2 问题排查

**AI未调用工具**:
- 检查MCP服务器配置
- 确认服务器已启动
- 查看Claude Code日志

**工具调用失败**:
- 检查参数格式是否正确
- 查看错误信息
- 确认会话/任务ID有效

**导出文件未生成**:
- 确认目录路径存在
- 检查文件写入权限

---

## 八、测试完成标准

全部通过以下检查即表示DeepThinking MCP功能完整可用：

### 核心功能
- [ ] 6种思考类型都能被AI正确调用
- [ ] 会话管理（5个操作）正常工作
- [ ] 任务管理（6个操作）正常工作
- [ ] 导出功能（4种格式）正常工作
- [ ] 可视化功能（2种格式）正常工作

### AI交互
- [ ] AI能理解工具用途
- [ ] AI能正确传递参数
- [ ] AI能处理返回结果
- [ ] AI能根据上下文连续调用工具

---

**测试提示**: 建议按顺序执行测试，每个功能独立验证后再进行综合场景测试。遇到问题时记录具体的对话内容、AI行为和错误信息，便于排查问题。
