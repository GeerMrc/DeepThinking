"""
集成测试 - 顺序思考工具
"""

import pytest

from deep_thinking import server
from deep_thinking.storage.storage_manager import StorageManager
from deep_thinking.tools import sequential_thinking


class TestSequentialThinkingIntegration:
    """顺序思考工具集成测试"""

    @pytest.fixture
    def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager

        yield manager

        # 清理
        server._storage_manager = None

    def test_regular_thinking(self, storage_manager):
        """测试常规思考"""
        result = sequential_thinking.sequential_thinking(
            thought="这是第一个思考步骤",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-regular",
        )

        assert "思考步骤 1/3" in result
        assert "常规思考" in result
        assert "这是第一个思考步骤" in result
        assert "继续下一步思考" in result

        # 验证会话已创建
        session = storage_manager.get_session("test-regular")
        assert session is not None
        assert session.thought_count() == 1
        assert session.thoughts[0].content == "这是第一个思考步骤"

    def test_revision_thinking(self, storage_manager):
        """测试修订思考"""
        # 先创建一个常规思考
        sequential_thinking.sequential_thinking(
            thought="原始思考",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-revision",
        )

        # 然后创建修订思考
        result = sequential_thinking.sequential_thinking(
            thought="这是修订后的思考",
            nextThoughtNeeded=False,
            thoughtNumber=2,
            totalThoughts=3,
            session_id="test-revision",
            isRevision=True,
            revisesThought=1,
        )

        assert "修订思考" in result
        assert "修订思考步骤 1" in result
        assert "这是修订后的思考" in result
        assert "思考完成" in result

        # 验证修订信息
        session = storage_manager.get_session("test-revision")
        assert session is not None
        assert session.thought_count() == 2
        assert session.thoughts[1].type == "revision"
        assert session.thoughts[1].revises_thought == 1

    def test_branch_thinking(self, storage_manager):
        """测试分支思考"""
        # 先创建一个常规思考
        sequential_thinking.sequential_thinking(
            thought="主线思考",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=5,
            session_id="test-branch",
        )

        # 然后创建分支思考
        result = sequential_thinking.sequential_thinking(
            thought="这是一个分支思考",
            nextThoughtNeeded=True,
            thoughtNumber=2,
            totalThoughts=5,
            session_id="test-branch",
            branchFromThought=1,
            branchId="branch-0-1",
        )

        assert "分支思考" in result
        assert "从步骤 1 分支" in result
        assert "这是一个分支思考" in result

        # 验证分支信息
        session = storage_manager.get_session("test-branch")
        assert session is not None
        assert session.thought_count() == 2
        assert session.thoughts[1].type == "branch"
        assert session.thoughts[1].branch_from_thought == 1
        assert session.thoughts[1].branch_id == "branch-0-1"

    def test_completion(self, storage_manager):
        """测试思考完成"""
        result = sequential_thinking.sequential_thinking(
            thought="最后一个思考",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
            session_id="test-complete",
        )

        assert "思考完成" in result
        assert "✅" in result

        # 验证会话已标记为完成
        session = storage_manager.get_session("test-complete")
        assert session is not None
        assert session.is_completed()

    def test_multiple_thoughts_same_session(self, storage_manager):
        """测试同一会话中的多个思考步骤"""
        session_id = "test-multiple"

        # 添加三个思考步骤
        sequential_thinking.sequential_thinking(
            thought="步骤1：分析问题",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
        )

        sequential_thinking.sequential_thinking(
            thought="步骤2：制定方案",
            nextThoughtNeeded=True,
            thoughtNumber=2,
            totalThoughts=3,
            session_id=session_id,
        )

        sequential_thinking.sequential_thinking(
            thought="步骤3：执行方案",
            nextThoughtNeeded=False,
            thoughtNumber=3,
            totalThoughts=3,
            session_id=session_id,
        )

        # 验证所有思考都已保存
        session = storage_manager.get_session(session_id)
        assert session is not None
        assert session.thought_count() == 3
        assert session.thoughts[0].content == "步骤1：分析问题"
        assert session.thoughts[1].content == "步骤2：制定方案"
        assert session.thoughts[2].content == "步骤3：执行方案"

    def test_default_session_creation(self, storage_manager):
        """测试默认会话自动创建"""
        result = sequential_thinking.sequential_thinking(
            thought="使用默认会话",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
        )

        assert "思考步骤 1/1" in result

        # 验证默认会话已创建
        session = storage_manager.get_session("default")
        assert session is not None
        assert session.thought_count() == 1

    def test_comparison_thinking(self, storage_manager):
        """测试对比思考类型"""
        result = sequential_thinking.sequential_thinking(
            thought="比较三种数据库方案",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-comparison",
            comparisonItems=[
                "MySQL: 成熟稳定，社区活跃",
                "PostgreSQL: 功能丰富，扩展性强",
                "MongoDB: 灵活文档存储",
            ],
            comparisonDimensions=["性能", "可靠性", "成本"],
            comparisonResult="PostgreSQL在功能和扩展性上最优",
        )

        assert "思考步骤 1/3" in result
        assert "对比思考 ⚖️" in result
        assert "比较三种数据库方案" in result
        assert "比较项" in result
        assert "性能, 可靠性, 成本" in result
        assert "PostgreSQL" in result

        # 验证对比思考数据
        session = storage_manager.get_session("test-comparison")
        assert session is not None
        assert session.thought_count() == 1
        assert session.thoughts[0].type == "comparison"
        assert session.thoughts[0].comparison_items is not None
        assert len(session.thoughts[0].comparison_items) == 3
        assert session.thoughts[0].comparison_result == "PostgreSQL在功能和扩展性上最优"

    def test_reverse_thinking(self, storage_manager):
        """测试逆向思考类型"""
        result = sequential_thinking.sequential_thinking(
            thought="反推微服务架构决策的前提条件",
            nextThoughtNeeded=False,
            thoughtNumber=3,
            totalThoughts=5,
            session_id="test-reverse",
            reverseFrom=2,
            reverseTarget="验证'采用微服务架构'结论的前提条件",
            reverseSteps=[
                "前提1: 团队规模超过20人",
                "前提2: 业务模块边界清晰",
                "验证结果: 前提3不成立",
            ],
        )

        assert "思考步骤 3/5" in result
        assert "逆向思考 🔙" in result
        assert "反推微服务架构" in result
        assert "反推起点" in result
        assert "思考步骤 2" in result
        assert "反推目标" in result
        assert "反推步骤" in result

        # 验证逆向思考数据
        session = storage_manager.get_session("test-reverse")
        assert session is not None
        assert session.thought_count() == 1
        assert session.thoughts[0].type == "reverse"
        assert session.thoughts[0].reverse_from == 2
        assert session.thoughts[0].reverse_target == "验证'采用微服务架构'结论的前提条件"
        assert session.thoughts[0].reverse_steps is not None
        assert len(session.thoughts[0].reverse_steps) == 3

    def test_hypothetical_thinking(self, storage_manager):
        """测试假设思考类型"""
        result = sequential_thinking.sequential_thinking(
            thought="探索用户增长10倍的影响",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=2,
            session_id="test-hypothetical",
            hypotheticalCondition="如果用户数量从10万增长到100万",
            hypotheticalImpact="服务器负载增加10倍，需要：1.数据库分库分表 2.引入缓存层",
            hypotheticalProbability="可能性：高",
        )

        assert "思考步骤 1/2" in result
        assert "假设思考 🤔" in result
        assert "探索用户增长10倍的影响" in result
        assert "假设条件" in result
        assert "如果用户数量从10万增长到100万" in result
        assert "影响分析" in result
        assert "服务器负载增加10倍" in result
        assert "可能性" in result

        # 验证假设思考数据
        session = storage_manager.get_session("test-hypothetical")
        assert session is not None
        assert session.thought_count() == 1
        assert session.thoughts[0].type == "hypothetical"
        assert session.thoughts[0].hypothetical_condition == "如果用户数量从10万增长到100万"
        assert (
            session.thoughts[0].hypothetical_impact
            == "服务器负载增加10倍，需要：1.数据库分库分表 2.引入缓存层"
        )
        assert session.thoughts[0].hypothetical_probability == "可能性：高"

    # ===== Phase 3: Interleaved Thinking 测试 =====

    def test_phase_auto_inference_thinking(self, storage_manager):
        """测试无工具调用时自动推断为 thinking 阶段"""
        result = sequential_thinking.sequential_thinking(
            thought="纯思考内容",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-phase-thinking",
        )
        assert "阶段**: 思考 🧠" in result

    def test_phase_auto_inference_tool_call(self, storage_manager):
        """测试有 toolCalls 时自动推断为 tool_call 阶段"""
        result = sequential_thinking.sequential_thinking(
            thought="需要调用工具",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-phase-toolcall",
            toolCalls=[{"name": "search", "arguments": {"q": "test"}}],
        )
        assert "阶段**: 工具调用 🔧" in result

    def test_phase_auto_inference_analysis(self, storage_manager):
        """测试有 toolResults 时自动推断为 analysis 阶段"""
        result = sequential_thinking.sequential_thinking(
            thought="分析工具结果",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-phase-analysis",
            toolResults=[{"call_id": "123", "result": "data", "success": True}],
        )
        assert "阶段**: 分析 📊" in result

    def test_explicit_phase_parameter(self, storage_manager):
        """测试显式指定 phase 参数"""
        result = sequential_thinking.sequential_thinking(
            thought="显式指定分析阶段",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-phase-explicit",
            phase="analysis",
        )
        assert "阶段**: 分析 📊" in result

    def test_tool_call_recording(self, storage_manager):
        """测试工具调用记录存储"""
        result = sequential_thinking.sequential_thinking(
            thought="调用工具获取数据",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-toolcall-record",
            toolCalls=[{"name": "read_file", "arguments": {"path": "/tmp/test.txt"}}],
        )
        assert "工具调用" in result
        assert "read_file" in result

        # 验证工具调用记录已存储
        session = storage_manager.get_session("test-toolcall-record")
        assert session is not None
        assert len(session.tool_call_history) == 1
        assert session.tool_call_history[0].call_data.tool_name == "read_file"

    def test_tool_result_recording(self, storage_manager):
        """测试工具结果记录存储"""
        result = sequential_thinking.sequential_thinking(
            thought="分析工具返回结果",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-toolresult-record",
            toolCalls=[{"name": "search", "arguments": {"q": "test"}}],
            toolResults=[{"call_id": "123", "result": "搜索结果", "success": True}],
        )
        assert "成功: 是" in result

        # 验证工具调用记录包含结果
        session = storage_manager.get_session("test-toolresult-record")
        assert session is not None
        record = session.tool_call_history[0]
        assert record.result_data is not None
        assert record.result_data.success is True

    def test_tool_call_limit_exceeded(self, storage_manager, monkeypatch):
        """测试超过工具调用限制"""
        # 设置较低的工具调用限制以便测试
        # 注意：由于 max_thoughts=50，所以 max_tool_calls 需要小于 50
        import os
        monkeypatch.setenv("DEEP_THINKING_MAX_TOOL_CALLS", "10")

        # 重新加载配置
        from deep_thinking.models.config import set_global_config, ThinkingConfig
        set_global_config(ThinkingConfig.from_env())

        # 添加 10 次工具调用（达到限制）
        for i in range(10):
            sequential_thinking.sequential_thinking(
                thought=f"思考{i}",
                nextThoughtNeeded=True,
                thoughtNumber=i + 1,
                totalThoughts=50,
                session_id="test-limit",
                toolCalls=[{"name": "test", "arguments": {}}],
            )

        # 确认有 10 次工具调用
        session = storage_manager.get_session("test-limit")
        assert session.statistics.total_tool_calls == 10

        # 第 11 次应该被拒绝
        result = sequential_thinking.sequential_thinking(
            thought="超限思考",
            nextThoughtNeeded=False,
            thoughtNumber=11,
            totalThoughts=50,
            session_id="test-limit",
            toolCalls=[{"name": "test", "arguments": {}}],
        )
        assert "工具调用次数将超限" in result

    def test_statistics_update(self, storage_manager):
        """测试统计信息更新"""
        sequential_thinking.sequential_thinking(
            thought="调用工具",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-stats",
            toolCalls=[{"name": "test", "arguments": {}}],
            toolResults=[{"call_id": "1", "result": "ok", "success": True}],
        )

        session = storage_manager.get_session("test-stats")
        assert session is not None
        assert session.statistics.total_tool_calls == 1
        assert session.statistics.successful_tool_calls == 1

    # ===== Phase 3.5: 1:N 映射测试 =====

    def test_multiple_tool_calls_single_step(self, storage_manager):
        """测试单步骤多次工具调用（1:N 映射）"""
        result = sequential_thinking.sequential_thinking(
            thought="并行调用多个工具",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-multi-calls",
            toolCalls=[
                {"name": "search_api", "arguments": {"q": "test1"}},
                {"name": "read_file", "arguments": {"path": "/tmp/data"}},
                {"name": "query_database", "arguments": {"sql": "SELECT *"}},
            ],
        )
        assert "工具调用 (3个)" in result
        assert "search_api" in result
        assert "read_file" in result
        assert "query_database" in result

        # 验证 3 个工具调用记录已存储
        session = storage_manager.get_session("test-multi-calls")
        assert session is not None
        assert len(session.tool_call_history) == 3
        assert session.statistics.total_tool_calls == 3

    def test_multiple_tool_calls_with_results(self, storage_manager):
        """测试多次工具调用和结果记录"""
        result = sequential_thinking.sequential_thinking(
            thought="调用工具并分析结果",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-multi-results",
            toolCalls=[
                {"name": "tool_a", "arguments": {}},
                {"name": "tool_b", "arguments": {}},
            ],
            toolResults=[
                {"call_id": "a1", "result": "result_a", "success": True},
                {"call_id": "b1", "result": "result_b", "success": False},
            ],
        )
        assert "工具调用 (2个)" in result
        assert "成功: 是" in result
        assert "成功: 否" in result

        # 验证工具调用记录包含正确的结果
        session = storage_manager.get_session("test-multi-results")
        assert session is not None
        assert len(session.tool_call_history) == 2
        # 验证第一个工具结果 success=True
        assert session.tool_call_history[0].result_data.success is True
        # 验证第二个工具结果 success=False
        assert session.tool_call_history[1].result_data.success is False
        # 统计：只有 success=True 的调用被计入 successful_tool_calls
        # 注意：failed_tool_calls 只统计 status="failed" 或 "timeout" 的记录
        # success=False 不等同于 status="failed"
        assert session.statistics.successful_tool_calls == 1

    def test_tool_calls_thought_linking(self, storage_manager):
        """测试 Thought.tool_calls 字段正确填充"""
        result = sequential_thinking.sequential_thinking(
            thought="测试工具调用关联",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-linking",
            toolCalls=[
                {"name": "tool_1", "arguments": {}},
                {"name": "tool_2", "arguments": {}},
            ],
        )
        assert "工具调用 (2个)" in result

        # 验证 Thought.tool_calls 字段包含 record_id
        session = storage_manager.get_session("test-linking")
        assert session is not None
        thought = session.thoughts[0]
        assert len(thought.tool_calls) == 2
        # 验证 record_id 格式正确
        for record_id in thought.tool_calls:
            assert isinstance(record_id, str)
            assert len(record_id) > 0

    def test_empty_tool_calls_list(self, storage_manager):
        """测试空工具调用列表（等同于无工具调用）"""
        result = sequential_thinking.sequential_thinking(
            thought="纯思考步骤",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-empty-calls",
            toolCalls=[],
        )
        assert "阶段**: 思考 🧠" in result
        assert "工具调用" not in result

    def test_tool_calls_with_call_id_matching(self, storage_manager):
        """测试使用 call_id 匹配工具调用和结果"""
        result = sequential_thinking.sequential_thinking(
            thought="使用 call_id 匹配",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-call-id",
            toolCalls=[
                {"name": "tool_x", "arguments": {}, "call_id": "xyz-123"},
                {"name": "tool_y", "arguments": {}, "call_id": "xyz-456"},
            ],
            toolResults=[
                {"call_id": "xyz-456", "result": "y_result", "success": True},
                {"call_id": "xyz-123", "result": "x_result", "success": True},
            ],
        )
        assert "工具调用 (2个)" in result

        # 验证结果正确关联
        session = storage_manager.get_session("test-call-id")
        assert session is not None
        # 验证两个工具调用都有结果
        for record in session.tool_call_history:
            assert record.result_data is not None
            assert record.result_data.success is True

    def test_tool_calls_per_thought_limit_exceeded(self, storage_manager, monkeypatch):
        """测试超过每步骤工具调用数量限制"""
        # 设置较低的每步骤工具调用限制
        monkeypatch.setenv("DEEP_THINKING_MAX_TOOL_CALLS_PER_THOUGHT", "5")

        # 重新加载配置
        from deep_thinking.models.config import set_global_config, ThinkingConfig
        set_global_config(ThinkingConfig.from_env())

        # 尝试调用 6 个工具（超过限制 5）
        result = sequential_thinking.sequential_thinking(
            thought="尝试调用过多工具",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-per-thought-limit",
            toolCalls=[
                {"name": f"tool_{i}", "arguments": {}} for i in range(6)
            ],
        )
        assert "单步骤工具调用数超限" in result
        assert "6" in result
        assert "5" in result

        # 验证没有工具调用被记录
        session = storage_manager.get_session("test-per-thought-limit")
        assert session is not None
        assert len(session.tool_call_history) == 0

    def test_tool_calls_per_thought_within_limit(self, storage_manager, monkeypatch):
        """测试在每步骤工具调用数量限制内"""
        # 设置较低的每步骤工具调用限制
        monkeypatch.setenv("DEEP_THINKING_MAX_TOOL_CALLS_PER_THOUGHT", "5")

        # 重新加载配置
        from deep_thinking.models.config import set_global_config, ThinkingConfig
        set_global_config(ThinkingConfig.from_env())

        # 调用 5 个工具（刚好等于限制）
        result = sequential_thinking.sequential_thinking(
            thought="调用刚好等于限制的工具数",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-per-thought-ok",
            toolCalls=[
                {"name": f"tool_{i}", "arguments": {}} for i in range(5)
            ],
        )
        assert "工具调用 (5个)" in result

        # 验证 5 个工具调用被记录
        session = storage_manager.get_session("test-per-thought-ok")
        assert session is not None
        assert len(session.tool_call_history) == 5


