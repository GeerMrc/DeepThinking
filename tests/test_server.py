"""
测试 server.py 模块的功能
"""

import logging
import os
from unittest.mock import patch


class TestGetServerInstructions:
    """测试 get_server_instructions 函数"""

    def test_returns_default_when_env_not_set(self, caplog):
        """测试环境变量未设置时返回默认值"""
        from deep_thinking.server import get_server_instructions

        # 清除环境变量
        env = os.environ.copy()
        env.pop("DEEP_THINKING_DESCRIPTION", None)

        with (
            patch.dict(os.environ, env, clear=True),
            caplog.at_level(logging.DEBUG),
        ):
            result = get_server_instructions()

        expected = "深度思考MCP服务器 - 高级思维编排引擎，提供顺序思考,适合处理多步骤、跨工具的复杂任务,会话管理和状态持久化功能"
        assert result == expected
        assert "使用默认instructions" in caplog.text

    def test_returns_custom_when_env_set(self, caplog):
        """测试环境变量设置时返回自定义值"""
        from deep_thinking.server import get_server_instructions

        custom_desc = "我的自定义MCP服务器"
        with (
            patch.dict(os.environ, {"DEEP_THINKING_DESCRIPTION": custom_desc}),
            caplog.at_level(logging.INFO),
        ):
            result = get_server_instructions()

        assert result == custom_desc
        assert f"使用自定义描述: {custom_desc}" in caplog.text

    def test_returns_default_for_empty_string(self, caplog):
        """测试空字符串时返回默认值"""
        from deep_thinking.server import get_server_instructions

        with (
            patch.dict(os.environ, {"DEEP_THINKING_DESCRIPTION": ""}),
            caplog.at_level(logging.DEBUG),
        ):
            result = get_server_instructions()

        expected = "深度思考MCP服务器 - 高级思维编排引擎，提供顺序思考,适合处理多步骤、跨工具的复杂任务,会话管理和状态持久化功能"
        assert result == expected
        assert "使用默认instructions" in caplog.text

    def test_returns_default_for_whitespace_only(self, caplog):
        """测试仅包含空格时返回默认值"""
        from deep_thinking.server import get_server_instructions

        with (
            patch.dict(os.environ, {"DEEP_THINKING_DESCRIPTION": "   "}),
            caplog.at_level(logging.DEBUG),
        ):
            result = get_server_instructions()

        expected = "深度思考MCP服务器 - 高级思维编排引擎，提供顺序思考,适合处理多步骤、跨工具的复杂任务,会话管理和状态持久化功能"
        assert result == expected

    def test_trims_whitespace(self, caplog):
        """测试去除首尾空格"""
        from deep_thinking.server import get_server_instructions

        custom_desc = "  自定义描述  "
        with (
            patch.dict(os.environ, {"DEEP_THINKING_DESCRIPTION": custom_desc}),
            caplog.at_level(logging.INFO),
        ):
            result = get_server_instructions()

        assert result == "自定义描述"
        assert "使用自定义描述: 自定义描述" in caplog.text

    def test_handles_special_characters(self, caplog):
        """测试特殊字符处理"""
        from deep_thinking.server import get_server_instructions

        custom_desc = "服务器@#$%^&*()描述"
        with (
            patch.dict(os.environ, {"DEEP_THINKING_DESCRIPTION": custom_desc}),
            caplog.at_level(logging.INFO),
        ):
            result = get_server_instructions()

        assert result == custom_desc

    def test_handles_multiline_text(self, caplog):
        """测试多行文本"""
        from deep_thinking.server import get_server_instructions

        custom_desc = """这是一个多行的
服务器描述，
包含多个段落。"""
        with (
            patch.dict(os.environ, {"DEEP_THINKING_DESCRIPTION": custom_desc}),
            caplog.at_level(logging.INFO),
        ):
            result = get_server_instructions()

        assert result == custom_desc
        assert "多行" in result

    def test_handles_long_text(self, caplog):
        """测试长文本"""
        from deep_thinking.server import get_server_instructions

        custom_desc = "A" * 1000
        with (
            patch.dict(os.environ, {"DEEP_THINKING_DESCRIPTION": custom_desc}),
            caplog.at_level(logging.INFO),
        ):
            result = get_server_instructions()

        assert len(result) == 1000

    def test_fastmcp_uses_custom_instructions(self, monkeypatch):
        """测试FastMCP使用自定义instructions"""
        custom_desc = "测试自定义instructions"
        monkeypatch.setenv("DEEP_THINKING_DESCRIPTION", custom_desc)

        # 重新导入模块以触发初始化
        import importlib

        import deep_thinking.server

        importlib.reload(deep_thinking.server)

        assert deep_thinking.server.app.instructions == custom_desc


