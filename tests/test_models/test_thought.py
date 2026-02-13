"""
思考步骤模型单元测试
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from deep_thinking.models.thought import (
    ExecutionPhase,
    Thought,
    ThoughtCreate,
    ThoughtUpdate,
)


class TestExecutionPhase:
    """ExecutionPhase类型测试 (Interleaved Thinking)"""

    def test_execution_phase_type_definition(self):
        """测试ExecutionPhase类型定义存在"""
        # 验证类型已定义
        assert ExecutionPhase is not None

    def test_execution_phase_valid_values(self):
        """测试ExecutionPhase有效值"""
        # 验证三种执行阶段都是有效值
        thinking_phase: ExecutionPhase = "thinking"
        tool_call_phase: ExecutionPhase = "tool_call"
        analysis_phase: ExecutionPhase = "analysis"

        assert thinking_phase == "thinking"
        assert tool_call_phase == "tool_call"
        assert analysis_phase == "analysis"


class TestThoughtInterleaved:
    """Thought Interleaved Thinking 功能测试"""

    def test_thought_has_phase_field(self):
        """测试Thought包含phase字段"""
        thought = Thought(thought_number=1, content="测试")
        assert hasattr(thought, "phase")
        assert thought.phase == "thinking"  # 默认值

    def test_thought_has_tool_calls_field(self):
        """测试Thought包含tool_calls字段"""
        thought = Thought(thought_number=1, content="测试")
        assert hasattr(thought, "tool_calls")
        assert thought.tool_calls == []

    def test_thought_phase_validation(self):
        """测试phase字段验证"""
        # 有效phase值
        for phase in ["thinking", "tool_call", "analysis"]:
            thought = Thought(thought_number=1, content="测试", phase=phase)
            assert thought.phase == phase

    def test_thought_tool_calls_with_records(self):
        """测试tool_calls字段存储记录ID"""
        thought = Thought(
            thought_number=1,
            content="需要调用工具的思考",
            phase="tool_call",
            tool_calls=["record-id-1", "record-id-2"],
        )
        assert thought.phase == "tool_call"
        assert len(thought.tool_calls) == 2

    def test_thought_to_dict_includes_new_fields(self):
        """测试to_dict包含新字段"""
        thought = Thought(
            thought_number=1,
            content="测试",
            phase="analysis",
            tool_calls=["record-1"],
        )
        data = thought.to_dict()

        assert "phase" in data
        assert data["phase"] == "analysis"
        assert "tool_calls" in data
        assert data["tool_calls"] == ["record-1"]

    def test_thoughtcreate_with_phase(self):
        """测试ThoughtCreate支持phase字段"""
        create_data = ThoughtCreate(
            thought_number=1,
            content="测试",
            phase="tool_call",
        )
        thought = create_data.to_thought()
        assert thought.phase == "tool_call"

    def test_thoughtupdate_with_phase(self):
        """测试ThoughtUpdate支持phase字段"""
        update_data = ThoughtUpdate(phase="analysis")
        assert update_data.phase == "analysis"


class TestThought:
    """Thought模型测试"""

    def test_create_regular_thought(self):
        """测试创建常规思考"""
        thought = Thought(thought_number=1, content="这是一个常规思考")
        assert thought.thought_number == 1
        assert thought.content == "这是一个常规思考"
        assert thought.type == "regular"
        assert thought.is_revision is False
        assert thought.is_regular_thought() is True
        assert thought.is_revision_thought() is False
        assert thought.is_branch_thought() is False
        assert thought.get_display_type() == "💭"

    def test_create_revision_thought(self):
        """测试创建修订思考"""
        thought = Thought(
            thought_number=2,
            content="这是修订后的思考",
            type="revision",
            is_revision=True,
            revises_thought=1,
        )
        assert thought.type == "revision"
        assert thought.is_revision is True
        assert thought.revises_thought == 1
        assert thought.is_revision_thought() is True
        assert thought.get_display_type() == "🔄"

    def test_create_branch_thought(self):
        """测试创建分支思考"""
        thought = Thought(
            thought_number=3,
            content="这是分支思考",
            type="branch",
            branch_from_thought=1,
            branch_id="alt-1",
        )
        assert thought.type == "branch"
        assert thought.branch_from_thought == 1
        assert thought.branch_id == "alt-1"
        assert thought.is_branch_thought() is True
        assert thought.get_display_type() == "🌿"

    def test_thought_number_validation(self):
        """测试思考编号验证"""
        with pytest.raises(ValidationError):
            Thought(thought_number=0, content="思考")  # 编号必须>=1

        with pytest.raises(ValidationError):
            Thought(thought_number=-1, content="思考")  # 编号必须>=1

    def test_content_validation(self):
        """测试思考内容验证"""
        with pytest.raises(ValidationError):
            Thought(thought_number=1, content="")  # 内容不能为空

        with pytest.raises(ValidationError):
            Thought(thought_number=1, content="x" * 10001)  # 内容不能超过10000字符

    def test_revision_requires_revises_thought(self):
        """测试修订思考必须指定revises_thought"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=2,
                content="修订思考",
                type="revision",
                is_revision=True,
            )
        assert "revises_thought" in str(exc_info.value)

    def test_revision_requires_is_revision_true(self):
        """测试修订思考类型需要is_revision=True"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=2,
                content="修订思考",
                type="revision",
                is_revision=False,
                revises_thought=1,
            )
        assert "is_revision" in str(exc_info.value)

    def test_branch_requires_branch_from_thought(self):
        """测试分支思考必须指定branch_from_thought"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=2,
                content="分支思考",
                type="branch",
            )
        assert "branch_from_thought" in str(exc_info.value)

    def test_branch_requires_branch_id(self):
        """测试分支思考必须指定branch_id"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=2,
                content="分支思考",
                type="branch",
                branch_from_thought=1,
            )
        assert "branch_id" in str(exc_info.value)

    def test_revises_thought_must_be_less_than_current(self):
        """测试revises_thought必须小于当前thought_number"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=2,
                content="修订思考",
                type="revision",
                is_revision=True,
                revises_thought=2,  # 不能等于当前编号
            )
        assert "必须小于" in str(exc_info.value)

        with pytest.raises(ValidationError):
            Thought(
                thought_number=2,
                content="修订思考",
                type="revision",
                is_revision=True,
                revises_thought=3,  # 不能大于当前编号
            )

    def test_branch_from_thought_must_be_less_than_current(self):
        """测试branch_from_thought必须小于当前thought_number"""
        with pytest.raises(ValidationError):
            Thought(
                thought_number=2,
                content="分支思考",
                type="branch",
                branch_from_thought=2,
                branch_id="alt-1",
            )

    def test_timestamp_default(self):
        """测试时间戳默认值"""
        before = datetime.now(timezone.utc)
        thought = Thought(thought_number=1, content="思考")
        after = datetime.now(timezone.utc)

        assert thought.timestamp >= before
        assert thought.timestamp <= after

    def test_to_dict(self):
        """测试转换为字典"""
        thought = Thought(thought_number=1, content="测试思考", type="regular")
        data = thought.to_dict()

        assert data["thought_number"] == 1
        assert data["content"] == "测试思考"
        assert data["type"] == "regular"
        assert "timestamp" in data
        assert data["display_type"] == "💭"
        assert isinstance(data["timestamp"], str)


