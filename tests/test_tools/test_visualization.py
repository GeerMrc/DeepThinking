"""
可视化工具单元测试

测试 visualization.py 中的可视化功能。
"""

from unittest.mock import MagicMock, patch

import pytest

from deep_thinking.models.thinking_session import ThinkingSession
from deep_thinking.models.thought import Thought
from deep_thinking.models.tool_call import ToolCallData, ToolCallRecord, ToolResultData
from deep_thinking.tools import visualization
from deep_thinking.utils.formatters import Visualizer

# =============================================================================
# Visualizer.to_mermaid 测试
# =============================================================================


class TestVisualizerToMermaid:
    """测试 Mermaid 流程图生成"""

    def test_to_mermaid_empty_session(self, sample_session_data):
        """测试空会话的 Mermaid 生成"""
        session = ThinkingSession(**sample_session_data)
        result = Visualizer.to_mermaid(session)

        assert "graph TD" in result
        assert "会话暂无思考步骤" in result
        assert "classDef" in result

    def test_to_mermaid_single_thought(self, sample_session_data):
        """测试单个思考步骤的 Mermaid 生成"""
        thought = Thought(thought_number=1, content="测试思考", type="regular")
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_mermaid(session)

        assert "graph TD" in result
        assert "T1" in result
        assert "测试思考" in result
        assert ":::regular" in result

    def test_to_mermaid_regular_thoughts(self, sample_session_data):
        """测试多个常规思考的 Mermaid 生成"""
        thought1 = Thought(thought_number=1, content="第一步", type="regular")
        thought2 = Thought(thought_number=2, content="第二步", type="regular")

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)

        result = Visualizer.to_mermaid(session)

        assert "T1" in result
        assert "T2" in result
        assert "T1 --> T2" in result

    def test_to_mermaid_revision_thought(self, sample_session_data):
        """测试修订思考的 Mermaid 生成"""
        thought1 = Thought(thought_number=1, content="原始思考", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="修订思考",
            type="revision",
            is_revision=True,
            revises_thought=1,
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)

        result = Visualizer.to_mermaid(session)

        assert "T1" in result
        assert "T2" in result
        assert "修订步骤1" in result
        assert ":::revision" in result
        assert ".-.->|修订|" in result or "-.->" in result

    def test_to_mermaid_branch_thought(self, sample_session_data):
        """测试分支思考的 Mermaid 生成"""
        thought1 = Thought(thought_number=1, content="主思考", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="分支思考",
            type="branch",
            branch_from_thought=1,
            branch_id="branch-1",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)

        result = Visualizer.to_mermaid(session)

        assert "T1" in result
        # 分支ID中的连字符被替换成下划线（Mermaid节点ID规范）
        assert "T2_branch_1" in result
        assert "分支自步骤1" in result
        assert ":::branch" in result

    def test_to_mermaid_content_truncation(self, sample_session_data):
        """测试长内容截断"""
        # 使用超过30字符的内容（中文字符也需要计数）
        long_content = "这是一个非常非常非常非常非常非常非常非常非常非常非常非常非常长的思考内容"
        thought = Thought(thought_number=1, content=long_content, type="regular")
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_mermaid(session)

        # 长内容应该被截断（每个中文字符算1个字符）
        assert len(long_content) > 30
        # 检查输出中包含截断标记或原始内容的一部分
        assert long_content[:27] in result or "..." in result


# =============================================================================
# Visualizer.to_ascii 测试
# =============================================================================