class TestSequentialThinkingBoundary:
    """顺序思考工具边界测试"""

    @pytest.fixture
    def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager

        yield manager

        # 清理
        server._storage_manager = None

    def test_thought_number_less_than_one(self, storage_manager):
        """测试thoughtNumber小于1的错误处理"""
        with pytest.raises(ValueError, match="thoughtNumber 必须大于等于 1"):
            sequential_thinking.sequential_thinking(
                thought="测试思考",
                nextThoughtNeeded=False,
                thoughtNumber=0,  # 无效值
                totalThoughts=3,
                session_id="test-boundary-1",
            )

    def test_thought_number_negative(self, storage_manager):
        """测试thoughtNumber为负数的错误处理"""
        with pytest.raises(ValueError, match="thoughtNumber 必须大于等于 1"):
            sequential_thinking.sequential_thinking(
                thought="测试思考",
                nextThoughtNeeded=False,
                thoughtNumber=-1,  # 无效值
                totalThoughts=3,
                session_id="test-boundary-2",
            )

    def test_total_thoughts_less_than_thought_number(self, storage_manager):
        """测试totalThoughts小于thoughtNumber的错误处理"""
        with pytest.raises(ValueError, match="totalThoughts.*必须大于等于.*thoughtNumber"):
            sequential_thinking.sequential_thinking(
                thought="测试思考",
                nextThoughtNeeded=False,
                thoughtNumber=5,  # thoughtNumber > totalThoughts
                totalThoughts=3,
                session_id="test-boundary-3",
            )

    def test_empty_thought_content(self, storage_manager):
        """测试空思考内容的错误处理"""
        with pytest.raises(ValueError, match="thought 内容不能为空"):
            sequential_thinking.sequential_thinking(
                thought="",  # 空内容
                nextThoughtNeeded=False,
                thoughtNumber=1,
                totalThoughts=3,
                session_id="test-boundary-4",
            )

    def test_whitespace_only_thought_content(self, storage_manager):
        """测试纯空白思考内容的错误处理"""
        with pytest.raises(ValueError, match="thought 内容不能为空"):
            sequential_thinking.sequential_thinking(
                thought="   ",  # 纯空白
                nextThoughtNeeded=False,
                thoughtNumber=1,
                totalThoughts=3,
                session_id="test-boundary-5",
            )

    def test_total_thoughts_exceeds_max_limit(self, storage_manager):
        """测试totalThoughts超过最大配置限制的错误处理"""
        with pytest.raises(ValueError, match="totalThoughts.*超过最大限制"):
            sequential_thinking.sequential_thinking(
                thought="测试思考",
                nextThoughtNeeded=False,
                thoughtNumber=1,
                totalThoughts=100000,  # 超过默认最大限制50
                session_id="test-boundary-6",
            )

    def test_needs_more_thoughts_at_max_limit(self, storage_manager):
        """测试needsMoreThoughts在达到最大限制时的行为"""
        # 创建一个接近最大限制的会话
        result = sequential_thinking.sequential_thinking(
            thought="测试思考",
            nextThoughtNeeded=True,
            thoughtNumber=50,  # 已经是最大限制
            totalThoughts=50,
            needsMoreThoughts=True,
            session_id="test-boundary-7",
        )

        # 应该返回警告信息，而不是增加totalThoughts
        assert "思考步骤 50/50" in result
        assert "警告：思考步骤数已达上限" in result
        assert "无法继续增加" in result

    def test_needs_more_thoughts_normal_increase(self, storage_manager):
        """测试needsMoreThoughts正常增加totalThoughts"""
        result = sequential_thinking.sequential_thinking(
            thought="测试思考",
            nextThoughtNeeded=True,
            thoughtNumber=10,
            totalThoughts=20,
            needsMoreThoughts=True,
            session_id="test-boundary-8",
        )

        # totalThoughts应该增加（从20增加到30）
        assert "思考步骤 10/30" in result
        assert "已自动调整为 30" in result or "预计总数: 30" in result

        # 验证会话元数据记录了调整历史
        session = storage_manager.get_session("test-boundary-8")
        assert session is not None
        assert "total_thoughts_history" in session.metadata
        assert len(session.metadata["total_thoughts_history"]) > 0

    def test_comparison_thinking_with_empty_items(self, storage_manager):
        """测试对比思考缺少比较项的错误处理（Pydantic验证）"""
        with pytest.raises(ValueError, match="List should have at least 2 items"):
            sequential_thinking.sequential_thinking(
                thought="对比测试",
                nextThoughtNeeded=False,
                thoughtNumber=1,
                totalThoughts=3,
                session_id="test-boundary-9",
                comparisonItems=[],  # 空列表
                comparisonDimensions=["性能", "成本"],
                comparisonResult="结论",
            )

    def test_comparison_thinking_with_single_item(self, storage_manager):
        """测试对比思考只有一个比较项的错误处理"""
        with pytest.raises(ValueError, match="List should have at least 2 items"):
            sequential_thinking.sequential_thinking(
                thought="对比测试",
                nextThoughtNeeded=False,
                thoughtNumber=1,
                totalThoughts=3,
                session_id="test-boundary-10",
                comparisonItems=["方案A"],  # 只有一个项
                comparisonDimensions=["性能", "成本"],
                comparisonResult="结论",
            )

    def test_reverse_thinking_invalid_reverse_from(self, storage_manager):
        """测试逆向思考reverse_from必须小于thought_number"""
        with pytest.raises(ValueError, match="reverse_from.*必须小于.*thought_number"):
            sequential_thinking.sequential_thinking(
                thought="逆向测试",
                nextThoughtNeeded=False,
                thoughtNumber=1,
                totalThoughts=3,
                session_id="test-boundary-11",
                reverseFrom=1,  # reverse_from应该<thought_number
                reverseTarget="反推目标",
                reverseSteps=["步骤1", "步骤2"],
            )

    def test_hypothetical_thinking_with_empty_condition(self, storage_manager):
        """测试假设思考缺少假设条件的错误处理（Pydantic验证）"""
        with pytest.raises(ValueError, match="String should have at least 1 character"):
            sequential_thinking.sequential_thinking(
                thought="假设测试",
                nextThoughtNeeded=False,
                thoughtNumber=1,
                totalThoughts=3,
                session_id="test-boundary-12",
                hypotheticalCondition="",  # 空字符串
                hypotheticalImpact="影响分析",
                hypotheticalProbability="高",
            )
