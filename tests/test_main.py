"""
CLI入口点测试

测试__main__.py模块的功能。
"""

from unittest.mock import AsyncMock, patch

import pytest

from deep_thinking.__main__ import create_server, main_async, parse_args


class TestParseArgs:
    """命令行参数解析测试"""

    def test_parse_args_defaults(self):
        """测试默认参数"""
        with patch("sys.argv", ["deep-thinking"]):
            args = parse_args()

            assert args.transport == "stdio"
            assert args.host == "localhost"
            assert args.port == 8000
            assert args.auth_token is None
            assert args.api_key is None
            assert args.log_level == "INFO"

    def test_parse_args_with_transport(self):
        """测试传输模式参数"""
        with patch("sys.argv", ["deep-thinking", "--transport", "sse"]):
            args = parse_args()
            assert args.transport == "sse"

    def test_parse_args_with_host(self):
        """测试主机参数"""
        with patch("sys.argv", ["deep-thinking", "--host", "0.0.0.0"]):
            args = parse_args()
            assert args.host == "0.0.0.0"

    def test_parse_args_with_port(self):
        """测试端口参数"""
        with patch("sys.argv", ["deep-thinking", "--port", "9000"]):
            args = parse_args()
            assert args.port == 9000

    def test_parse_args_with_auth_token(self):
        """测试认证token参数"""
        with patch("sys.argv", ["deep-thinking", "--auth-token", "my-token"]):
            args = parse_args()
            assert args.auth_token == "my-token"

    def test_parse_args_with_api_key(self):
        """测试API key参数"""
        with patch("sys.argv", ["deep-thinking", "--api-key", "my-key"]):
            args = parse_args()
            assert args.api_key == "my-key"

    def test_parse_args_with_log_level(self):
        """测试日志级别参数"""
        with patch("sys.argv", ["deep-thinking", "--log-level", "DEBUG"]):
            args = parse_args()
            assert args.log_level == "DEBUG"

    def test_parse_args_invalid_transport(self):
        """测试无效的传输模式"""
        with (
            patch("sys.argv", ["deep-thinking", "--transport", "invalid"]),
            pytest.raises(SystemExit),
        ):
            parse_args()

    def test_parse_args_invalid_log_level(self):
        """测试无效的日志级别"""
        with (
            patch("sys.argv", ["deep-thinking", "--log-level", "INVALID"]),
            pytest.raises(SystemExit),
        ):
            parse_args()


class TestCreateServer:
    """create_server函数测试"""

    def test_create_server_returns_fastmcp(self):
        """测试create_server返回FastMCP实例"""
        from mcp.server import FastMCP

        server = create_server()

        assert isinstance(server, FastMCP)
        assert server.name == "DeepThinking"

    def test_create_server_has_lifespan(self):
        """测试create_server的服务器配置"""
        server = create_server()

        # 验证服务器名称
        assert server.name == "DeepThinking"

        # 验证服务器是FastMCP类型
        from mcp.server import FastMCP

        assert isinstance(server, FastMCP)


