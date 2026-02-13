"""
集成测试 - Interleaved Thinking 功能

测试 Interleaved Thinking 的完整功能集成，包括：
- 完整交错思考工作流
- 自动阶段推断
- 工具调用追踪
- 统计信息正确性
- 资源控制限制
- 结果缓存
- 持久化和恢复
- 导出功能

Phase 7 任务 7.1-7.8
"""

import json

import pytest

from deep_thinking import server
from deep_thinking.models.config import ThinkingConfig, set_global_config
from deep_thinking.storage.storage_manager import StorageManager
from deep_thinking.tools import sequential_thinking
from deep_thinking.utils.formatters import Visualizer, export_session_to_file


class TestInterleavedThinkingWorkflow:
    """
    任务 7.1: 测试完整交错思考工作流

    测试 thinking -> tool_call -> analysis 的完整工作流
    """

    @pytest.fixture
    def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager
        yield manager
        server._storage_manager = None

    def test_complete_interleaved_workflow(self, storage_manager):
        """测试完整的交错思考工作流"""
        session_id = "test-workflow-complete"

        # Step 1: thinking 阶段 - 初始思考
        result1 = sequential_thinking.sequential_thinking(
            thought="首先需要分析问题，确定需要查询哪些数据",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=5,
            session_id=session_id,
        )
        assert "思考 🧠" in result1

        # Step 2: tool_call 阶段 - 决定调用工具
        result2 = sequential_thinking.sequential_thinking(
            thought="调用搜索工具获取相关数据",
            nextThoughtNeeded=True,
            thoughtNumber=2,
            totalThoughts=5,
            session_id=session_id,
            toolCalls=[
                {"name": "search", "arguments": {"query": "test data"}},
            ],
        )
        assert "工具调用 🔧" in result2
        assert "search" in result2

        # Step 3: analysis 阶段 - 分析工具结果
        result3 = sequential_thinking.sequential_thinking(
            thought="分析搜索结果，提取关键信息",
            nextThoughtNeeded=True,
            thoughtNumber=3,
            totalThoughts=5,
            session_id=session_id,
            toolResults=[
                {"call_id": "call-1", "result": "found 10 items", "success": True},
            ],
        )
        assert "分析 📊" in result3

        # Step 4: thinking 阶段 - 继续思考
        result4 = sequential_thinking.sequential_thinking(
            thought="根据分析结果，制定下一步方案",
            nextThoughtNeeded=True,
            thoughtNumber=4,
            totalThoughts=5,
            session_id=session_id,
        )
        assert "思考 🧠" in result4

        # Step 5: 完成思考
        result5 = sequential_thinking.sequential_thinking(
            thought="最终方案已确定",
            nextThoughtNeeded=False,
            thoughtNumber=5,
            totalThoughts=5,
            session_id=session_id,
        )
        assert "思考完成" in result5

        # 验证会话状态
        session = storage_manager.get_session(session_id)
        assert session is not None
        assert session.thought_count() == 5
        assert session.is_completed()

        # 验证各步骤的阶段
        phases = [t.phase for t in session.thoughts]
        assert phases[0] == "thinking"
        assert phases[1] == "tool_call"
        assert phases[2] == "analysis"
        assert phases[3] == "thinking"
        assert phases[4] == "thinking"

    def test_multiple_tool_calls_workflow(self, storage_manager):
        """测试多工具调用的完整工作流"""
        session_id = "test-multi-tool-workflow"

        # Step 1: 并行调用多个工具
        result = sequential_thinking.sequential_thinking(
            thought="并行调用多个数据源",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[
                {"name": "api_a", "arguments": {"endpoint": "/data"}},
                {"name": "api_b", "arguments": {"endpoint": "/info"}},
                {"name": "db_query", "arguments": {"sql": "SELECT *"}},
            ],
        )
        assert "工具调用 (3个)" in result

        # 验证工具调用记录
        session = storage_manager.get_session(session_id)
        assert len(session.tool_call_history) == 3

        # 验证工具名称
        tool_names = [r.call_data.tool_name for r in session.tool_call_history]
        assert "api_a" in tool_names
        assert "api_b" in tool_names
        assert "db_query" in tool_names


