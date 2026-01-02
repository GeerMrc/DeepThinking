# DeepThinking MCP 测试指南

> 版本: v0.2.0
> 更新时间: 2026-01-02

本文档提供DeepThinking MCP项目的完整测试指南，帮助验证所有功能正常工作。

---

## 快速开始

### 前置条件

1. **安装wheel包**：
   ```bash
   pip install dist/deepthinking-0.2.0-py3-none-any.whl --force-reinstall
   ```

2. **验证安装**：
   ```bash
   python -c "import deep_thinking; print(deep_thinking.__version__)"
   # 应输出: 0.2.0
   ```

3. **运行基础测试**：
   ```bash
   pytest tests/ -q
   # 应输出: 390 passed
   ```

---

## 一、六种思考类型测试

### 1.1 常规思考（Regular）💭

**测试方法**：
```python
from deep_thinking.tools import sequential_thinking

result = sequential_thinking.sequential_thinking(
    thought="这是第一个常规思考步骤",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=3,
    session_id="test-regular"
)

print(result)
```

**验证点**：
- [ ] 输出包含"常规思考 💭"
- [ ] 显示思考步骤编号（1/3）
- [ ] 会话已创建

### 1.2 修订思考（Revision）🔄

**测试方法**：
```python
# 先创建常规思考
sequential_thinking.sequential_thinking(
    thought="原始思考",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=3,
    session_id="test-revision"
)

# 创建修订思考
result = sequential_thinking.sequential_thinking(
    thought="这是修订后的思考",
    nextThoughtNeeded=False,
    thoughtNumber=2,
    totalThoughts=3,
    session_id="test-revision",
    isRevision=True,
    revisesThought=1
)

print(result)
```

**验证点**：
- [ ] 输出包含"修订思考 🔄"
- [ ] 显示"修订思考步骤 1"
- [ ] revises_thought字段正确

### 1.3 分支思考（Branch）🌿

**测试方法**：
```python
# 先创建主线思考
sequential_thinking.sequential_thinking(
    thought="主线思考",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=5,
    session_id="test-branch"
)

# 创建分支思考
result = sequential_thinking.sequential_thinking(
    thought="这是一个分支思考",
    nextThoughtNeeded=True,
    thoughtNumber=2,
    totalThoughts=5,
    session_id="test-branch",
    branchFromThought=1,
    branchId="branch-0-1"
)

print(result)
```

**验证点**：
- [ ] 输出包含"分支思考 🌿"
- [ ] 显示"从步骤 1 分支"
- [ ] branch_id字段正确

### 1.4 对比思考（Comparison）⚖️

**测试方法**：
```python
result = sequential_thinking.sequential_thinking(
    thought="比较三种数据库方案",
    nextThoughtNeeded=False,
    thoughtNumber=1,
    totalThoughts=3,
    session_id="test-comparison",
    comparisonItems=[
        "MySQL: 成熟稳定，社区活跃",
        "PostgreSQL: 功能丰富，扩展性强",
        "MongoDB: 灵活文档存储"
    ],
    comparisonDimensions=["性能", "可靠性", "成本"],
    comparisonResult="PostgreSQL在功能和扩展性上最优"
)

print(result)
```

**验证点**：
- [ ] 输出包含"对比思考 ⚖️"
- [ ] 显示比较项列表（3个）
- [ ] 显示比较维度和结论
- [ ] comparison_items字段正确

### 1.5 逆向思考（Reverse）🔙

**测试方法**：
```python
result = sequential_thinking.sequential_thinking(
    thought="反推微服务架构决策的前提条件",
    nextThoughtNeeded=False,
    thoughtNumber=3,
    totalThoughts=5,
    session_id="test-reverse",
    reverseFrom=2,
    reverseTarget="验证'采用微服务架构'结论的前提条件",
    reverseSteps=[
        "前提1: 团队规模超过20人",
        "前提2: 业务模块边界清晰",
        "验证结果: 前提3不成立"
    ]
)

print(result)
```