class TestThoughtCreate:
    """ThoughtCreate模型测试"""

    def test_to_thought(self):
        """测试转换为Thought模型"""
        create_data = ThoughtCreate(
            thought_number=1,
            content="新思考",
            type="regular",
        )
        thought = create_data.to_thought()

        assert isinstance(thought, Thought)
        assert thought.thought_number == 1
        assert thought.content == "新思考"
        assert thought.type == "regular"

    def test_create_revision(self):
        """测试创建修订思考输入"""
        create_data = ThoughtCreate(
            thought_number=2,
            content="修订思考",
            type="revision",
            is_revision=True,
            revises_thought=1,
        )
        thought = create_data.to_thought()

        assert thought.type == "revision"
        assert thought.revises_thought == 1

    def test_create_branch(self):
        """测试创建分支思考输入"""
        create_data = ThoughtCreate(
            thought_number=2,
            content="分支思考",
            type="branch",
            branch_from_thought=1,
            branch_id="alt-1",
        )
        thought = create_data.to_thought()

        assert thought.type == "branch"
        assert thought.branch_id == "alt-1"


class TestThoughtUpdate:
    """ThoughtUpdate模型测试"""

    def test_update_content_only(self):
        """测试只更新内容"""
        update_data = ThoughtUpdate(content="更新后的内容")
        assert update_data.content == "更新后的内容"
        assert update_data.type is None

    def test_update_multiple_fields(self):
        """测试更新多个字段"""
        update_data = ThoughtUpdate(
            content="新内容",
            type="revision",
            is_revision=True,
            revises_thought=1,
        )
        assert update_data.content == "新内容"
        assert update_data.type == "revision"
        assert update_data.revises_thought == 1

    def test_all_fields_optional(self):
        """测试所有字段都是可选的"""
        update_data = ThoughtUpdate()
        assert update_data.content is None
        assert update_data.type is None
        assert update_data.is_revision is None