class TestPhaseAutoInference:
    """
    任务 7.2: 测试自动阶段推断完整流程

    测试各种情况下阶段自动推断的正确性
    """

    @pytest.fixture
    def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager
        yield manager
        server._storage_manager = None

    def test_inference_without_tool_params(self, storage_manager):
        """测试无工具参数时推断为 thinking"""
        result = sequential_thinking.sequential_thinking(
            thought="纯思考内容",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-infer-1",
        )
        assert "思考 🧠" in result

    def test_inference_with_tool_calls_only(self, storage_manager):
        """测试仅有 toolCalls 时推断为 tool_call"""
        result = sequential_thinking.sequential_thinking(
            thought="调用工具",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-infer-2",
            toolCalls=[{"name": "test", "arguments": {}}],
        )
        assert "工具调用 🔧" in result

    def test_inference_with_tool_results_only(self, storage_manager):
        """测试仅有 toolResults 时推断为 analysis"""
        result = sequential_thinking.sequential_thinking(
            thought="分析结果",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-infer-3",
            toolResults=[{"call_id": "1", "result": "data", "success": True}],
        )
        assert "分析 📊" in result

    def test_inference_with_both_params(self, storage_manager):
        """测试同时有 toolCalls 和 toolResults 时推断为 analysis（优先级）"""
        result = sequential_thinking.sequential_thinking(
            thought="同时有调用和结果",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-infer-4",
            toolCalls=[{"name": "test", "arguments": {}}],
            toolResults=[{"call_id": "1", "result": "data", "success": True}],
        )
        # 有 toolResults 时应该是 analysis 阶段
        assert "分析 📊" in result

    def test_explicit_phase_overrides_inference(self, storage_manager):
        """测试显式 phase 参数覆盖自动推断"""
        # 即使有 toolCalls，显式指定 thinking 仍为 thinking
        result = sequential_thinking.sequential_thinking(
            thought="显式指定阶段",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-infer-5",
            phase="thinking",
            toolCalls=[{"name": "test", "arguments": {}}],
        )
        assert "思考 🧠" in result

    def test_empty_lists_inference(self, storage_manager):
        """测试空列表参数的推断"""
        result = sequential_thinking.sequential_thinking(
            thought="空列表测试",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-infer-6",
            toolCalls=[],
            toolResults=[],
        )
        # 空列表等同于无参数
        assert "思考 🧠" in result


class TestToolCallTracking:
    """
    任务 7.3: 测试工具调用追踪完整流程

    测试工具调用记录的正确存储和关联
    """

    @pytest.fixture
    def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager
        yield manager
        server._storage_manager = None

    def test_tool_call_record_storage(self, storage_manager):
        """测试工具调用记录正确存储"""
        session_id = "test-track-1"

        sequential_thinking.sequential_thinking(
            thought="调用工具",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[
                {"name": "tool_a", "arguments": {"arg1": "val1"}},
            ],
        )

        session = storage_manager.get_session(session_id)
        assert len(session.tool_call_history) == 1

        record = session.tool_call_history[0]
        assert record.call_data.tool_name == "tool_a"
        assert record.call_data.arguments == {"arg1": "val1"}
        assert record.thought_number == 1

    def test_tool_result_association(self, storage_manager):
        """测试工具结果正确关联到调用"""
        session_id = "test-track-2"

        sequential_thinking.sequential_thinking(
            thought="调用并获取结果",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[
                {"name": "test_tool", "arguments": {}, "call_id": "call-123"},
            ],
            toolResults=[
                {"call_id": "call-123", "result": "success_data", "success": True},
            ],
        )

        session = storage_manager.get_session(session_id)
        record = session.tool_call_history[0]

        assert record.result_data is not None
        assert record.result_data.success is True
        assert record.result_data.result == "success_data"

    def test_one_to_many_mapping(self, storage_manager):
        """测试 1:N 映射（一个思考步骤多个工具调用）"""
        session_id = "test-track-3"

        sequential_thinking.sequential_thinking(
            thought="并行调用",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[
                {"name": "tool_1", "arguments": {}},
                {"name": "tool_2", "arguments": {}},
                {"name": "tool_3", "arguments": {}},
            ],
        )

        session = storage_manager.get_session(session_id)

        # 验证 3 个工具调用记录
        assert len(session.tool_call_history) == 3

        # 验证 Thought.tool_calls 字段包含 3 个 record_id
        thought = session.thoughts[0]
        assert len(thought.tool_calls) == 3

        # 验证所有 record_id 都在 tool_call_history 中
        record_ids = {r.record_id for r in session.tool_call_history}
        for tc_id in thought.tool_calls:
            assert tc_id in record_ids

    def test_call_id_matching(self, storage_manager):
        """测试使用 call_id 匹配工具调用和结果"""
        session_id = "test-track-4"

        sequential_thinking.sequential_thinking(
            thought="使用 call_id 匹配",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[
                {"name": "tool_x", "arguments": {}, "call_id": "id-x"},
                {"name": "tool_y", "arguments": {}, "call_id": "id-y"},
            ],
            toolResults=[
                {"call_id": "id-y", "result": "y_result", "success": True},
                {"call_id": "id-x", "result": "x_result", "success": True},
            ],
        )

        session = storage_manager.get_session(session_id)

        # 验证结果正确关联
        for record in session.tool_call_history:
            assert record.result_data is not None
            if record.call_data.tool_name == "tool_x":
                assert record.result_data.result == "x_result"
            elif record.call_data.tool_name == "tool_y":
                assert record.result_data.result == "y_result"