class TestVisualizerToAscii:
    """测试 ASCII 流程图生成"""

    def test_to_ascii_empty_session(self, sample_session_data):
        """测试空会话的 ASCII 生成"""
        session = ThinkingSession(**sample_session_data)
        result = Visualizer.to_ascii(session)

        assert "会话暂无思考步骤" in result

    def test_to_ascii_single_thought(self, sample_session_data):
        """测试单个思考步骤的 ASCII 生成"""
        thought = Thought(thought_number=1, content="测试思考", type="regular")
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_ascii(session)

        assert "步骤 1" in result
        assert "测试思考" in result
        assert "💭" in result

    def test_to_ascii_regular_thoughts(self, sample_session_data):
        """测试多个常规思考的 ASCII 生成"""
        thought1 = Thought(thought_number=1, content="第一步", type="regular")
        thought2 = Thought(thought_number=2, content="第二步", type="regular")

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)

        result = Visualizer.to_ascii(session)

        assert "第一步" in result
        assert "第二步" in result
        assert "│" in result  # 连接线
        assert "▼" in result  # 箭头

    def test_to_ascii_revision_thought(self, sample_session_data):
        """测试修订思考的 ASCII 生成"""
        thought = Thought(
            thought_number=2,
            content="修订内容",
            type="revision",
            is_revision=True,
            revises_thought=1,
        )
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_ascii(session)

        assert "🔄" in result
        assert "修订" in result
        assert "修订步骤 1" in result

    def test_to_ascii_branch_thought(self, sample_session_data):
        """测试分支思考的 ASCII 生成"""
        thought = Thought(
            thought_number=2,
            content="分支内容",
            type="branch",
            branch_from_thought=1,
            branch_id="b1",
        )
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_ascii(session)

        assert "🌿" in result
        assert "分支" in result
        assert "分支自步骤 1" in result

    def test_to_ascii_content_truncation(self, sample_session_data):
        """测试长内容截断"""
        # 使用超过28字符的内容
        long_content = "这是一个非常非常非常非常非常非常非常非常非常非常非常非常非常长的思考内容"
        thought = Thought(thought_number=1, content=long_content, type="regular")
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_ascii(session)

        # 长内容应该被截断或显示完整
        assert len(long_content) > 28
        # 检查输出中包含内容的一部分
        assert long_content[:20] in result or long_content in result


# =============================================================================
# Visualizer.to_tree 测试
# =============================================================================


class TestVisualizerToTree:
    """测试树状结构生成"""

    def test_to_tree_empty_session(self, sample_session_data):
        """测试空会话的树状结构生成"""
        session = ThinkingSession(**sample_session_data)
        result = Visualizer.to_tree(session)

        assert "会话暂无思考步骤" in result

    def test_to_tree_single_thought(self, sample_session_data):
        """测试单个思考步骤的树状结构生成"""
        thought = Thought(thought_number=1, content="测试思考", type="regular")
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_tree(session)

        assert "🧠 思考流程树" in result
        assert "└──" in result
        assert "💭" in result
        assert "步骤 1" in result

    def test_to_tree_multiple_thoughts(self, sample_session_data):
        """测试多个思考步骤的树状结构生成"""
        thought1 = Thought(thought_number=1, content="第一步", type="regular")
        thought2 = Thought(thought_number=2, content="第二步", type="regular")

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)

        result = Visualizer.to_tree(session)

        assert "├──" in result  # 第一个思考
        assert "└──" in result  # 最后一个思考
        assert "步骤 1" in result
        assert "步骤 2" in result

    def test_to_tree_revision_thought(self, sample_session_data):
        """测试修订思考的树状结构生成"""
        thought1 = Thought(thought_number=1, content="原始", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="修订",
            type="revision",
            is_revision=True,
            revises_thought=1,
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)

        result = Visualizer.to_tree(session)

        assert "📝 修订步骤 1" in result

    def test_to_tree_branch_thought(self, sample_session_data):
        """测试分支思考的树状结构生成"""
        thought1 = Thought(thought_number=1, content="主思考", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="分支",
            type="branch",
            branch_from_thought=1,
            branch_id="b1",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)

        result = Visualizer.to_tree(session)

        assert "🔀 分支自步骤 1" in result


# =============================================================================
# visualize_session MCP 工具测试
# =============================================================================


