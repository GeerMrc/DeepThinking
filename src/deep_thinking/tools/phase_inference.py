"""
阶段推断模块 (Interleaved Thinking)

提供自动推断执行阶段的功能。
根据工具调用参数自动判断当前处于 thinking/tool_call/analysis 阶段。
"""

from typing import Any

from deep_thinking.models.thought import ExecutionPhase


def infer_phase(
    tool_call: dict[str, Any] | None = None,
    tool_result: dict[str, Any] | None = None,
) -> ExecutionPhase:
    """
    自动推断执行阶段

    根据传入的参数自动判断当前思考步骤所处的执行阶段。

    推断规则（按优先级）：
    1. 如果有 tool_result 参数 → analysis 阶段（分析工具结果）
    2. 如果有 tool_call 参数 → tool_call 阶段（调用工具）
    3. 其他情况 → thinking 阶段（纯思考）

    Args:
        tool_call: 工具调用参数，包含工具名称和参数
        tool_result: 工具结果参数，包含调用结果

    Returns:
        推断出的执行阶段：thinking/tool_call/analysis

    Example:
        >>> infer_phase()  # doctest: +SKIP
        'thinking'
        >>> infer_phase(tool_call={"name": "search", "arguments": {"q": "test"}})  # doctest: +SKIP
        'tool_call'
        >>> infer_phase(tool_result={"call_id": "123", "result": "data"})  # doctest: +SKIP
        'analysis'
    """
    # 规则 1: 有工具结果 → analysis 阶段
    if tool_result is not None and tool_result:
        return "analysis"

    # 规则 2: 有工具调用 → tool_call 阶段
    if tool_call is not None and tool_call:
        return "tool_call"

    # 规则 3: 默认 → thinking 阶段
    return "thinking"


def infer_phase_from_content(content: str) -> ExecutionPhase:
    """
    根据思考内容推断执行阶段（辅助函数）

    通过分析思考内容中的关键词来推断阶段。
    这是一个辅助函数，主要用于测试和边界情况处理。

    关键词规则：
    - 包含"调用工具"、"执行工具"等 → tool_call
    - 包含"分析结果"、"工具返回"、"根据结果"等 → analysis
    - 其他 → thinking

    Args:
        content: 思考内容

    Returns:
        推断出的执行阶段
    """
    if not content:
        return "thinking"

    content_lower = content.lower()

    # tool_call 关键词
    tool_call_keywords = [
        "调用工具",
        "执行工具",
        "使用工具",
        "call tool",
        "invoke tool",
        "需要调用",
        "需要执行",
    ]

    # analysis 关键词
    analysis_keywords = [
        "分析结果",
        "工具返回",
        "根据结果",
        "结果显示",
        "返回了",
        "analyze result",
        "tool returned",
        "based on result",
        "结果显示",
        "执行完毕",
    ]

    # 检查 analysis 关键词（优先级更高）
    for keyword in analysis_keywords:
        if keyword.lower() in content_lower:
            return "analysis"

    # 检查 tool_call 关键词
    for keyword in tool_call_keywords:
        if keyword.lower() in content_lower:
            return "tool_call"

    return "thinking"


def validate_phase_transition(
    current_phase: ExecutionPhase,
    next_phase: ExecutionPhase,
) -> bool:
    """
    验证阶段转换是否合法

    有效的阶段转换：
    - thinking → thinking (继续思考)
    - thinking → tool_call (决定调用工具)
    - tool_call → analysis (分析工具结果)
    - analysis → thinking (继续思考)
    - analysis → tool_call (再次调用工具)
    - analysis → analysis (继续分析)

    无效的阶段转换：
    - tool_call → thinking (必须先分析结果)
    - tool_call → tool_call (必须先分析结果)

    Args:
        current_phase: 当前阶段
        next_phase: 下一阶段

    Returns:
        True 如果转换合法，False 否则
    """
    # 定义合法的状态转换
    valid_transitions: dict[ExecutionPhase, set[ExecutionPhase]] = {
        "thinking": {"thinking", "tool_call"},
        "tool_call": {"analysis"},
        "analysis": {"thinking", "tool_call", "analysis"},
    }

    return next_phase in valid_transitions.get(current_phase, set())


def get_phase_description(phase: ExecutionPhase) -> str:
    """
    获取阶段的描述文本

    Args:
        phase: 执行阶段

    Returns:
        阶段的中文描述
    """
    descriptions: dict[ExecutionPhase, str] = {
        "thinking": "思考阶段：进行纯思维推理，不涉及工具调用",
        "tool_call": "工具调用阶段：准备调用外部工具获取信息或执行操作",
        "analysis": "分析阶段：分析工具调用结果，整合信息",
    }
    return descriptions.get(phase, "未知阶段")


__all__ = [
    "infer_phase",
    "infer_phase_from_content",
    "validate_phase_transition",
    "get_phase_description",
]
