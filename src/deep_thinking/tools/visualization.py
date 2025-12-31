"""
可视化工具

提供思考会话的可视化功能。
"""

import logging

from deep_thinking.server import app, get_storage_manager
from deep_thinking.utils.formatters import Visualizer

logger = logging.getLogger(__name__)


@app.tool()
async def visualize_session(
    session_id: str,
    format_type: str = "mermaid",
) -> str:
    """
    可视化思考会话

    支持的可视化格式:
    - mermaid: Mermaid 流程图代码（可用于 Markdown 文档或 Mermaid 编辑器）
    - ascii: ASCII 流程图（纯文本，适合终端显示）
    - tree: 树状结构（简化的层次显示）

    Args:
        session_id: 会话ID
        format_type: 可视化格式（mermaid/ascii/tree），默认为mermaid

    Returns:
        可视化结果

    Raises:
        ValueError: 参数验证失败（会话不存在、格式不支持等）

    Examples:
        >>> # 使用默认 Mermaid 格式
        >>> await visualize_session("abc-123")
        >>> # 使用 ASCII 格式
        >>> await visualize_session("abc-123", "ascii")
        >>> # 使用树状结构
        >>> await visualize_session("abc-123", "tree")
    """
    manager = get_storage_manager()

    # 获取会话
    session = manager.get_session(session_id)
    if session is None:
        raise ValueError(f"会话不存在: {session_id}")

    # 标准化格式类型
    format_normalized = _normalize_format(format_type)

    # 生成可视化
    try:
        if format_normalized == "mermaid":
            result = Visualizer.to_mermaid(session)
            format_desc = "Mermaid 流程图"
            usage_hint = """您可以将以下代码复制到 Mermaid 编辑器中查看：
https://mermaid.live

或者直接在支持 Mermaid 的 Markdown 编辑器中使用。"""
        elif format_normalized == "ascii":
            result = Visualizer.to_ascii(session)
            format_desc = "ASCII 流程图"
            usage_hint = "此图使用纯文本字符绘制，可在任何终端中正确显示。"
        elif format_normalized == "tree":
            result = Visualizer.to_tree(session)
            format_desc = "树状结构"
            usage_hint = "树状结构清晰地展示了思考步骤的层次关系。"
        else:
            raise ValueError(f"不支持的格式: {format_normalized}")

    except Exception as e:
        logger.error(f"可视化会话 {session_id} 失败: {e}")
        raise ValueError(f"可视化失败: {e}") from e

    # 返回结果
    return f"""## 思考会话可视化

**会话名称**: {session.name}
**会话ID**: {session.session_id}
**可视化格式**: {format_desc}
**思考步骤数**: {session.thought_count()}

---
```mermaid
{result}
```

---
{usage_hint}


您可以：
1. 复制上述代码到 Mermaid 编辑器查看图形
2. 将代码嵌入到支持 Mermaid 的 Markdown 文档中
3. 使用其他格式重新可视化：ascii、tree"""


@app.tool()
async def visualize_session_simple(
    session_id: str,
    format_type: str = "tree",
) -> str:
    """
    简化的会话可视化（直接返回可视化内容）

    与 visualize_session 不同，此工具直接返回可视化内容，
    不包含额外的说明文字，适合用于程序处理。

    Args:
        session_id: 会话ID
        format_type: 可视化格式（mermaid/ascii/tree），默认为tree

    Returns:
        纯可视化内容

    Raises:
        ValueError: 参数验证失败
    """
    manager = get_storage_manager()

    # 获取会话
    session = manager.get_session(session_id)
    if session is None:
        raise ValueError(f"会话不存在: {session_id}")

    # 标准化格式类型
    format_normalized = _normalize_format(format_type)

    # 生成可视化
    if format_normalized == "mermaid":
        return Visualizer.to_mermaid(session)
    elif format_normalized == "ascii":
        return Visualizer.to_ascii(session)
    elif format_normalized == "tree":
        return Visualizer.to_tree(session)
    else:
        raise ValueError(f"不支持的格式: {format_normalized}")


def _normalize_format(format_type: str) -> str:
    """
    标准化格式类型

    Args:
        format_type: 原始格式类型

    Returns:
        标准化后的格式类型

    Raises:
        ValueError: 格式不支持
    """
    format_map = {
        "mermaid": "mermaid",
        "mmd": "mermaid",
        "ascii": "ascii",
        "text": "ascii",
        "tree": "tree",
    }

    normalized = format_map.get(format_type.lower())
    if normalized is None:
        supported = ", ".join(set(format_map.values()))
        raise ValueError(
            f"不支持的格式: {format_type}。支持的格式: {supported}"
        )

    return normalized


# 注册工具
__all__ = [
    "visualize_session",
    "visualize_session_simple",
]