**验证点**：
- [ ] 输出包含"逆向思考 🔙"
- [ ] 显示反推起点和目标
- [ ] 显示反推步骤列表
- [ ] reverse_target字段正确

### 1.6 假设思考（Hypothetical）🤔

**测试方法**：
```python
result = sequential_thinking.sequential_thinking(
    thought="探索用户增长10倍的影响",
    nextThoughtNeeded=False,
    thoughtNumber=1,
    totalThoughts=2,
    session_id="test-hypothetical",
    hypotheticalCondition="如果用户数量从10万增长到100万",
    hypotheticalImpact="服务器负载增加10倍，需要：1.数据库分库分表 2.引入缓存层",
    hypotheticalProbability="可能性：高"
)

print(result)
```

**验证点**：
- [ ] 输出包含"假设思考 🤔"
- [ ] 显示假设条件、影响分析、可能性
- [ ] hypothetical_condition字段正确

---

## 二、会话管理功能测试

### 2.1 创建和查询会话

**测试方法**：
```python
from deep_thinking.tools import session_manager

# 创建会话
result = session_manager.create_session(
    name="测试会话",
    description="这是一个测试会话"
)
print(result)

# 获取会话
session_id = result.split("**会话ID**: ")[1].split("\n")[0].strip()
get_result = session_manager.get_session(session_id)
print(get_result)
```

**验证点**：
- [ ] 会话创建成功
- [ ] 会话ID格式正确（UUID）
- [ ] get_session返回完整信息

### 2.2 列出所有会话

**测试方法**：
```python
result = session_manager.list_sessions()
print(result)
```

**验证点**：
- [ ] 显示会话列表
- [ ] 包含会话数量统计

### 2.3 更新会话状态

**测试方法**：
```python
result = session_manager.update_session_status(
    session_id=session_id,
    status="completed"
)
print(result)
```

**验证点**：
- [ ] 状态更新成功
- [ ] 显示"会话状态已更新"

### 2.4 会话恢复

**测试方法**：
```python
result = session_manager.resume_session(
    session_id=session_id,
    total_thoughts=5
)
print(result)
```

**验证点**：
- [ ] 会话恢复成功
- [ ] 显示会话历史信息

---

## 三、任务管理功能测试

### 3.1 创建任务

**测试方法**：
```python
from deep_thinking.tools import task_manager

result = task_manager.create_task(
    title="测试任务",
    description="这是一个测试任务",
    priority="P1"
)
print(result)
```

**验证点**：
- [ ] 任务创建成功
- [ ] 任务ID格式正确（task-xxx）
- [ ] 优先级设置正确

### 3.2 列出任务

**测试方法**：
```python
result = task_manager.list_tasks()
print(result)
```

**验证点**：
- [ ] 显示任务列表
- [ ] 包含任务数量统计

### 3.3 更新任务状态

**测试方法**：
```python
task_id = result.split("ID: ")[1].split("\n")[0].strip()
update_result = task_manager.update_task_status(
    task_id=task_id,
    status="in_progress"
)
print(update_result)
```

**验证点**：
- [ ] 状态更新成功
- [ ] 显示"任务状态已更新"

### 3.4 获取下一个任务

**测试方法**：
```python
result = task_manager.get_next_task()
print(result)
```

**验证点**：
- [ ] 返回优先级最高的待执行任务
- [ ] P0 > P1 > P2 优先级正确

### 3.5 关联任务与会话

**测试方法**：
```python
link_result = task_manager.link_task_session(
    task_id=task_id,
    session_id=session_id
)
print(link_result)
```

**验证点**：
- [ ] 关联成功
- [ ] 显示"任务已关联到思考会话"

---

## 四、导出功能测试

### 4.1 JSON格式导出

**测试方法**：
```python
from deep_thinking.tools import export
import tempfile
import os

with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
    temp_path = f.name

result = export.export_session(
    session_id=session_id,
    format="json",
    output_path=temp_path
)

print(result)
print(f"\n文件内容:\n{open(temp_path).read()}")
os.unlink(temp_path)
```

**验证点**：
- [ ] 导出成功
- [ ] JSON格式正确
- [ ] 包含所有思考步骤

