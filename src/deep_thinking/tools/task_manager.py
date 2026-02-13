"""
任务管理MCP工具

提供任务清单管理的MCP工具接口。
"""

import logging

from deep_thinking.models.task import TaskStatus
from deep_thinking.server import app, get_storage_manager
from deep_thinking.storage.task_list_store import TaskListStore

logger = logging.getLogger(__name__)


def _get_task_store() -> TaskListStore:
    """
    获取任务列表存储管理器

    Returns:
        TaskListStore实例

    Raises:
        RuntimeError: 如果存储管理器未初始化
    """
    storage_manager = get_storage_manager()
    # 在数据目录下创建任务存储
    task_store = TaskListStore(storage_manager.data_dir)
    return task_store


@app.tool(
    name="create_task",
    description="创建新的任务",
)
def create_task(
    title: str,
    description: str = "",
    task_id: str | None = None,
) -> str:
    """
    创建新任务

    Args:
        title: 任务标题
        description: 任务描述（可选）
        task_id: 任务ID（可选，不提供则自动生成）

    Returns:
        创建的任务信息描述
    """
    task_store = _get_task_store()

    # 创建任务
    task = task_store.create_task(
        title=title,
        description=description,
        task_id=task_id,
    )

    logger.info(f"创建任务成功: {task.task_id}")
    return f"✅ 任务已创建\nID: {task.task_id}\n标题: {task.title}\n状态: {task.status.value}"


@app.tool(
    name="list_tasks",
    description="列出任务，支持按状态过滤",
)
def list_tasks(
    status: str | None = None,
    limit: int = 100,
) -> str:
    """
    列出任务

    Args:
        status: 过滤状态（pending/in_progress/completed/failed/blocked）
        limit: 最大返回数量（默认100）

    Returns:
        任务列表描述
    """
    task_store = _get_task_store()

    # 转换过滤参数
    task_status = TaskStatus(status) if status else None

    # 获取任务列表
    tasks = task_store.list_tasks(
        status=task_status,
        limit=limit,
    )

    if not tasks:
        return "📋 没有找到符合条件的任务"

    # 格式化输出
    lines = [f"📋 任务列表 (共{len(tasks)}个任务)\n"]
    for task in tasks:
        status_icon = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.BLOCKED: "🚫",
        }.get(task.status, "❓")

        lines.append(
            f"{status_icon} {task.title}\n"
            f"   ID: {task.task_id}\n"
            f"   状态: {task.status.value}\n"
            f"   更新: {task.updated_at.strftime('%Y-%m-%d %H:%M')}\n"
        )

    return "\n".join(lines)


@app.tool(
    name="update_task_status",
    description="更新任务状态",
)
def update_task_status(
    task_id: str,
    new_status: str,
) -> str:
    """
    更新任务状态

    Args:
        task_id: 任务ID
        new_status: 新状态（pending/in_progress/completed/failed/blocked）

    Returns:
        更新结果描述
    """
    task_store = _get_task_store()

    # 获取任务
    task = task_store.get_task(task_id)
    if not task:
        return f"❌ 错误: 任务 '{task_id}' 不存在"

    # 转换状态
    try:
        status = TaskStatus(new_status)
    except ValueError:
        return f"❌ 错误: 无效的状态 '{new_status}'"

    # 更新状态
    old_status = task.status
    task.update_status(status)
    success = task_store.update_task(task)

    if success:
        logger.info(f"任务状态更新: {task_id} {old_status.value} -> {new_status}")
        return f"✅ 任务状态已更新\nID: {task_id}\n状态: {old_status.value} → {new_status}"
    else:
        return "❌ 错误: 更新任务失败"


@app.tool(
    name="get_next_task",
    description="获取下一个待执行任务",
)
def get_next_task() -> str:
    """
    获取下一个待执行任务

    返回第一个状态为 pending 的任务。

    Returns:
        下一个待执行任务信息，如果没有则返回提示
    """
    task_store = _get_task_store()

    # 获取下一个待执行任务
    task = task_store.get_next_task()

    if not task:
        return "📋 没有待执行的任务"

    return (
        f"📋 下一个待执行任务\n"
        f"ID: {task.task_id}\n"
        f"标题: {task.title}\n"
        f"描述: {task.description or '(无描述)'}\n"
        f"创建: {task.created_at.strftime('%Y-%m-%d %H:%M')}"
    )


@app.tool(
    name="link_task_session",
    description="关联任务与思考会话",
)
def link_task_session(
    task_id: str,
    session_id: str,
) -> str:
    """
    关联任务与思考会话

    Args:
        task_id: 任务ID
        session_id: 思考会话ID

    Returns:
        关联结果描述
    """
    task_store = _get_task_store()

    # 获取任务
    task = task_store.get_task(task_id)
    if not task:
        return f"❌ 错误: 任务 '{task_id}' 不存在"

    # 关联会话
    task.link_session(session_id)
    success = task_store.update_task(task)

    if success:
        logger.info(f"任务关联会话: {task_id} -> {session_id}")
        return f"✅ 任务已关联到思考会话\n任务ID: {task_id}\n会话ID: {session_id}"
    else:
        return "❌ 错误: 关联失败"


@app.tool(
    name="get_task_stats",
    description="获取任务统计信息",
)
def get_task_stats() -> str:
    """
    获取任务统计信息

    Returns:
        任务统计描述
    """
    task_store = _get_task_store()

    # 获取统计信息
    stats = task_store.get_stats()

    lines = [
        "📊 任务统计\n",
        f"总任务数: {stats['total_tasks']}\n",
        "状态分布:",
    ]

    for status, count in stats["status_counts"].items():
        lines.append(f"  - {status}: {count}")

    return "\n".join(lines)


# 注册工具
__all__ = [
    "create_task",
    "list_tasks",
    "update_task_status",
    "get_next_task",
    "link_task_session",
    "get_task_stats",
]
