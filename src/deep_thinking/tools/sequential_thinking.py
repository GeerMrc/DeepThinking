"""
顺序思考工具

实现MCP顺序思考工具，支持六种思考类型：
- 常规思考(Regular): 正常顺序思考步骤 💭
- 修订思考(Revision): 修订之前的思考内容 🔄
- 分支思考(Branch): 从某点分出新思考分支 🌿
- 对比思考(Comparison): 比较多个选项或方案的优劣 ⚖️
- 逆向思考(Reverse): 从结论反推前提条件 🔙
- 假设思考(Hypothetical): 探索假设条件下的影响 🤔

Interleaved Thinking 扩展：
- 执行阶段(thinking/tool_call/analysis)
- 1:N 工具调用追踪和记录（每步骤支持多次工具调用）
- 资源控制和统计
"""

import logging
from datetime import datetime, timezone
from typing import Any, Literal

from deep_thinking.models.config import get_global_config
from deep_thinking.models.thought import ExecutionPhase, Thought
from deep_thinking.models.tool_call import (
    ToolCallData,
    ToolCallRecord,
    ToolResultData,
)
from deep_thinking.server import app, get_storage_manager
from deep_thinking.tools.phase_inference import infer_phase_from_lists

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
    # Interleaved Thinking 参数 (Phase 3.5: 1:N 映射)
    phase: ExecutionPhase | None = None,
    toolCalls: list[dict[str, Any]] | None = None,
    toolResults: list[dict[str, Any]] | None = None,
) -> str:
    """
    执行顺序思考步骤

    支持六种思考类型：常规思考、修订思考、分支思考、对比思考、逆向思考、假设思考。
    支持 Interleaved Thinking 三阶段模型：thinking、tool_call、analysis。

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
        comparisonItems: 对比思考的比较项列表（至少2个，每个1-500字符）
        comparisonDimensions: 对比思考的比较维度列表（最多10个，每个1-50字符）
        comparisonResult: 对比思考的比较结论（1-2000字符）
        reverseFrom: 逆向思考的反推起点思考编号
        reverseTarget: 逆向思考的反推目标描述（1-500字符）
        reverseSteps: 逆向思考的反推步骤列表（最多20个，每个1-500字符）
        hypotheticalCondition: 假设思考的假设条件描述（1-500字符）
        hypotheticalImpact: 假设思考的影响分析（1-2000字符）
        hypotheticalProbability: 假设思考的可能性评估（1-50字符）
        phase: 执行阶段（thinking/tool_call/analysis），None时自动推断
        toolCalls: 多个工具调用参数列表（Interleaved Thinking 1:N 映射）
        toolResults: 多个工具结果参数列表（Interleaved Thinking 1:N 映射）

    Returns:
        思考结果描述，包含当前思考信息和会话状态

    Raises:
        ValueError: 参数验证失败
    """
    # ===== 输入参数边界验证 =====
    # 验证 thoughtNumber 范围（必须 >= 1）
    if thoughtNumber < 1:
        raise ValueError(f"thoughtNumber 必须大于等于 1，当前值: {thoughtNumber}")

    # 验证 totalThoughts 范围（必须 >= thoughtNumber）
    if totalThoughts < thoughtNumber:
        raise ValueError(
            f"totalThoughts ({totalThoughts}) 必须大于等于 thoughtNumber ({thoughtNumber})"
        )

    # 验证 thought 内容非空
    if not thought or not thought.strip():
        raise ValueError("thought 内容不能为空")

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

    # ===== 配置限制验证 =====
    # 无论 needsMoreThoughts 是否为 True，都验证 totalThoughts 不超过配置限制
    if totalThoughts > max_thoughts_limit:
        raise ValueError(f"totalThoughts ({totalThoughts}) 超过最大限制 ({max_thoughts_limit})")

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
    thought_type: Literal[
        "regular", "revision", "branch", "comparison", "reverse", "hypothetical"
    ] = "regular"

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

    # ===== Interleaved Thinking: 阶段推断 =====
    # 如果 phase 参数为 None，则自动推断执行阶段
    inferred_phase: ExecutionPhase
    if phase is not None:
        inferred_phase = phase
    else:
        inferred_phase = infer_phase_from_lists(tool_calls=toolCalls, tool_results=toolResults)

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
        # Interleaved Thinking 字段
        phase=inferred_phase,
        tool_calls=[],  # 稍后填充 record_id
        timestamp=datetime.now(timezone.utc),
    )

    # 添加思考步骤到会话
    manager.add_thought(session_id, thought_obj)

    # ===== Interleaved Thinking: 工具调用记录存储 (1:N 映射) =====
    tool_call_records: list[ToolCallRecord] = []

    # 如果有工具调用参数，创建并存储工具调用记录
    if toolCalls is not None and len(toolCalls) > 0:
        # ===== 每步骤调用数量检查 (Phase 3.6.3) =====
        max_tool_calls_per_thought = config.max_tool_calls_per_thought
        if len(toolCalls) > max_tool_calls_per_thought:
            logger.warning(
                f"会话 {session_id} 单步骤工具调用数超限: "
                f"请求 {len(toolCalls)} > 每步骤上限 {max_tool_calls_per_thought}"
            )
            result = [
                f"## 思考步骤 {thoughtNumber}/{totalThoughts}",
                "",
                f"**类型**: {get_type_name(thought_type)}",
                f"**阶段**: {get_phase_display(inferred_phase)}",
                "",
                f"{thought}",
                "",
                "---",
                "**会话信息**:",
                f"- 会话ID: {session_id}",
                "",
                f"⚠️ 警告：单步骤工具调用数超限，请求 {len(toolCalls)} > "
                f"每步骤上限 {max_tool_calls_per_thought}。",
            ]
            return "\n".join(result)

        # ===== 资源控制检查 (Phase 3.5.7: 批量检查配额) =====
        current_session = manager.get_session(session_id)
        if current_session is not None:
            current_tool_calls = current_session.statistics.total_tool_calls
            max_tool_calls_limit = config.max_tool_calls
            new_calls_count = len(toolCalls)

            if current_tool_calls + new_calls_count > max_tool_calls_limit:
                logger.warning(
                    f"会话 {session_id} 工具调用次数将超限: "
                    f"当前 {current_tool_calls} + 新增 {new_calls_count} > 上限 {max_tool_calls_limit}"
                )
                result = [
                    f"## 思考步骤 {thoughtNumber}/{totalThoughts}",
                    "",
                    f"**类型**: {get_type_name(thought_type)}",
                    f"**阶段**: {get_phase_display(inferred_phase)}",
                    "",
                    f"{thought}",
                    "",
                    "---",
                    "**会话信息**:",
                    f"- 会话ID: {session_id}",
                    f"- 总思考数: {current_session.thought_count()}",
                    f"- 工具调用数: {current_tool_calls}",
                    "",
                    f"⚠️ 警告：工具调用次数将超限，当前 {current_tool_calls} + "
                    f"新增 {new_calls_count} > 上限 {max_tool_calls_limit}。",
                ]
                return "\n".join(result)

        # 创建 tool_call_id 到 result 的映射
        results_map: dict[str, dict[str, Any]] = {}
        if toolResults is not None:
            for result_item in toolResults:
                call_id = result_item.get("call_id", "")
                if call_id:
                    results_map[call_id] = result_item

        # 循环处理多个工具调用 (Phase 3.5.5)
        for i, call_item in enumerate(toolCalls):
            # 从 toolCall 字典创建 ToolCallData
            call_data = ToolCallData(
                tool_name=call_item.get("name", call_item.get("tool_name", "unknown")),
                arguments=call_item.get("arguments", call_item.get("args", {})),
            )

            # 查找对应的工具结果
            result_data: ToolResultData | None = None
            # 优先使用 call_id 匹配
            call_id = call_item.get("call_id", call_data.call_id)
            if call_id in results_map:
                result_item = results_map[call_id]
                result_data = ToolResultData(
                    call_id=call_id,
                    success=result_item.get("success", True),
                    result=result_item.get("result"),
                    execution_time_ms=result_item.get("execution_time_ms"),
                    from_cache=result_item.get("from_cache", False),
                )
            # 其次使用索引匹配
            elif toolResults is not None and i < len(toolResults):
                result_item = toolResults[i]
                result_data = ToolResultData(
                    call_id=result_item.get("call_id", call_data.call_id),
                    success=result_item.get("success", True),
                    result=result_item.get("result"),
                    execution_time_ms=result_item.get("execution_time_ms"),
                    from_cache=result_item.get("from_cache", False),
                )

            # 创建工具调用记录
            record = ToolCallRecord(
                thought_number=thoughtNumber,
                call_data=call_data,
                result_data=result_data,
                status="completed" if result_data else "pending",
            )
            tool_call_records.append(record)

            # 重新获取会话并添加记录
            session = manager.get_session(session_id)
            if session is not None:
                session.add_tool_call_record(record)
                # 更新统计信息
                session.update_statistics()
                manager.update_session(session)

        # 填充 Thought.tool_calls 字段 (Phase 3.5.6)
        record_ids = [record.record_id for record in tool_call_records]
        thought_obj.tool_calls = record_ids
        manager.update_thought(session_id, thought_obj)

    # 获取会话状态
    session = manager.get_session(session_id)
    if session is None:
        raise RuntimeError("会话丢失")

    # 构建返回结果
    result_parts = [
        f"## 思考步骤 {thoughtNumber}/{totalThoughts}",
        "",
        f"**类型**: {get_type_name(thought_type)}",
        f"**阶段**: {get_phase_display(inferred_phase)}",
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

    # ===== Interleaved Thinking: 添加多工具调用信息 (Phase 3.5.8) =====
    if len(tool_call_records) > 0:
        result_parts.append(f"🔧 工具调用 ({len(tool_call_records)}个)")
        for i, record in enumerate(tool_call_records, 1):
            result_parts.append(f"  {i}. **{record.call_data.tool_name}** - {record.status}")
            if record.result_data:
                result_parts.append(f"     成功: {'是' if record.result_data.success else '否'}")
                if record.result_data.execution_time_ms:
                    result_parts.append(f"     耗时: {record.result_data.execution_time_ms:.2f}ms")
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
        ]
    )

    # 添加工具调用统计信息（Interleaved Thinking）
    if session.statistics.total_tool_calls > 0:
        stats = session.statistics
        result_parts.extend(
            [
                f"- 工具调用数: {stats.total_tool_calls}",
                f"  - 成功: {stats.successful_tool_calls}, 失败: {stats.failed_tool_calls}, 缓存命中: {stats.cached_tool_calls}",
            ]
        )

    result_parts.append("")

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


def get_phase_display(phase: ExecutionPhase) -> str:
    """
    获取执行阶段的显示名称

    Args:
        phase: 执行阶段

    Returns:
        阶段显示名称
    """
    phase_names: dict[ExecutionPhase, str] = {
        "thinking": "思考 🧠",
        "tool_call": "工具调用 🔧",
        "analysis": "分析 📊",
    }
    return phase_names.get(phase, "思考 🧠")


# 注册工具
__all__ = ["sequential_thinking"]
