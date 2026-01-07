"""
测试 server.py 模块的功能
"""

import os
from unittest.mock import patch


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
        with patch.dict(os.environ, {"HOME": test_home, "DEEP_THINKING_DATA_DIR": "$HOME/.deep-thinking-data"}):
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
            os.environ,
            {"HOME": test_home, "DEEP_THINKING_DATA_DIR": "~/.deep-$HOME-data"}
        ):
            result = get_default_data_dir()
            # ~ 应该被扩展
            assert "~" not in str(result)
            # $HOME 应该被扩展
            assert "$HOME" not in str(result)
            assert "test_home" in str(result)
