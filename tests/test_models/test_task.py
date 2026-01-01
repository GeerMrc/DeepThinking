"""
任务数据模型单元测试
"""

import pytest
from pydantic import ValidationError

from deep_thinking.models.task import (
    TaskPriority,
    TaskStatus,
    ThinkingTask,
)


class TestTaskStatus:
    """测试任务状态枚举"""

    def test_status_values(self):
        """测试：状态枚举值正确"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.BLOCKED.value == "blocked"


class TestTaskPriority:
    """测试任务优先级枚举"""

    def test_priority_values(self):
        """测试：优先级枚举值正确"""
        assert TaskPriority.P0.value == "P0"
        assert TaskPriority.P1.value == "P1"
        assert TaskPriority.P2.value == "P2"


class TestThinkingTask:
    """测试思考任务模型"""

    def test_create_task_minimal(self):
        """测试：创建最小任务"""
        task = ThinkingTask(
            task_id="test-1",
            title="Test Task",
        )

        assert task.task_id == "test-1"
        assert task.title == "Test Task"
        assert task.description == ""
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.P2
        assert task.session_id is None

    def test_create_task_full(self):
        """测试：创建完整任务"""
        from datetime import datetime

        task = ThinkingTask(
            task_id="test-2",
            title="Full Task",
            description="Task Description",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.P0,
            session_id="session-123",
            metadata={"key": "value"},
        )

        assert task.task_id == "test-2"
        assert task.title == "Full Task"
        assert task.description == "Task Description"
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.P0
        assert task.session_id == "session-123"
        assert task.metadata == {"key": "value"}

    def test_to_dict(self):
        """测试：转换为字典"""
        task = ThinkingTask(
            task_id="test-3",
            title="Dict Test",
        )

        data = task.to_dict()

        assert data["task_id"] == "test-3"
        assert data["title"] == "Dict Test"
        assert data["status"] == "pending"
        assert data["priority"] == "P2"
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_summary(self):
        """测试：获取摘要"""
        task = ThinkingTask(
            task_id="test-4",
            title="Summary Test",
        )

        summary = task.get_summary()

        assert summary["task_id"] == "test-4"
        assert summary["title"] == "Summary Test"
        assert summary["status"] == "pending"
        assert "description" not in summary

    def test_update_status(self):
        """测试：更新状态"""
        task = ThinkingTask(
            task_id="test-5",
            title="Status Update Test",
        )

        original_updated_at = task.updated_at
        task.update_status(TaskStatus.IN_PROGRESS)

        assert task.status == TaskStatus.IN_PROGRESS
        assert task.updated_at > original_updated_at

    def test_link_session(self):
        """测试：关联会话"""
        task = ThinkingTask(
            task_id="test-6",
            title="Session Link Test",
        )

        task.link_session("session-abc")

        assert task.session_id == "session-abc"

    def test_unlink_session(self):
        """测试：取消关联会话"""
        task = ThinkingTask(
            task_id="test-7",
            title="Session Unlink Test",
            session_id="session-xyz",
        )

        task.unlink_session()

        assert task.session_id is None

    def test_is_active(self):
        """测试：检查任务是否活跃"""
        task_pending = ThinkingTask(task_id="test-8", title="Pending")
        task_in_progress = ThinkingTask(task_id="test-9", title="In Progress", status=TaskStatus.IN_PROGRESS)
        task_completed = ThinkingTask(task_id="test-10", title="Completed", status=TaskStatus.COMPLETED)

        assert task_pending.is_active() is True
        assert task_in_progress.is_active() is True
        assert task_completed.is_active() is False

    def test_can_start(self):
        """测试：检查任务是否可以开始"""
        task_pending = ThinkingTask(task_id="test-11", title="Pending")
        task_in_progress = ThinkingTask(task_id="test-12", title="In Progress", status=TaskStatus.IN_PROGRESS)

        assert task_pending.can_start() is True
        assert task_in_progress.can_start() is False

    def test_is_completed(self):
        """测试：检查任务是否完成"""
        task_pending = ThinkingTask(task_id="test-13", title="Pending")
        task_completed = ThinkingTask(task_id="test-14", title="Completed", status=TaskStatus.COMPLETED)

        assert task_pending.is_completed() is False
        assert task_completed.is_completed() is True

    def test_get_priority_weight(self):
        """测试：获取优先级权重"""
        task_p0 = ThinkingTask(task_id="test-15", title="P0", priority=TaskPriority.P0)
        task_p1 = ThinkingTask(task_id="test-16", title="P1", priority=TaskPriority.P1)
        task_p2 = ThinkingTask(task_id="test-17", title="P2", priority=TaskPriority.P2)

        assert task_p0.get_priority_weight() == 100
        assert task_p1.get_priority_weight() == 50
        assert task_p2.get_priority_weight() == 10

        # 验证排序：P0 > P1 > P2
        assert task_p0.get_priority_weight() > task_p1.get_priority_weight() > task_p2.get_priority_weight()
