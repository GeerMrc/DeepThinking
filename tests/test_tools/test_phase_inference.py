"""
阶段推断模块单元测试 (Interleaved Thinking)
"""

import pytest

from deep_thinking.tools.phase_inference import (
    get_phase_description,
    infer_phase,
    infer_phase_from_content,
    validate_phase_transition,
)


class TestInferPhase:
    """infer_phase 函数测试"""

    def test_infer_phase_no_args(self):
        """测试无参数时返回 thinking"""
        result = infer_phase()
        assert result == "thinking"

    def test_infer_phase_with_tool_call(self):
        """测试有 tool_call 参数时返回 tool_call"""
        result = infer_phase(tool_call={"name": "search", "arguments": {"q": "test"}})
        assert result == "tool_call"

    def test_infer_phase_with_empty_tool_call(self):
        """测试空 tool_call 参数时返回 thinking"""
        result = infer_phase(tool_call={})
        assert result == "thinking"

    def test_infer_phase_with_none_tool_call(self):
        """测试 None tool_call 参数时返回 thinking"""
        result = infer_phase(tool_call=None)
        assert result == "thinking"

    def test_infer_phase_with_tool_result(self):
        """测试有 tool_result 参数时返回 analysis"""
        result = infer_phase(tool_result={"call_id": "123", "result": "data"})
        assert result == "analysis"

    def test_infer_phase_with_empty_tool_result(self):
        """测试空 tool_result 参数时返回 thinking"""
        result = infer_phase(tool_result={})
        assert result == "thinking"

    def test_infer_phase_with_none_tool_result(self):
        """测试 None tool_result 参数时返回 thinking"""
        result = infer_phase(tool_result=None)
        assert result == "thinking"

    def test_infer_phase_both_args(self):
        """测试同时有 tool_call 和 tool_result 时返回 analysis（tool_result 优先）"""
        result = infer_phase(
            tool_call={"name": "search"},
            tool_result={"call_id": "123", "result": "data"},
        )
        assert result == "analysis"

    def test_infer_phase_with_no_args(self):
        """测试无参数时返回 thinking（默认行为）"""
        result = infer_phase()
        assert result == "thinking"

    def test_infer_phase_priority(self):
        """测试推断优先级：tool_result > tool_call > thinking"""
        # 只有 tool_call
        assert infer_phase(tool_call={"name": "test"}) == "tool_call"

        # 只有 tool_result
        assert infer_phase(tool_result={"result": "data"}) == "analysis"

        # 两者都有，tool_result 优先
        assert infer_phase(
            tool_call={"name": "test"},
            tool_result={"result": "data"},
        ) == "analysis"


class TestInferPhaseFromContent:
    """infer_phase_from_content 函数测试"""

    def test_empty_content(self):
        """测试空内容返回 thinking"""
        result = infer_phase_from_content("")
        assert result == "thinking"

    def test_thinking_content(self):
        """测试纯思考内容"""
        result = infer_phase_from_content("我需要分析这个问题...")
        assert result == "thinking"

    def test_tool_call_keywords_chinese(self):
        """测试中文工具调用关键词"""
        keywords = [
            "我需要调用工具来搜索",
            "执行工具获取数据",
            "使用工具进行计算",
            "需要调用外部API",
        ]
        for content in keywords:
            result = infer_phase_from_content(content)
            assert result == "tool_call", f"Failed for: {content}"

    def test_tool_call_keywords_english(self):
        """测试英文工具调用关键词"""
        keywords = [
            "I need to call tool",
            "invoke tool to get data",
        ]
        for content in keywords:
            result = infer_phase_from_content(content)
            assert result == "tool_call", f"Failed for: {content}"

    def test_analysis_keywords_chinese(self):
        """测试中文分析关键词"""
        keywords = [
            "根据结果分析",
            "工具返回了数据",
            "分析结果显示",
            "执行完毕后",
            "工具返回的信息",
        ]
        for content in keywords:
            result = infer_phase_from_content(content)
            assert result == "analysis", f"Failed for: {content}"

    def test_analysis_keywords_english(self):
        """测试英文分析关键词"""
        keywords = [
            "analyze result from tool",
            "tool returned data",
            "based on result",
        ]
        for content in keywords:
            result = infer_phase_from_content(content)
            assert result == "analysis", f"Failed for: {content}"

    def test_analysis_priority_over_tool_call(self):
        """测试分析关键词优先级高于工具调用关键词"""
        # 同时包含两种关键词
        content = "调用工具后，根据结果分析"
        result = infer_phase_from_content(content)
        assert result == "analysis"


