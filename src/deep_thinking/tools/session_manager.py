"""
会话管理工具

提供思考会话的CRUD操作工具。
"""

import logging

from deep_thinking.server import app, get_storage_manager

logger = logging.getLogger(__name__)


@app.tool()
def create_session(
    name: str,
    description: str = "",
    metadata: str | None = None,
) -> str:
    """
    创建新的思考会话

    Args:
        name: 会话名称
        description: 会话描述（可选）
        metadata: 元数据JSON字符串（可选）

    Returns:
        创建的会话信息

    Raises:
        ValueError: 参数验证失败
    """
    manager = get_storage_manager()

    # 解析元数据
    import json

    parsed_metadata: dict = {}
    if metadata:
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


# 注册工具
__all__ = [
    "create_session",
    "get_session",
    "list_sessions",
    "delete_session",
    "update_session_status",
]