class TestThoughtComparison:
    """Comparison类型思考测试"""

    def test_create_comparison_thought_valid(self):
        """测试创建有效的对比思考"""
        thought = Thought(
            thought_number=1,
            content="比较两种数据库方案",
            type="comparison",
            comparison_items=["MySQL: 成熟稳定，社区活跃", "PostgreSQL: 功能丰富，扩展性强"],
            comparison_dimensions=["性能", "可靠性", "成本"],
            comparison_result="PostgreSQL在功能和扩展性上更优",
        )
        assert thought.type == "comparison"
        assert thought.is_comparison_thought() is True
        assert len(thought.comparison_items) == 2
        assert thought.get_display_type() == "⚖️"

    def test_comparison_requires_items(self):
        """测试对比思考必须指定comparison_items"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=1,
                content="比较",
                type="comparison",
            )
        assert "comparison_items" in str(exc_info.value)

    def test_comparison_requires_at_least_two_items(self):
        """测试对比思考至少需要2个比较项"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=1,
                content="比较",
                type="comparison",
                comparison_items=["只有一个项"],
            )
        # Pydantic会自动验证min_length
        assert "at least 2" in str(exc_info.value) or "too_short" in str(exc_info.value)

    def test_comparison_items_no_duplicates(self):
        """测试对比思考不能有重复的比较项"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=1,
                content="比较",
                type="comparison",
                comparison_items=["相同的项", "相同的项"],
            )
        assert "重复" in str(exc_info.value)

    def test_comparison_item_length_validation(self):
        """测试比较项长度验证"""
        # 空字符串应该被Pydantic的min_length=1拦截
        with pytest.raises(ValidationError):
            Thought(
                thought_number=1,
                content="比较",
                type="comparison",
                comparison_items=["", "有效项"],
            )

    def test_comparison_dimensions_max_ten(self):
        """测试比较维度最多10个"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=1,
                content="比较",
                type="comparison",
                comparison_items=["A", "B"],
                comparison_dimensions=[f"维度{i}" for i in range(11)],  # 11个维度
            )
        # Pydantic会自动验证max_length
        assert "at most 10" in str(exc_info.value) or "too_long" in str(exc_info.value)

    def test_comparison_result_optional(self):
        """测试comparison_result是可选的"""
        thought = Thought(
            thought_number=1,
            content="比较",
            type="comparison",
            comparison_items=["选项A", "选项B"],
        )
        assert thought.comparison_result is None

    def test_comparison_dimensions_optional(self):
        """测试comparison_dimensions是可选的"""
        thought = Thought(
            thought_number=1,
            content="比较",
            type="comparison",
            comparison_items=["选项A", "选项B"],
            comparison_result="A更好",
        )
        assert thought.comparison_dimensions is None
        assert thought.comparison_result == "A更好"

    def test_thoughtcreate_comparison_valid(self):
        """测试ThoughtCreate支持comparison类型"""
        create_data = ThoughtCreate(
            thought_number=1,
            content="比较",
            type="comparison",
            comparison_items=["A", "B"],
            comparison_dimensions=["成本", "性能"],
        )
        thought = create_data.to_thought()
        assert thought.is_comparison_thought() is True
        assert thought.comparison_items == ["A", "B"]

    def test_thoughtupdate_comparison_fields(self):
        """测试ThoughtUpdate支持comparison字段"""
        update_data = ThoughtUpdate(
            comparison_items=["新A", "新B"],
            comparison_result="新结论",
        )
        assert update_data.comparison_items == ["新A", "新B"]
        assert update_data.comparison_result == "新结论"

    def test_comparison_to_dict(self):
        """测试对比思考转换为字典"""
        thought = Thought(
            thought_number=1,
            content="比较",
            type="comparison",
            comparison_items=["A", "B"],
            comparison_dimensions=["成本"],
            comparison_result="A胜出",
        )
        data = thought.to_dict()
        assert data["display_type"] == "⚖️"
        assert data["comparison_items"] == ["A", "B"]