class TestStatisticsCorrectness:
    """
    任务 7.4: 测试统计信息正确性

    测试会话统计信息的正确计算和更新
    """

    @pytest.fixture
    def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager
        yield manager
        server._storage_manager = None

    def test_tool_call_count_statistics(self, storage_manager):
        """测试工具调用计数统计"""
        session_id = "test-stats-1"

        # 添加 3 个工具调用
        sequential_thinking.sequential_thinking(
            thought="调用3个工具",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[{"name": f"tool_{i}", "arguments": {}} for i in range(3)],
        )

        session = storage_manager.get_session(session_id)
        assert session.statistics.total_tool_calls == 3

    def test_successful_failed_count(self, storage_manager):
        """测试成功/失败计数"""
        session_id = "test-stats-2"

        sequential_thinking.sequential_thinking(
            thought="混合结果",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[
                {"name": "success_tool", "arguments": {}},
                {"name": "fail_tool", "arguments": {}},
            ],
            toolResults=[
                {"call_id": "1", "result": "ok", "success": True},
                {"call_id": "2", "result": "error", "success": False},
            ],
        )

        session = storage_manager.get_session(session_id)
        # 只有 success=True 的被计入 successful_tool_calls
        assert session.statistics.successful_tool_calls == 1

    def test_execution_time_tracking(self, storage_manager):
        """测试执行时间追踪"""
        session_id = "test-stats-3"

        sequential_thinking.sequential_thinking(
            thought="记录执行时间",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[{"name": "timed_tool", "arguments": {}}],
            toolResults=[
                {"call_id": "1", "result": "ok", "success": True, "execution_time_ms": 150.5},
            ],
        )

        session = storage_manager.get_session(session_id)
        assert session.statistics.total_execution_time_ms == 150.5

    def test_thought_length_statistics(self, storage_manager):
        """测试思考内容长度统计"""
        session_id = "test-stats-4"

        thoughts_content = [
            "短内容",
            "这是一段中等长度的思考内容",
            "这是一段更长的思考内容，用于测试平均长度计算的正确性",
        ]

        for i, content in enumerate(thoughts_content, 1):
            sequential_thinking.sequential_thinking(
                thought=content,
                nextThoughtNeeded=i < len(thoughts_content),
                thoughtNumber=i,
                totalThoughts=len(thoughts_content),
                session_id=session_id,
            )

        session = storage_manager.get_session(session_id)
        session.statistics.update_from_thoughts(session.thoughts)

        # 验证平均长度计算
        total_length = sum(len(c) for c in thoughts_content)
        expected_avg = total_length / len(thoughts_content)
        assert abs(session.statistics.avg_thought_length - expected_avg) < 0.01

    def test_accumulative_statistics(self, storage_manager):
        """测试累计统计信息"""
        session_id = "test-stats-5"

        # 第一次调用 2 个工具
        sequential_thinking.sequential_thinking(
            thought="第一批",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[
                {"name": "tool_a", "arguments": {}},
                {"name": "tool_b", "arguments": {}},
            ],
        )

        # 第二次调用 1 个工具
        sequential_thinking.sequential_thinking(
            thought="第二批",
            nextThoughtNeeded=False,
            thoughtNumber=2,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[{"name": "tool_c", "arguments": {}}],
        )

        session = storage_manager.get_session(session_id)
        assert session.statistics.total_tool_calls == 3


