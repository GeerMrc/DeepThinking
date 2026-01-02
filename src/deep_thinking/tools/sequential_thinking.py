"""
顺序思考工具

实现MCP顺序思考工具，支持六种思考类型：
- 常规思考(Regular): 正常顺序思考步骤 💭
- 修订思考(Revision): 修订之前的思考内容 🔄
- 分支思考(Branch): 从某点分出新思考分支 🌿
- 对比思考(Comparison): 比较多个选项或方案的优劣 ⚖️
- 逆向思考(Reverse): 从结论反推前提条件 🔙
- 假设思考(Hypothetical): 探索假设条件下的影响 🤔
"""

import logging
from datetime import datetime, timezone
from typing import Literal

from deep_thinking.models.config import get_global_config
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
    needsMoreThoughts: bool = False,
    # Comparison类型参数
    comparisonItems: list[str] | None = None,
    comparisonDimensions: list[str] | None = None,
    comparisonResult: str | None = None,
    # Reverse类型参数
    reverseFrom: int | None = None,
    reverseTarget: str | None = None,
    reverseSteps: list[str] | None = None,
    # Hypothetical类型参数
    hypotheticalCondition: str | None = None,
    hypotheticalImpact: str | None = None,
    hypotheticalProbability: str | None = None,
) -> str:
    """
    执行顺序思考步骤

    支持六种思考类型：常规思考、修订思考、分支思考、对比思考、逆向思考、假设思考。

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
        needsMoreThoughts: 是否需要增加总思考步骤数
        # Comparison类型参数
        comparisonItems: 对比思考的比较项列表（至少2个，每个1-500字符）
        comparisonDimensions: 对比思考的比较维度列表（最多10个，每个1-50字符）
        comparisonResult: 对比思考的比较结论（1-2000字符）
        # Reverse类型参数
        reverseFrom: 逆向思考的反推起点思考编号
        reverseTarget: 逆向思考的反推目标描述（1-500字符）
        reverseSteps: 逆向思考的反推步骤列表（最多20个，每个1-500字符）
        # Hypothetical类型参数
        hypotheticalCondition: 假设思考的假设条件描述（1-500字符）
        hypotheticalImpact: 假设思考的影响分析（1-2000字符）
        hypotheticalProbability: 假设思考的可能性评估（1-50字符）

    Returns:
        思考结果描述，包含当前思考信息和会话状态

    Raises:
        ValueError: 参数验证失败
    """
    manager = get_storage_manager()

    # 获取或创建会话
    session = manager.get_session(session_id)

    if session is None:
        session = manager.create_session(
            name=f"会话-{session_id[:8]}",
            description="自动创建的思考会话",
            metadata={"session_type": "sequential_thinking"},
            session_id=session_id,
        )

    # 处理 needsMoreThoughts 功能
    original_total = totalThoughts

    # 从全局配置获取思考限制参数
    config = get_global_config()
    max_thoughts_limit = config.max_thoughts  # 最大思考步骤限制
    thoughts_increment = config.thoughts_increment  # 每次增加的思考步骤数

    if needsMoreThoughts:
        # 检查是否超过最大限制
        if totalThoughts >= max_thoughts_limit:
            logger.warning(f"思考步骤数已达上限 {max_thoughts_limit}，不再增加")
            result = [
                f"## 思考步骤 {thoughtNumber}/{totalThoughts}",
                "",
                "**类型**: 常规思考 💭",
                "",
                f"{thought}",
                "",
                "---",
                "**会话信息**:",
                f"- 会话ID: {session_id}",
                f"- 总思考数: {session.thought_count()}",
                f"- 预计总数: {totalThoughts}",
                "",
                f"⚠️ 警告：思考步骤数已达上限 {max_thoughts_limit}，无法继续增加。",
            ]
            return "\n".join(result)

        # 增加思考步骤总数
        new_total = min(totalThoughts + thoughts_increment, max_thoughts_limit)
        totalThoughts = new_total

        # 记录调整历史到会话元数据
        if "total_thoughts_history" not in session.metadata:
            session.metadata["total_thoughts_history"] = []

        session.metadata["total_thoughts_history"].append(
            {
                "original_total": original_total,
                "new_total": new_total,
                "thought_number": thoughtNumber,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # 更新会话
        manager.update_session(session)
        logger.info(f"会话 {session_id} 调整思考步骤数: {original_total} -> {new_total}")

    # 确定思考类型
    # 优先级: Revision > Branch > Comparison > Reverse > Hypothetical > Regular
    thought_type: Literal["regular", "revision", "branch", "comparison", "reverse", "hypothetical"] = "regular"

    if isRevision:
        thought_type = "revision"
    elif branchFromThought is not None:
        thought_type = "branch"
    elif comparisonItems is not None and len(comparisonItems) >= 2:
        thought_type = "comparison"
    elif reverseTarget is not None:
        thought_type = "reverse"
    elif hypotheticalCondition is not None:
        thought_type = "hypothetical"

    # 创建思考步骤对象
    thought_obj = Thought(
        thought_number=thoughtNumber,
        content=thought,
        type=thought_type,
        is_revision=isRevision,
        revises_thought=revisesThought,
        branch_from_thought=branchFromThought,
        branch_id=branchId,
        # Comparison类型字段
        comparison_items=comparisonItems,
        comparison_dimensions=comparisonDimensions,
        comparison_result=comparisonResult,
        # Reverse类型字段
        reverse_from=reverseFrom,
        reverse_target=reverseTarget,
        reverse_steps=reverseSteps,
        # Hypothetical类型字段
        hypothetical_condition=hypotheticalCondition,
        hypothetical_impact=hypotheticalImpact,
        hypothetical_probability=hypotheticalProbability,
        timestamp=datetime.now(timezone.utc),
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

    # 添加对比思考信息
    if thought_type == "comparison" and comparisonItems:
        result_parts.append("⚖️ 对比思考")
        result_parts.append(f"**比较项** ({len(comparisonItems)}个):")
        for i, item in enumerate(comparisonItems, 1):
            result_parts.append(f"  {i}. {item}")
        if comparisonDimensions:
            result_parts.append(f"**比较维度**: {', '.join(comparisonDimensions)}")
        if comparisonResult:
            result_parts.append(f"**比较结论**: {comparisonResult}")
        result_parts.append("")

    # 添加逆向思考信息
    if thought_type == "reverse":
        result_parts.append("🔙 逆向思考")
        if reverseFrom is not None:
            result_parts.append(f"**反推起点**: 思考步骤 {reverseFrom}")
        if reverseTarget:
            result_parts.append(f"**反推目标**: {reverseTarget}")
        if reverseSteps:
            result_parts.append(f"**反推步骤** ({len(reverseSteps)}个):")
            for i, step in enumerate(reverseSteps, 1):
                result_parts.append(f"  {i}. {step}")
        result_parts.append("")

    # 添加假设思考信息
    if thought_type == "hypothetical":
        result_parts.append("🤔 假设思考")
        if hypotheticalCondition:
            result_parts.append(f"**假设条件**: {hypotheticalCondition}")
        if hypotheticalImpact:
            result_parts.append(f"**影响分析**: {hypotheticalImpact}")
        if hypotheticalProbability:
            result_parts.append(f"**可能性**: {hypotheticalProbability}")
        result_parts.append("")

    # 添加思考步骤调整信息
    if needsMoreThoughts and totalThoughts > original_total:
        result_parts.append(f"📈 思考步骤总数已调整: {original_total} → {totalThoughts}")
        result_parts.append("")

    # 添加会话状态
    result_parts.extend(
        [
            "---",
            "**会话信息**:",
            f"- 会话ID: {session_id}",
            f"- 总思考数: {session.thought_count()}",
            f"- 预计总数: {totalThoughts}",
            "",
        ]
    )

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
        "comparison": "对比思考 ⚖️",
        "reverse": "逆向思考 🔙",
        "hypothetical": "假设思考 🤔",
    }
    return type_names.get(thought_type, "常规思考 💭")


# 注册工具
__all__ = ["sequential_thinking"]
