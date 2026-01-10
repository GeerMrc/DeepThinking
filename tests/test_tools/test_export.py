"""
导出工具单元测试

测试 export.py 中的导出功能。
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from deep_thinking.models.thinking_session import ThinkingSession
from deep_thinking.models.thought import Thought
from deep_thinking.tools import export
from deep_thinking.utils.formatters import SessionFormatter, export_session_to_file

# =============================================================================
# SessionFormatter.to_json 测试
# =============================================================================


class TestSessionFormatterToJson:
    """测试 JSON 格式导出"""

    def test_to_json_basic_session(self, sample_session_data):
        """测试基本会话的 JSON 导出"""
        session = ThinkingSession(**sample_session_data)
        result = SessionFormatter.to_json(session)

        # 验证是有效的 JSON
        data = json.loads(result)
        assert data["session_id"] == "test-session-123"
        assert data["name"] == "测试会话"
        assert data["status"] == "active"

    def test_to_json_with_thoughts(self, sample_session_data):
        """测试包含思考步骤的会话 JSON 导出"""
        # 创建思考步骤
        thought = Thought(
            thought_number=1,
            content="测试思考内容",
            type="regular",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = SessionFormatter.to_json(session)
        data = json.loads(result)

        assert data["thought_count"] == 1
        assert len(data["thoughts"]) == 1
        assert data["thoughts"][0]["content"] == "测试思考内容"

    def test_to_json_indent(self, sample_session_data):
        """测试 JSON 缩进参数"""
        session = ThinkingSession(**sample_session_data)

        # 默认缩进
        result_default = SessionFormatter.to_json(session)
        assert "\n" in result_default  # 应该有换行

        # 无缩进
        result_no_indent = SessionFormatter.to_json(session, indent=None)
        assert "\n" not in result_no_indent


# =============================================================================
# SessionFormatter.to_markdown 测试
# =============================================================================


class TestSessionFormatterToMarkdown:
    """测试 Markdown 格式导出"""

    def test_to_markdown_basic_structure(self, sample_session_data):
        """测试 Markdown 基本结构"""
        session = ThinkingSession(**sample_session_data)
        result = SessionFormatter.to_markdown(session)

        # 验证基本元素
        assert "# 测试会话" in result
        assert "## 会话信息" in result
        assert "**会话ID**" in result
        assert "**状态**" in result
        assert "**思考步骤数**" in result

    def test_to_markdown_with_description(self, sample_session_data):
        """测试带描述的会话"""
        sample_session_data["description"] = "这是一个测试描述"
        session = ThinkingSession(**sample_session_data)
        result = SessionFormatter.to_markdown(session)

        assert "> 这是一个测试描述" in result

    def test_to_markdown_with_thoughts(self, sample_session_data):
        """测试包含思考步骤的会话"""
        thought1 = Thought(thought_number=1, content="第一个思考", type="regular")
        thought2 = Thought(
            thought_number=2,
            content="修订第一个思考",
            type="revision",
            is_revision=True,
            revises_thought=1,
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought1)
        session.add_thought(thought2)

        result = SessionFormatter.to_markdown(session)

        assert "## 思考步骤" in result
        assert "💭 **步骤 1**" in result
        assert "🔄 **步骤 2**" in result
        assert "第一个思考" in result
        assert "修订第一个思考" in result

    def test_to_markdown_branch_thought(self, sample_session_data):
        """测试分支思考的 Markdown 导出"""
        # 先添加一个常规思考作为分支的起点
        thought0 = Thought(thought_number=1, content="基础思考", type="regular")
        # 分支思考从第1步分支，但自身编号为2
        thought1 = Thought(
            thought_number=2,
            content="分支思考",
            type="branch",
            branch_from_thought=1,
            branch_id="branch-1",
        )

        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought0)
        session.add_thought(thought1)

        result = SessionFormatter.to_markdown(session)

        assert "🌿 **步骤 2**" in result
        assert "分支自步骤 1" in result

    def test_to_markdown_with_metadata(self, sample_session_data):
        """测试带元数据的会话"""
        sample_session_data["metadata"] = {"key": "value", "number": 42}
        session = ThinkingSession(**sample_session_data)
        result = SessionFormatter.to_markdown(session)

        assert "## 元数据" in result
        assert '"key": "value"' in result
        assert '"number": 42' in result


# =============================================================================
# SessionFormatter.to_html 测试
# =============================================================================


class TestSessionFormatterToHtml:
    """测试 HTML 格式导出"""

    def test_to_html_basic_structure(self, sample_session_data):
        """测试 HTML 基本结构"""
        session = ThinkingSession(**sample_session_data)
        result = SessionFormatter.to_html(session)

        # 验证基本元素
        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "<title>" in result
        assert "<body>" in result
        assert "测试会话" in result

    def test_to_html_with_thoughts(self, sample_session_data):
        """测试包含思考步骤的 HTML 导出"""
        thought = Thought(thought_number=1, content="HTML 测试思考", type="regular")
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = SessionFormatter.to_html(session)

        assert "HTML 测试思考" in result
        assert '<div class="thought">' in result
        assert "步骤 1" in result

    def test_to_html_escaping(self, sample_session_data):
        """测试 HTML 特殊字符转义"""
        sample_session_data["name"] = 'Test <script>alert("test")</script>'
        session = ThinkingSession(**sample_session_data)
        result = SessionFormatter.to_html(session)

        # 应该被转义
        assert "&lt;script&gt;" in result
        assert "<script>" not in result


# =============================================================================
# SessionFormatter.to_text 测试
# =============================================================================


class TestSessionFormatterToText:
    """测试纯文本格式导出"""

    def test_to_text_basic_structure(self, sample_session_data):
        """测试纯文本基本结构"""
        session = ThinkingSession(**sample_session_data)
        result = SessionFormatter.to_text(session)

        # 验证基本元素
        assert "======" in result
        assert "测试会话" in result
        assert "会话信息" in result
        assert "会话ID:" in result

    def test_to_text_with_thoughts(self, sample_session_data):
        """测试包含思考步骤的纯文本导出"""
        thought = Thought(thought_number=1, content="纯文本测试", type="regular")
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = SessionFormatter.to_text(session)

        assert "纯文本测试" in result
        assert "[步骤 1]" in result

    def test_to_text_revision_thought(self, sample_session_data):
        """测试修订思考的纯文本导出"""
        thought = Thought(
            thought_number=2,
            content="修订内容",
            type="revision",
            is_revision=True,
            revises_thought=1,
        )
        session = ThinkingSession(**sample_session_data)
        session.add_thought(thought)

        result = SessionFormatter.to_text(session)

        assert "类型: 修订思考" in result
        assert "修订: 步骤 1" in result


# =============================================================================
# export_session_to_file 测试
# =============================================================================


class TestExportSessionToFile:
    """测试导出到文件功能"""

    def test_export_json_file(self, sample_session_data, temp_dir):
        """测试导出为 JSON 文件"""
        session = ThinkingSession(**sample_session_data)
        output_path = temp_dir / "test_export.json"

        result_path = export_session_to_file(session, "json", output_path)

        assert result_path == str(output_path.absolute())
        assert output_path.exists()

        # 验证文件内容
        content = output_path.read_text(encoding="utf-8")
        data = json.loads(content)
        assert data["session_id"] == "test-session-123"

    def test_export_markdown_file(self, sample_session_data, temp_dir):
        """测试导出为 Markdown 文件"""
        session = ThinkingSession(**sample_session_data)
        output_path = temp_dir / "test_export.md"

        result_path = export_session_to_file(session, "markdown", output_path)

        assert result_path == str(output_path.absolute())
        assert output_path.exists()

        content = output_path.read_text(encoding="utf-8")
        assert "# 测试会话" in content

    def test_export_html_file(self, sample_session_data, temp_dir):
        """测试导出为 HTML 文件"""
        session = ThinkingSession(**sample_session_data)
        output_path = temp_dir / "test_export.html"

        result_path = export_session_to_file(session, "html", output_path)

        assert result_path == str(output_path.absolute())
        assert output_path.exists()

        content = output_path.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content

    def test_export_text_file(self, sample_session_data, temp_dir):
        """测试导出为纯文本文件"""
        session = ThinkingSession(**sample_session_data)
        output_path = temp_dir / "test_export.txt"

        result_path = export_session_to_file(session, "text", output_path)

        assert result_path == str(output_path.absolute())
        assert output_path.exists()

    def test_export_creates_directory(self, sample_session_data, temp_dir):
        """测试自动创建输出目录"""
        session = ThinkingSession(**sample_session_data)
        output_path = temp_dir / "subdir" / "nested" / "test.json"

        export_session_to_file(session, "json", output_path)

        assert output_path.exists()
        assert output_path.parent.exists()

    def test_export_invalid_format(self, sample_session_data, temp_dir):
        """测试无效格式抛出异常"""
        session = ThinkingSession(**sample_session_data)
        output_path = temp_dir / "test.txt"

        with pytest.raises(ValueError, match="不支持的格式"):
            export_session_to_file(session, "invalid_format", output_path)


# =============================================================================
# export_session MCP 工具测试
# =============================================================================


@pytest.mark.asyncio
class TestExportSessionTool:
    """测试 export_session MCP 工具"""

    async def test_export_session_default_format(self, sample_session_data, temp_dir, clean_env):
        """测试默认格式导出"""
        # Mock 存储管理器
        session = ThinkingSession(**sample_session_data)

        mock_manager = MagicMock()
        mock_manager.get_session.return_value = session

        with (
            patch("deep_thinking.tools.export.get_storage_manager", return_value=mock_manager),
            patch("deep_thinking.tools.export.Path.home", return_value=temp_dir),
        ):
            result = await export.export_session("test-session-123")

        # 验证返回结果
        assert "会话已导出" in result
        assert "测试会话" in result
        assert "markdown" in result


    async def test_export_session_json_format(self, sample_session_data, temp_dir, clean_env):
        """测试 JSON 格式导出"""
        session = ThinkingSession(**sample_session_data)

        mock_manager = MagicMock()
        mock_manager.get_session.return_value = session

        with (
            patch("deep_thinking.tools.export.get_storage_manager", return_value=mock_manager),
            patch("deep_thinking.tools.export.Path.home", return_value=temp_dir),
        ):
            result = await export.export_session("test-session-123", "json")

        assert "会话已导出" in result
        assert "json" in result


    async def test_export_session_custom_path(self, sample_session_data, temp_dir, clean_env):
        """测试自定义输出路径"""
        session = ThinkingSession(**sample_session_data)
        output_path = temp_dir / "custom_output.md"

        mock_manager = MagicMock()
        mock_manager.get_session.return_value = session

        with patch("deep_thinking.tools.export.get_storage_manager", return_value=mock_manager):
            result = await export.export_session("test-session-123", "markdown", str(output_path))

        assert "会话已导出" in result
        assert str(output_path) in result
        assert output_path.exists()


    async def test_export_session_not_found(self, clean_env):
        """测试会话不存在时的错误处理"""
        mock_manager = MagicMock()
        mock_manager.get_session.return_value = None

        with (
            patch("deep_thinking.tools.export.get_storage_manager", return_value=mock_manager),
            pytest.raises(ValueError, match="会话不存在"),
        ):
            await export.export_session("nonexistent-session")


    async def test_export_session_invalid_format(self, sample_session_data, temp_dir, clean_env):
        """测试无效格式时的错误处理"""
        session = ThinkingSession(**sample_session_data)

        mock_manager = MagicMock()
        mock_manager.get_session.return_value = session

        with (
            patch("deep_thinking.tools.export.get_storage_manager", return_value=mock_manager),
            pytest.raises(ValueError, match="不支持的格式"),
        ):
            await export.export_session("test-session-123", "invalid_format")


# =============================================================================
# 辅助函数测试
# =============================================================================


class TestHelperFunctions:
    """测试辅助函数"""

    def test_sanitize_filename(self):
        """测试文件名清理"""
        from deep_thinking.tools.export import _sanitize_filename

        # 测试非法字符替换
        assert _sanitize_filename('test<>:"/\\|?*file') == "test_________file"
        assert _sanitize_filename("  test  ") == "test"
        assert _sanitize_filename("") == "session"

        # 测试长度限制
        long_name = "a" * 100
        result = _sanitize_filename(long_name)
        assert len(result) <= 50

    def test_normalize_format(self):
        """测试格式标准化"""
        from deep_thinking.tools.export import _normalize_format

        assert _normalize_format("json") == "json"
        assert _normalize_format("JSON") == "json"
        assert _normalize_format("md") == "markdown"
        assert _normalize_format("markdown") == "markdown"
        assert _normalize_format("txt") == "text"
        assert _normalize_format("text") == "text"

        with pytest.raises(ValueError, match="不支持的格式"):
            _normalize_format("invalid")
