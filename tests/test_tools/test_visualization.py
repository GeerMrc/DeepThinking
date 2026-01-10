"""
可视化工具单元测试

测试 visualization.py 中的可视化功能。
"""

from unittest.mock import MagicMock, patch

import pytest

from deep_thinking.models.thinking_session import ThinkingSession
from deep_thinking.models.thought import Thought
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