class TestThoughtReverse:
    """Reverse类型思考测试"""

    def test_create_reverse_thought_valid(self):
        """测试创建有效的逆向思考"""
        thought = Thought(
            thought_number=5,
            content="反推微服务架构决策的前提条件",
            type="reverse",
            reverse_from=3,
            reverse_target="验证微服务架构结论的前提条件",
            reverse_steps=[
                "前提1: 团队规模超过20人",
                "前提2: 业务模块边界清晰",
                "前提3: 具备分布式运维能力",
            ],
        )
        assert thought.type == "reverse"
        assert thought.is_reverse_thought() is True
        assert thought.reverse_target == "验证微服务架构结论的前提条件"
        assert len(thought.reverse_steps) == 3
        assert thought.get_display_type() == "🔙"

    def test_reverse_requires_target(self):
        """测试逆向思考必须指定reverse_target"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=1,
                content="反推",
                type="reverse",
            )
        assert "reverse_target" in str(exc_info.value)

    def test_reverse_target_length_validation(self):
        """测试reverse_target长度验证"""
        with pytest.raises(ValidationError):
            Thought(
                thought_number=1,
                content="反推",
                type="reverse",
                reverse_target="x" * 2001,  # 超过2000字符
            )

    def test_reverse_from_must_be_less_than_thought_number(self):
        """测试reverse_from必须小于当前thought_number"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=5,
                content="反推",
                type="reverse",
                reverse_from=5,  # 不能等于当前编号
                reverse_target="验证",
            )
        assert "必须小于" in str(exc_info.value)

        with pytest.raises(ValidationError):
            Thought(
                thought_number=5,
                content="反推",
                type="reverse",
                reverse_from=10,  # 不能大于当前编号
                reverse_target="验证",
            )

    def test_reverse_steps_max_twenty(self):
        """测试reverse_steps最多20个"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=1,
                content="反推",
                type="reverse",
                reverse_target="验证",
                reverse_steps=[f"步骤{i}" for i in range(21)],  # 21个步骤
            )
        assert "20" in str(exc_info.value) or "too_long" in str(exc_info.value)

    def test_reverse_steps_optional(self):
        """测试reverse_steps是可选的"""
        thought = Thought(
            thought_number=1,
            content="反推",
            type="reverse",
            reverse_target="验证前提条件",
        )
        assert thought.reverse_steps is None

    def test_reverse_from_optional(self):
        """测试reverse_from是可选的"""
        thought = Thought(
            thought_number=1,
            content="反推",
            type="reverse",
            reverse_target="验证前提条件",
        )
        assert thought.reverse_from is None

    def test_thoughtcreate_reverse_valid(self):
        """测试ThoughtCreate支持reverse类型"""
        create_data = ThoughtCreate(
            thought_number=1,
            content="反推",
            type="reverse",
            reverse_target="验证",
            reverse_steps=["步骤1", "步骤2"],
        )
        thought = create_data.to_thought()
        assert thought.is_reverse_thought() is True
        assert thought.reverse_target == "验证"

    def test_thoughtupdate_reverse_fields(self):
        """测试ThoughtUpdate支持reverse字段"""
        update_data = ThoughtUpdate(
            reverse_target="新目标",
            reverse_steps=["新步骤"],
        )
        assert update_data.reverse_target == "新目标"
        assert update_data.reverse_steps == ["新步骤"]

    def test_reverse_to_dict(self):
        """测试逆向思考转换为字典"""
        thought = Thought(
            thought_number=5,
            content="反推",
            type="reverse",
            reverse_from=3,
            reverse_target="验证",
            reverse_steps=["步骤1"],
        )
        data = thought.to_dict()
        assert data["display_type"] == "🔙"
        assert data["reverse_target"] == "验证"


class TestThoughtHypothetical:
    """Hypothetical类型思考测试"""

    def test_create_hypothetical_thought_valid(self):
        """测试创建有效的假设思考"""
        thought = Thought(
            thought_number=7,
            content="探索用户增长10倍的影响",
            type="hypothetical",
            hypothetical_condition="如果用户数量从10万增长到100万",
            hypothetical_impact="服务器负载增加10倍，需要扩容",
            hypothetical_probability="可能性：高",
        )
        assert thought.type == "hypothetical"
        assert thought.is_hypothetical_thought() is True
        assert thought.hypothetical_condition == "如果用户数量从10万增长到100万"
        assert thought.get_display_type() == "🤔"

    def test_hypothetical_requires_condition(self):
        """测试假设思考必须指定hypothetical_condition"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=1,
                content="假设",
                type="hypothetical",
            )
        assert "hypothetical_condition" in str(exc_info.value)

    def test_hypothetical_condition_length_validation(self):
        """测试hypothetical_condition长度验证"""
        with pytest.raises(ValidationError):
            Thought(
                thought_number=1,
                content="假设",
                type="hypothetical",
                hypothetical_condition="x" * 2001,  # 超过2000字符
            )

    def test_hypothetical_impact_optional(self):
        """测试hypothetical_impact是可选的"""
        thought = Thought(
            thought_number=1,
            content="假设",
            type="hypothetical",
            hypothetical_condition="如果发生X",
        )
        assert thought.hypothetical_impact is None

    def test_hypothetical_impact_length_validation(self):
        """测试hypothetical_impact长度验证"""
        with pytest.raises(ValidationError):
            Thought(
                thought_number=1,
                content="假设",
                type="hypothetical",
                hypothetical_condition="如果发生X",
                hypothetical_impact="x" * 10001,  # 超过10000字符
            )

    def test_hypothetical_probability_optional(self):
        """测试hypothetical_probability是可选的"""
        thought = Thought(
            thought_number=1,
            content="假设",
            type="hypothetical",
            hypothetical_condition="如果发生X",
            hypothetical_impact="影响分析",
        )
        assert thought.hypothetical_probability is None

    def test_hypothetical_probability_length_validation(self):
        """测试hypothetical_probability长度验证"""
        with pytest.raises(ValidationError):
            Thought(
                thought_number=1,
                content="假设",
                type="hypothetical",
                hypothetical_condition="如果发生X",
                hypothetical_probability="x" * 51,  # 超过50字符
            )

    def test_thoughtcreate_hypothetical_valid(self):
        """测试ThoughtCreate支持hypothetical类型"""
        create_data = ThoughtCreate(
            thought_number=1,
            content="假设",
            type="hypothetical",
            hypothetical_condition="如果发生X",
            hypothetical_impact="影响Y",
        )
        thought = create_data.to_thought()
        assert thought.is_hypothetical_thought() is True
        assert thought.hypothetical_condition == "如果发生X"

    def test_thoughtupdate_hypothetical_fields(self):
        """测试ThoughtUpdate支持hypothetical字段"""
        update_data = ThoughtUpdate(
            hypothetical_condition="新假设",
            hypothetical_probability="可能性：中",
        )
        assert update_data.hypothetical_condition == "新假设"
        assert update_data.hypothetical_probability == "可能性：中"

    def test_hypothetical_to_dict(self):
        """测试假设思考转换为字典"""
        thought = Thought(
            thought_number=1,
            content="假设",
            type="hypothetical",
            hypothetical_condition="如果发生X",
            hypothetical_impact="影响Y",
        )
        data = thought.to_dict()
        assert data["display_type"] == "🤔"
        assert data["hypothetical_condition"] == "如果发生X"


