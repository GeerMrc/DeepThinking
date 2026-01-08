"""
任务列表存储模块

提供任务清单的持久化存储和管理功能。
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from deep_thinking.models.task import TaskStatus, ThinkingTask

logger = logging.getLogger(__name__)


class TaskListStore:
    """
    任务列表存储管理器

    负责任务的持久化存储、查询和更新操作。

    Attributes:
        data_dir: 数据存储根目录
        tasks_dir: 任务文件存储目录
        index_path: 任务索引文件路径
    """

    def __init__(self, data_dir: str | Path):
        """
        初始化任务列表存储管理器

        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = Path(data_dir)
        self.tasks_dir = self.data_dir / "tasks"
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

        # 任务索引文件路径
        self.index_path = self.data_dir / "tasks" / ".tasks.json"

        # 初始化索引
        self._init_index()

    def _init_index(self) -> None:
        """初始化任务索引文件"""
        if not self.index_path.exists():
            self._write_index({})

    def _read_index(self) -> dict[str, Any]:
        """读取任务索引"""
        if not self.index_path.exists():
            return cast("dict[str, Any]", {})

        try:
            with open(self.index_path, encoding="utf-8") as f:
                return cast("dict[str, Any]", json.load(f))
        except Exception as e:
            logger.error(f"读取任务索引失败: {e}")
            return cast("dict[str, Any]", {})

    def _write_index(self, index: dict[str, Any]) -> None:
        """写入任务索引"""
        try:
            with open(self.index_path, "w", encoding="utf-8") as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"写入任务索引失败: {e}")

    def _update_index_entry(self, task_id: str, task: ThinkingTask) -> None:
        """更新索引条目"""
        index = self._read_index()
        index[task_id] = {
            "title": task.title,
            "status": task.status.value,
            "updated_at": task.updated_at.isoformat(),
        }
        self._write_index(index)

    def _remove_index_entry(self, task_id: str) -> None:
        """移除索引条目"""
        index = self._read_index()
        if task_id in index:
            del index[task_id]
            self._write_index(index)

    def create_task(
        self,
        title: str,
        description: str = "",
        task_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ThinkingTask:
        """
        创建新任务

        Args:
            title: 任务标题
            description: 任务描述
            task_id: 任务ID（可选，不提供则自动生成UUID）
            metadata: 元数据

        Returns:
            创建的任务对象
        """
        import uuid

        if task_id is None:
            task_id = f"task-{uuid.uuid4().hex[:12]}"

        task = ThinkingTask(
            task_id=task_id,
            title=title,
            description=description,
            metadata=metadata or {},
        )

        # 保存任务
        self._save_task(task)

        # 更新索引
        self._update_index_entry(task_id, task)

        logger.info(f"创建任务: {task_id}")
        return task

    def get_task(self, task_id: str) -> ThinkingTask | None:
        """
        获取任务

        Args:
            task_id: 任务ID

        Returns:
            任务对象，如果不存在则返回None
        """
        task_file = self.tasks_dir / f"{task_id}.json"
        if not task_file.exists():
            return None

        try:
            with open(task_file, encoding="utf-8") as f:
                data = json.load(f)

            # 转换枚举类型
            data["status"] = TaskStatus(data["status"])
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

            return ThinkingTask(**data)
        except Exception as e:
            logger.error(f"读取任务失败: {e}")
            return None

    def update_task(self, task: ThinkingTask) -> bool:
        """
        更新任务

        Args:
            task: 任务对象

        Returns:
            是否成功更新
        """
        # 检查任务是否存在
        if not self.exists(task.task_id):
            return False

        # 保存任务
        self._save_task(task)

        # 更新索引
        self._update_index_entry(task.task_id, task)

        logger.debug(f"更新任务: {task.task_id}")
        return True

    def delete_task(self, task_id: str) -> bool:
        """
        删除任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功删除
        """
        task_file = self.tasks_dir / f"{task_id}.json"
        if not task_file.exists():
            return False

        try:
            task_file.unlink()
            self._remove_index_entry(task_id)
            logger.info(f"删除任务: {task_id}")
            return True
        except Exception as e:
            logger.error(f"删除任务失败: {e}")
            return False

    def exists(self, task_id: str) -> bool:
        """
        检查任务是否存在

        Args:
            task_id: 任务ID

        Returns:
            任务是否存在
        """
        return (self.tasks_dir / f"{task_id}.json").exists()

    def list_tasks(
        self,
        status: TaskStatus | None = None,
        limit: int = 100,
    ) -> list[ThinkingTask]:
        """
        列出任务

        Args:
            status: 过滤状态
            limit: 最大返回数量

        Returns:
            任务列表
        """
        tasks = []

        # 从索引读取
        index = self._read_index()

        for task_id in list(index.keys())[:limit]:
            # 状态过滤
            task_info = index[task_id]
            if status and TaskStatus(task_info["status"]) != status:
                continue

            # 获取完整任务数据
            task = self.get_task(task_id)
            if task:
                tasks.append(task)

        # 按更新时间排序
        tasks.sort(key=lambda t: t.updated_at)

        return tasks

    def get_next_task(self) -> ThinkingTask | None:
        """
        获取下一个待执行任务

        返回第一个状态为 pending 的任务。

        Returns:
            下一个待执行任务，如果没有则返回None
        """
        tasks = self.list_tasks(status=TaskStatus.PENDING)
        return tasks[0] if tasks else None

    def count_by_status(self) -> dict[TaskStatus, int]:
        """
        统计各状态任务数量

        Returns:
            状态到数量的映射字典
        """
        counts = {status: 0 for status in TaskStatus}
        index = self._read_index()

        for task_info in index.values():
            status = TaskStatus(task_info["status"])
            counts[status] = counts.get(status, 0) + 1

        return counts

    def _save_task(self, task: ThinkingTask) -> None:
        """保存任务到文件"""
        task_file = self.tasks_dir / f"{task.task_id}.json"
        data = task.to_dict()

        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_stats(self) -> dict[str, Any]:
        """
        获取存储统计信息

        Returns:
            统计信息字典
        """
        index = self._read_index()

        # 统计各状态的任务数量
        status_counts = {status.value: 0 for status in TaskStatus}

        for task_info in index.values():
            status = task_info.get("status", "pending")
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_tasks": len(index),
            "status_counts": status_counts,
            "data_dir": str(self.data_dir),
        }
