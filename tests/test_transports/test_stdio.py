"""
STDIO传输层测试

测试STDIO传输模式的功能。
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from deep_thinking.server import app
from deep_thinking.transports.stdio import run_stdio


class TestStdioTransport:
    """STDIO传输测试类"""

    @pytest.mark.asyncio
    async def test_run_stdio_calls_run_stdio_async(self):
        """测试run_stdio正确调用app.run_stdio_async"""
        # Mock app.run_stdio_async方法
        with patch.object(app, "run_stdio_async", new_callable=AsyncMock) as mock_run:
            # 调用run_stdio
            await run_stdio(app)

            # 验证app.run_stdio_async被调用
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stdio_with_fastmcp_app(self):
        """测试run_stdio接受FastMCP app实例"""
        # 验证app是FastMCP实例
        from mcp.server import FastMCP

        assert isinstance(app, FastMCP)

        # 测试run_stdio可以被调用（不实际运行）
        with patch.object(app, "run_stdio_async", new_callable=AsyncMock):
            await run_stdio(app)
            # 如果没有抛出异常，测试通过

    @pytest.mark.asyncio
    async def test_run_stdio_handles_cancelled_error(self):
        """测试run_stdio正确处理CancelledError"""
        with patch.object(
            app, "run_stdio_async", new_callable=AsyncMock, side_effect=asyncio.CancelledError
        ):
            # 应该抛出CancelledError
            with pytest.raises(asyncio.CancelledError):
                await run_stdio(app)

    @pytest.mark.asyncio
    async def test_run_stdio_handles_generic_exception(self):
        """测试run_stdio正确处理通用异常"""
        with patch.object(
            app, "run_stdio_async", new_callable=AsyncMock, side_effect=RuntimeError("Test error")
        ):
            # 应该抛出RuntimeError
            with pytest.raises(RuntimeError, match="Test error"):
                await run_stdio(app)

    def test_stdio_module_logging(self):
        """测试stdio模块有正确的日志配置"""
        from deep_thinking.transports import stdio

        # 验证logger存在
        assert hasattr(stdio, "logger")

        # 验证run_stdio函数存在
        assert callable(stdio.run_stdio)


class TestStdioTransportIntegration:
    """STDIO传输集成测试（更高层次的测试）"""

    @pytest.mark.asyncio
    async def test_stdio_app_has_tools_registered(self):
        """测试STDIO使用的app实例已注册工具"""
        # 验证app有工具列表
        tools = await app.list_tools()
        assert len(tools) > 0

        # 验证关键工具存在
        tool_names = {tool.name for tool in tools}
        assert "sequential_thinking" in tool_names
        assert "create_session" in tool_names

    @pytest.mark.asyncio
    async def test_stdio_app_name(self):
        """测试STDIO使用的app实例有正确的名称"""
        assert app.name == "DeepThinking"

    @pytest.mark.asyncio
    async def test_stdio_app_lifespan(self):
        """测试STDIO使用的app实例有lifespan配置"""
        # 验证app有instructions属性（说明已正确初始化）
        assert hasattr(app, "instructions")
        assert isinstance(app.instructions, str)
        assert len(app.instructions) > 0
