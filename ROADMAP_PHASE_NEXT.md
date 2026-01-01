# Deep-Thinking-MCP 下一阶段开发任务

> 📅 制定日期: 2026-01-01
> 🎯 基于: autonomous-coding 项目深度分析
> 📊 分析会话: design-analysis (存储于 ~/.deep-thinking/sessions/)

---

## 📋 分析总结

### 核心发现

1. **思考步骤设计现状**
   - ✅ 无硬编码步数限制
   - ✅ 支持常规、修订、分支三种类型
   - ❌ 缺少任务分解能力
   - ❌ 无优先级和依赖关系概念
   - ❌ needsMoreThoughts 参数未实现

2. **存储架构问题**
   - 当前：全局存储 (~/.deep-thinking/)
   - 问题：多项目混淆、无法版本控制、团队协作困难
   - 建议：改为项目本地 (./.deep-thinking-mcp/)

3. **存储结构对比**
   - 当前方案：会话驱动（记录思考历史）
   - autonomous：任务驱动（定义开发计划）
   - 结论：不建议完全替换，建议混合方案

---

## 🎯 优化方案总览

### 方案 A: 项目本地存储（P0 - 立即实施）

**目标**：将存储位置从全局改为项目本地

**变更内容**：
```
当前: ~/.deep-thinking/sessions/{session_id}.json
改为: ./.deep-thinking-mcp/sessions/{session_id}.json
```

**优势**：
- ✅ 项目数据隔离
- ✅ 可纳入版本控制
- ✅ 团队协作友好
- ✅ 符合 autonomous-coding 模式

---

### 方案 B: 任务清单系统（P1 - 第二阶段）

**目标**：新增任务清单层，与现有会话系统配合

**架构设计**：
```
Layer 1: Task List (计划层)
├── task_list.json
└── 定义"要思考什么"

Layer 2: Session (记录层)
├── sessions/{session_id}.json
└── 记录"实际思考过程"
```

**关系**：一个 Task 可以对应多个 Session

---

### 方案 C: needsMoreThoughts 实现（P2 - 第三阶段）

**目标**：启用预留参数，支持动态增加思考步骤

**实现逻辑**：
```python
if needsMoreThoughts:
    additional = estimate_additional_thoughts()
    totalThoughts += additional
    return f"已增加 {additional} 个思考步骤，总计 {totalThoughts} 步"
```

---

### 方案 D: 自动会话恢复（P3 - 第四阶段）

**目标**：减少用户手动操作，智能推荐会话

**新增工具**：
- `get_or_resume_session()` - 获取或恢复最近会话
- `suggest_next_task()` - 基于任务清单推荐下一步

---

## 📦 阶段 7: 存储架构优化（P0）

### 任务 7.1: 修改默认存储目录

**文件**：`src/deep_thinking/__main__.py`

**变更内容**：
```python
# 当前
DEFAULT_STORAGE_DIR = Path.home() / ".deep-thinking"

# 改为
DEFAULT_STORAGE_DIR = Path.cwd() / ".deep-thinking-mcp"
```

**环境变量支持**：
```python
# 支持通过环境变量覆盖
storage_dir = Path(os.getenv(
    "DEEP_THINKING_STORAGE_DIR",
    DEFAULT_STORAGE_DIR
))
```

**预计工时**：1-2 小时

---

### 任务 7.2: 实现存储目录自动迁移

**文件**：`src/deep_thinking/storage/storage_manager.py`

**新增方法**：
```python
def migrate_old_data(old_dir: Path, new_dir: Path) -> None:
    """
    自动迁移旧数据到新位置

    Args:
        old_dir: 旧的存储目录
        new_dir: 新的存储目录
    """
    if not old_dir.exists():
        return

    # 迁移 sessions
    old_sessions = old_dir / "sessions"
    new_sessions = new_dir / "sessions"
    if old_sessions.exists():
        new_sessions.mkdir(parents=True, exist_ok=True)
        shutil.copytree(old_sessions, new_sessions, dirs_exist_ok=True)

    # 迁移 templates
    old_templates = old_dir / "templates"
    new_templates = new_dir / "templates"
    if old_templates.exists():
        new_templates.mkdir(parents=True, exist_ok=True)
        shutil.copytree(old_templates, new_templates, dirs_exist_ok=True)
```

**预计工时**：2-3 小时

---

### 任务 7.3: 更新文档和配置说明

**文件**：
- `docs/installation.md`
- `README.md`

**更新内容**：
1. 存储位置说明
2. 迁移指南
3. 环境变量配置

**预计工时**：1 小时

---