class TestResourceControl:
    """
    任务 7.5: 测试资源控制限制

    测试工具调用次数限制和每步骤限制
    """

    @pytest.fixture
    def storage_manager(self, tmp_path, monkeypatch):
        """创建存储管理器"""
        # 设置较低的限制以便测试
        monkeypatch.setenv("DEEP_THINKING_MAX_TOOL_CALLS", "5")
        monkeypatch.setenv("DEEP_THINKING_MAX_TOOL_CALLS_PER_THOUGHT", "3")

        # 重新加载配置
        set_global_config(ThinkingConfig.from_env())

        manager = StorageManager(tmp_path)
        server._storage_manager = manager
        yield manager
        server._storage_manager = None

    def test_total_tool_calls_limit(self, storage_manager):
        """测试总工具调用次数限制"""
        session_id = "test-limit-total"

        # 调用 5 次（达到限制）
        for i in range(5):
            result = sequential_thinking.sequential_thinking(
                thought=f"思考{i + 1}",
                nextThoughtNeeded=True,
                thoughtNumber=i + 1,
                totalThoughts=10,
                session_id=session_id,
                toolCalls=[{"name": "test", "arguments": {}}],
            )

        session = storage_manager.get_session(session_id)
        assert session.statistics.total_tool_calls == 5

        # 第 6 次应该被拒绝
        result = sequential_thinking.sequential_thinking(
            thought="超限思考",
            nextThoughtNeeded=False,
            thoughtNumber=6,
            totalThoughts=10,
            session_id=session_id,
            toolCalls=[{"name": "test", "arguments": {}}],
        )
        assert "工具调用次数将超限" in result

    def test_per_thought_limit(self, storage_manager):
        """测试每步骤工具调用数量限制"""
        session_id = "test-limit-per-thought"

        # 尝试调用 4 个工具（超过限制 3）
        result = sequential_thinking.sequential_thinking(
            thought="超限调用",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[{"name": f"tool_{i}", "arguments": {}} for i in range(4)],
        )

        assert "单步骤工具调用数超限" in result

        # 验证没有工具调用被记录
        session = storage_manager.get_session(session_id)
        assert len(session.tool_call_history) == 0

    def test_limit_boundary_exact(self, storage_manager):
        """测试刚好等于限制的情况"""
        session_id = "test-limit-boundary"

        # 刚好调用 3 个工具（等于限制）
        result = sequential_thinking.sequential_thinking(
            thought="边界测试",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[{"name": f"tool_{i}", "arguments": {}} for i in range(3)],
        )

        # 应该成功
        assert "工具调用 (3个)" in result
        assert "超限" not in result

        session = storage_manager.get_session(session_id)
        assert len(session.tool_call_history) == 3