class TestValidatePhaseTransition:
    """validate_phase_transition 函数测试"""

    def test_valid_thinking_transitions(self):
        """测试 thinking 的合法转换"""
        assert validate_phase_transition("thinking", "thinking") is True
        assert validate_phase_transition("thinking", "tool_call") is True

    def test_invalid_thinking_transitions(self):
        """测试 thinking 的非法转换"""
        assert validate_phase_transition("thinking", "analysis") is False

    def test_valid_tool_call_transitions(self):
        """测试 tool_call 的合法转换"""
        assert validate_phase_transition("tool_call", "analysis") is True

    def test_invalid_tool_call_transitions(self):
        """测试 tool_call 的非法转换"""
        assert validate_phase_transition("tool_call", "thinking") is False
        assert validate_phase_transition("tool_call", "tool_call") is False

    def test_valid_analysis_transitions(self):
        """测试 analysis 的合法转换"""
        assert validate_phase_transition("analysis", "thinking") is True
        assert validate_phase_transition("analysis", "tool_call") is True
        assert validate_phase_transition("analysis", "analysis") is True

    def test_full_workflow_transitions(self):
        """测试完整工作流的阶段转换"""
        # thinking -> tool_call
        assert validate_phase_transition("thinking", "tool_call") is True

        # tool_call -> analysis
        assert validate_phase_transition("tool_call", "analysis") is True

        # analysis -> thinking
        assert validate_phase_transition("analysis", "thinking") is True

        # 或者继续调用工具
        assert validate_phase_transition("analysis", "tool_call") is True


class TestGetPhaseDescription:
    """get_phase_description 函数测试"""

    def test_thinking_description(self):
        """测试 thinking 阶段描述"""
        desc = get_phase_description("thinking")
        assert "思考阶段" in desc
        assert "纯思维推理" in desc

    def test_tool_call_description(self):
        """测试 tool_call 阶段描述"""
        desc = get_phase_description("tool_call")
        assert "工具调用阶段" in desc
        assert "外部工具" in desc

    def test_analysis_description(self):
        """测试 analysis 阶段描述"""
        desc = get_phase_description("analysis")
        assert "分析阶段" in desc
        assert "分析工具调用结果" in desc

    def test_unknown_phase(self):
        """测试未知阶段"""
        # 类型检查会阻止传入无效值，但测试默认行为
        # 由于使用 Literal 类型，这里只测试已知的阶段
        for phase in ["thinking", "tool_call", "analysis"]:
            desc = get_phase_description(phase)
            assert isinstance(desc, str)
            assert len(desc) > 0


class TestPhaseInferenceIntegration:
    """阶段推断集成测试"""

    def test_interleaved_thinking_workflow(self):
        """测试交错思考工作流"""
        # 第一步：纯思考
        phase1 = infer_phase()
        assert phase1 == "thinking"

        # 第二步：决定调用工具
        phase2 = infer_phase(tool_call={"name": "search", "arguments": {"q": "test"}})
        assert phase2 == "tool_call"
        assert validate_phase_transition(phase1, phase2) is True

        # 第三步：分析结果
        phase3 = infer_phase(tool_result={"call_id": "123", "result": "data"})
        assert phase3 == "analysis"
        assert validate_phase_transition(phase2, phase3) is True

        # 第四步：继续思考
        phase4 = infer_phase()
        assert phase4 == "thinking"
        assert validate_phase_transition(phase3, phase4) is True

    def test_multiple_tool_calls_workflow(self):
        """测试多次工具调用工作流"""
        phases = []

        # 思考 -> 调用1
        phases.append(infer_phase())
        phases.append(infer_phase(tool_call={"name": "tool1"}))

        # 调用1 -> 分析1
        phases.append(infer_phase(tool_result={"result": "data1"}))

        # 分析1 -> 调用2
        phases.append(infer_phase(tool_call={"name": "tool2"}))

        # 调用2 -> 分析2
        phases.append(infer_phase(tool_result={"result": "data2"}))

        # 验证转换
        expected_phases = ["thinking", "tool_call", "analysis", "tool_call", "analysis"]
        assert phases == expected_phases

        # 验证转换合法性
        for i in range(len(phases) - 1):
            assert validate_phase_transition(phases[i], phases[i + 1]) is True