## 📦 阶段 8: 任务清单系统（P1）

### 任务 8.1: 创建 ThinkingTask 数据模型

**新建文件**：`src/deep_thinking/models/thinking_task.py`

**数据结构**：
```python
from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime

class ThinkingTask(BaseModel):
    """思考任务模型"""

    task_id: str = Field(..., description="任务唯一ID")
    description: str = Field(..., description="任务描述")
    category: Literal["analysis", "design", "solution", "review"] = Field(
        default="analysis", description="任务类别"
    )
    status: Literal["pending", "in_progress", "completed"] = Field(
        default="pending", description="任务状态"
    )
    priority: int = Field(default=5, ge=1, le=10, description="优先级 (1-10)")
    dependencies: list[str] = Field(
        default_factory=list, description="依赖的任务ID列表"
    )
    estimated_thoughts: int = Field(default=5, ge=1, description="预计思考步骤数")
    completed_thoughts: int = Field(default=0, ge=0, description="已完成步骤数")
    associated_session: str | None = Field(
        default=None, description="关联的会话ID"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def progress_percentage(self) -> float:
        """计算任务进度百分比"""
        if self.estimated_thoughts == 0:
            return 0.0
        return (self.completed_thoughts / self.estimated_thoughts) * 100

    @property
    def is_ready_to_start(self) -> bool:
        """检查任务是否可以开始（依赖已满足）"""
        return self.status == "pending"
```

**预计工时**：2 小时

---

### 任务 8.2: 实现 TaskListStore

**新建文件**：`src/deep_thinking/storage/task_list_store.py`

**核心方法**：
```python
class TaskListStore:
    """任务清单存储管理"""

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.task_list_file = storage_dir / "task_list.json"

    def create_task(self, task: ThinkingTask) -> ThinkingTask:
        """创建新任务"""

    def get_task(self, task_id: str) -> ThinkingTask | None:
        """获取任务"""

    def list_tasks(
        self, status: str | None = None
    ) -> list[ThinkingTask]:
        """列出任务"""

    def update_task(
        self, task_id: str, **updates
    ) -> ThinkingTask:
        """更新任务"""

    def get_next_task(self) -> ThinkingTask | None:
        """获取下一个待执行任务（优先级驱动）"""

    def delete_task(self, task_id: str) -> None:
        """删除任务"""
```

**预计工时**：3-4 小时

---

### 任务 8.3: 新增任务管理工具

**新建文件**：`src/deep_thinking/tools/task_manager.py`

**工具函数**：
```python
@app.tool()
def create_task(
    description: str,
    category: str = "analysis",
    priority: int = 5,
    estimated_thoughts: int = 5,
    dependencies: list[str] | None = None,
) -> str:
    """创建新的思考任务"""

@app.tool()
def get_next_task() -> str:
    """获取下一个待执行的任务"""

@app.tool()
def update_task_status(
    task_id: str,
    status: str,
) -> str:
    """更新任务状态"""

@app.tool()
def list_tasks(status: str | None = None) -> str:
    """列出所有任务"""
```

**预计工时**：3-4 小时

---

### 任务 8.4: 集成进度跟踪文件

**新建文件**：`src/deep_thinking/utils/progress_tracker.py`

**功能**：
```python
def update_progress_file(storage_dir: Path) -> None:
    """
    更新 thinking-progress.txt

    内容格式：
    ================
    思考进度追踪
    ================

    📊 总体进度
    - 总任务数: 10
    - 已完成: 3
    - 进行中: 2
    - 待开始: 5
    - 完成率: 30.0%

    📝 下一步建议
    1. [P10] 分析系统架构 (task-001)
    2. [P8] 评估技术方案 (task-003)

    📅 最近更新
    - 2026-01-01 12:30: 完成任务 task-002
    """
```

**预计工时**：2 小时

---

## 📦 阶段 9: 功能增强（P2）

### 任务 9.1: 实现 needsMoreThoughts 功能

**文件**：`src/deep_thinking/tools/sequential_thinking.py`

**变更内容**：
```python
@app.tool()
def sequential_thinking(
    thought: str,
    nextThoughtNeeded: bool,
    thoughtNumber: int,
    totalThoughts: int,
    needsMoreThoughts: bool = False,
    # ... 其他参数
) -> str:
    # 当 needsMoreThoughts=True 时
    if needsMoreThoughts:
        # 估算额外需要的步骤数（简单启发式）
        additional = max(3, totalThoughts // 4)
        totalThoughts += additional

        session.total_thoughts = totalThoughts
        session.save()

        return f"""...
⚠️ 注意：已增加 {additional} 个思考步骤
新的总计: {totalThoughts} 步
当前进度: {thoughtNumber}/{totalThoughts}
"""
```

