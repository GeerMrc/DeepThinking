# DeepThinking MCP 开发规范

> 版本: 1.0
> 更新日期: 2026-01-01
> 目的: 防止技术债务积累，确保代码质量

---

## 1. MCP 工具注册规范

### 1.1 统一使用装饰器模式

**要求**: 所有 MCP 工具必须使用 `@app.tool()` 装饰器模式。

**正确示例** (`src/deep_thinking/tools/your_tool.py`):
```python
from deep_thinking.server import app, get_storage_manager

@app.tool(
    name="your_tool_name",
    description="工具功能描述",
)
def your_tool_function(
    param1: str,
    param2: int = 10,
) -> str:
    """
    工具功能描述

    Args:
        param1: 参数1说明
        param2: 参数2说明（可选）

    Returns:
        返回值说明
    """
    # 实现代码
    return "结果"

# 注册工具
__all__ = ["your_tool_function"]
```

**禁止模式** ❌:
```python
# 禁止使用 register 函数模式
def register_your_tools(app: FastMCP) -> None:
    @app.tool(...)
    def your_tool_function(...):
        ...
```

**理由**:
- 与项目中其他5个工具模块保持一致
- 导入时自动注册，无需额外调用
- 代码更简洁，可维护性更高

---

## 2. 开发前检查清单

### 2.1 新增工具模块时

- [ ] 确认使用 `@app.tool()` 装饰器
- [ ] 添加完整的类型注解
- [ ] 编写详细的 docstring
- [ ] 实现 `__all__` 导出列表
- [ ] 添加单元测试
- [ ] 添加集成测试

### 2.2 修改现有工具时

- [ ] 检查是否影响工具注册
- [ ] 更新相关测试用例
- [ ] 验证测试覆盖率
- [ ] 更新 API 文档

---

## 3. 测试要求

### 3.1 测试覆盖率

- **单元测试**: 覆盖率 > 80%
- **集成测试**: 必须验证工具可被正确调用
- **端到端测试**: 关键流程必须覆盖

### 3.2 集成测试模板

```python
# tests/test_integration/test_your_tool.py
import pytest
from deep_thinking import server
from deep_thinking.storage.storage_manager import StorageManager
from deep_thinking.tools import your_tool

@pytest.mark.asyncio
class TestYourToolIntegration:
    """你的工具集成测试"""

    @pytest.fixture
    async def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager
        yield manager
        server._storage_manager = None

    async def test_tool_functionality(self, storage_manager):
        """测试工具核心功能"""
        result = your_tool.your_function(...)
        assert "预期结果" in result

    async def test_tool_exports(self):
        """测试工具模块导出"""
        expected_exports = ["your_function"]
        for export in expected_exports:
            assert hasattr(your_tool, export)
```

---

## 4. 文档更新要求

### 4.1 代码变更时必须同步更新

- `docs/api.md` - API 接口文档
- `TASKS.md` - 任务状态文档
- `README.md` - 如有用户可见变更

### 4.2 技术债务记录

发现并修复技术债务时，必须在 `TASKS.md` 中记录：

```markdown
| YYYY-MM-DD | **技术债务修复（模块名）**: 问题描述和修复方案 | 负责人 |
```

---

## 5. 代码审查 Check List

### 5.1 提交前自查

```bash
# 1. 代码格式检查
ruff check src/

# 2. 类型检查
mypy src/

# 3. 运行测试
pytest tests/ -v

# 4. 检查测试覆盖率
pytest --cov --cov-report=term-missing
```

### 5.2 提交信息规范

```
type(scope): description

# 类型：
feat: 新功能
fix: 问题修复
docs: 文档更新
refactor: 代码重构
test: 测试相关
chore: 构建工具变动

# 示例：
fix(task_manager): 修复任务工具未注册问题
```

---

## 6. 禁止事项

### 6.1 严禁批量化操作

- 禁止同时修改多个文件而不逐一验证
- 禁止批量数据库操作而不进行事务控制
- 禁止跳过测试直接提交

### 6.2 严禁虚假完成

- 禁止标记任务为完成而实际未完成
- 禁止伪造测试结果
- 禁止简化测试绕过审核

---

## 7. 技术债务预防

### 7.1 定期审核

- 每周进行代码质量检查
- 每月进行技术债务盘点
- 每季度进行架构审核

### 7.2 技术债务分类

| 分类 | 描述 | 处理时限 |
|--------|------|----------|
| 阻塞性 | 影响核心功能，阻塞开发进度 | 立即修复 |
| 中等 | 影响可维护性，但无阻塞 | 3天内修复 |
| 轻微 | 优化项，不影响功能 | 1周内修复 |

---

## 8. 开发流程

### 8.1 规范开发流程

```
需求分析 → 技术调研 → 方案设计 → 任务拆解 → 代码实现
    ↑                                                      ↓
    └────────── 验证确认 ← 测试验证 ← 代码审查 ←──────┘
```

### 8.2 每个阶段的输出

1. **需求分析**: 需求文档，验收标准
2. **技术调研**: 技术选型报告，风险评估
3. **方案设计**: 架构设计，接口定义
4. **任务拆解**: TODO 清单，依赖关系
5. **代码实现**: 符合规范的代码
6. **代码审查**: 审查意见，修复记录
7. **测试验证**: 测试报告，覆盖率数据
8. **验证确认**: 验收通过，状态更新

---

## 9. 附录

### 9.1 相关文档

- `ARCHITECTURE.md` - 架构文档
- `docs/api.md` - API 文档
- `TASKS.md` - 任务追踪文档

### 9.2 工具参考

- FastMCP 文档
- Pydantic 文档
- pytest 文档

---

> 本文档基于 2026-01-01 技术债务修复经验制定，目的在于防止类似问题再次发生。
