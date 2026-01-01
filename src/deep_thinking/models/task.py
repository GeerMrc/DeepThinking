"""
任务数据模型

定义任务清单系统的核心数据结构。
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态枚举"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    """任务优先级枚举"""

    P0 = "P0"  # 高优先级（紧急重要）
    P1 = "P1"  # 中优先级（重要）
    P2 = "P2"  # 低优先级（普通）


# 优先级排序权重
PRIORITY_WEIGHT = {
    TaskPriority.P0: 100,
    TaskPriority.P1: 50,
    TaskPriority.P2: 10,
}


class ThinkingTask(BaseModel):
    """
    思考任务模型

    表示一个待执行或正在执行的任务，可以与思考会话关联。

    Attributes:
        task_id: 任务唯一标识符
        title: 任务标题
        description: 任务详细描述
        status: 任务状态
        priority: 任务优先级
        session_id: 关联的思考会话ID（可选）
        created_at: 创建时间
        updated_at: 最后更新时间
        metadata: 扩展元数据
    """

    task_id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.P2
    session_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        转换为字典格式

        Returns:
            包含所有字段的字典
        """
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    def get_summary(self) -> dict[str, Any]:
        """
        获取任务摘要

        Returns:
            包含关键信息的摘要字典
        """
        return {
            "task_id": self.task_id,
            "title": self.title,
            "status": self.status.value,
            "priority": self.priority.value,
            "session_id": self.session_id,
            "updated_at": self.updated_at.isoformat(),
        }

    def update_status(self, new_status: TaskStatus) -> None:
        """
        更新任务状态

        Args:
            new_status: 新的任务状态
        """
        self.status = new_status
        self.updated_at = datetime.now()

    def link_session(self, session_id: str) -> None:
        """
        关联思考会话

        Args:
            session_id: 思考会话ID
        """
        self.session_id = session_id
        self.updated_at = datetime.now()

    def unlink_session(self) -> None:
        """取消与思考会话的关联"""
        self.session_id = None
        self.updated_at = datetime.now()

    def is_active(self) -> bool:
        """
        检查任务是否处于活跃状态

        Returns:
            如果任务状态为 pending 或 in_progress 返回 True
        """
        return self.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS)

    def can_start(self) -> bool:
        """
        检查任务是否可以开始执行

        Returns:
            如果任务状态为 pending 返回 True
        """
        return self.status == TaskStatus.PENDING

    def is_completed(self) -> bool:
        """
        检查任务是否已完成

        Returns:
            如果任务状态为 completed 返回 True
        """
        return self.status == TaskStatus.COMPLETED

    def get_priority_weight(self) -> int:
        """
        获取优先级权重值

        Returns:
            优先级对应的权重值（用于排序）
        """
        return PRIORITY_WEIGHT.get(self.priority, 0)
