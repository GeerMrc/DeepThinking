"""
会话管理工具

提供思考会话的CRUD操作工具。
"""

import json
import logging
from typing import Any

from deep_thinking.server import app, get_storage_manager

logger = logging.getLogger(__name__)


@app.tool()
def create_session(
    name: str,
    description: str = "",
    metadata: dict[str, Any] | str | None = None,
) -> str:
    """
    创建新的思考会话

    Args:
        name: 会话名称
        description: 会话描述（可选）
        metadata: 元数据，支持dict或JSON字符串格式（可选）

    Returns:
        创建的会话信息

    Raises:
        ValueError: 参数验证失败
    """
    manager = get_storage_manager()

    # 处理元数据：支持dict和str两种格式
    parsed_metadata: dict[str, Any] = {}
    if metadata is not None:
        if isinstance(metadata, dict):
            # 直接使用dict
            parsed_metadata = metadata
        elif isinstance(metadata, str):
            # 解析JSON字符串
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError as e:
                raise ValueError(f"元数据JSON格式错误: {e}") from e

    # 创建会话
    session = manager.create_session(
        name=name,
        description=description,
        metadata=parsed_metadata,
    )

    # 返回结果
    return f"""## 会话已创建

**会话ID**: {session.session_id}
**名称**: {session.name}
**描述**: {session.description or "无"}
**创建时间**: {session.created_at.isoformat()}
**状态**: {session.status}

---
使用此会话ID进行后续思考操作。"""


@app.tool()
def get_session(session_id: str) -> str:
    """
    获取会话详情

    Args:
        session_id: 会话ID

    Returns:
        会话详细信息

    Raises:
        ValueError: 会话不存在
    """
    manager = get_storage_manager()

    session = manager.get_session(session_id)
    if session is None:
        raise ValueError(f"会话不存在: {session_id}")

    # 构建返回结果
    description = session.description or "无"
    parts = [
        "## 会话详情",
        "",
        f"**会话ID**: {session.session_id}",
        f"**名称**: {session.name}",
        f"**描述**: {description}",
        f"**状态**: {session.status}",
        f"**创建时间**: {session.created_at.isoformat()}",
        f"**更新时间**: {session.updated_at.isoformat()}",
        f"**思考步骤数**: {session.thought_count()}",
        "",
    ]

    # 思考步骤列表
    if session.thoughts:
        parts.append("### 思考步骤")
        parts.append("")
        for thought in session.thoughts:
            type_emoji = {
                "regular": "💭",
                "revision": "🔄",
                "branch": "🌿",
            }.get(thought.type, "💭")

            parts.append(f"{type_emoji} **步骤 {thought.thought_number}**")
            parts.append(f"{thought.content}")
            parts.append("")

    return "\n".join(parts)


@app.tool()
def list_sessions(
    status: str | None = None,
    limit: int = 20,
) -> str:
    """
    列出所有会话

    Args:
        status: 过滤状态（active/completed/archived），为空则显示所有
        limit: 最大返回数量（默认20）

    Returns:
        会话列表
    """
    manager = get_storage_manager()

    # 状态映射
    status_map = {
        "active": "active",
        "completed": "completed",
        "archived": "archived",
    }

    # 解析状态
    filter_status: str | None = None
    if status:
        filter_status = status_map.get(status.lower())
        if filter_status is None:
            raise ValueError(f"无效的状态值: {status}。有效值为: active, completed, archived")

    # 获取会话列表
    sessions = manager.list_sessions(status=filter_status, limit=limit)

    # 构建返回结果
    parts = [
        "## 会话列表",
        "",
    ]

    if not sessions:
        parts.append("暂无会话")
        return "\n".join(parts)

    # 状态过滤说明
    if filter_status:
        parts.append(f"**状态过滤**: {filter_status}")
        parts.append("")

    parts.append(f"**总数**: {len(sessions)}")
    parts.append("")

    # 会话列表
    for i, session_info in enumerate(sessions, 1):
        parts.append(f"### {i}. {session_info['name']}")
        parts.append(f"- **会话ID**: {session_info['session_id']}")
        parts.append(f"- **状态**: {session_info['status']}")
        parts.append(f"- **思考数**: {session_info['thought_count']}")
        parts.append(f"- **更新时间**: {session_info['updated_at']}")
        parts.append("")

    return "\n".join(parts)


@app.tool()
def delete_session(session_id: str) -> str:
    """
    删除会话

    Args:
        session_id: 会话ID

    Returns:
        删除结果
    """
    manager = get_storage_manager()

    result = manager.delete_session(session_id)

    if result:
        return f"""## 会话已删除

**会话ID**: {session_id}

---
会话已成功删除。"""
    else:
        return f"""## 删除失败

会话不存在: {session_id}

---
请检查会话ID是否正确。"""