**预计工时**：2-3 小时

---

### 任务 9.2: 新增自动会话恢复工具

**新建文件**：`src/deep_thinking/tools/session_recovery.py`

**工具函数**：
```python
@app.tool()
def get_or_resume_session() -> str:
    """
    获取或恢复最近活跃的会话

    Returns:
        会话信息，包含：
        - 最近修改的会话ID
        - 会话名称
        - 思考步骤数
        - 未完成内容摘要
    """
    manager = get_storage_manager()

    # 获取所有会话，按更新时间排序
    sessions = manager.list_sessions()
    if not sessions:
        return "❌ 没有找到任何会话，请先创建会话"

    # 找到最近修改的活跃会话
    recent_active = sorted(
        [s for s in sessions if s["status"] == "active"],
        key=lambda x: x["updated_at"],
        reverse=True
    )[0]

    session = manager.get_session(recent_active["session_id"])
    unfinished = [
        t for t in session.thoughts
        if t.content.endswith("继续下一步思考")
    ]

    return f"""## 📍 最近活跃会话

**会话ID**: {session.session_id}
**名称**: {session.name}
**状态**: {session.status}
**思考步骤**: {session.thought_count()} 步
**最后更新**: {session.updated_at}

**未完成内容**:
{chr(10).join(f"- {t.content[:50]}..." for t in unfinished[:3])}

💡 建议：使用 session_id="{session.session_id}" 继续思考
"""
```

**预计工时**：2-3 小时

---

### 任务 9.3: 增强可视化功能

**文件**：`src/deep_thinking/tools/visualization.py`

**新增功能**：
```python
@app.tool()
def visualize_tasks(format_type: str = "tree") -> str:
    """
    可视化任务清单

    支持格式：
    - tree: 树状结构（按优先级分组）
    - mermaid: Mermaid 流程图
    - timeline: 时间线视图
    """
```

**预计工时**：2-3 小时

---

## 📊 实施优先级和时间估算

### P0 - 存储架构优化（立即实施）
- 任务 7.1: 1-2h
- 任务 7.2: 2-3h
- 任务 7.3: 1h
- **小计**: 4-6h

### P1 - 任务清单系统（第二阶段）
- 任务 8.1: 2h
- 任务 8.2: 3-4h
- 任务 8.3: 3-4h
- 任务 8.4: 2h
- **小计**: 10-12h

### P2 - 功能增强（第三阶段）
- 任务 9.1: 2-3h
- 任务 9.2: 2-3h
- 任务 9.3: 2-3h
- **小计**: 6-9h

**总计**: 20-27 小时

---

## ⚠️ 实施注意事项

### 1. 向后兼容
- 保留全局存储模式（通过环境变量启用）
- 自动迁移旧数据
- 现有工具 API 不变

### 2. 测试要求
- 每个阶段完成后运行完整测试套件
- 测试覆盖率保持在 80% 以上
- 添加新功能的专项测试

### 3. 文档更新
- 及时更新 API 文档
- 更新用户指南
- 添加迁移指南

### 4. 渐进式发布
- 每个阶段独立提交
- 充分测试后再进入下一阶段
- 保留回滚方案

---

## 📚 参考资料

- autonomous-coding 项目分析: `autonomous-coding/PROJECT_ANALYSIS.md`
- 深度思考会话: `~/.deep-thinking/sessions/design-analysis.json`
- 深度思考会话: `~/.deep-thinking/sessions/autonomous-analysis.json`

---

## ✅ 检查清单

### 阶段 7 开始前
- [ ] 备份当前数据: `cp -r ~/.deep-thinking ~/.deep-thinking.backup`
- [ ] 创建测试分支: `git checkout -b feature/storage-optimization`
- [ ] 运行测试确保基准正常: `pytest`

### 阶段 7 完成后
- [ ] 所有测试通过: `pytest`
- [ ] 覆盖率 >= 80%: `pytest --cov`
- [ ] 手动测试存储迁移
- [ ] 文档已更新

### 阶段 8 开始前
- [ ] 阶段 7 已合并到主分支
- [ ] 创建新分支: `git checkout -b feature/task-list-system`

### 阶段 8 完成后
- [ ] 所有测试通过
- [ ] 新增工具已注册验证
- [ ] 集成测试通过
- [ ] API 文档已更新

---

> 📋 **文档版本**: 1.0
> 🎯 **适用项目**: Deep-Thinking-MCP
> 📅 **最后更新**: 2026-01-01
