"""
任务列表存储管理器单元测试
"""

from pathlib import Path

import pytest

from deep_thinking.models.task import TaskStatus, ThinkingTask
from deep_thinking.storage.task_list_store import TaskListStore


@pytest.fixture
def temp_task_store(tmp_path: Path):
    """创建临时任务存储管理器"""
    store = TaskListStore(tmp_path)
    yield store
    # 清理
    import shutil

    if tmp_path.exists():
        shutil.rmtree(tmp_path)


class TestTaskListStore:
    """测试任务列表存储管理器"""

    def test_create_task(self, temp_task_store: TaskListStore):
        """测试：创建任务"""
        task = temp_task_store.create_task(
            title="Test Task",
            description="Test Description",
        )

        assert task.task_id.startswith("task-")
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.status == TaskStatus.PENDING

    def test_create_task_with_id(self, temp_task_store: TaskListStore):
        """测试：使用指定ID创建任务"""
        task = temp_task_store.create_task(
            title="Custom ID Task",
            task_id="custom-123",
        )

        assert task.task_id == "custom-123"

    def test_get_task(self, temp_task_store: TaskListStore):
        """测试：获取任务"""
        created = temp_task_store.create_task(title="Get Test")

        retrieved = temp_task_store.get_task(created.task_id)

        assert retrieved is not None
        assert retrieved.task_id == created.task_id
        assert retrieved.title == "Get Test"

    def test_get_task_not_found(self, temp_task_store: TaskListStore):
        """测试：获取不存在的任务"""
        task = temp_task_store.get_task("nonexistent")
        assert task is None

    def test_update_task(self, temp_task_store: TaskListStore):
        """测试：更新任务"""
        task = temp_task_store.create_task(title="Update Test")

        task.update_status(TaskStatus.IN_PROGRESS)
        success = temp_task_store.update_task(task)

        assert success is True

        retrieved = temp_task_store.get_task(task.task_id)
        assert retrieved.status == TaskStatus.IN_PROGRESS

    def test_update_task_not_exists(self, temp_task_store: TaskListStore):
        """测试：更新不存在的任务"""
        task = ThinkingTask(task_id="fake", title="Fake")

        success = temp_task_store.update_task(task)
        assert success is False

    def test_delete_task(self, temp_task_store: TaskListStore):
        """测试：删除任务"""
        task = temp_task_store.create_task(title="Delete Test")

        success = temp_task_store.delete_task(task.task_id)

        assert success is True
        assert temp_task_store.get_task(task.task_id) is None

    def test_delete_task_not_exists(self, temp_task_store: TaskListStore):
        """测试：删除不存在的任务"""
        success = temp_task_store.delete_task("nonexistent")
        assert success is False

    def test_exists(self, temp_task_store: TaskListStore):
        """测试：检查任务是否存在"""
        task = temp_task_store.create_task(title="Exists Test")

        assert temp_task_store.exists(task.task_id) is True
        assert temp_task_store.exists("nonexistent") is False

    def test_list_tasks_empty(self, temp_task_store: TaskListStore):
        """测试：列出空任务列表"""
        tasks = temp_task_store.list_tasks()
        assert tasks == []

    def test_list_tasks(self, temp_task_store: TaskListStore):
        """测试：列出任务"""
        temp_task_store.create_task(title="Task 1")
        temp_task_store.create_task(title="Task 2")
        temp_task_store.create_task(title="Task 3")

        tasks = temp_task_store.list_tasks()

        assert len(tasks) == 3

    def test_list_tasks_with_status_filter(self, temp_task_store: TaskListStore):
        """测试：按状态过滤任务"""
        temp_task_store.create_task(title="Pending Task")
        temp_task_store.create_task(title="Completed Task")

        # 获取刚创建的任务并更新状态
        tasks = temp_task_store.list_tasks()
        if len(tasks) >= 2:
            tasks[1].update_status(TaskStatus.COMPLETED)
            temp_task_store.update_task(tasks[1])

        pending_tasks = temp_task_store.list_tasks(status=TaskStatus.PENDING)

        assert len(pending_tasks) == 1
        assert pending_tasks[0].title == "Pending Task"

    def test_get_next_task(self, temp_task_store: TaskListStore):
        """测试：获取下一个待执行任务"""
        temp_task_store.create_task(title="Task 1")
        temp_task_store.create_task(title="Task 2")
        temp_task_store.create_task(title="Task 3")

        next_task = temp_task_store.get_next_task()

        assert next_task is not None

    def test_get_next_task_no_pending(self, temp_task_store: TaskListStore):
        """测试：没有待执行任务"""
        temp_task_store.create_task(title="Completed Task")
        # 将任务标记为完成
        tasks = temp_task_store.list_tasks()
        if tasks:
            tasks[0].update_status(TaskStatus.COMPLETED)
            temp_task_store.update_task(tasks[0])

        next_task = temp_task_store.get_next_task()

        assert next_task is None

    def test_count_by_status(self, temp_task_store: TaskListStore):
        """测试：统计各状态任务数量"""
        temp_task_store.create_task(title="Pending 1")
        temp_task_store.create_task(title="Pending 2")

        # 创建并更新一个任务为进行中
        task = temp_task_store.create_task(title="In Progress")
        task.update_status(TaskStatus.IN_PROGRESS)
        temp_task_store.update_task(task)

        counts = temp_task_store.count_by_status()

        assert counts[TaskStatus.PENDING] == 2
        assert counts[TaskStatus.IN_PROGRESS] == 1

    def test_get_stats(self, temp_task_store: TaskListStore):
        """测试：获取统计信息"""
        temp_task_store.create_task(title="Task 1")
        temp_task_store.create_task(title="Task 2")

        stats = temp_task_store.get_stats()

        assert stats["total_tasks"] == 2
        assert stats["status_counts"]["pending"] == 2