class TestMainAsync:
    """main_async函数测试"""

    @pytest.mark.asyncio
    async def test_main_async_stdio_transport(self):
        """测试STDIO传输模式"""
        with (
            patch("deep_thinking.__main__.run_stdio", new_callable=AsyncMock) as mock_run_stdio,
            patch("sys.argv", ["deep-thinking", "--transport", "stdio"]),
        ):
            return_code = await main_async()

            # 验证返回成功
            assert return_code == 0
            # 验证run_stdio被调用
            mock_run_stdio.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_async_sse_transport(self):
        """测试SSE传输模式"""
        with (
            patch("deep_thinking.__main__.run_sse", new_callable=AsyncMock) as mock_run_sse,
            patch("sys.argv", ["deep-thinking", "--transport", "sse"]),
        ):
            return_code = await main_async()

            # 验证返回成功
            assert return_code == 0
            # 验证run_sse被调用
            mock_run_sse.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_async_keyboard_interrupt(self):
        """测试键盘中断"""
        with patch("deep_thinking.__main__.run_stdio", new_callable=AsyncMock) as mock_run_stdio:
            # 模拟键盘中断
            mock_run_stdio.side_effect = KeyboardInterrupt()

            with patch("sys.argv", ["deep-thinking"]):
                return_code = await main_async()

                # 验证返回成功（优雅退出）
                assert return_code == 0

    @pytest.mark.asyncio
    async def test_main_async_exception_handling(self):
        """测试异常处理"""
        with patch("deep_thinking.__main__.run_stdio", new_callable=AsyncMock) as mock_run_stdio:
            # 模拟运行时错误
            mock_run_stdio.side_effect = RuntimeError("Test error")

            with patch("sys.argv", ["deep-thinking"]):
                return_code = await main_async()

                # 验证返回错误码
                assert return_code == 1

    @pytest.mark.asyncio
    async def test_main_async_sse_with_auth(self):
        """测试SSE模式带认证"""
        with (
            patch("deep_thinking.__main__.run_sse", new_callable=AsyncMock) as mock_run_sse,
            patch("sys.argv", ["deep-thinking", "--transport", "sse", "--auth-token", "token"]),
        ):
            return_code = await main_async()

            # 验证返回成功
            assert return_code == 0
            # 验证run_sse被调用，包含认证参数
            mock_run_sse.assert_called_once()

            # 获取调用参数
            call_args = mock_run_sse.call_args
            assert call_args[1]["auth_token"] == "token"

    @pytest.mark.asyncio
    async def test_main_async_sse_with_host_port(self):
        """测试SSE模式带主机端口"""
        with (
            patch("deep_thinking.__main__.run_sse", new_callable=AsyncMock) as mock_run_sse,
            patch(
                "sys.argv",
                ["deep-thinking", "--transport", "sse", "--host", "0.0.0.0", "--port", "9000"],
            ),
        ):
            return_code = await main_async()

            # 验证返回成功
            assert return_code == 0

            # 获取调用参数
            call_args = mock_run_sse.call_args
            assert call_args[1]["host"] == "0.0.0.0"
            assert call_args[1]["port"] == 9000


class TestServerLifespan:
    """server_lifespan函数测试"""

    @pytest.mark.asyncio
    async def test_server_lifespan_context_manager(self):
        """测试server_lifespan可以作为上下文管理器"""
        from mcp.server import FastMCP

        from deep_thinking.__main__ import server_lifespan

        server = FastMCP(name="test")

        # 验证可以作为异步上下文管理器
        async with server_lifespan(server):
            # 上下文中应该可以执行代码
            pass


class TestEnvironmentVariables:
    """环境变量测试"""

    def test_transport_from_env(self):
        """测试从环境变量读取传输模式"""
        with (
            patch.dict("os.environ", {"DEEP_THINKING_TRANSPORT": "sse"}),
            patch("sys.argv", ["deep-thinking"]),
        ):
            args = parse_args()
            assert args.transport == "sse"

    def test_host_from_env(self):
        """测试从环境变量读取主机"""
        with (
            patch.dict("os.environ", {"DEEP_THINKING_HOST": "0.0.0.0"}),
            patch("sys.argv", ["deep-thinking"]),
        ):
            args = parse_args()
            assert args.host == "0.0.0.0"

    def test_port_from_env(self):
        """测试从环境变量读取端口"""
        with (
            patch.dict("os.environ", {"DEEP_THINKING_PORT": "9000"}),
            patch("sys.argv", ["deep-thinking"]),
        ):
            args = parse_args()
            assert args.port == 9000

    def test_auth_token_from_env(self):
        """测试从环境变量读取认证token"""
        with (
            patch.dict("os.environ", {"DEEP_THINKING_AUTH_TOKEN": "env-token"}),
            patch("sys.argv", ["deep-thinking"]),
        ):
            args = parse_args()
            assert args.auth_token == "env-token"

    def test_api_key_from_env(self):
        """测试从环境变量读取API key"""
        with (
            patch.dict("os.environ", {"DEEP_THINKING_API_KEY": "env-key"}),
            patch("sys.argv", ["deep-thinking"]),
        ):
            args = parse_args()
            assert args.api_key == "env-key"

    def test_log_level_from_env(self):
        """测试从环境变量读取日志级别"""
        with (
            patch.dict("os.environ", {"DEEP_THINKING_LOG_LEVEL": "DEBUG"}),
            patch("sys.argv", ["deep-thinking"]),
        ):
            args = parse_args()
            assert args.log_level == "DEBUG"

    def test_cli_args_override_env(self):
        """测试CLI参数覆盖环境变量"""
        with (
            patch.dict(
                "os.environ", {"DEEP_THINKING_TRANSPORT": "sse", "DEEP_THINKING_PORT": "9000"}
            ),
            patch("sys.argv", ["deep-thinking", "--port", "8080"]),
        ):
            args = parse_args()
            # 环境变量设置传输模式
            assert args.transport == "sse"
            # CLI参数覆盖端口
            assert args.port == 8080