class TestThoughtLongContent:
    """长内容边界测试 - 验证新边界值允许更长的内容"""

    def test_comparison_result_with_5000_chars(self):
        """测试comparison_result支持5000字符"""
        long_result = "分析结论：" + "详细说明" * 1249  # 5 + 4996 = 5001，截断到5000
        long_result = long_result[:5000]
        thought = Thought(
            thought_number=1,
            content="比较分析",
            type="comparison",
            comparison_items=["方案A", "方案B"],
            comparison_result=long_result,
        )
        assert len(thought.comparison_result) == 5000
        assert thought.comparison_result == long_result

    def test_comparison_result_with_10000_chars(self):
        """测试comparison_result支持10000字符"""
        long_result = "分析结论：" + "详细说明" * 2499  # ~10000字符
        long_result = long_result[:10000]
        thought = Thought(
            thought_number=1,
            content="比较分析",
            type="comparison",
            comparison_items=["方案A", "方案B"],
            comparison_result=long_result,
        )
        assert len(thought.comparison_result) == 10000
        assert thought.comparison_result == long_result

    def test_hypothetical_impact_with_5000_chars(self):
        """测试hypothetical_impact支持5000字符"""
        long_impact = "影响分析：" + "详细描述" * 1249
        long_impact = long_impact[:5000]
        thought = Thought(
            thought_number=1,
            content="假设分析",
            type="hypothetical",
            hypothetical_condition="如果发生X",
            hypothetical_impact=long_impact,
        )
        assert len(thought.hypothetical_impact) == 5000
        assert thought.hypothetical_impact == long_impact

    def test_hypothetical_impact_with_10000_chars(self):
        """测试hypothetical_impact支持10000字符"""
        long_impact = "影响分析：" + "详细描述" * 2499
        long_impact = long_impact[:10000]
        thought = Thought(
            thought_number=1,
            content="假设分析",
            type="hypothetical",
            hypothetical_condition="如果发生X",
            hypothetical_impact=long_impact,
        )
        assert len(thought.hypothetical_impact) == 10000
        assert thought.hypothetical_impact == long_impact

    def test_reverse_target_with_1000_chars(self):
        """测试reverse_target支持1000字符"""
        long_target = "验证目标：" + "详细说明" * 249
        long_target = long_target[:1000]
        thought = Thought(
            thought_number=1,
            content="反推分析",
            type="reverse",
            reverse_target=long_target,
        )
        assert len(thought.reverse_target) == 1000
        assert thought.reverse_target == long_target

    def test_reverse_target_with_2000_chars(self):
        """测试reverse_target支持2000字符"""
        long_target = "验证目标：" + "详细说明" * 499
        long_target = long_target[:2000]
        thought = Thought(
            thought_number=1,
            content="反推分析",
            type="reverse",
            reverse_target=long_target,
        )
        assert len(thought.reverse_target) == 2000
        assert thought.reverse_target == long_target

    def test_hypothetical_condition_with_1000_chars(self):
        """测试hypothetical_condition支持1000字符"""
        long_condition = "假设条件：" + "详细描述" * 249
        long_condition = long_condition[:1000]
        thought = Thought(
            thought_number=1,
            content="假设分析",
            type="hypothetical",
            hypothetical_condition=long_condition,
        )
        assert len(thought.hypothetical_condition) == 1000
        assert thought.hypothetical_condition == long_condition

    def test_hypothetical_condition_with_2000_chars(self):
        """测试hypothetical_condition支持2000字符"""
        long_condition = "假设条件：" + "详细描述" * 499
        long_condition = long_condition[:2000]
        thought = Thought(
            thought_number=1,
            content="假设分析",
            type="hypothetical",
            hypothetical_condition=long_condition,
        )
        assert len(thought.hypothetical_condition) == 2000
        assert thought.hypothetical_condition == long_condition
