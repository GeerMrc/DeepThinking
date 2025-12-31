"""
模板工具

提供模板应用和管理的 MCP 工具。
"""

import logging
from uuid import uuid4

from deep_thinking.models.thought import Thought
from deep_thinking.server import app, get_storage_manager
from deep_thinking.utils.template_loader import TemplateLoader

logger = logging.getLogger(__name__)


@app.tool()
async def apply_template(
    template_id: str,
    context: str = "",
    session_name: str | None = None,
) -> str:
    """
    应用思考模板创建新会话

    模板提供预设的思考框架，引导您按特定模式进行思考。

    可用模板:
    - problem_solving: 问题求解模板 - 系统地分析和解决问题
    - decision_making: 决策模板 - 帮助做出理性决策
    - analysis: 分析模板 - 深入分析复杂问题

    Args:
        template_id: 模板ID（如 problem_solving, decision_making, analysis）
        context: 当前问题或任务的上下文描述（可选）
        session_name: 会话名称（可选，默认使用模板名称）

    Returns:
        创建的会话信息和模板引导步骤

    Raises:
        ValueError: 模板不存在或参数无效

    Examples:
        >>> # 应用问题求解模板
        >>> await apply_template("problem_solving", "如何优化团队协作效率")
        >>> # 应用决策模板
        >>> await apply_template("decision_making", "选择哪个技术方案")
    """
    manager = get_storage_manager()

    # 加载模板
    loader = TemplateLoader()
    try:
        template = loader.load_template(template_id)
    except FileNotFoundError as e:
        # 提供可用模板列表
        available = loader.list_available_templates()
        raise ValueError(
            f"{str(e)}\n\n可用模板:\n" + "\n".join(f"  - {tid}" for tid in available)
        ) from e

    # 生成会话名称
    if not session_name:
        session_name = f"{template['name']} - {str(uuid4())[:8]}"

    # 创建会话
    session = manager.create_session(
        name=session_name,
        description=f"使用 {template['name']} 处理: {context or '自定义思考'}",
        metadata={
            "template_id": template_id,
            "template_name": template["name"],
            "context": context,
        },
    )

    # 获取模板步骤
    steps = template.get("structure", {}).get("steps", [])

    # 将模板步骤转换为思考步骤
    for step_data in steps:
        # 根据上下文定制提示词
        prompt = step_data["prompt"]
        if context and step_data["step_number"] == 1:
            # 在第一步插入上下文
            prompt = f"{prompt}\n\n当前上下文: {context}"

        thought = Thought(
            thought_number=step_data["step_number"],
            content=prompt,
            type=step_data.get("type", "regular"),
            is_revision=step_data.get("type") == "revision",
            revises_thought=step_data.get("revises_thought"),
            branch_from_thought=step_data.get("branch_from_thought"),
            branch_id=step_data.get("branch_id"),
        )
        session.add_thought(thought)

    # 保存会话
    manager.update_session(session)

    # 构建返回结果
    parts = [
        f"## 📋 {template['name']} 已应用",
        "",
        f"**会话ID**: {session.session_id}",
        f"**会话名称**: {session.name}",
        f"**模板描述**: {template['description']}",
        f"**步骤数**: {len(steps)}",
        "",
    ]

    if context:
        parts.append(f"**上下文**: {context}")
        parts.append("")

    parts.append("### 🎯 思考步骤")
    parts.append("")

    for i, step_data in enumerate(steps, 1):
        emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"][i - 1] if i <= 10 else f"{i}."
        parts.append(f"{emoji} {step_data['prompt']}")
        parts.append("")

    parts.append("---")
    parts.append(f"会话已创建！使用会话ID `{session.session_id}` 继续思考。")
    parts.append("")
    parts.append("您可以:")
    parts.append("1. 使用 `sequential_thinking` 工具继续思考")
    parts.append("2. 使用 `get_session` 查看会话详情")
    parts.append("3. 使用 `export_session` 导出会话")
    parts.append("4. 使用 `visualize_session` 可视化思考流程")

    return "\n".join(parts)


@app.tool()
async def list_templates(
    category: str | None = None,
) -> str:
    """
    列出所有可用的思考模板

    Args:
        category: 过滤类别（problem_solving/decision/analysis），为空则显示所有

    Returns:
        模板列表

    Examples:
        >>> # 列出所有模板
        >>> await list_templates()
        >>> # 只列决策类模板
        >>> await list_templates("decision")
    """
    loader = TemplateLoader()

    templates = loader.list_templates()

    # 按类别过滤
    if category:
        category_map = {
            "problem": "problem_solving",
            "solving": "problem_solving",
            "decision": "decision",
            "making": "decision",
            "analysis": "analysis",
            "analytical": "analysis",
        }

        filter_category = category_map.get(category.lower(), category.lower())
        templates = [t for t in templates if t.get("category") == filter_category]

    # 构建返回结果
    parts = [
        "## 📚 可用思考模板",
        "",
    ]

    if not templates:
        parts.append("没有找到匹配的模板。")
        return "\n".join(parts)

    if category:
        parts.append(f"**类别过滤**: {category}")
        parts.append("")

    parts.append(f"**总数**: {len(templates)}")
    parts.append("")

    for i, template in enumerate(templates, 1):
        # 模板图标
        icon_map = {
            "problem_solving": "🔧",
            "decision": "🎯",
            "analysis": "🔍",
        }
        icon = icon_map.get(template.get("category", ""), "📋")

        parts.append(f"{i}. {icon} **{template['name']}**")
        parts.append(f"   - ID: `{template['template_id']}`")
        parts.append(f"   - 描述: {template['description']}")

        metadata = template.get("metadata", {})
        if "tags" in metadata:
            parts.append(f"   - 标签: {', '.join(metadata['tags'])}")

        parts.append("")

    parts.append("---")
    parts.append("使用 `apply_template` 工具来应用模板。")
    parts.append("")
    parts.append("示例:")
    parts.append("```")
    parts.append(f"apply_template(\"{templates[0]['template_id']}\", \"我的问题上下文\")")
    parts.append("```")

    return "\n".join(parts)


def _normalize_format(format_type: str) -> str:
    """
    标准化格式类型（用于其他工具）

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


# 注册工具
__all__ = [
    "apply_template",
    "list_templates",
]