### 4.2 Markdown格式导出

**测试方法**：
```python
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
    temp_path = f.name

result = export.export_session(
    session_id=session_id,
    format="markdown",
    output_path=temp_path
)

print(result)
print(f"\n文件内容:\n{open(temp_path).read()}")
os.unlink(temp_path)
```

**验证点**：
- [ ] Markdown格式正确
- [ ] 标题层级正确
- [ ] 思考类型符号显示

### 4.3 HTML格式导出

**测试方法**：
```python
with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
    temp_path = f.name

result = export.export_session(
    session_id=session_id,
    format="html",
    output_path=temp_path
)

print(result)
os.unlink(temp_path)
```

**验证点**：
- [ ] HTML结构完整
- [ ] 样式正确应用

### 4.4 Text格式导出

**测试方法**：
```python
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
    temp_path = f.name

result = export.export_session(
    session_id=session_id,
    format="text",
    output_path=temp_path
)

print(result)
print(f"\n文件内容:\n{open(temp_path).read()}")
os.unlink(temp_path)
```

**验证点**：
- [ ] 纯文本格式正确
- [ ] 易于阅读

---

## 五、可视化功能测试

### 5.1 Mermaid流程图

**测试方法**：
```python
from deep_thinking.tools import visualization

result = visualization.visualize_session(
    session_id=session_id,
    format="mermaid"
)

print(result)
```

**验证点**：
- [ ] Mermaid语法正确
- [ ] 显示思考步骤节点
- [ ] 显示类型关系（revision/branch）

### 5.2 ASCII流程图

**测试方法**：
```python
result = visualization.visualize_session(
    session_id=session_id,
    format="ascii"
)

print(result)
```

**验证点**：
- [ ] ASCII图正确显示
- [ ] 树状结构清晰
- [ ] 思考类型符号显示

---

## 六、配置参数测试

### 6.1 环境变量配置

**测试方法**：
```bash
export DEEP_THINKING_MAX_THOUGHTS=100
export DEEP_THINKING_MIN_THOUGHTS=5
export DEEP_THINKING_THOUGHTS_INCREMENT=20

python -c "
from deep_thinking.models.config import get_global_config
config = get_global_config()
print(f'Max: {config.max_thoughts}')
print(f'Min: {config.min_thoughts}')
print(f'Increment: {config.thoughts_increment}')
"
```

**验证点**：
- [ ] 环境变量正确读取
- [ ] 配置值正确应用

### 6.2 needsMoreThoughts功能

**测试方法**：
```python
# 第一次思考，请求增加步骤
result1 = sequential_thinking.sequential_thinking(
    thought="需要更多思考",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=3,
    session_id="test-needs-more",
    needsMoreThoughts=True
)

print(result1)

# 第二次思考，验证总数已增加
result2 = sequential_thinking.sequential_thinking(
    thought="继续思考",
    nextThoughtNeeded=False,
    thoughtNumber=2,
    totalThoughts=3,
    session_id="test-needs-more"
)

print(result2)
```

**验证点**：
- [ ] 第一次调用显示"思考步骤总数已调整: 3 → 13"
- [ ] 第二次调用使用新的总数

---

## 七、SSE认证测试

### 7.1 Bearer Token认证

**启动SSE服务器**：
```bash
python -m deep_thinking --transport sse --auth-token test-token-123 &
```

**测试认证**：
```bash
# 无token - 应该返回401
curl -H "Authorization: Bearer invalid" http://localhost:8000/sse

# 正确token - 应该返回200
curl -H "Authorization: Bearer test-token-123" http://localhost:8000/sse
```

**验证点**：
- [ ] 无token请求被拒绝
- [ ] 正确token请求成功

### 7.2 API Key认证

**启动SSE服务器**：
```bash
python -m deep_thinking --transport sse --api-key test-api-key &
```

**测试认证**：
```bash
# 无API key - 应该返回401
curl http://localhost:8000/sse

# 正确API key - 应该返回200
curl -H "x-api-key: test-api-key" http://localhost:8000/sse
```