class TestResultCaching:
    """
    任务 7.6: 测试结果缓存功能

    测试工具调用结果缓存的正确性
    """

    @pytest.fixture
    def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager
        yield manager
        server._storage_manager = None

    def test_cached_result_marked(self, storage_manager):
        """测试缓存结果被正确标记"""
        session_id = "test-cache-1"

        sequential_thinking.sequential_thinking(
            thought="缓存测试",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[{"name": "test", "arguments": {}}],
            toolResults=[
                {"call_id": "1", "result": "data", "success": True, "from_cache": True},
            ],
        )

        session = storage_manager.get_session(session_id)
        record = session.tool_call_history[0]

        assert record.result_data is not None
        assert record.result_data.from_cache is True

    def test_cached_tool_calls_count(self, storage_manager):
        """测试缓存命中计数"""
        session_id = "test-cache-2"

        sequential_thinking.sequential_thinking(
            thought="缓存计数测试",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[
                {"name": "tool_a", "arguments": {}},
                {"name": "tool_b", "arguments": {}},
            ],
            toolResults=[
                {"call_id": "1", "result": "a", "success": True, "from_cache": True},
                {"call_id": "2", "result": "b", "success": True, "from_cache": False},
            ],
        )

        session = storage_manager.get_session(session_id)
        session.statistics.update_from_tool_calls(session.tool_call_history)

        assert session.statistics.cached_tool_calls == 1


class TestPersistenceAndRecovery:
    """
    任务 7.7: 测试持久化和恢复

    测试会话数据的正确保存和恢复
    """

    @pytest.fixture
    def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager
        yield manager
        server._storage_manager = None

    def test_session_persistence(self, storage_manager, tmp_path):
        """测试会话数据持久化"""
        session_id = "test-persist-1"

        # 创建包含工具调用的会话
        sequential_thinking.sequential_thinking(
            thought="持久化测试",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
            session_id=session_id,
            phase="tool_call",
            toolCalls=[{"name": "persist_tool", "arguments": {"key": "value"}}],
            toolResults=[{"call_id": "1", "result": "persisted", "success": True}],
        )

        # 创建新的存储管理器来模拟重启
        new_manager = StorageManager(tmp_path)
        server._storage_manager = new_manager

        # 恢复会话
        recovered = new_manager.get_session(session_id)
        assert recovered is not None
        assert recovered.thought_count() == 1

        # 验证思考步骤
        thought = recovered.thoughts[0]
        assert thought.phase == "tool_call"
        assert len(thought.tool_calls) == 1

        # 验证工具调用记录
        assert len(recovered.tool_call_history) == 1
        record = recovered.tool_call_history[0]
        assert record.call_data.tool_name == "persist_tool"
        assert record.result_data.result == "persisted"

    def test_statistics_persistence(self, storage_manager, tmp_path):
        """测试统计信息持久化"""
        session_id = "test-persist-2"

        # 创建会话并调用工具
        sequential_thinking.sequential_thinking(
            thought="统计持久化",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
            session_id=session_id,
            toolCalls=[
                {"name": "tool_a", "arguments": {}},
                {"name": "tool_b", "arguments": {}},
            ],
        )

        # 创建新的存储管理器
        new_manager = StorageManager(tmp_path)
        server._storage_manager = new_manager

        # 恢复会话
        recovered = new_manager.get_session(session_id)
        assert recovered.statistics.total_tool_calls == 2

    def test_phase_persistence(self, storage_manager, tmp_path):
        """测试执行阶段持久化"""
        session_id = "test-persist-3"

        # 创建不同阶段的思考
        phases = ["thinking", "tool_call", "analysis"]
        for i, phase in enumerate(phases, 1):
            sequential_thinking.sequential_thinking(
                thought=f"{phase}阶段",
                nextThoughtNeeded=i < len(phases),
                thoughtNumber=i,
                totalThoughts=len(phases),
                session_id=session_id,
                phase=phase,
            )

        # 创建新的存储管理器
        new_manager = StorageManager(tmp_path)
        server._storage_manager = new_manager

        # 恢复并验证
        recovered = new_manager.get_session(session_id)
        for i, expected_phase in enumerate(phases):
            assert recovered.thoughts[i].phase == expected_phase


