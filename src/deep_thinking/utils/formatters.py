"""
格式化工具

提供会话数据的多种格式导出功能。
"""

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from deep_thinking.models.thinking_session import ThinkingSession

# 格式化器类型别名
FormatterFunc = Callable[[ThinkingSession], str]


class SessionFormatter:
    """
    会话格式化器

    提供将思考会话导出为不同格式的功能。
    """

    # 思考类型到表情符号的映射
    TYPE_EMOJI = {
        "regular": "💭",
        "revision": "🔄",
        "branch": "🌿",
    }

    # 思考类型中文名称
    TYPE_NAME = {
        "regular": "常规思考",
        "revision": "修订思考",
        "branch": "分支思考",
    }

    @staticmethod
    def to_json(session: ThinkingSession, indent: int = 2) -> str:
        """
        导出为JSON格式

        Args:
            session: 思考会话对象
            indent: JSON缩进空格数

        Returns:
            JSON格式的字符串
        """
        return json.dumps(session.to_dict(), ensure_ascii=False, indent=indent)

    @staticmethod
    def to_markdown(session: ThinkingSession) -> str:
        """
        导出为Markdown格式

        Args:
            session: 思考会话对象

        Returns:
            Markdown格式的字符串
        """
        lines: list[str] = []

        # 标题和元信息
        lines.append(f"# {session.name}")
        lines.append("")

        if session.description:
            lines.append(f"> {session.description}")
            lines.append("")

        # 会话信息
        lines.append("## 会话信息")
        lines.append("")
        lines.append(f"- **会话ID**: `{session.session_id}`")
        lines.append(f"- **状态**: {SessionFormatter._status_badge(session.status)}")
        lines.append(f"- **创建时间**: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- **更新时间**: {session.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- **思考步骤数**: {session.thought_count()}")
        lines.append("")

        # 思考步骤
        if session.thoughts:
            lines.append("## 思考步骤")
            lines.append("")

            for thought in session.thoughts:
                lines.append(SessionFormatter._thought_to_markdown(thought))
                lines.append("")

        # 元数据
        if session.metadata:
            lines.append("## 元数据")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(session.metadata, ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")

        # 页脚
        lines.append("---")
        lines.append(f"*导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("")
        lines.append("*由 DeepThinking-MCP 生成*")

        return "\n".join(lines)

    @staticmethod
    def _thought_to_markdown(thought: Any) -> str:
        """
        将单个思考步骤转换为Markdown格式

        Args:
            thought: 思考步骤对象

        Returns:
            Markdown格式的字符串
        """
        emoji = SessionFormatter.TYPE_EMOJI.get(thought.type, "💭")
        type_name = SessionFormatter.TYPE_NAME.get(thought.type, "思考")

        header = f"{emoji} **步骤 {thought.thought_number}**"

        # 添加思考类型标签
        if thought.type == "revision" and thought.revises_thought:
            header += f" 📝 (修订步骤 {thought.revises_thought})"
        elif thought.type == "branch" and thought.branch_from_thought:
            header += f" 🔀 (分支自步骤 {thought.branch_from_thought})"

        lines: list[str] = [header, ""]

        # 添加类型标签（仅非常规思考）
        if thought.type != "regular":
            lines.append(f"*{type_name}*")
            lines.append("")

        # 思考内容
        lines.append(thought.content)
        lines.append("")

        # 时间戳
        time_str = thought.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        lines.append(f"<details><summary>🕒 {time_str}</summary>")
        lines.append("")
        lines.append("</details>")

        return "\n".join(lines)

    @staticmethod
    def _status_badge(status: str) -> str:
        """
        生成状态徽章

        Args:
            status: 状态值

        Returns:
            Markdown格式的状态徽章
        """
        badges = {
            "active": "🟢 进行中",
            "completed": "✅ 已完成",
            "archived": "📦 已归档",
        }
        return badges.get(status, status)

    @staticmethod
    def to_html(session: ThinkingSession) -> str:
        """
        导出为HTML格式

        Args:
            session: 思考会话对象

        Returns:
            HTML格式的字符串
        """
        html_parts: list[str] = []

        # HTML头部
        title_escaped = SessionFormatter._escape_html(session.name)
        html_parts.append(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_escaped}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: #fff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            font-size: 2em;
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        .description {{
            font-style: italic;
            color: #7f8c8d;
            margin-bottom: 30px;
            padding-left: 15px;
            border-left: 3px solid #3498db;
        }}
        h2 {{
            font-size: 1.5em;
            margin-top: 30px;
            margin-bottom: 15px;
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        .session-info {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .session-info p {{
            margin: 5px 0;
        }}
        .thought {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f9f9f9;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}
        .thought-header {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        .thought-type {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            margin-left: 10px;
        }}
        .thought-type.regular {{
            background-color: #3498db;
            color: #fff;
        }}
        .thought-type.revision {{
            background-color: #e67e22;
            color: #fff;
        }}
        .thought-type.branch {{
            background-color: #27ae60;
            color: #fff;
        }}
        .thought-content {{
            margin: 10px 0;
            white-space: pre-wrap;
        }}
        .thought-meta {{
            font-size: 0.85em;
            color: #95a5a6;
            margin-top: 10px;
        }}
        .metadata {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
        }}
        .metadata pre {{
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #95a5a6;
            font-size: 0.9em;
        }}
        .status {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .status.active {{
            background-color: #2ecc71;
            color: #fff;
        }}
        .status.completed {{
            background-color: #3498db;
            color: #fff;
        }}
        .status.archived {{
            background-color: #95a5a6;
            color: #fff;
        }}
    </style>
</head>
<body>
    <div class="container">
""")

        # 标题
        html_parts.append(f'        <h1>{SessionFormatter._escape_html(session.name)}</h1>')
        html_parts.append("")

        # 描述
        if session.description:
            html_parts.append(f'        <p class="description">{SessionFormatter._escape_html(session.description)}</p>')
            html_parts.append("")

        # 会话信息
        html_parts.append('        <h2>会话信息</h2>')
        html_parts.append('        <div class="session-info">')
        html_parts.append(f'            <p><strong>会话ID:</strong> <code>{SessionFormatter._escape_html(session.session_id)}</code></p>')
        html_parts.append(f'            <p><strong>状态:</strong> <span class="status {session.status}">{SessionFormatter._status_badge(session.status).split(" ", 1)[1]}</span></p>')
        html_parts.append(f'            <p><strong>创建时间:</strong> {session.created_at.strftime("%Y-%m-%d %H:%M:%S")}</p>')
        html_parts.append(f'            <p><strong>更新时间:</strong> {session.updated_at.strftime("%Y-%m-%d %H:%M:%S")}</p>')
        html_parts.append(f'            <p><strong>思考步骤数:</strong> {session.thought_count()}</p>')
        html_parts.append('        </div>')
        html_parts.append("")

        # 思考步骤
        if session.thoughts:
            html_parts.append('        <h2>思考步骤</h2>')
            html_parts.append("")

            for thought in session.thoughts:
                html_parts.append(SessionFormatter._thought_to_html(thought))
                html_parts.append("")

        # 元数据
        if session.metadata:
            html_parts.append('        <h2>元数据</h2>')
            html_parts.append('        <div class="metadata">')
            html_parts.append('            <pre>' + json.dumps(session.metadata, ensure_ascii=False, indent=2) + '</pre>')
            html_parts.append('        </div>')
            html_parts.append("")

        # 页脚
        html_parts.append('        <div class="footer">')
        html_parts.append(f'            <p>导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>')
        html_parts.append('            <p>由 DeepThinking-MCP 生成</p>')
        html_parts.append('        </div>')

        # HTML尾部
        html_parts.append('    </div>')
        html_parts.append('</body>')
        html_parts.append('</html>')

        return "\n".join(html_parts)

    @staticmethod
    def _thought_to_html(thought: Any) -> str:
        """
        将单个思考步骤转换为HTML格式

        Args:
            thought: 思考步骤对象

        Returns:
            HTML格式的字符串
        """
        emoji = SessionFormatter.TYPE_EMOJI.get(thought.type, "💭")

        lines: list[str] = ["        <div class=\"thought\">"]
        lines.append(f'            <div class="thought-header">{emoji} 步骤 {thought.thought_number}')

        # 添加类型标签
        if thought.type != "regular":
            type_name = SessionFormatter.TYPE_NAME.get(thought.type, "思考")
            lines.append(f'                <span class="thought-type {thought.type}">{type_name}</span>')

        lines.append('            </div>')

        # 添加修订/分支信息
        if thought.type == "revision" and thought.revises_thought:
            lines.append(f'            <p style="color: #e67e22; font-size: 0.9em;">📝 修订步骤 {thought.revises_thought}</p>')
        elif thought.type == "branch" and thought.branch_from_thought:
            lines.append(f'            <p style="color: #27ae60; font-size: 0.9em;">🔀 分支自步骤 {thought.branch_from_thought}')

        # 思考内容
        lines.append(f'            <div class="thought-content">{SessionFormatter._escape_html(thought.content)}</div>')

        # 时间戳
        time_str = thought.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        lines.append(f'            <div class="thought-meta">🕒 {time_str}</div>')

        lines.append('        </div>')

        return "\n".join(lines)

    @staticmethod
    def _escape_html(text: str) -> str:
        """
        转义HTML特殊字符

        Args:
            text: 原始文本

        Returns:
            转义后的文本
        """
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#x27;"))

    @staticmethod
    def to_text(session: ThinkingSession) -> str:
        """
        导出为纯文本格式

        Args:
            session: 思考会话对象

        Returns:
            纯文本格式的字符串
        """
        lines: list[str] = []

        # 标题
        lines.append("=" * 60)
        lines.append(f"  {session.name}")
        lines.append("=" * 60)
        lines.append("")

        # 描述
        if session.description:
            lines.append(f"描述: {session.description}")
            lines.append("")

        # 会话信息
        lines.append("-" * 60)
        lines.append("会话信息")
        lines.append("-" * 60)
        lines.append(f"会话ID: {session.session_id}")
        lines.append(f"状态: {SessionFormatter._status_text(session.status)}")
        lines.append(f"创建时间: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"更新时间: {session.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"思考步骤数: {session.thought_count()}")
        lines.append("")

        # 思考步骤
        if session.thoughts:
            lines.append("-" * 60)
            lines.append("思考步骤")
            lines.append("-" * 60)
            lines.append("")

            for thought in session.thoughts:
                lines.append(SessionFormatter._thought_to_text(thought))
                lines.append("")
                lines.append("")

        # 元数据
        if session.metadata:
            lines.append("-" * 60)
            lines.append("元数据")
            lines.append("-" * 60)
            lines.append(json.dumps(session.metadata, ensure_ascii=False, indent=2))
            lines.append("")

        # 页脚
        lines.append("-" * 60)
        lines.append(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("由 DeepThinking-MCP 生成")
        lines.append("=" * 60)

        return "\n".join(lines)

    @staticmethod
    def _thought_to_text(thought: Any) -> str:
        """
        将单个思考步骤转换为纯文本格式

        Args:
            thought: 思考步骤对象

        Returns:
            纯文本格式的字符串
        """
        emoji = SessionFormatter.TYPE_EMOJI.get(thought.type, "💭")

        lines: list[str] = []
        lines.append(f"{emoji} [步骤 {thought.thought_number}]")

        # 添加类型信息
        if thought.type == "revision":
            type_name = SessionFormatter.TYPE_NAME.get(thought.type, "修订思考")
            lines.append(f"类型: {type_name}")
            if thought.revises_thought:
                lines.append(f"修订: 步骤 {thought.revises_thought}")
        elif thought.type == "branch":
            type_name = SessionFormatter.TYPE_NAME.get(thought.type, "分支思考")
            lines.append(f"类型: {type_name}")
            if thought.branch_from_thought:
                lines.append(f"分支自: 步骤 {thought.branch_from_thought}")
            if thought.branch_id:
                lines.append(f"分支ID: {thought.branch_id}")

        lines.append("")
        lines.append(thought.content)
        lines.append("")
        lines.append(f"时间: {thought.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(lines)

    @staticmethod
    def _status_text(status: str) -> str:
        """
        获取状态文本

        Args:
            status: 状态值

        Returns:
            状态文本
        """
        status_map = {
            "active": "进行中",
            "completed": "已完成",
            "archived": "已归档",
        }
        return status_map.get(status, status)


def export_session_to_file(
    session: ThinkingSession,
    format_type: str,
    output_path: Path,
) -> str:
    """
    导出会话到文件

    Args:
        session: 思考会话对象
        format_type: 导出格式 (json/markdown/html/text)
        output_path: 输出文件路径

    Returns:
        导出文件的绝对路径

    Raises:
        ValueError: 格式不支持或路径无效
    """
    # 支持的格式
    formatters: dict[str, FormatterFunc] = {
        "json": SessionFormatter.to_json,
        "markdown": SessionFormatter.to_markdown,
        "md": SessionFormatter.to_markdown,
        "html": SessionFormatter.to_html,
        "text": SessionFormatter.to_text,
        "txt": SessionFormatter.to_text,
    }

    if format_type not in formatters:
        raise ValueError(f"不支持的格式: {format_type}。支持的格式: {', '.join(formatters.keys())}")

    # 确保输出目录存在
    output_path = output_path.expanduser().absolute()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 格式化内容
    formatter = formatters[format_type]
    content = formatter(session)

    # 写入文件
    output_path.write_text(content, encoding="utf-8")

    return str(output_path)


__all__ = [
    "SessionFormatter",
    "Visualizer",
    "export_session_to_file",
]


# =============================================================================
# 可视化格式化器
# =============================================================================


class Visualizer:
    """
    思考会话可视化器

    提供将思考会话转换为可视化图表的功能。
    """

    # Mermaid 样式定义
    MERMAID_STYLES = """
classDef regular fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
classDef revision fill:#fff3e0,stroke:#f57c00,stroke-width:2px;
classDef branch fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
"""

    @staticmethod
    def to_mermaid(session: ThinkingSession) -> str:
        """
        导出为 Mermaid 流程图

        Args:
            session: 思考会话对象

        Returns:
            Mermaid 格式的流程图代码
        """
        if not session.thoughts:
            return """graph TD
    Start["会话暂无思考步骤"]:::regular
    """ + Visualizer.MERMAID_STYLES

        lines: list[str] = ["graph TD"]

        # 添加节点
        for thought in session.thoughts:
            node_id = Visualizer._mermaid_node_id(thought)
            node_label = Visualizer._escape_mermaid_label(thought.content)
            node_class = thought.type

            # 添加节点
            if thought.type == "revision":
                revises = thought.revises_thought or 0
                lines.append(
                    f'    {node_id}["{node_label}<br/><small>(修订步骤{revises})</small>"]:::{node_class}'
                )
            elif thought.type == "branch":
                branch_from = thought.branch_from_thought or 0
                lines.append(
                    f'    {node_id}["{node_label}<br/><small>(分支自步骤{branch_from})</small>"]:::{node_class}'
                )
            else:
                lines.append(f'    {node_id}["{node_label}"]:::{node_class}')

        # 添加连接线
        for i, thought in enumerate(session.thoughts):
            current_id = Visualizer._mermaid_node_id(thought)

            # 常规思考连接到下一个
            if thought.type == "regular" and i + 1 < len(session.thoughts):
                next_thought = session.thoughts[i + 1]
                # 只有当下一个也是常规思考或修订时才连接
                if next_thought.type in ("regular", "revision"):
                    next_id = Visualizer._mermaid_node_id(next_thought)
                    lines.append(f"    {current_id} --> {next_id}")

            # 修订思考连接到被修订的思考
            if thought.type == "revision" and thought.revises_thought:
                revises_id = Visualizer._find_node_id(session, thought.revises_thought, thought.thought_number)
                if revises_id:
                    lines.append(f"    {current_id} -.->|修订| {revises_id}")
                    # 修订后继续
                    if i + 1 < len(session.thoughts):
                        next_thought = session.thoughts[i + 1]
                        if next_thought.type in ("regular", "revision"):
                            next_id = Visualizer._mermaid_node_id(next_thought)
                            lines.append(f"    {current_id} --> {next_id}")

            # 分支思考连接到来源思考
            if thought.type == "branch" and thought.branch_from_thought:
                branch_from_id = Visualizer._find_node_id(
                    session, thought.branch_from_thought, thought.thought_number
                )
                if branch_from_id:
                    lines.append(f"    {branch_from_id} -.->|分支| {current_id}")

        # 添加样式
        lines.append(Visualizer.MERMAID_STYLES.strip())

        return "\n".join(lines)

    @staticmethod
    def _mermaid_node_id(thought: Any) -> str:
        """生成 Mermaid 节点 ID"""
        branch_suffix = f"_{thought.branch_id}" if thought.branch_id else ""
        return f"T{thought.thought_number}{branch_suffix}".replace("-", "_")

    @staticmethod
    def _find_node_id(session: ThinkingSession, target_number: int, current_number: int) -> str | None:
        """
        查找指定思考步骤的节点 ID

        Args:
            session: 思考会话
            target_number: 目标思考编号
            current_number: 当前思考编号（用于避免自引用）

        Returns:
            节点 ID，如果未找到返回 None
        """
        for thought in session.thoughts:
            if thought.thought_number == target_number and thought.thought_number != current_number:
                return Visualizer._mermaid_node_id(thought)
        return None

    @staticmethod
    def _escape_mermaid_label(text: str) -> str:
        """
        转义 Mermaid 标签中的特殊字符

        Args:
            text: 原始文本

        Returns:
            转义后的文本
        """
        # 限制标签长度
        if len(text) > 30:
            text = text[:27] + "..."
        # 替换特殊字符
        text = text.replace('"', '#quot;')
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        return text

    @staticmethod
    def to_ascii(session: ThinkingSession) -> str:
        """
        导出为 ASCII 流程图

        Args:
            session: 思考会话对象

        Returns:
            ASCII 格式的流程图
        """
        if not session.thoughts:
            return "┌─────────────────────────────┐\n│   会话暂无思考步骤        │\n└─────────────────────────────┘"

        lines: list[str] = []

        # 为每个思考步骤生成 ASCII 表示
        for thought in session.thoughts:
            block = Visualizer._thought_to_ascii_block(thought)
            lines.append(block)

            # 添加连接线
            if thought.type == "regular" and thought.thought_number < session.thought_count():
                lines.append("           │")
                lines.append("           ▼")

        return "\n".join(lines)

    @staticmethod
    def _thought_to_ascii_block(thought: Any) -> str:
        """
        将思考步骤转换为 ASCII 块

        Args:
            thought: 思考步骤对象

        Returns:
            ASCII 格式的块
        """
        # 根据类型选择样式
        if thought.type == "revision":
            emoji = "🔄"
            border = "═════════════════════════════"
            prefix = "│"
        elif thought.type == "branch":
            emoji = "🌿"
            border = "╔═════════════════════════════╗"
            prefix = "║"
        else:
            emoji = "💭"
            border = "─────────────────────────────"
            prefix = "│"

        # 截断内容
        content = thought.content
        if len(content) > 28:
            content = content[:25] + "..."

        lines: list[str] = []

        # 上边框
        if thought.type == "branch":
            lines.append(f"        {border}")
        else:
            lines.append(f"        {border}")

        # 第一行：emoji 和编号
        type_label = {
            "regular": "常规",
            "revision": "修订",
            "branch": "分支",
        }.get(thought.type, "")

        lines.append(f"        {prefix} {emoji} 步骤 {thought.thought_number} [{type_label}]")

        # 第二行：内容
        lines.append(f"        {prefix} {content}")

        # 第三行：修订/分支信息
        if thought.type == "revision" and thought.revises_thought:
            lines.append(f"        {prefix} → 修订步骤 {thought.revises_thought}")
        elif thought.type == "branch" and thought.branch_from_thought:
            lines.append(f"        {prefix} ← 分支自步骤 {thought.branch_from_thought}")

        # 下边框
        if thought.type == "branch":
            lines.append(f"        {border}")
        else:
            lines.append(f"        {border}")

        return "\n".join(lines)

    @staticmethod
    def to_tree(session: ThinkingSession) -> str:
        """
        导出为树状结构（适合显示分支关系）

        Args:
            session: 思考会话对象

        Returns:
            树状结构的字符串
        """
        if not session.thoughts:
            return "会话暂无思考步骤"

        lines: list[str] = []
        lines.append("🧠 思考流程树")
        lines.append("")

        # 构建思考步骤树
        for i, thought in enumerate(session.thoughts):
            # 确定前缀符号
            prefix = "└──" if i == len(session.thoughts) - 1 else "├──"

            # 根据类型选择 emoji
            emoji = SessionFormatter.TYPE_EMOJI.get(thought.type, "💭")

            # 格式化行
            line = f"{prefix} {emoji} 步骤 {thought.thought_number}: {thought.content[:50]}"
            if len(thought.content) > 50:
                line += "..."

            lines.append(line)

            # 添加修订/分支信息
            if thought.type == "revision" and thought.revises_thought:
                lines.append(f"    │   └─ 📝 修订步骤 {thought.revises_thought}")
            elif thought.type == "branch" and thought.branch_from_thought:
                lines.append(f"    │   └─ 🔀 分支自步骤 {thought.branch_from_thought}")

        return "\n".join(lines)