@app.tool()
def update_session_status(
    session_id: str,
    status: str,
) -> str:
    """
    更新会话状态

    Args:
        session_id: 会话ID
        status: 新状态（active/completed/archived）

    Returns:
        更新结果

    Raises:
        ValueError: 参数验证失败
    """
    manager = get_storage_manager()

    # 状态映射
    status_map = {
        "active": "active",
        "completed": "completed",
        "archived": "archived",
    }

    new_status = status_map.get(status.lower())
    if new_status is None:
        raise ValueError(f"无效的状态值: {status}。有效值为: active, completed, archived")

    # 获取会话
    session = manager.get_session(session_id)
    if session is None:
        raise ValueError(f"会话不存在: {session_id}")

    # 更新状态
    if new_status == "completed":
        session.mark_completed()
    elif new_status == "archived":
        session.mark_archived()
    elif new_status == "active":
        session.mark_active()

    # 保存更新
    result = manager.update_session(session)

    if result:
        return f"""## 会话状态已更新

**会话ID**: {session_id}
**新状态**: {new_status}

---
会话状态已成功更新。"""
    else:
        return f"""## 更新失败

无法更新会话: {session_id}

---
请检查会话ID是否正确。"""


@app.tool()
def resume_session(
    session_id: str,
) -> str:
    """
    恢复已暂停的思考会话（断点续传）

    获取会话的最后一个思考步骤，返回可以继续思考的上下文信息。

    Args:
        session_id: 要恢复的会话ID

    Returns:
        会话恢复信息，包含最后一个思考步骤和继续指导

    Raises:
        ValueError: 会话不存在或已完成
    """
    manager = get_storage_manager()

    # 获取会话
    session = manager.get_session(session_id)
    if session is None:
        raise ValueError(f"会话不存在: {session_id}")

    # 检查会话状态
    if session.status == "completed":
        return f"""## 会话已完成

**会话ID**: {session_id}
**名称**: {session.name}

该会话已经标记为完成，无法继续。

如需继续思考，请创建新会话。"""

    # 获取最后一个思考步骤
    last_thought = session.get_latest_thought()

    if not last_thought:
        # 会话存在但没有思考步骤
        return f"""## 会话恢复成功（新会话）

**会话ID**: {session_id}
**名称**: {session.name}
**描述**: {session.description or "(无描述)"}

该会话尚未包含任何思考步骤，可以直接开始思考。

使用 `sequential_thinking` 工具开始添加思考步骤。"""

    # 构建恢复信息
    result_parts = [
        "## 🔄 会话恢复成功",
        "",
        f"**会话ID**: {session_id}",
        f"**名称**: {session.name}",
        f"**状态**: {session.status}",
        f"**总思考数**: {session.thought_count()}",
        "",
    ]

    # 显示最后一个思考步骤
    result_parts.extend(
        [
            "---",
            "### 上一个思考步骤",
            "",
            f"**步骤 {last_thought.thought_number}**: {last_thought.content[:100]}"
            f"{'...' if len(last_thought.content) > 100 else ''}",
            f"**类型**: {last_thought.type}",
            f"**时间**: {last_thought.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
    )

    # 检查是否有total_thoughts历史记录
    if "total_thoughts_history" in session.metadata:
        history = session.metadata["total_thoughts_history"]
        if history:
            last_adjustment = history[-1]
            current_total = last_adjustment["new_total"]
            result_parts.extend(
                [
                    "### 思考步骤调整历史",
                    "",
                    f"**当前总数**: {current_total}",
                    f"**调整次数**: {len(history)}",
                    "",
                ]
            )

    # 继续指导
    result_parts.extend(
        [
            "---",
            "### 继续思考",
            "",
            "要继续添加思考步骤，请使用 `sequential_thinking` 工具：",
            "",
            f"- 设置 `thoughtNumber` 为 {session.thought_count() + 1}",
            "- 设置 `session_id` 为当前会话ID",
            "- 如果需要增加思考步骤总数，设置 `needsMoreThoughts=true`",
            "",
        ]
    )

    return "\n".join(result_parts)


@app.tool()
def get_tool_call_history(
    session_id: str,
    thought_number: int | None = None,
    limit: int = 50,
) -> str:
    """
    获取会话的工具调用历史（Interleaved Thinking）

    查询会话中的工具调用记录，支持按思考步骤过滤。

    Args:
        session_id: 会话ID
        thought_number: 过滤特定思考步骤的工具调用（可选，为空则返回全部）
        limit: 最大返回数量（默认50）

    Returns:
        工具调用历史记录

    Raises:
        ValueError: 会话不存在
    """
    manager = get_storage_manager()

    # 获取会话
    session = manager.get_session(session_id)
    if session is None:
        raise ValueError(f"会话不存在: {session_id}")

    # 过滤工具调用记录
    if thought_number is not None:
        records = [r for r in session.tool_call_history if r.thought_number == thought_number]
    else:
        records = session.tool_call_history

    # 限制数量
    records = records[:limit]

    # 构建返回结果
    parts = [
        "## 工具调用历史",
        "",
        f"**会话ID**: {session_id}",
        f"**总记录数**: {len(session.tool_call_history)}",
    ]

    if thought_number is not None:
        parts.append(f"**过滤条件**: 思考步骤 {thought_number}")

    parts.append("")

    if not records:
        parts.append("暂无工具调用记录")
        return "\n".join(parts)

    # 状态图标映射
    status_icons = {
        "pending": "⏳",
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
        "timeout": "⏱️",
        "cancelled": "🚫",
    }

    # 工具调用记录列表
    for record in records:
        icon = status_icons.get(record.status, "❓")
        parts.append(f"### {icon} {record.call_data.tool_name}")
        parts.append(f"- **记录ID**: {record.record_id}")
        parts.append(f"- **思考步骤**: {record.thought_number}")
        parts.append(f"- **状态**: {record.status}")
        parts.append(f"- **调用时间**: {record.call_data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        # 参数（如果有）
        if record.call_data.arguments:
            args_str = json.dumps(record.call_data.arguments, ensure_ascii=False)
            if len(args_str) > 100:
                args_str = args_str[:100] + "..."
            parts.append(f"- **参数**: `{args_str}`")

        # 结果信息（如果有）
        if record.result_data:
            parts.append(f"- **成功**: {'是' if record.result_data.success else '否'}")
            if record.result_data.execution_time_ms:
                parts.append(f"- **执行时间**: {record.result_data.execution_time_ms:.2f}ms")
            if record.result_data.from_cache:
                parts.append("- **缓存命中**: 是")

            # 错误信息（如果有）
            if record.result_data.error:
                parts.append(f"- **错误类型**: {record.result_data.error.error_type}")
                error_msg = record.result_data.error.error_message
                if len(error_msg) > 100:
                    error_msg = error_msg[:100] + "..."
                parts.append(f"- **错误信息**: {error_msg}")

        parts.append("")

    return "\n".join(parts)


@app.tool()
def get_session_statistics(session_id: str) -> str:
    """
    获取会话统计信息（Interleaved Thinking）

    返回会话的详细统计数据，包括思考步骤、工具调用等指标。

    Args:
        session_id: 会话ID

    Returns:
        会话统计信息

    Raises:
        ValueError: 会话不存在
    """
    manager = get_storage_manager()

    # 获取会话
    session = manager.get_session(session_id)
    if session is None:
        raise ValueError(f"会话不存在: {session_id}")

    stats = session.statistics

    # 构建返回结果
    parts = [
        "## 会话统计信息",
        "",
        f"**会话ID**: {session_id}",
        f"**会话名称**: {session.name}",
        "",
        "---",
        "",
        "### 思考步骤统计",
        "",
        f"- **总思考数**: {stats.total_thoughts}",
        f"- **平均思考长度**: {stats.avg_thought_length:.1f} 字符",
        "",
        "### 工具调用统计",
        "",
        f"- **总调用次数**: {stats.total_tool_calls}",
        f"- **成功次数**: {stats.successful_tool_calls}",
        f"- **失败次数**: {stats.failed_tool_calls}",
        f"- **缓存命中**: {stats.cached_tool_calls}",
    ]

    # 计算成功率
    if stats.total_tool_calls > 0:
        success_rate = (stats.successful_tool_calls / stats.total_tool_calls) * 100
        parts.append(f"- **成功率**: {success_rate:.1f}%")
    else:
        parts.append("- **成功率**: N/A")

    # 执行时间
    if stats.total_execution_time_ms > 0:
        parts.append(f"- **总执行时间**: {stats.total_execution_time_ms:.2f}ms")
        if stats.total_tool_calls > 0:
            avg_time = stats.total_execution_time_ms / stats.total_tool_calls
            parts.append(f"- **平均执行时间**: {avg_time:.2f}ms")
    else:
        parts.append("- **总执行时间**: N/A")

    parts.append("")
    parts.append("### 执行阶段分布")
    parts.append("")

    phase_dist = stats.phase_distribution
    total_phases = sum(phase_dist.values())

    if total_phases > 0:
        for phase, count in phase_dist.items():
            percentage = (count / total_phases) * 100
            phase_names = {
                "thinking": "思考",
                "tool_call": "工具调用",
                "analysis": "分析",
            }
            phase_name = phase_names.get(phase, phase)
            parts.append(f"- **{phase_name}**: {count} ({percentage:.1f}%)")
    else:
        parts.append("- 暂无阶段分布数据")

    # 思考类型分布
    if session.thoughts:
        parts.append("")
        parts.append("### 思考类型分布")
        parts.append("")

        type_counts: dict[str, int] = {}
        for thought in session.thoughts:
            type_counts[thought.type] = type_counts.get(thought.type, 0) + 1

        type_names = {
            "regular": "常规思考",
            "revision": "修订思考",
            "branch": "分支思考",
            "comparison": "对比思考",
            "reverse": "逆向思考",
            "hypothetical": "假设思考",
        }

        for thought_type, count in type_counts.items():
            type_name = type_names.get(thought_type, thought_type)
            parts.append(f"- **{type_name}**: {count}")

    return "\n".join(parts)


# 注册工具
__all__ = [
    "create_session",
    "get_session",
    "list_sessions",
    "delete_session",
    "update_session_status",
    "resume_session",
    "get_tool_call_history",
    "get_session_statistics",
]