class TestExportFunctionality:
    """
    任务 7.8: 测试导出功能

    测试 Interleaved Thinking 数据在各导出格式中的正确性
    使用同步的底层 formatter 函数进行测试
    """

    @pytest.fixture
    def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager
        yield manager
        server._storage_manager = None

    def test_json_export_interleaved_data(self, storage_manager, tmp_path):
        """测试 JSON 导出包含 Interleaved Thinking 数据"""
        session_id = "test-export-1"

        # 创建包含工具调用的会话
        sequential_thinking.sequential_thinking(
            thought="导出测试",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
            session_id=session_id,
            phase="tool_call",
            toolCalls=[{"name": "export_tool", "arguments": {"test": "value"}}],
            toolResults=[{"call_id": "1", "result": "exported", "success": True}],
        )

        # 获取会话
        session = storage_manager.get_session(session_id)
        assert session is not None

        # 使用同步的 formatter 导出为 JSON
        output_path = tmp_path / "export_test.json"
        export_session_to_file(session, "json", output_path)

        assert output_path.exists()

        # 验证 JSON 内容
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)

        # 验证思考步骤包含 phase 和 tool_calls
        assert data["thoughts"][0]["phase"] == "tool_call"
        assert len(data["thoughts"][0]["tool_calls"]) == 1

        # 验证工具调用历史
        assert len(data["tool_call_history"]) == 1
        assert data["tool_call_history"][0]["call_data"]["tool_name"] == "export_tool"

        # 验证统计信息
        assert "statistics" in data
        assert data["statistics"]["total_tool_calls"] == 1

    def test_markdown_export_interleaved_data(self, storage_manager, tmp_path):
        """测试 Markdown 导出包含 Interleaved Thinking 数据"""
        session_id = "test-export-2"

        sequential_thinking.sequential_thinking(
            thought="Markdown导出测试",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
            session_id=session_id,
            phase="analysis",
            toolCalls=[{"name": "md_tool", "arguments": {}}],
        )

        session = storage_manager.get_session(session_id)
        assert session is not None

        output_path = tmp_path / "export_test.md"
        export_session_to_file(session, "markdown", output_path)

        content = output_path.read_text(encoding="utf-8")

        # 验证阶段信息
        assert "分析阶段" in content or "analysis" in content

        # 验证工具调用信息
        assert "md_tool" in content

        # 验证统计信息
        assert "统计" in content

    def test_html_export_interleaved_data(self, storage_manager, tmp_path):
        """测试 HTML 导出包含 Interleaved Thinking 数据"""
        session_id = "test-export-3"

        sequential_thinking.sequential_thinking(
            thought="HTML导出测试",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
            session_id=session_id,
            phase="tool_call",
            toolCalls=[{"name": "html_tool", "arguments": {}}],
        )

        session = storage_manager.get_session(session_id)
        assert session is not None

        output_path = tmp_path / "export_test.html"
        export_session_to_file(session, "html", output_path)

        content = output_path.read_text(encoding="utf-8")

        # 验证 HTML 结构
        assert "<!DOCTYPE html>" in content

        # 验证阶段标签
        assert "tool_call" in content

        # 验证工具调用显示
        assert "html_tool" in content

    def test_text_export_interleaved_data(self, storage_manager, tmp_path):
        """测试 Text 导出包含 Interleaved Thinking 数据"""
        session_id = "test-export-4"

        sequential_thinking.sequential_thinking(
            thought="Text导出测试",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
            session_id=session_id,
            phase="analysis",
            toolCalls=[{"name": "text_tool", "arguments": {}}],
        )

        session = storage_manager.get_session(session_id)
        assert session is not None

        output_path = tmp_path / "export_test.txt"
        export_session_to_file(session, "text", output_path)

        content = output_path.read_text(encoding="utf-8")

        # 验证阶段信息
        assert "analysis" in content or "分析" in content

        # 验证工具调用
        assert "text_tool" in content


