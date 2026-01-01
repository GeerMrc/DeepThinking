"""
顺序思考工具

实现MCP顺序思考工具，支持常规、修订、分支三种思考类型。
"""

import logging
from datetime import datetime, timezone
from typing import Literal

from deep_thinking.models.thought import Thought
from deep_thinking.server import app, get_storage_manager

logger = logging.getLogger(__name__)


@app.tool()
def sequential_thinking(
    thought: str,
    nextThoughtNeeded: bool,
    thoughtNumber: int,
    totalThoughts: int,
    session_id: str = "default",
    isRevision: bool = False,
    revisesThought: int | None = None,
    branchFromThought: int | None = None,
    branchId: str | None = None,
    needsMoreThoughts: bool = False,  # noqa: ARG001 - 预留参数，用于API兼容性
) -> str:
    """
    执行顺序思考步骤

    支持常规思考、修订思考和分支思考三种类型。

    Args:
        thought: 当前思考内容
        nextThoughtNeeded: 是否需要继续思考
        thoughtNumber: 当前思考步骤编号（从1开始）
        totalThoughts: 预计总思考步骤数
        session_id: 会话ID（默认为"default"）
        isRevision: 是否为修订思考
        revisesThought: 修订的思考步骤编号（仅修订思考使用）
        branchFromThought: 分支来源思考步骤编号（仅分支思考使用）
        branchId: 分支ID（仅分支思考使用，格式如"branch-0-1"）
        needsMoreThoughts: 是否需要增加总思考步骤数（预留参数）

    Returns:
        思考结果描述，包含当前思考信息和会话状态

    Raises:
        ValueError: 参数验证失败
    """
    # needsMoreThoughts 是预留参数，未来将用于动态调整思考步骤总数
    _ = needsMoreThoughts  # 标记为有意未使用

    manager = get_storage_manager()

    # 确定思考类型
    thought_type: Literal["regular", "revision", "branch"] = "regular"
    if isRevision:
        thought_type = "revision"
    elif branchFromThought is not None:
        thought_type = "branch"

    # 创建思考步骤对象
    thought_obj = Thought(
        thought_number=thoughtNumber,
        content=thought,
        type=thought_type,
        is_revision=isRevision,
        revises_thought=revisesThought,
        branch_from_thought=branchFromThought,
        branch_id=branchId,
        timestamp=datetime.now(timezone.utc),
    )

    # 获取或创建会话
    session = manager.get_session(session_id)

    if session is None:
        session = manager.create_session(
            name=f"会话-{session_id[:8]}",
            description="自动创建的思考会话",
            metadata={"session_type": "sequential_thinking"},
            session_id=session_id,  # 使用提供的session_id
        )

    # 添加思考步骤到会话
    manager.add_thought(session_id, thought_obj)

    # 获取会话状态
    session = manager.get_session(session_id)
    if session is None:
        raise RuntimeError("会话丢失")

    # 构建返回结果
    result_parts = [
        f"## 思考步骤 {thoughtNumber}/{totalThoughts}",
        "",
        f"**类型**: {get_type_name(thought_type)}",
        "",
        f"{thought}",
        "",
    ]

    # 添加修订信息
    if isRevision and revisesThought is not None:
        result_parts.append(f"🔄 修订思考步骤 {revisesThought}")
        result_parts.append("")

    # 添加分支信息
    if branchFromThought is not None:
        branch_info = f"🌿 从步骤 {branchFromThought} 分支"
        if branchId:
            branch_info += f" (分支ID: {branchId})"
        result_parts.append(branch_info)
        result_parts.append("")

    # 添加会话状态
    result_parts.extend([
        "---",
        "**会话信息**:",
        f"- 会话ID: {session_id}",
        f"- 总思考数: {session.thought_count()}",
        f"- 预计总数: {totalThoughts}",
        "",
    ])

    # 下一步提示
    if nextThoughtNeeded:
        result_parts.append("➡️ 继续下一步思考...")
    else:
        result_parts.append("✅ 思考完成！")
        # 标记会话为已完成
        session.mark_completed()
        manager.update_session(session)

    return "\n".join(result_parts)


def get_type_name(thought_type: str) -> str:
    """
    获取思考类型的显示名称

    Args:
        thought_type: 思考类型

    Returns:
        类型显示名称
    """
    type_names = {
        "regular": "常规思考 💭",
        "revision": "修订思考 🔄",
        "branch": "分支思考 🌿",
    }
    return type_names.get(thought_type, "常规思考 💭")


# 注册工具
__all__ = ["sequential_thinking"]
