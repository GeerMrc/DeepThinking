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
        "comparison": "⚖️",
        "reverse": "🔙",
        "hypothetical": "🤔",
    }

    # 思考类型中文名称
    TYPE_NAME = {
        "regular": "常规思考",
        "revision": "修订思考",
        "branch": "分支思考",
        "comparison": "对比思考",
        "reverse": "逆向思考",
        "hypothetical": "假设思考",
    }

    # 执行阶段中文名称 (Interleaved Thinking)
    PHASE_NAME = {
        "thinking": "思考阶段",
        "tool_call": "工具调用阶段",
        "analysis": "分析阶段",
    }

    # 执行阶段图标 (Interleaved Thinking)
    PHASE_EMOJI = {
        "thinking": "💭",
        "tool_call": "🔧",
        "analysis": "📊",
    }

    # 工具调用状态图标 (Interleaved Thinking)
    TOOL_STATUS_EMOJI = {
        "pending": "⏳",
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
        "timeout": "⏱️",
        "cancelled": "🚫",
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
                lines.append(SessionFormatter._thought_to_markdown(thought, session))
                lines.append("")

        # 工具调用历史 (Interleaved Thinking)
        if session.tool_call_history:
            lines.append("## 工具调用历史")
            lines.append("")
            lines.append(SessionFormatter._tool_calls_to_markdown(session.tool_call_history))
            lines.append("")

        # 统计信息 (Interleaved Thinking)
        if session.statistics.total_thoughts > 0 or session.statistics.total_tool_calls > 0:
            lines.append("## 统计信息")
            lines.append("")
            lines.append(SessionFormatter._statistics_to_markdown(session.statistics))
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
    def _thought_to_markdown(thought: Any, session: ThinkingSession | None = None) -> str:
        """
        将单个思考步骤转换为Markdown格式

        Args:
            thought: 思考步骤对象
            session: 会话对象（用于获取工具调用详情）

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

        # 添加执行阶段信息 (Interleaved Thinking)
        phase_emoji = SessionFormatter.PHASE_EMOJI.get(thought.phase, "💭")
        phase_name = SessionFormatter.PHASE_NAME.get(thought.phase, "思考阶段")
        lines.append(f"*{phase_emoji} {phase_name}*")
        lines.append("")

        # 添加类型标签（仅非常规思考）
        if thought.type != "regular":
            lines.append(f"*{type_name}*")
            lines.append("")

        # 思考内容
        lines.append(thought.content)
        lines.append("")

        # 显示关联的工具调用 (Interleaved Thinking)
        if thought.tool_calls and session:
            lines.append("**关联工具调用:**")
            lines.append("")
            for record_id in thought.tool_calls:
                # 查找对应的工具调用记录
                record = SessionFormatter._find_tool_call_record(session, record_id)
                if record:
                    status_emoji = SessionFormatter.TOOL_STATUS_EMOJI.get(record.status, "❓")
                    tool_name = record.call_data.tool_name
                    lines.append(f"- {status_emoji} `{tool_name}` ({record.status})")
            lines.append("")

        # 时间戳
        time_str = thought.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"<details><summary>🕒 {time_str}</summary>")
        lines.append("")
        lines.append("</details>")

        return "\n".join(lines)

    @staticmethod
    def _find_tool_call_record(session: ThinkingSession, record_id: str) -> Any | None:
        """
        查找工具调用记录

        Args:
            session: 会话对象
            record_id: 记录ID

        Returns:
            工具调用记录对象，如果未找到返回 None
        """
        for record in session.tool_call_history:
            if record.record_id == record_id:
                return record
        return None

    @staticmethod
    def _tool_calls_to_markdown(tool_call_history: list[Any]) -> str:
        """
        将工具调用历史转换为Markdown格式

        Args:
            tool_call_history: 工具调用记录列表

        Returns:
            Markdown格式的字符串
        """
        lines: list[str] = []

        lines.append("| 步骤 | 工具名称 | 状态 | 执行时间 |")
        lines.append("|------|----------|------|----------|")

        for record in tool_call_history:
            status_emoji = SessionFormatter.TOOL_STATUS_EMOJI.get(record.status, "❓")
            tool_name = record.call_data.tool_name
            thought_num = record.thought_number

            # 执行时间
            exec_time = "-"
            if record.result_data and record.result_data.execution_time_ms:
                exec_time = f"{record.result_data.execution_time_ms:.1f}ms"

            # 状态文本
            status_text = f"{status_emoji} {record.status}"

            lines.append(f"| {thought_num} | `{tool_name}` | {status_text} | {exec_time} |")

        if not tool_call_history:
            lines.append("| - | - | - | - |")

        return "\n".join(lines)

    @staticmethod
    def _statistics_to_markdown(statistics: Any) -> str:
        """
        将统计信息转换为Markdown格式

        Args:
            statistics: 会话统计信息对象

        Returns:
            Markdown格式的字符串
        """
        lines: list[str] = []

        # 基本信息
        lines.append(f"- **总思考步骤数**: {statistics.total_thoughts}")
        lines.append(f"- **平均思考长度**: {statistics.avg_thought_length:.1f} 字符")

        # 工具调用统计
        if statistics.total_tool_calls > 0:
            lines.append("")
            lines.append("### 工具调用统计")
            lines.append("")
            lines.append(f"- **总调用次数**: {statistics.total_tool_calls}")
            lines.append(f"- **成功次数**: {statistics.successful_tool_calls}")
            lines.append(f"- **失败次数**: {statistics.failed_tool_calls}")

            if statistics.cached_tool_calls > 0:
                lines.append(f"- **缓存命中**: {statistics.cached_tool_calls}")

            if statistics.total_execution_time_ms > 0:
                lines.append(f"- **总执行时间**: {statistics.total_execution_time_ms:.1f}ms")

            # 成功率
            success_rate = statistics.successful_tool_calls / statistics.total_tool_calls * 100
            lines.append(f"- **成功率**: {success_rate:.1f}%")

        # 阶段分布
        if statistics.phase_distribution:
            lines.append("")
            lines.append("### 阶段分布")
            lines.append("")
            for phase, count in statistics.phase_distribution.items():
                phase_name = SessionFormatter.PHASE_NAME.get(phase, phase)
                phase_emoji = SessionFormatter.PHASE_EMOJI.get(phase, "")
                lines.append(f"- {phase_emoji} **{phase_name}**: {count} 次")

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
            font-family:
                -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                "Helvetica Neue", Arial, sans-serif;
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
        /* Interleaved Thinking 样式 */
        .thought-phase {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            margin-left: 10px;
            background-color: #9b59b6;
            color: #fff;
        }}
        .thought-phase.thinking {{
            background-color: #3498db;
        }}
        .thought-phase.tool_call {{
            background-color: #e74c3c;
        }}
        .thought-phase.analysis {{
            background-color: #2ecc71;
        }}
        .tool-calls {{
            margin: 10px 0;
            padding: 10px;
            background-color: #fff3e0;
            border-radius: 4px;
            border: 1px solid #ffcc80;
        }}
        .tool-call-item {{
            padding: 5px 0;
            border-bottom: 1px dashed #ffcc80;
        }}
        .tool-call-item:last-child {{
            border-bottom: none;
        }}
        .tool-call-status {{
            display: inline-block;
            padding: 1px 6px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-left: 5px;
        }}
        .tool-call-status.completed {{
            background-color: #27ae60;
            color: #fff;
        }}
        .tool-call-status.failed {{
            background-color: #e74c3c;
            color: #fff;
        }}
        .tool-call-status.pending {{
            background-color: #f39c12;
            color: #fff;
        }}
        .tool-call-history {{
            margin-top: 20px;
            overflow-x: auto;
        }}
        .tool-call-history table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .tool-call-history th, .tool-call-history td {{
            padding: 8px;
            border: 1px solid #ecf0f1;
            text-align: left;
        }}
        .tool-call-history th {{
            background-color: #34495e;
            color: #fff;
        }}
        .statistics {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
        }}
        .statistics h3 {{
            margin-bottom: 10px;
            color: #34495e;
        }}
        .statistics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .stat-card {{
            background-color: #fff;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #ecf0f1;
        }}
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #3498db;
        }}
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
""")

        # 标题
        html_parts.append(f"        <h1>{SessionFormatter._escape_html(session.name)}</h1>")
        html_parts.append("")

        # 描述
        if session.description:
            escaped_desc = SessionFormatter._escape_html(session.description)
            html_parts.append(f'        <p class="description">{escaped_desc}</p>')
            html_parts.append("")

        # 会话信息
        html_parts.append("        <h2>会话信息</h2>")
        html_parts.append('        <div class="session-info">')
        sid = SessionFormatter._escape_html(session.session_id)
        html_parts.append(f"            <p><strong>会话ID:</strong> <code>{sid}</code></p>")
        badge = SessionFormatter._status_badge(session.status).split(" ", 1)[1]
        status_html = f'<span class="status {session.status}">{badge}</span>'
        html_parts.append(f"            <p><strong>状态:</strong> {status_html}</p>")
        created = session.created_at.strftime("%Y-%m-%d %H:%M:%S")
        html_parts.append(f"            <p><strong>创建时间:</strong> {created}</p>")
        updated = session.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        html_parts.append(f"            <p><strong>更新时间:</strong> {updated}</p>")
        count = session.thought_count()
        html_parts.append(f"            <p><strong>思考步骤数:</strong> {count}</p>")
        html_parts.append("        </div>")
        html_parts.append("")

        # 思考步骤
        if session.thoughts:
            html_parts.append("        <h2>思考步骤</h2>")
            html_parts.append("")

            for thought in session.thoughts:
                html_parts.append(SessionFormatter._thought_to_html(thought, session))
                html_parts.append("")

        # 工具调用历史 (Interleaved Thinking)
        if session.tool_call_history:
            html_parts.append("        <h2>工具调用历史</h2>")
            html_parts.append(SessionFormatter._tool_calls_to_html(session.tool_call_history))
            html_parts.append("")

        # 统计信息 (Interleaved Thinking)
        if session.statistics.total_thoughts > 0 or session.statistics.total_tool_calls > 0:
            html_parts.append("        <h2>统计信息</h2>")
            html_parts.append(SessionFormatter._statistics_to_html(session.statistics))
            html_parts.append("")

        # 元数据
        if session.metadata:
            html_parts.append("        <h2>元数据</h2>")
            html_parts.append('        <div class="metadata">')
            metadata_json = json.dumps(session.metadata, ensure_ascii=False, indent=2)
            html_parts.append(f"            <pre>{metadata_json}</pre>")
            html_parts.append("        </div>")
            html_parts.append("")

        # 页脚
        html_parts.append('        <div class="footer">')
        export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_parts.append(f"            <p>导出时间: {export_time}</p>")
        html_parts.append("            <p>由 DeepThinking-MCP 生成</p>")
        html_parts.append("        </div>")

        # HTML尾部
        html_parts.append("    </div>")
        html_parts.append("</body>")
        html_parts.append("</html>")

        return "\n".join(html_parts)

    @staticmethod
    def _thought_to_html(thought: Any, session: ThinkingSession | None = None) -> str:
        """
        将单个思考步骤转换为HTML格式

        Args:
            thought: 思考步骤对象
            session: 会话对象（用于获取工具调用详情）

        Returns:
            HTML格式的字符串
        """
        emoji = SessionFormatter.TYPE_EMOJI.get(thought.type, "💭")

        lines: list[str] = ['        <div class="thought">']
        header = f"{emoji} 步骤 {thought.thought_number}"
        lines.append(f'            <div class="thought-header">{header}')

        # 添加类型标签
        if thought.type != "regular":
            type_name = SessionFormatter.TYPE_NAME.get(thought.type, "思考")
            type_span = f'<span class="thought-type {thought.type}">{type_name}</span>'
            lines.append(f"                {type_span}")

        # 添加执行阶段标签 (Interleaved Thinking)
        phase_emoji = SessionFormatter.PHASE_EMOJI.get(thought.phase, "")
        phase_name = SessionFormatter.PHASE_NAME.get(thought.phase, "思考阶段")
        phase_span = (
            f'<span class="thought-phase {thought.phase}">{phase_emoji} {phase_name}</span>'
        )
        lines.append(f"                {phase_span}")

        lines.append("            </div>")

        # 添加修订/分支信息
        if thought.type == "revision" and thought.revises_thought:
            rev_info = f"📝 修订步骤 {thought.revises_thought}"
            lines.append(f'            <p style="color: #e67e22; font-size: 0.9em;">{rev_info}</p>')
        elif thought.type == "branch" and thought.branch_from_thought:
            branch_info = f"🔀 分支自步骤 {thought.branch_from_thought}"
            branch_p = f'<p style="color: #27ae60; font-size: 0.9em;">{branch_info}</p>'
            lines.append(f"            {branch_p}")

        # 思考内容
        content = SessionFormatter._escape_html(thought.content)
        lines.append(f'            <div class="thought-content">{content}</div>')

        # 显示关联的工具调用 (Interleaved Thinking)
        if thought.tool_calls and session:
            lines.append('            <div class="tool-calls">')
            lines.append("                <strong>关联工具调用:</strong>")
            for record_id in thought.tool_calls:
                record = SessionFormatter._find_tool_call_record(session, record_id)
                if record:
                    status_emoji = SessionFormatter.TOOL_STATUS_EMOJI.get(record.status, "❓")
                    tool_name = SessionFormatter._escape_html(record.call_data.tool_name)
                    status_class = (
                        record.status if record.status in ("completed", "failed", "pending") else ""
                    )
                    status_span = (
                        f'<span class="tool-call-status {status_class}">{status_emoji}</span>'
                    )
                    lines.append(
                        f'                <div class="tool-call-item">{status_span} <code>{tool_name}</code></div>'
                    )
            lines.append("            </div>")

        # 时间戳
        time_str = thought.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f'            <div class="thought-meta">🕒 {time_str}</div>')

        lines.append("        </div>")

        return "\n".join(lines)

    @staticmethod
    def _tool_calls_to_html(tool_call_history: list[Any]) -> str:
        """
        将工具调用历史转换为HTML格式

        Args:
            tool_call_history: 工具调用记录列表

        Returns:
            HTML格式的字符串
        """
        lines: list[str] = []
        lines.append('        <div class="tool-call-history">')
        lines.append("            <table>")
        lines.append("                <thead>")
        lines.append("                    <tr>")
        lines.append("                        <th>步骤</th>")
        lines.append("                        <th>工具名称</th>")
        lines.append("                        <th>状态</th>")
        lines.append("                        <th>执行时间</th>")
        lines.append("                    </tr>")
        lines.append("                </thead>")
        lines.append("                <tbody>")

        for record in tool_call_history:
            status_emoji = SessionFormatter.TOOL_STATUS_EMOJI.get(record.status, "❓")
            tool_name = SessionFormatter._escape_html(record.call_data.tool_name)
            thought_num = record.thought_number

            # 执行时间
            exec_time = "-"
            if record.result_data and record.result_data.execution_time_ms:
                exec_time = f"{record.result_data.execution_time_ms:.1f}ms"

            # 状态
            status_class = (
                record.status if record.status in ("completed", "failed", "pending") else ""
            )
            status_html = f'<span class="tool-call-status {status_class}">{status_emoji} {record.status}</span>'

            lines.append("                    <tr>")
            lines.append(f"                        <td>{thought_num}</td>")
            lines.append(f"                        <td><code>{tool_name}</code></td>")
            lines.append(f"                        <td>{status_html}</td>")
            lines.append(f"                        <td>{exec_time}</td>")
            lines.append("                    </tr>")

        lines.append("                </tbody>")
        lines.append("            </table>")
        lines.append("        </div>")

        return "\n".join(lines)

    @staticmethod
    def _statistics_to_html(statistics: Any) -> str:
        """
        将统计信息转换为HTML格式

        Args:
            statistics: 会话统计信息对象

        Returns:
            HTML格式的字符串
        """
        lines: list[str] = []
        lines.append('        <div class="statistics">')
        lines.append('            <div class="statistics-grid">')

        # 基本统计卡片
        lines.append('                <div class="stat-card">')
        lines.append(
            f'                    <div class="stat-value">{statistics.total_thoughts}</div>'
        )
        lines.append('                    <div class="stat-label">总思考步骤数</div>')
        lines.append("                </div>")

        lines.append('                <div class="stat-card">')
        lines.append(
            f'                    <div class="stat-value">{statistics.avg_thought_length:.0f}</div>'
        )
        lines.append('                    <div class="stat-label">平均思考长度</div>')
        lines.append("                </div>")

        if statistics.total_tool_calls > 0:
            lines.append('                <div class="stat-card">')
            lines.append(
                f'                    <div class="stat-value">{statistics.total_tool_calls}</div>'
            )
            lines.append('                    <div class="stat-label">工具调用次数</div>')
            lines.append("                </div>")

            # 成功率
            success_rate = statistics.successful_tool_calls / statistics.total_tool_calls * 100
            lines.append('                <div class="stat-card">')
            lines.append(f'                    <div class="stat-value">{success_rate:.0f}%</div>')
            lines.append('                    <div class="stat-label">调用成功率</div>')
            lines.append("                </div>")

            if statistics.total_execution_time_ms > 0:
                lines.append('                <div class="stat-card">')
                lines.append(
                    f'                    <div class="stat-value">{statistics.total_execution_time_ms:.0f}ms</div>'
                )
                lines.append('                    <div class="stat-label">总执行时间</div>')
                lines.append("                </div>")

        lines.append("            </div>")

        # 阶段分布
        if statistics.phase_distribution:
            lines.append("            <h3>阶段分布</h3>")
            lines.append('            <div class="statistics-grid">')
            for phase, count in statistics.phase_distribution.items():
                phase_name = SessionFormatter.PHASE_NAME.get(phase, phase)
                phase_emoji = SessionFormatter.PHASE_EMOJI.get(phase, "")
                lines.append('                <div class="stat-card">')
                lines.append(f'                    <div class="stat-value">{count}</div>')
                lines.append(
                    f'                    <div class="stat-label">{phase_emoji} {phase_name}</div>'
                )
                lines.append("                </div>")
            lines.append("            </div>")

        lines.append("        </div>")

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
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )

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
                lines.append(SessionFormatter._thought_to_text(thought, session))
                lines.append("")
                lines.append("")

        # 工具调用历史 (Interleaved Thinking)
        if session.tool_call_history:
            lines.append("-" * 60)
            lines.append("工具调用历史")
            lines.append("-" * 60)
            lines.append(SessionFormatter._tool_calls_to_text(session.tool_call_history))
            lines.append("")

        # 统计信息 (Interleaved Thinking)
        if session.statistics.total_thoughts > 0 or session.statistics.total_tool_calls > 0:
            lines.append("-" * 60)
            lines.append("统计信息")
            lines.append("-" * 60)
            lines.append(SessionFormatter._statistics_to_text(session.statistics))
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
    def _thought_to_text(thought: Any, session: ThinkingSession | None = None) -> str:
        """
        将单个思考步骤转换为纯文本格式

        Args:
            thought: 思考步骤对象
            session: 会话对象（用于获取工具调用详情）

        Returns:
            纯文本格式的字符串
        """
        emoji = SessionFormatter.TYPE_EMOJI.get(thought.type, "💭")

        lines: list[str] = []
        lines.append(f"{emoji} [步骤 {thought.thought_number}]")

        # 添加执行阶段信息 (Interleaved Thinking)
        phase_emoji = SessionFormatter.PHASE_EMOJI.get(thought.phase, "")
        phase_name = SessionFormatter.PHASE_NAME.get(thought.phase, "思考阶段")
        lines.append(f"阶段: {phase_emoji} {phase_name}")

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

        # 显示关联的工具调用 (Interleaved Thinking)
        if thought.tool_calls and session:
            lines.append("关联工具调用:")
            for record_id in thought.tool_calls:
                record = SessionFormatter._find_tool_call_record(session, record_id)
                if record:
                    status_emoji = SessionFormatter.TOOL_STATUS_EMOJI.get(record.status, "?")
                    tool_name = record.call_data.tool_name
                    lines.append(f"  {status_emoji} {tool_name} ({record.status})")
            lines.append("")

        lines.append(f"时间: {thought.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(lines)

    @staticmethod
    def _tool_calls_to_text(tool_call_history: list[Any]) -> str:
        """
        将工具调用历史转换为纯文本格式

        Args:
            tool_call_history: 工具调用记录列表

        Returns:
            纯文本格式的字符串
        """
        lines: list[str] = []

        for record in tool_call_history:
            status_emoji = SessionFormatter.TOOL_STATUS_EMOJI.get(record.status, "?")
            tool_name = record.call_data.tool_name
            thought_num = record.thought_number

            # 执行时间
            exec_time = "-"
            if record.result_data and record.result_data.execution_time_ms:
                exec_time = f"{record.result_data.execution_time_ms:.1f}ms"

            lines.append(
                f"  [{thought_num}] {status_emoji} {tool_name} - {record.status} ({exec_time})"
            )

        if not tool_call_history:
            lines.append("  (无工具调用)")

        return "\n".join(lines)

    @staticmethod
    def _statistics_to_text(statistics: Any) -> str:
        """
        将统计信息转换为纯文本格式

        Args:
            statistics: 会话统计信息对象

        Returns:
            纯文本格式的字符串
        """
        lines: list[str] = []

        # 基本信息
        lines.append(f"  总思考步骤数: {statistics.total_thoughts}")
        lines.append(f"  平均思考长度: {statistics.avg_thought_length:.1f} 字符")

        # 工具调用统计
        if statistics.total_tool_calls > 0:
            lines.append("")
            lines.append("  工具调用统计:")
            lines.append(f"    总调用次数: {statistics.total_tool_calls}")
            lines.append(f"    成功次数: {statistics.successful_tool_calls}")
            lines.append(f"    失败次数: {statistics.failed_tool_calls}")

            if statistics.cached_tool_calls > 0:
                lines.append(f"    缓存命中: {statistics.cached_tool_calls}")

            if statistics.total_execution_time_ms > 0:
                lines.append(f"    总执行时间: {statistics.total_execution_time_ms:.1f}ms")

            # 成功率
            success_rate = statistics.successful_tool_calls / statistics.total_tool_calls * 100
            lines.append(f"    成功率: {success_rate:.1f}%")

        # 阶段分布
        if statistics.phase_distribution:
            lines.append("")
            lines.append("  阶段分布:")
            for phase, count in statistics.phase_distribution.items():
                phase_name = SessionFormatter.PHASE_NAME.get(phase, phase)
                phase_emoji = SessionFormatter.PHASE_EMOJI.get(phase, "")
                lines.append(f"    {phase_emoji} {phase_name}: {count} 次")

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
    支持 Interleaved Thinking 的工具调用和执行阶段显示。
    """

    # Mermaid 样式定义 - 思考类型样式
    MERMAID_STYLES = """
classDef regular fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
classDef revision fill:#fff3e0,stroke:#f57c00,stroke-width:2px;
classDef branch fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
classDef comparison fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;
classDef reverse fill:#fff8e1,stroke:#ffa000,stroke-width:2px;
classDef hypothetical fill:#fce4ec,stroke:#c2185b,stroke-width:2px;
classDef tool_call fill:#fff3e0,stroke:#ff9800,stroke-width:2px,stroke-dasharray: 5 5;
classDef thinking_phase fill:#e3f2fd,stroke:#2196f3,stroke-width:3px;
classDef tool_call_phase fill:#fff8e1,stroke:#ff9800,stroke-width:3px;
classDef analysis_phase fill:#e8f5e9,stroke:#4caf50,stroke-width:3px;
"""

    @staticmethod
    def to_mermaid(session: ThinkingSession) -> str:
        """
        导出为 Mermaid 流程图

        支持 Interleaved Thinking 特性：
        - 显示执行阶段（thinking/tool_call/analysis）
        - 显示关联的工具调用节点

        Args:
            session: 思考会话对象

        Returns:
            Mermaid 格式的流程图代码
        """
        if not session.thoughts:
            return (
                """graph TD
    Start["会话暂无思考步骤"]:::regular
    """
                + Visualizer.MERMAID_STYLES
            )

        lines: list[str] = ["graph TD"]

        # 添加节点
        for thought in session.thoughts:
            node_id = Visualizer._mermaid_node_id(thought)
            node_label = Visualizer._escape_mermaid_label(thought.content)
            node_class = thought.type

            # 获取阶段信息 (Interleaved Thinking)
            phase = getattr(thought, "phase", "thinking")
            phase_emoji = SessionFormatter.PHASE_EMOJI.get(phase, "💭")
            phase_name = SessionFormatter.PHASE_NAME.get(phase, "思考阶段")

            # 构建节点标签，包含阶段信息
            if thought.type == "revision":
                revises = thought.revises_thought or 0
                label = f"{node_label}<br/><small>(修订步骤{revises})</small><br/><small>{phase_emoji}{phase_name}</small>"
                lines.append(f'    {node_id}["{label}"]:::{node_class}')
            elif thought.type == "branch":
                branch_from = thought.branch_from_thought or 0
                label = f"{node_label}<br/><small>(分支自步骤{branch_from})</small><br/><small>{phase_emoji}{phase_name}</small>"
                lines.append(f'    {node_id}["{label}"]:::{node_class}')
            else:
                label = f"{node_label}<br/><small>{phase_emoji}{phase_name}</small>"
                lines.append(f'    {node_id}["{label}"]:::{node_class}')

            # 添加工具调用节点 (Interleaved Thinking)
            tool_calls = getattr(thought, "tool_calls", None)
            if tool_calls and session:
                for idx, record_id in enumerate(tool_calls):
                    record = SessionFormatter._find_tool_call_record(session, record_id)
                    if record:
                        tool_node_id = f"{node_id}_TOOL{idx + 1}"
                        tool_name = record.call_data.tool_name
                        status_emoji = SessionFormatter.TOOL_STATUS_EMOJI.get(record.status, "❓")
                        tool_label = f"🔧 {tool_name} {status_emoji}"
                        lines.append(f'    {tool_node_id}["{tool_label}"]:::tool_call')
                        # 连接思考节点到工具调用节点
                        lines.append(f"    {node_id} -.->|调用| {tool_node_id}")

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
                revises_id = Visualizer._find_node_id(
                    session, thought.revises_thought, thought.thought_number
                )
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
    def _find_node_id(
        session: ThinkingSession, target_number: int, current_number: int
    ) -> str | None:
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
        text = text.replace('"', "#quot;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        return text

    @staticmethod
    def to_ascii(session: ThinkingSession) -> str:
        """
        导出为 ASCII 流程图

        支持 Interleaved Thinking 特性：
        - 显示执行阶段（thinking/tool_call/analysis）
        - 显示关联的工具调用信息

        Args:
            session: 思考会话对象

        Returns:
            ASCII 格式的流程图
        """
        if not session.thoughts:
            return (
                "┌─────────────────────────────┐\n"
                "│   会话暂无思考步骤        │\n"
                "└─────────────────────────────┘"
            )

        lines: list[str] = []

        # 为每个思考步骤生成 ASCII 表示
        for thought in session.thoughts:
            block = Visualizer._thought_to_ascii_block(thought, session)
            lines.append(block)

            # 添加连接线
            if thought.type == "regular" and thought.thought_number < session.thought_count():
                lines.append("           │")
                lines.append("           ▼")

        return "\n".join(lines)

    @staticmethod
    def _thought_to_ascii_block(thought: Any, session: ThinkingSession | None = None) -> str:
        """
        将思考步骤转换为 ASCII 块

        支持 Interleaved Thinking 特性：
        - 显示执行阶段信息
        - 显示关联的工具调用

        Args:
            thought: 思考步骤对象
            session: 会话对象（用于获取工具调用详情）

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

        # 获取阶段信息 (Interleaved Thinking)
        phase = getattr(thought, "phase", "thinking")
        phase_emoji = SessionFormatter.PHASE_EMOJI.get(phase, "💭")
        phase_name = SessionFormatter.PHASE_NAME.get(phase, "思考阶段")

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
            "comparison": "对比",
            "reverse": "逆向",
            "hypothetical": "假设",
        }.get(thought.type, "")

        lines.append(f"        {prefix} {emoji} 步骤 {thought.thought_number} [{type_label}]")

        # 第二行：内容
        lines.append(f"        {prefix} {content}")

        # 第三行：阶段信息 (Interleaved Thinking)
        lines.append(f"        {prefix} {phase_emoji} {phase_name}")

        # 第四行：修订/分支信息
        if thought.type == "revision" and thought.revises_thought:
            lines.append(f"        {prefix} → 修订步骤 {thought.revises_thought}")
        elif thought.type == "branch" and thought.branch_from_thought:
            lines.append(f"        {prefix} ← 分支自步骤 {thought.branch_from_thought}")

        # 第五行：工具调用信息 (Interleaved Thinking)
        tool_calls = getattr(thought, "tool_calls", None)
        if tool_calls and session:
            for record_id in tool_calls:
                record = SessionFormatter._find_tool_call_record(session, record_id)
                if record:
                    status_emoji = SessionFormatter.TOOL_STATUS_EMOJI.get(record.status, "❓")
                    tool_name = record.call_data.tool_name
                    # 截断工具名称
                    if len(tool_name) > 20:
                        tool_name = tool_name[:17] + "..."
                    lines.append(f"        {prefix} 🔧 {tool_name} {status_emoji}")

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

        支持 Interleaved Thinking 特性：
        - 显示执行阶段（thinking/tool_call/analysis）
        - 显示关联的工具调用信息

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
            is_last = i == len(session.thoughts) - 1
            prefix = "└──" if is_last else "├──"
            sub_prefix = "    " if is_last else "│   "

            # 根据类型选择 emoji
            emoji = SessionFormatter.TYPE_EMOJI.get(thought.type, "💭")

            # 获取阶段信息 (Interleaved Thinking)
            phase = getattr(thought, "phase", "thinking")
            phase_emoji = SessionFormatter.PHASE_EMOJI.get(phase, "💭")
            phase_name = SessionFormatter.PHASE_NAME.get(phase, "思考阶段")

            # 格式化行
            line = f"{prefix} {emoji} 步骤 {thought.thought_number}: {thought.content[:50]}"
            if len(thought.content) > 50:
                line += "..."

            lines.append(line)

            # 添加阶段信息 (Interleaved Thinking)
            lines.append(f"{sub_prefix}├─ {phase_emoji} {phase_name}")

            # 添加修订/分支信息
            if thought.type == "revision" and thought.revises_thought:
                lines.append(f"{sub_prefix}├─ 📝 修订步骤 {thought.revises_thought}")
            elif thought.type == "branch" and thought.branch_from_thought:
                lines.append(f"{sub_prefix}├─ 🔀 分支自步骤 {thought.branch_from_thought}")

            # 添加工具调用信息 (Interleaved Thinking)
            tool_calls = getattr(thought, "tool_calls", None)
            if tool_calls and session:
                for idx, record_id in enumerate(tool_calls):
                    record = SessionFormatter._find_tool_call_record(session, record_id)
                    if record:
                        status_emoji = SessionFormatter.TOOL_STATUS_EMOJI.get(record.status, "❓")
                        tool_name = record.call_data.tool_name
                        # 最后一个工具调用使用 └─，否则使用 ├─
                        tool_prefix = "└─" if idx == len(tool_calls) - 1 else "├─"
                        lines.append(f"{sub_prefix}{tool_prefix} 🔧 {tool_name} {status_emoji}")

        return "\n".join(lines)
