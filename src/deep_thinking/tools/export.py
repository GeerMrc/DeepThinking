"""
导出工具

提供思考会话的导出功能，支持多种格式输出。
"""

import logging
from pathlib import Path

from deep_thinking.server import app, get_storage_manager
from deep_thinking.utils.formatters import export_session_to_file

logger = logging.getLogger(__name__)


@app.tool()
async def export_session(
    session_id: str,
    format_type: str = "markdown",
    output_path: str = "",
) -> str:
    """
    导出思考会话为指定格式

    支持的格式:
    - json: JSON格式，包含完整的会话数据
    - markdown/md: Markdown格式，适合文档查看
    - html: HTML格式，带有样式，适合浏览器查看
    - text/txt: 纯文本格式，兼容性最好

    Args:
        session_id: 会话ID
        format_type: 导出格式（json/markdown/html/text），默认为markdown
        output_path: 输出文件路径（可选）
                     - 如果为空，自动生成文件名到用户主目录的 exports/ 目录
                     - 如果指定路径，使用指定路径
                     - 支持相对路径和绝对路径
                     - 支持波浪号(~)展开

    Returns:
        导出结果信息，包含文件路径

    Raises:
        ValueError: 参数验证失败（会话不存在、格式不支持等）

    Examples:
        >>> # 使用默认格式和路径
        >>> await export_session("abc-123")
        >>> # 导出为JSON格式
        >>> await export_session("abc-123", "json")
        >>> # 指定输出路径
        >>> await export_session("abc-123", "html", "~/my-session.html")
        >>> # 使用相对路径
        >>> await export_session("abc-123", "markdown", "./exports/session.md")
    """
    manager = get_storage_manager()

    # 获取会话
    session = manager.get_session(session_id)
    if session is None:
        raise ValueError(f"会话不存在: {session_id}")

    # 标准化格式类型
    format_normalized = _normalize_format(format_type)

    # 确定输出路径
    output_file: Path
    if not output_path:
        # 自动生成路径: ~/exports/{session_name}.{ext}
        export_dir = Path.home() / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)

        # 文件扩展名映射
        ext_map = {
            "json": "json",
            "markdown": "md",
            "md": "md",
            "html": "html",
            "text": "txt",
            "txt": "txt",
        }

        ext = ext_map.get(format_normalized, "txt")
        # 清理文件名（移除非法字符）
        safe_name = _sanitize_filename(session.name)
        output_file = export_dir / f"{safe_name}_{session.session_id[:8]}.{ext}"
    else:
        output_file = Path(output_path)

    # 执行导出
    try:
        exported_path = export_session_to_file(session, format_normalized, output_file)
    except ValueError as e:
        raise ValueError(f"导出失败: {e}") from e
    except Exception as e:
        logger.error(f"导出会话 {session_id} 失败: {e}")
        raise ValueError(f"导出失败: {e}") from e

    # 返回结果
    return f"""## 会话已导出

**会话名称**: {session.name}
**会话ID**: {session.session_id}
**导出格式**: {format_normalized}
**文件路径**: `{exported_path}`
**思考步骤数**: {session.thought_count()}

---
会话已成功导出。您可以使用以下命令查看文件：

```bash
cat {exported_path}
```

或者在支持的编辑器中打开。"""


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
        "json": "json",
        "markdown": "markdown",
        "md": "markdown",
        "html": "html",
        "text": "text",
        "txt": "text",
    }

    normalized = format_map.get(format_type.lower())
    if normalized is None:
        supported = ", ".join(set(format_map.values()))
        raise ValueError(f"不支持的格式: {format_type}。支持的格式: {supported}")

    return normalized


def _sanitize_filename(name: str) -> str:
    """
    清理文件名，移除非法字符

    Args:
        name: 原始文件名

    Returns:
        清理后的文件名
    """
    # 移除或替换非法字符
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, "_")

    # 移除前后空格
    name = name.strip()

    # 限制长度（保留名称和扩展名空间）
    if len(name) > 50:
        name = name[:50]

    # 确保不为空
    if not name:
        name = "session"

    return name


# 注册工具
__all__ = [
    "export_session",
]