@pytest.mark.asyncio
class TestVisualizeSessionTool:
    """测试 visualize_session MCP 工具"""

    async def test_visualize_session_default_mermaid(self, sample_session_data, clean_env):
        """测试默认 Mermaid 格式可视化"""
        thought = Thought(thought_number=1, content="测试", type="regular")
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        mock_manager = MagicMock()
        mock_manager.get_session.return_value = session

        with patch(
            "deep_thinking.tools.visualization.get_storage_manager", return_value=mock_manager
        ):
            result = await visualization.visualize_session("test-session-123")

        assert "思考会话可视化" in result
        assert "Mermaid 流程图" in result
        assert "```mermaid" in result
        assert "graph TD" in result

    async def test_visualize_session_ascii_format(self, sample_session_data, clean_env):
        """测试 ASCII 格式可视化"""
        thought = Thought(thought_number=1, content="测试", type="regular")
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        mock_manager = MagicMock()
        mock_manager.get_session.return_value = session

        with patch(
            "deep_thinking.tools.visualization.get_storage_manager", return_value=mock_manager
        ):
            result = await visualization.visualize_session("test-session-123", "ascii")

        assert "ASCII 流程图" in result

    async def test_visualize_session_tree_format(self, sample_session_data, clean_env):
        """测试树状结构可视化"""
        thought = Thought(thought_number=1, content="测试", type="regular")
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        mock_manager = MagicMock()
        mock_manager.get_session.return_value = session

        with patch(
            "deep_thinking.tools.visualization.get_storage_manager", return_value=mock_manager
        ):
            result = await visualization.visualize_session("test-session-123", "tree")

        assert "树状结构" in result

    async def test_visualize_session_not_found(self, clean_env):
        """测试会话不存在时的错误处理"""
        mock_manager = MagicMock()
        mock_manager.get_session.return_value = None

        with (
            patch(
                "deep_thinking.tools.visualization.get_storage_manager", return_value=mock_manager
            ),
            pytest.raises(ValueError, match="会话不存在"),
        ):
            await visualization.visualize_session("nonexistent-session")

    async def test_visualize_session_invalid_format(self, sample_session_data, clean_env):
        """测试无效格式时的错误处理"""
        session = ThinkingSession(**sample_session_data)

        mock_manager = MagicMock()
        mock_manager.get_session.return_value = session

        with (
            patch(
                "deep_thinking.tools.visualization.get_storage_manager", return_value=mock_manager
            ),
            pytest.raises(ValueError, match="不支持的格式"),
        ):
            await visualization.visualize_session("test-session-123", "invalid")


# =============================================================================
# visualize_session_simple MCP 工具测试
# =============================================================================


@pytest.mark.asyncio
class TestVisualizeSessionSimpleTool:
    """测试 visualize_session_simple MCP 工具"""

    async def test_visualize_session_simple_mermaid(self, sample_session_data, clean_env):
        """测试简化版 Mermaid 可视化"""
        thought = Thought(thought_number=1, content="测试", type="regular")
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        mock_manager = MagicMock()
        mock_manager.get_session.return_value = session

        with patch(
            "deep_thinking.tools.visualization.get_storage_manager", return_value=mock_manager
        ):
            # 明确指定 mermaid 格式
            result = await visualization.visualize_session_simple("test-session-123", "mermaid")

        # 简化版直接返回内容，不包含额外说明
        assert "graph TD" in result
        assert "思考会话可视化" not in result

    async def test_visualize_session_simple_ascii(self, sample_session_data, clean_env):
        """测试简化版 ASCII 可视化"""
        thought = Thought(thought_number=1, content="测试", type="regular")
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        mock_manager = MagicMock()
        mock_manager.get_session.return_value = session

        with patch(
            "deep_thinking.tools.visualization.get_storage_manager", return_value=mock_manager
        ):
            result = await visualization.visualize_session_simple("test-session-123", "ascii")

        assert "步骤 1" in result

    async def test_visualize_session_simple_tree(self, sample_session_data, clean_env):
        """测试简化版树状结构可视化"""
        thought = Thought(thought_number=1, content="测试", type="regular")
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        mock_manager = MagicMock()
        mock_manager.get_session.return_value = session

        with patch(
            "deep_thinking.tools.visualization.get_storage_manager", return_value=mock_manager
        ):
            result = await visualization.visualize_session_simple("test-session-123", "tree")

        assert "🧠 思考流程树" in result