class TestGetDefaultDataDir:
    """测试 get_default_data_dir 函数"""

    def test_expands_tilde_in_env_var(self):
        """测试环境变量中的 ~ 符号被正确扩展"""
        from deep_thinking.server import get_default_data_dir

        with patch.dict(os.environ, {"DEEP_THINKING_DATA_DIR": "~/.deep-thinking-data"}):
            result = get_default_data_dir()
            # 应该扩展为实际的 home 目录
            assert str(result).startswith(os.path.expanduser("~"))
            assert str(result).endswith(".deep-thinking-data")
            # 不应该包含 ~ 符号
            assert "~" not in str(result)

    def test_expands_home_env_var(self):
        """测试环境变量中的 $HOME 被正确扩展"""
        from deep_thinking.server import get_default_data_dir

        # 设置一个临时的 HOME 环境变量用于测试
        test_home = "/tmp/test_home"
        with patch.dict(
            os.environ, {"HOME": test_home, "DEEP_THINKING_DATA_DIR": "$HOME/.deep-thinking-data"}
        ):
            result = get_default_data_dir()
            # 应该扩展 $HOME
            assert str(result) == "/tmp/test_home/.deep-thinking-data"
            # 不应该包含 $HOME
            assert "$HOME" not in str(result)

    def test_relative_path_unchanged(self):
        """测试相对路径保持不变"""
        from deep_thinking.server import get_default_data_dir

        with patch.dict(os.environ, {"DEEP_THINKING_DATA_DIR": "./.deep-thinking-data"}):
            result = get_default_data_dir()
            # Path 会规范化路径，去掉开头的 ./
            assert result.name == ".deep-thinking-data"
            assert "./" not in str(result)

    def test_absolute_path_unchanged(self):
        """测试绝对路径保持不变"""
        from deep_thinking.server import get_default_data_dir

        with patch.dict(os.environ, {"DEEP_THINKING_DATA_DIR": "/tmp/custom-data"}):
            result = get_default_data_dir()
            # 绝对路径应该保持不变
            assert str(result) == "/tmp/custom-data"

    def test_no_env_var_returns_local_dir(self):
        """测试没有环境变量时返回本地目录"""
        from deep_thinking.server import get_default_data_dir

        # 清除环境变量
        env = os.environ.copy()
        env.pop("DEEP_THINKING_DATA_DIR", None)

        with patch.dict(os.environ, env, clear=True):
            result = get_default_data_dir()
            # 应该返回当前工作目录下的 .deepthinking
            assert result.name == ".deepthinking"

    def test_combined_tilde_and_env_var(self):
        """测试同时包含 ~ 和环境变量的路径"""
        from deep_thinking.server import get_default_data_dir

        test_home = "/tmp/test_home"
        with patch.dict(
            os.environ, {"HOME": test_home, "DEEP_THINKING_DATA_DIR": "~/.deep-$HOME-data"}
        ):
            result = get_default_data_dir()
            # ~ 应该被扩展
            assert "~" not in str(result)
            # $HOME 应该被扩展
            assert "$HOME" not in str(result)
            assert "test_home" in str(result)
