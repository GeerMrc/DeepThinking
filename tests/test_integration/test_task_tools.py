"""
集成测试 - 任务管理工具

测试所有任务管理MCP工具的功能。
"""

import pytest

from deep_thinking import server
from deep_thinking.storage.storage_manager import StorageManager
from deep_thinking.tools import task_manager


@pytest.mark.asyncio(loop_scope="class")
class TestTaskManagerIntegration:
    """任务管理工具集成测试"""

    @pytest.fixture
    async def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager

        yield manager

        server._storage_manager = None

    async def test_create_and_get_task(self, storage_manager):
        """测试创建和获取任务"""
        result = task_manager.create_task(
            title="测试任务",
            description="这是一个测试任务",
        )

        assert "任务已创建" in result
        assert "测试任务" in result

        # 提取任务ID
        import re

        task_id = re.search(r"ID: (task-[a-f0-9]+)", result)
        assert task_id is not None
        task_id = task_id.group(1)

    async def test_list_tasks(self, storage_manager):
        """测试列出任务"""
        # 创建多个任务
        task_manager.create_task(title="任务1")
        task_manager.create_task(title="任务2")
        task_manager.create_task(title="任务3")

        # 列出所有任务
        result = task_manager.list_tasks()
        assert "任务列表" in result
        assert "任务1" in result
        assert "任务2" in result
        assert "任务3" in result
        assert "共3个任务" in result

    async def test_list_tasks_with_status_filter(self, storage_manager):
        """测试按状态过滤任务"""
        # 创建任务
        task_manager.create_task(title="待执行任务")
        r2 = task_manager.create_task(title="进行中任务")

        # 提取任务ID
        import re

        task_id2 = re.search(r"ID: (task-[a-f0-9]+)", r2).group(1)

        # 更新第二个任务状态
        task_manager.update_task_status(task_id2, "in_progress")

        # 按状态过滤
        pending_result = task_manager.list_tasks(status="pending")
        assert "待执行任务" in pending_result
        assert "进行中任务" not in pending_result

        in_progress_result = task_manager.list_tasks(status="in_progress")
        assert "进行中任务" in in_progress_result
        assert "待执行任务" not in in_progress_result

    async def test_update_task_status(self, storage_manager):
        """测试更新任务状态"""
        # 创建任务
        result = task_manager.create_task(title="状态测试任务")
        import re

        task_id = re.search(r"ID: (task-[a-f0-9]+)", result).group(1)

        # 更新状态
        update_result = task_manager.update_task_status(task_id, "in_progress")
        assert "任务状态已更新" in update_result
        assert "in_progress" in update_result

    async def test_get_next_task(self, storage_manager):
        """测试获取下一个待执行任务"""
        # 创建多个任务
        task_manager.create_task(title="任务1")
        task_manager.create_task(title="任务2")
        task_manager.create_task(title="任务3")

        # 获取下一个任务
        result = task_manager.get_next_task()
        assert "下一个待执行任务" in result

    async def test_get_task_stats(self, storage_manager):
        """测试获取任务统计"""
        # 创建多个任务
        task_manager.create_task(title="任务1")
        task_manager.create_task(title="任务2")

        # 获取统计信息
        result = task_manager.get_task_stats()
        assert "任务统计" in result
        assert "总任务数: 2" in result

    async def test_link_task_session(self, storage_manager):
        """测试关联任务与会话"""
        # 创建任务
        task_result = task_manager.create_task(title="需要会话的任务")
        import re

        task_id = re.search(r"ID: (task-[a-f0-9]+)", task_result).group(1)

        # 创建会话
        from deep_thinking.tools import session_manager

        session_result = session_manager.create_session(name="测试会话")
        session_id = re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", session_result).group(1)

        # 关联任务与会话
        link_result = task_manager.link_task_session(task_id, session_id)
        assert "任务已关联到思考会话" in link_result
        assert task_id in link_result
        assert session_id in link_result

    async def test_update_nonexistent_task(self, storage_manager):
        """测试更新不存在的任务"""
        result = task_manager.update_task_status("nonexistent-task", "in_progress")
        assert "错误" in result
        assert "不存在" in result

    async def test_get_next_task_no_pending(self, storage_manager):
        """测试没有待执行任务"""
        # 创建一个已完成任务
        result = task_manager.create_task(title="已完成任务")
        import re

        task_id = re.search(r"ID: (task-[a-f0-9]+)", result).group(1)
        task_manager.update_task_status(task_id, "completed")

        # 获取下一个任务
        result = task_manager.get_next_task()
        assert "没有待执行的任务" in result

    async def test_task_manager_module_exports(self):
        """测试：task_manager 模块导出正确"""
        expected_exports = [
            "create_task",
            "list_tasks",
            "update_task_status",
            "get_next_task",
            "link_task_session",
            "get_task_stats",
        ]
        for export in expected_exports:
            assert hasattr(task_manager, export), f"task_manager 模块缺少导出: {export}"

    async def test_task_tools_consistency(self):
        """测试：任务工具与其他模块一致（使用装饰器模式）"""
        # 验证task_manager使用装饰器模式
        assert hasattr(task_manager, "create_task")
        assert callable(task_manager.create_task)
        # 确保没有register_task_tools函数（已重构）
        assert not hasattr(task_manager, "register_task_tools")