**验证点**：
- [ ] 无API key请求被拒绝
- [ ] 正确API key请求成功

---

## 八、完整测试套件

### 8.1 运行所有测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=src/deep_thinking --cov-report=html

# 只运行集成测试
pytest tests/test_integration/

# 只运行特定测试
pytest tests/test_models/test_thought.py::TestThoughtComparison
```

### 8.2 代码质量检查

```bash
# Mypy类型检查
mypy src/deep_thinking/

# Ruff代码检查
ruff check src/deep_thinking/

# Ruff格式化检查
ruff format --check src/deep_thinking/
```

---

## 九、问题排查

### 问题1：测试失败

**可能原因**：
- 环境变量未设置
- 依赖包版本冲突
- 旧版本残留

**解决方法**：
```bash
# 清理并重新安装
pip uninstall DeepThinking -y
pip install dist/deepthinking-0.2.0-py3-none-any.whl --force-reinstall

# 清理旧数据
rm -rf .deepthinking/
```

### 问题2：导入错误

**可能原因**：
- Python版本不兼容（需要>=3.10）
- 虚拟环境未激活

**解决方法**：
```bash
# 检查Python版本
python --version

# 激活虚拟环境
source venv/bin/activate
```

### 问题3：SSE连接失败

**可能原因**：
- 端口被占用
- 防火墙阻止

**解决方法**：
```bash
# 检查端口占用
lsof -i :8000

# 使用其他端口
python -m deep_thinking --transport sse --port 8001
```

---

## 十、测试检查清单

### 功能测试

- [ ] 六种思考类型（常规/修订/分支/对比/逆向/假设）
- [ ] 会话管理（创建/查询/列表/更新/删除/恢复）
- [ ] 任务管理（创建/列表/更新/获取下一个/关联/统计）
- [ ] 导出功能（JSON/Markdown/HTML/Text）
- [ ] 可视化功能（Mermaid/ASCII）
- [ ] 配置参数（max/min/increment）
- [ ] needsMoreThoughts功能
- [ ] SSE认证（Bearer Token/API Key）

### 质量测试

- [ ] 单元测试：390/390 通过
- [ ] 代码覆盖率：>86%
- [ ] mypy检查：0错误
- [ ] ruff检查：All checks passed

### 文档测试

- [ ] README.md完整
- [ ] API文档准确
- [ ] 用户指南清晰
- [ ] 配置示例可用

---

## 附录：快速测试脚本

创建文件 `quick_test.py`：

```python
#!/usr/bin/env python3
"""快速功能测试脚本"""

from deep_thinking.tools import sequential_thinking, session_manager, task_manager

print("=== DeepThinking MCP v0.2.0 快速测试 ===\n")

# 1. 测试常规思考
print("1. 测试常规思考...")
result = sequential_thinking.sequential_thinking(
    thought="这是一个快速测试",
    nextThoughtNeeded=False,
    thoughtNumber=1,
    totalThoughts=1
)
assert "常规思考" in result
print("✅ 常规思考通过\n")

# 2. 测试对比思考
print("2. 测试对比思考...")
result = sequential_thinking.sequential_thinking(
    thought="比较方案A和方案B",
    nextThoughtNeeded=False,
    thoughtNumber=1,
    totalThoughts=1,
    comparisonItems=["方案A: 成本低", "方案B: 性能好"]
)
assert "对比思考" in result
print("✅ 对比思考通过\n")

# 3. 测试会话管理
print("3. 测试会话管理...")
result = session_manager.create_session(name="快速测试会话")
assert "会话已创建" in result
print("✅ 会话管理通过\n")

# 4. 测试任务管理
print("4. 测试任务管理...")
result = task_manager.create_task(title="快速测试任务")
assert "任务已创建" in result
print("✅ 任务管理通过\n")

print("=== 所有快速测试通过！===")
```

**运行快速测试**：
```bash
python quick_test.py
```

---

**文档结束**

如有问题，请查阅：
- [API文档](docs/api.md)
- [用户指南](docs/user_guide.md)
- [安装指南](docs/installation.md)