class TestVisualizationWithToolCalls:
    """
    测试可视化功能包含工具调用信息
    使用同步的底层 Visualizer 类进行测试
    """

    @pytest.fixture
    def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager
        yield manager
        server._storage_manager = None

    def test_mermaid_shows_tool_calls(self, storage_manager):
        """测试 Mermaid 可视化显示工具调用"""
        session_id = "test-viz-mermaid"

        sequential_thinking.sequential_thinking(
            thought="Mermaid测试",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
            session_id=session_id,
            phase="tool_call",
            toolCalls=[
                {"name": "viz_tool_a", "arguments": {}},
                {"name": "viz_tool_b", "arguments": {}},
            ],
        )

        session = storage_manager.get_session(session_id)
        assert session is not None

        # 使用同步的 Visualizer
        result = Visualizer.to_mermaid(session)

        # 验证工具调用节点
        assert "TOOL" in result

        # 验证阶段标签
        assert "工具调用" in result or "tool_call" in result

    def test_ascii_shows_tool_calls(self, storage_manager):
        """测试 ASCII 可视化显示工具调用"""
        session_id = "test-viz-ascii"

        sequential_thinking.sequential_thinking(
            thought="ASCII测试",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
            session_id=session_id,
            phase="tool_call",
            toolCalls=[{"name": "ascii_tool", "arguments": {}}],
        )

        session = storage_manager.get_session(session_id)
        assert session is not None

        # 使用同步的 Visualizer
        result = Visualizer.to_ascii(session)

        # 验证工具调用信息
        assert "ascii_tool" in result or "TOOL" in result

    def test_tree_shows_tool_calls(self, storage_manager):
        """测试 Tree 可视化显示工具调用"""
        session_id = "test-viz-tree"

        sequential_thinking.sequential_thinking(
            thought="Tree测试",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
            session_id=session_id,
            phase="tool_call",
            toolCalls=[{"name": "tree_tool", "arguments": {}}],
        )

        session = storage_manager.get_session(session_id)
        assert session is not None

        # 使用同步的 Visualizer
        result = Visualizer.to_tree(session)

        # 验证树形结构包含工具调用
        assert "tree_tool" in result or "TOOL" in result


class TestEdgeCases:
    """
    边界情况和异常处理测试
    """

    @pytest.fixture
    def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager
        yield manager
        server._storage_manager = None

    def test_tool_call_without_result(self, storage_manager):
        """测试工具调用没有结果的情况"""
        session_id = "test-edge-1"

        sequential_thinking.sequential_thinking(
            thought="无结果调用",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[{"name": "no_result_tool", "arguments": {}}],
        )

        session = storage_manager.get_session(session_id)
        record = session.tool_call_history[0]

        # 验证状态为 pending
        assert record.status == "pending"
        assert record.result_data is None

    def test_tool_result_without_call(self, storage_manager):
        """测试仅有结果没有调用的情况（应该推断为 analysis）"""
        session_id = "test-edge-2"

        result = sequential_thinking.sequential_thinking(
            thought="只有结果",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolResults=[{"call_id": "orphan", "result": "data", "success": True}],
        )

        # 应该推断为 analysis 阶段
        assert "分析 📊" in result

    def test_mixed_success_failure_results(self, storage_manager):
        """测试混合成功和失败的结果"""
        session_id = "test-edge-3"

        sequential_thinking.sequential_thinking(
            thought="混合结果",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
            session_id=session_id,
            toolCalls=[
                {"name": "success_tool", "arguments": {}},
                {"name": "fail_tool", "arguments": {}},
            ],
            toolResults=[
                {"call_id": "1", "result": "ok", "success": True},
                {"call_id": "2", "result": "error", "success": False},
            ],
        )

        session = storage_manager.get_session(session_id)

        # 验证成功/失败计数
        assert session.statistics.successful_tool_calls == 1

    def test_long_tool_name(self, storage_manager):
        """测试长工具名称"""
        session_id = "test-edge-4"
        long_name = "a" * 99  # 接近最大长度限制

        result = sequential_thinking.sequential_thinking(
            thought="长名称测试",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
            toolCalls=[{"name": long_name, "arguments": {}}],
        )

        # 应该正常处理
        assert "工具调用" in result

    def test_special_characters_in_arguments(self, storage_manager):
        """测试参数中包含特殊字符"""
        session_id = "test-edge-5"

        sequential_thinking.sequential_thinking(
            thought="特殊字符测试",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
            session_id=session_id,
            toolCalls=[
                {
                    "name": "special_tool",
                    "arguments": {
                        "unicode": "你好世界",
                        "emoji": "🔧",
                        "newline": "line1\nline2",
                    },
                }
            ],
        )

        session = storage_manager.get_session(session_id)
        record = session.tool_call_history[0]

        assert record.call_data.arguments["unicode"] == "你好世界"
        assert record.call_data.arguments["emoji"] == "🔧"