# =============================================================================
# 辅助函数测试
# =============================================================================


class TestHelperFunctions:
    """测试辅助函数"""

    def test_normalize_format(self):
        """测试格式标准化"""
        from deep_thinking.tools.visualization import _normalize_format

        assert _normalize_format("mermaid") == "mermaid"
        assert _normalize_format("mmd") == "mermaid"
        assert _normalize_format("ascii") == "ascii"
        assert _normalize_format("text") == "ascii"
        assert _normalize_format("tree") == "tree"

        with pytest.raises(ValueError, match="不支持的格式"):
            _normalize_format("invalid")


# =============================================================================
# Interleaved Thinking 可视化测试
# =============================================================================


class TestInterleavedThinkingMermaid:
    """测试 Mermaid 格式的 Interleaved Thinking 支持"""

    def test_mermaid_with_tool_calls(self, sample_session_data):
        """测试 Mermaid 显示工具调用节点"""
        # 创建带工具调用的思考步骤
        thought = Thought(
            thought_number=1,
            content="需要查询数据",
            type="regular",
            phase="tool_call",
            tool_calls=["record-001"],
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        # 添加工具调用记录
        record = ToolCallRecord(
            record_id="record-001",
            thought_number=1,
            call_data=ToolCallData(tool_name="search_api", arguments={"query": "test"}),
            result_data=ToolResultData(call_id="call-001", success=True, result="found"),
            status="completed",
        )
        session.tool_call_history.append(record)

        result = Visualizer.to_mermaid(session)

        # 验证工具调用节点存在
        assert "T1_TOOL1" in result
        assert "search_api" in result
        assert ":::tool_call" in result
        # 验证工具调用连接线
        assert "-.->|调用|" in result or "-.->" in result

    def test_mermaid_with_phase_info(self, sample_session_data):
        """测试 Mermaid 显示阶段信息"""
        thought = Thought(
            thought_number=1,
            content="分析数据",
            type="regular",
            phase="analysis",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_mermaid(session)

        # 验证阶段信息存在
        assert "分析阶段" in result or "📊" in result

    def test_mermaid_multiple_tool_calls(self, sample_session_data):
        """测试 Mermaid 显示多个工具调用"""
        thought = Thought(
            thought_number=1,
            content="多工具调用",
            type="regular",
            phase="tool_call",
            tool_calls=["record-001", "record-002"],
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        # 添加多个工具调用记录
        session.tool_call_history.append(
            ToolCallRecord(
                record_id="record-001",
                thought_number=1,
                call_data=ToolCallData(tool_name="read_file", arguments={}),
                status="completed",
            )
        )
        session.tool_call_history.append(
            ToolCallRecord(
                record_id="record-002",
                thought_number=1,
                call_data=ToolCallData(tool_name="write_file", arguments={}),
                status="failed",
            )
        )

        result = Visualizer.to_mermaid(session)

        # 验证两个工具调用节点
        assert "T1_TOOL1" in result
        assert "T1_TOOL2" in result
        assert "read_file" in result
        assert "write_file" in result

    def test_mermaid_tool_call_style(self, sample_session_data):
        """测试 Mermaid 工具调用样式定义"""
        session = ThinkingSession(**sample_session_data)
        result = Visualizer.to_mermaid(session)

        # 验证工具调用样式定义存在
        assert "classDef tool_call" in result


class TestInterleavedThinkingAscii:
    """测试 ASCII 格式的 Interleaved Thinking 支持"""

    def test_ascii_with_tool_calls(self, sample_session_data):
        """测试 ASCII 显示工具调用"""
        thought = Thought(
            thought_number=1,
            content="需要查询数据",
            type="regular",
            phase="tool_call",
            tool_calls=["record-001"],
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        # 添加工具调用记录
        session.tool_call_history.append(
            ToolCallRecord(
                record_id="record-001",
                thought_number=1,
                call_data=ToolCallData(tool_name="search_api", arguments={}),
                status="completed",
            )
        )

        result = Visualizer.to_ascii(session)

        # 验证工具调用信息
        assert "🔧" in result
        assert "search_api" in result
        assert "✅" in result  # completed status emoji

    def test_ascii_with_phase_info(self, sample_session_data):
        """测试 ASCII 显示阶段信息"""
        thought = Thought(
            thought_number=1,
            content="思考中",
            type="regular",
            phase="thinking",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_ascii(session)

        # 验证阶段信息
        assert "思考阶段" in result or "💭" in result

    def test_ascii_analysis_phase(self, sample_session_data):
        """测试 ASCII 显示分析阶段"""
        thought = Thought(
            thought_number=1,
            content="分析结果",
            type="regular",
            phase="analysis",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_ascii(session)

        # 验证分析阶段
        assert "分析阶段" in result or "📊" in result


class TestInterleavedThinkingTree:
    """测试 Tree 格式的 Interleaved Thinking 支持"""

    def test_tree_with_tool_calls(self, sample_session_data):
        """测试 Tree 显示工具调用"""
        thought = Thought(
            thought_number=1,
            content="执行工具",
            type="regular",
            phase="tool_call",
            tool_calls=["record-001"],
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        # 添加工具调用记录
        session.tool_call_history.append(
            ToolCallRecord(
                record_id="record-001",
                thought_number=1,
                call_data=ToolCallData(tool_name="execute_cmd", arguments={}),
                status="completed",
            )
        )

        result = Visualizer.to_tree(session)

        # 验证工具调用信息
        assert "🔧" in result
        assert "execute_cmd" in result

    def test_tree_with_phase_info(self, sample_session_data):
        """测试 Tree 显示阶段信息"""
        thought = Thought(
            thought_number=1,
            content="分析数据",
            type="regular",
            phase="analysis",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_tree(session)

        # 验证阶段信息
        assert "分析阶段" in result or "📊" in result

    def test_tree_multiple_tool_calls(self, sample_session_data):
        """测试 Tree 显示多个工具调用"""
        thought = Thought(
            thought_number=1,
            content="多工具",
            type="regular",
            phase="tool_call",
            tool_calls=["record-001", "record-002", "record-003"],
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        # 添加多个工具调用记录
        for i, tool_name in enumerate(["tool_a", "tool_b", "tool_c"]):
            session.tool_call_history.append(
                ToolCallRecord(
                    record_id=f"record-00{i + 1}",
                    thought_number=1,
                    call_data=ToolCallData(tool_name=tool_name, arguments={}),
                    status="completed",
                )
            )

        result = Visualizer.to_tree(session)

        # 验证所有工具调用都显示
        assert "tool_a" in result
        assert "tool_b" in result
        assert "tool_c" in result

    def test_tree_different_phases(self, sample_session_data):
        """测试 Tree 显示不同阶段"""
        phases = [
            ("thinking", "思考阶段", "💭"),
            ("tool_call", "工具调用阶段", "🔧"),
            ("analysis", "分析阶段", "📊"),
        ]

        for phase, phase_name, emoji in phases:
            thought = Thought(
                thought_number=1,
                content=f"测试{phase}",
                type="regular",
                phase=phase,  # type: ignore
            )

            session = ThinkingSession(**sample_session_data)
            session.add_thought(thought)

            result = Visualizer.to_tree(session)

            # 验证阶段信息显示
            assert phase_name in result or emoji in result, f"Phase {phase} not found in result"


# =============================================================================
# 分支思考可视化测试 (Branch Thinking Visualization)
# =============================================================================


class TestBranchThinkingMermaid:
    """测试分支思考的 Mermaid 可视化连接"""

    def test_branch_continuation_mermaid(self, sample_session_data):
        """测试分支后的延续步骤有正确连接"""
        # T1 -> T2(branch) -> T3(regular)
        thought1 = Thought(thought_number=1, content="主思考", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="分支思考",
            type="branch",
            branch_from_thought=1,
            branch_id="b1",
        )
        thought3 = Thought(thought_number=3, content="延续思考", type="regular")

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)
        session.add_thought(thought3)

        result = Visualizer.to_mermaid(session)

        # 验证分支连接存在
        assert "T1" in result
        assert "T2_b1" in result
        assert "T3" in result
        # 验证分支连接线 T1 -.->|分支| T2
        assert "-.->|分支|" in result
        # 验证延续连接 T2 --> T3
        assert "T2_b1 --> T3" in result

    def test_multilevel_branch_mermaid(self, sample_session_data):
        """测试多级分支的连接关系"""
        # T1 -> T2(branch from 1) -> T3(branch from 2)
        thought1 = Thought(thought_number=1, content="主思考", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="一级分支",
            type="branch",
            branch_from_thought=1,
            branch_id="b1",
        )
        thought3 = Thought(
            thought_number=3,
            content="二级分支",
            type="branch",
            branch_from_thought=2,
            branch_id="b1-1",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)
        session.add_thought(thought3)

        result = Visualizer.to_mermaid(session)

        # 验证多级分支连接
        assert "T1" in result
        assert "T2_b1" in result
        assert "T3_b1_1" in result
        # 验证 T1 -.-> T2 -.-> T3 连接链
        assert "T1 -.->|分支| T2_b1" in result
        assert "T2_b1 --> T3_b1_1" in result

    def test_same_branch_multiple_thoughts_mermaid(self, sample_session_data):
        """测试同分支内多个思考步骤的连接"""
        # T1 -> T2(branch from 1, id=b1) -> T3(branch id=b1) -> T4(branch id=b1)
        thought1 = Thought(thought_number=1, content="主思考", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="分支开始",
            type="branch",
            branch_from_thought=1,
            branch_id="b1",
        )
        thought3 = Thought(
            thought_number=3,
            content="分支继续",
            type="regular",
            branch_id="b1",
        )
        thought4 = Thought(
            thought_number=4,
            content="分支结束",
            type="regular",
            branch_id="b1",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)
        session.add_thought(thought3)
        session.add_thought(thought4)

        result = Visualizer.to_mermaid(session)

        # 验证节点存在
        assert "T1" in result
        assert "T2_b1" in result
        assert "T3_b1" in result
        assert "T4_b1" in result
        # 验证连接链 T1 -.-> T2 --> T3 --> T4
        assert "T1 -.->|分支| T2_b1" in result
        # 验证 T2 -> T3 连接（分支思考到同分支常规思考）
        assert "T2_b1 --> T3_b1" in result

    def test_branch_to_main_flow_return(self, sample_session_data):
        """测试分支返回主流程的连接"""
        # T1 -> T2(branch) -> T3(返回主流程)
        thought1 = Thought(thought_number=1, content="主流程1", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="分支",
            type="branch",
            branch_from_thought=1,
            branch_id="b1",
        )
        thought3 = Thought(thought_number=3, content="主流程2", type="regular")

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)
        session.add_thought(thought3)

        result = Visualizer.to_mermaid(session)

        # 验证分支到主流程的连接
        assert "T2_b1 --> T3" in result


class TestBranchThinkingAscii:
    """测试分支思考的 ASCII 可视化连接"""

    def test_branch_continuation_ascii(self, sample_session_data):
        """测试 ASCII 显示分支延续"""
        thought1 = Thought(thought_number=1, content="主思考", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="分支",
            type="branch",
            branch_from_thought=1,
            branch_id="b1",
        )
        thought3 = Thought(thought_number=3, content="延续", type="regular")

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)
        session.add_thought(thought3)

        result = Visualizer.to_ascii(session)

        # 验证分支思考存在
        assert "🌿" in result
        assert "分支" in result
        # 验证连接线
        assert "║" in result or "│" in result

    def test_multilevel_branch_ascii(self, sample_session_data):
        """测试 ASCII 多级分支显示"""
        thought1 = Thought(thought_number=1, content="主思考", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="一级分支",
            type="branch",
            branch_from_thought=1,
            branch_id="b1",
        )
        thought3 = Thought(
            thought_number=3,
            content="二级分支",
            type="branch",
            branch_from_thought=2,
            branch_id="b1-1",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)
        session.add_thought(thought3)

        result = Visualizer.to_ascii(session)

        # 验证多级分支显示
        assert "🌿" in result
        assert "一级分支" in result or "一级" in result
        assert "二级分支" in result or "二级" in result

    def test_same_branch_multiple_thoughts_ascii(self, sample_session_data):
        """测试 ASCII 同分支内多个思考步骤的连接线"""
        # T1 -> T2(branch from 1, id=b1) -> T3(branch id=b1) -> T4(branch id=b1)
        thought1 = Thought(thought_number=1, content="主思考", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="分支开始",
            type="branch",
            branch_from_thought=1,
            branch_id="b1",
        )
        thought3 = Thought(
            thought_number=3,
            content="分支继续",
            type="regular",
            branch_id="b1",
        )
        thought4 = Thought(
            thought_number=4,
            content="分支结束",
            type="regular",
            branch_id="b1",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)
        session.add_thought(thought3)
        session.add_thought(thought4)

        result = Visualizer.to_ascii(session)

        # 验证所有步骤显示
        assert "步骤 1" in result
        assert "步骤 2" in result
        assert "步骤 3" in result
        assert "步骤 4" in result
        # 验证分支标识
        assert "🌿" in result
        # 验证连接线（分支延续使用 ║ 或 │）
        assert "║" in result or "│" in result


class TestBranchThinkingTree:
    """测试分支思考的树状结构可视化"""

    def test_branch_tree_indentation(self, sample_session_data):
        """测试树状结构的分支缩进"""
        thought1 = Thought(thought_number=1, content="主思考", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="分支",
            type="branch",
            branch_from_thought=1,
            branch_id="b1",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)

        result = Visualizer.to_tree(session)

        # 验证分支显示
        assert "分支自步骤 1" in result
        assert "🔀" in result

    def test_multilevel_branch_tree(self, sample_session_data):
        """测试多级分支的树状结构"""
        thought1 = Thought(thought_number=1, content="主思考", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="一级分支",
            type="branch",
            branch_from_thought=1,
            branch_id="b1",
        )
        thought3 = Thought(
            thought_number=3,
            content="二级分支",
            type="branch",
            branch_from_thought=2,
            branch_id="b1-1",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)
        session.add_thought(thought3)

        result = Visualizer.to_tree(session)

        # 验证多级分支缩进
        assert "🧠 思考流程树" in result
        assert "步骤 1" in result
        assert "步骤 2" in result
        assert "步骤 3" in result
        # 验证分支信息
        assert "分支自步骤" in result

    def test_same_branch_continuation_tree(self, sample_session_data):
        """测试同分支内多个步骤的树状结构"""
        thought1 = Thought(thought_number=1, content="主思考", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="分支开始",
            type="branch",
            branch_from_thought=1,
            branch_id="b1",
        )
        thought3 = Thought(
            thought_number=3,
            content="分支继续",
            type="regular",
            branch_id="b1",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)
        session.add_thought(thought3)

        result = Visualizer.to_tree(session)

        # 验证所有步骤都显示
        assert "步骤 1" in result
        assert "步骤 2" in result
        assert "步骤 3" in result


# =============================================================================
# 其他思考类型可视化测试 (Comparison/Reverse/Hypothetical)
# =============================================================================


class TestComparisonThinkingVisualization:
    """测试对比思考的可视化"""

    def test_comparison_mermaid(self, sample_session_data):
        """测试 Mermaid 显示对比思考信息"""
        thought = Thought(
            thought_number=1,
            content="对比方案",
            type="comparison",
            comparison_items=["方案A", "方案B", "方案C"],
            comparison_dimensions=["成本", "效率"],
            comparison_result="方案B最优",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_mermaid(session)

        # 验证对比思考节点存在
        assert "T1" in result
        assert ":::comparison" in result
        # 验证对比项数量显示
        assert "对比3项" in result

    def test_comparison_ascii(self, sample_session_data):
        """测试 ASCII 显示对比思考信息"""
        thought = Thought(
            thought_number=1,
            content="对比方案",
            type="comparison",
            comparison_items=["方案A", "方案B"],
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_ascii(session)

        # 验证对比思考显示
        assert "⚖️" in result
        assert "对比" in result

    def test_comparison_tree(self, sample_session_data):
        """测试 Tree 显示对比思考信息"""
        thought = Thought(
            thought_number=1,
            content="对比方案",
            type="comparison",
            comparison_items=["A", "B"],
            comparison_result="选B",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_tree(session)

        # 验证对比思考显示
        assert "⚖️" in result
        assert "对比" in result


class TestReverseThinkingVisualization:
    """测试逆向思考的可视化"""

    def test_reverse_mermaid(self, sample_session_data):
        """测试 Mermaid 显示逆向思考信息"""
        thought = Thought(
            thought_number=3,
            content="逆向分析",
            type="reverse",
            reverse_from=1,  # reverse_from 必须小于 thought_number
            reverse_target="找出根本原因",
            reverse_steps=["步骤1", "步骤2", "步骤3"],
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_mermaid(session)

        # 验证逆向思考节点存在 (thought_number=3 所以节点 ID 是 T3)
        assert "T3" in result
        assert ":::reverse" in result
        # 验证目标显示
        assert "目标" in result

    def test_reverse_ascii(self, sample_session_data):
        """测试 ASCII 显示逆向思考信息"""
        thought = Thought(
            thought_number=1,
            content="逆向分析",
            type="reverse",
            reverse_target="找出问题根源",
            reverse_steps=["step1", "step2"],
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_ascii(session)

        # 验证逆向思考显示
        assert "🔙" in result
        assert "目标" in result

    def test_reverse_tree(self, sample_session_data):
        """测试 Tree 显示逆向思考信息"""
        thought = Thought(
            thought_number=1,
            content="逆向分析",
            type="reverse",
            reverse_target="找到根因",
            reverse_steps=["回溯1", "回溯2"],
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_tree(session)

        # 验证逆向思考显示
        assert "🔙" in result
        assert "目标" in result or "反推" in result


class TestHypotheticalThinkingVisualization:
    """测试假设思考的可视化"""

    def test_hypothetical_mermaid(self, sample_session_data):
        """测试 Mermaid 显示假设思考信息"""
        thought = Thought(
            thought_number=1,
            content="假设分析",
            type="hypothetical",
            hypothetical_condition="如果用户增长100%",
            hypothetical_impact="需要扩容服务器",
            hypothetical_probability="70%",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_mermaid(session)

        # 验证假设思考节点存在
        assert "T1" in result
        assert ":::hypothetical" in result
        # 验证假设条件显示
        assert "假设" in result

    def test_hypothetical_ascii(self, sample_session_data):
        """测试 ASCII 显示假设思考信息"""
        thought = Thought(
            thought_number=1,
            content="假设分析",
            type="hypothetical",
            hypothetical_condition="如果流量翻倍",
            hypothetical_probability="高",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_ascii(session)

        # 验证假设思考显示
        assert "🤔" in result
        assert "假设" in result

    def test_hypothetical_tree(self, sample_session_data):
        """测试 Tree 显示假设思考信息"""
        thought = Thought(
            thought_number=1,
            content="假设分析",
            type="hypothetical",
            hypothetical_condition="假设需求变更",
            hypothetical_impact="需要重新设计",
            hypothetical_probability="中等",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = Visualizer.to_tree(session)

        # 验证假设思考显示
        assert "🤔" in result
        assert "假设" in result
