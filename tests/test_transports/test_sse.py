"""
SSE传输层测试

测试SSE传输模式的功能。
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from deep_thinking.server import app
from deep_thinking.transports.sse import SSETransport, run_sse


class TestSSETransport:
    """SSE传输类测试"""

    def test_sse_transport_init_no_auth(self):
        """测试SSETransport初始化（无认证）"""
        transport = SSETransport(app)

        assert transport.app is app
        assert transport.auth_token is None
        assert transport.api_key is None
        assert transport.web_app is None
        assert transport.runner is None

    def test_sse_transport_init_with_auth_token(self):
        """测试SSETransport初始化（Bearer Token）"""
        transport = SSETransport(app, auth_token="test-token")

        assert transport.auth_token == "test-token"
        assert transport.api_key is None

    def test_sse_transport_init_with_api_key(self):
        """测试SSETransport初始化（API Key）"""
        transport = SSETransport(app, api_key="test-api-key")

        assert transport.auth_token is None
        assert transport.api_key == "test-api-key"

    def test_sse_transport_init_with_both_auth(self):
        """测试SSETransport初始化（双重认证）"""
        transport = SSETransport(app, auth_token="token", api_key="key")

        assert transport.auth_token == "token"
        assert transport.api_key == "key"

    @pytest.mark.asyncio
    async def test_sse_transport_start(self):
        """测试SSETransport启动"""
        transport = SSETransport(app)

        # Mock aiohttp组件
        with patch("deep_thinking.transports.sse.web.Application") as mock_app_class, \
             patch("deep_thinking.transports.sse.web.AppRunner") as mock_runner_class, \
             patch("deep_thinking.transports.sse.web.TCPSite") as mock_site_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app

            mock_runner = MagicMock()
            mock_runner.setup = AsyncMock()
            mock_runner_class.return_value = mock_runner

            mock_site = MagicMock()
            mock_site.start = AsyncMock()
            mock_site_class.return_value = mock_site

            # 调用start
            await transport.start("localhost", 8000)

            # 验证
            mock_runner.setup.assert_called_once()
            mock_site.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_sse_transport_stop(self):
        """测试SSETransport停止"""
        transport = SSETransport(app)
        transport.runner = MagicMock()
        transport.runner.cleanup = AsyncMock()

        # 调用stop
        await transport.stop()

        # 验证cleanup被调用
        transport.runner.cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_sse_transport_stop_without_runner(self):
        """测试SSETransport停止（无runner）"""
        transport = SSETransport(app)
        # runner为None

        # 调用stop不应抛出异常
        await transport.stop()

    @pytest.mark.asyncio
    async def test_sse_health_handler(self):
        """测试健康检查端点"""
        from aiohttp import web

        transport = SSETransport(app)
        response = await transport._health_handler(None)

        assert isinstance(response, web.Response)
        assert response.status == 200
        assert response.text == "OK"


class TestSSETransportAuth:
    """SSE传输认证测试"""

    def test_setup_auth_without_credentials(self):
        """测试设置认证（无凭据）"""
        from aiohttp import web

        transport = SSETransport(app)
        mock_app = MagicMock(spec=web.Application)
        mock_app.middlewares = []

        transport._setup_auth(mock_app)

        # 不应添加中间件
        assert len(mock_app.middlewares) == 0

    def test_setup_auth_with_token(self):
        """测试设置认证（Bearer Token）"""
        from aiohttp import web

        transport = SSETransport(app, auth_token="test-token")
        mock_app = MagicMock(spec=web.Application)
        mock_app.middlewares = []

        transport._setup_auth(mock_app)

        # 应添加中间件
        assert len(mock_app.middlewares) == 1

    def test_setup_auth_with_api_key(self):
        """测试设置认证（API Key）"""
        from aiohttp import web

        transport = SSETransport(app, api_key="test-key")
        mock_app = MagicMock(spec=web.Application)
        mock_app.middlewares = []

        transport._setup_auth(mock_app)

        # 应添加中间件
        assert len(mock_app.middlewares) == 1


class TestRunSSE:
    """run_sse函数测试"""

    @pytest.mark.asyncio
    async def test_run_sse_creates_transport(self):
        """测试run_sse创建SSETransport"""
        with patch("deep_thinking.transports.sse.SSETransport") as mock_transport_class:
            mock_transport = MagicMock()
            mock_transport.start = AsyncMock()
            mock_transport.stop = AsyncMock()  # 添加AsyncMock的stop
            mock_transport_class.return_value = mock_transport

            # Mock asyncio.Event
            with patch("deep_thinking.transports.sse.asyncio.Event") as mock_event_class:
                mock_event = MagicMock()
                mock_event.wait = AsyncMock(side_effect=asyncio.CancelledError)
                mock_event_class.return_value = mock_event

                # 调用run_sse（会被CancelledError中断）
                with pytest.raises(asyncio.CancelledError):
                    await run_sse(app, host="localhost", port=8000)

                # 验证transport被创建
                mock_transport_class.assert_called_once_with(app, auth_token=None, api_key=None)

    @pytest.mark.asyncio
    async def test_run_sse_with_auth(self):
        """测试run_sse带认证参数"""
        with patch("deep_thinking.transports.sse.SSETransport") as mock_transport_class:
            mock_transport = MagicMock()
            mock_transport.start = AsyncMock()
            mock_transport.stop = AsyncMock()  # 添加AsyncMock的stop
            mock_transport_class.return_value = mock_transport

            with patch("deep_thinking.transports.sse.asyncio.Event") as mock_event_class:
                mock_event = MagicMock()
                mock_event.wait = AsyncMock(side_effect=asyncio.CancelledError)
                mock_event_class.return_value = mock_event

                # 调用run_sse带认证
                with pytest.raises(asyncio.CancelledError):
                    await run_sse(
                        app,
                        host="localhost",
                        port=8000,
                        auth_token="token",
                        api_key="key",
                    )

                # 验证transport被创建时包含认证参数
                mock_transport_class.assert_called_once_with(app, auth_token="token", api_key="key")

    @pytest.mark.asyncio
    async def test_run_sse_cleanup_on_error(self):
        """测试run_sse在错误时清理资源"""
        with patch("deep_thinking.transports.sse.SSETransport") as mock_transport_class:
            mock_transport = MagicMock()
            mock_transport.start = AsyncMock()
            mock_transport.stop = AsyncMock()
            mock_transport_class.return_value = mock_transport

            with patch("deep_thinking.transports.sse.asyncio.Event") as mock_event_class:
                mock_event = MagicMock()
                mock_event.wait = AsyncMock(side_effect=RuntimeError("Test error"))
                mock_event_class.return_value = mock_event

                # 调用run_sse（抛出错误）
                with pytest.raises(RuntimeError, match="Test error"):
                    await run_sse(app)

                # 验证stop被调用（清理）
                mock_transport.stop.assert_called_once()


class TestSSEAuthMiddleware:
    """SSE认证中间件功能测试"""

    @pytest.mark.asyncio
    async def test_bearer_token_auth_success(self):
        """测试Bearer Token认证成功"""
        from aiohttp import web
        from aiohttp.test_utils import make_mocked_request

        transport = SSETransport(app, auth_token="valid-token")

        # 创建模拟请求
        request = make_mocked_request(
            "POST",
            "/sse",
            headers={"Authorization": "Bearer valid-token"},
        )

        # 创建模拟handler
        async def mock_handler(req):
            return web.Response(status=200, text="Success")

        # 获取认证中间件
        web_app = web.Application()
        transport._setup_auth(web_app)
        auth_middleware = web_app.middlewares[0]

        # 调用中间件
        response = await auth_middleware(request, mock_handler)

        # 验证成功
        assert response.status == 200
        assert response.text == "Success"

    @pytest.mark.asyncio
    async def test_bearer_token_auth_missing(self):
        """测试Bearer Token缺失"""
        from aiohttp import web
        from aiohttp.test_utils import make_mocked_request

        transport = SSETransport(app, auth_token="valid-token")

        # 创建没有Authorization头的请求
        request = make_mocked_request("POST", "/sse", headers={})

        async def mock_handler(req):
            return web.Response(status=200, text="Success")

        # 获取认证中间件
        web_app = web.Application()
        transport._setup_auth(web_app)
        auth_middleware = web_app.middlewares[0]

        # 调用中间件
        response = await auth_middleware(request, mock_handler)

        # 验证401错误
        assert response.status == 401
        assert "Missing Bearer token" in response.text

    @pytest.mark.asyncio
    async def test_bearer_token_auth_invalid(self):
        """测试Bearer Token无效"""
        from aiohttp import web
        from aiohttp.test_utils import make_mocked_request

        transport = SSETransport(app, auth_token="valid-token")

        # 创建使用错误token的请求
        request = make_mocked_request(
            "POST",
            "/sse",
            headers={"Authorization": "Bearer wrong-token"},
        )

        async def mock_handler(req):
            return web.Response(status=200, text="Success")

        # 获取认证中间件
        web_app = web.Application()
        transport._setup_auth(web_app)
        auth_middleware = web_app.middlewares[0]

        # 调用中间件
        response = await auth_middleware(request, mock_handler)

        # 验证403错误
        assert response.status == 403
        assert "Invalid Bearer token" in response.text

    @pytest.mark.asyncio
    async def test_bearer_token_auth_wrong_prefix(self):
        """测试Bearer Token前缀错误"""
        from aiohttp import web
        from aiohttp.test_utils import make_mocked_request

        transport = SSETransport(app, auth_token="valid-token")

        # 创建使用错误前缀的请求
        request = make_mocked_request(
            "POST",
            "/sse",
            headers={"Authorization": "Basic valid-token"},
        )

        async def mock_handler(req):
            return web.Response(status=200, text="Success")

        # 获取认证中间件
        web_app = web.Application()
        transport._setup_auth(web_app)
        auth_middleware = web_app.middlewares[0]

        # 调用中间件
        response = await auth_middleware(request, mock_handler)

        # 验证401错误
        assert response.status == 401
        assert "Missing Bearer token" in response.text

    @pytest.mark.asyncio
    async def test_api_key_auth_success(self):
        """测试API Key认证成功"""
        from aiohttp import web
        from aiohttp.test_utils import make_mocked_request

        transport = SSETransport(app, api_key="valid-api-key")

        # 创建模拟请求
        request = make_mocked_request(
            "POST",
            "/sse",
            headers={"X-API-Key": "valid-api-key"},
        )

        async def mock_handler(req):
            return web.Response(status=200, text="Success")

        # 获取认证中间件
        web_app = web.Application()
        transport._setup_auth(web_app)
        auth_middleware = web_app.middlewares[0]

        # 调用中间件
        response = await auth_middleware(request, mock_handler)

        # 验证成功
        assert response.status == 200
        assert response.text == "Success"

    @pytest.mark.asyncio
    async def test_api_key_auth_missing(self):
        """测试API Key缺失"""
        from aiohttp import web
        from aiohttp.test_utils import make_mocked_request

        transport = SSETransport(app, api_key="valid-api-key")

        # 创建没有X-API-Key头的请求
        request = make_mocked_request("POST", "/sse", headers={})

        async def mock_handler(req):
            return web.Response(status=200, text="Success")

        # 获取认证中间件
        web_app = web.Application()
        transport._setup_auth(web_app)
        auth_middleware = web_app.middlewares[0]

        # 调用中间件
        response = await auth_middleware(request, mock_handler)

        # 验证403错误
        assert response.status == 403
        assert "Invalid API Key" in response.text

    @pytest.mark.asyncio
    async def test_api_key_auth_invalid(self):
        """测试API Key无效"""
        from aiohttp import web
        from aiohttp.test_utils import make_mocked_request

        transport = SSETransport(app, api_key="valid-api-key")

        # 创建使用错误key的请求
        request = make_mocked_request(
            "POST",
            "/sse",
            headers={"X-API-Key": "wrong-api-key"},
        )

        async def mock_handler(req):
            return web.Response(status=200, text="Success")

        # 获取认证中间件
        web_app = web.Application()
        transport._setup_auth(web_app)
        auth_middleware = web_app.middlewares[0]

        # 调用中间件
        response = await auth_middleware(request, mock_handler)

        # 验证403错误
        assert response.status == 403
        assert "Invalid API Key" in response.text

    @pytest.mark.asyncio
    async def test_dual_auth_both_success(self):
        """测试双重认证都成功"""
        from aiohttp import web
        from aiohttp.test_utils import make_mocked_request

        transport = SSETransport(app, auth_token="valid-token", api_key="valid-api-key")

        # 创建包含两种认证的请求
        request = make_mocked_request(
            "POST",
            "/sse",
            headers={
                "Authorization": "Bearer valid-token",
                "X-API-Key": "valid-api-key",
            },
        )

        async def mock_handler(req):
            return web.Response(status=200, text="Success")

        # 获取认证中间件
        web_app = web.Application()
        transport._setup_auth(web_app)
        auth_middleware = web_app.middlewares[0]

        # 调用中间件
        response = await auth_middleware(request, mock_handler)

        # 验证成功
        assert response.status == 200
        assert response.text == "Success"

    @pytest.mark.asyncio
    async def test_dual_auth_token_fail(self):
        """测试双重认证时Token失败"""
        from aiohttp import web
        from aiohttp.test_utils import make_mocked_request

        transport = SSETransport(app, auth_token="valid-token", api_key="valid-api-key")

        # Token错误但API Key正确
        request = make_mocked_request(
            "POST",
            "/sse",
            headers={
                "Authorization": "Bearer wrong-token",
                "X-API-Key": "valid-api-key",
            },
        )

        async def mock_handler(req):
            return web.Response(status=200, text="Success")

        # 获取认证中间件
        web_app = web.Application()
        transport._setup_auth(web_app)
        auth_middleware = web_app.middlewares[0]

        # 调用中间件
        response = await auth_middleware(request, mock_handler)

        # 验证403错误（Token检查失败）
        assert response.status == 403

    @pytest.mark.asyncio
    async def test_dual_auth_api_key_fail(self):
        """测试双重认证时API Key失败"""
        from aiohttp import web
        from aiohttp.test_utils import make_mocked_request

        transport = SSETransport(app, auth_token="valid-token", api_key="valid-api-key")

        # Token正确但API Key错误
        request = make_mocked_request(
            "POST",
            "/sse",
            headers={
                "Authorization": "Bearer valid-token",
                "X-API-Key": "wrong-api-key",
            },
        )

        async def mock_handler(req):
            return web.Response(status=200, text="Success")

        # 获取认证中间件
        web_app = web.Application()
        transport._setup_auth(web_app)
        auth_middleware = web_app.middlewares[0]

        # 调用中间件
        response = await auth_middleware(request, mock_handler)

        # 验证403错误（API Key检查失败）
        assert response.status == 403
        assert "Invalid API Key" in response.text

    @pytest.mark.asyncio
    async def test_dual_auth_both_fail(self):
        """测试双重认证都失败"""
        from aiohttp import web
        from aiohttp.test_utils import make_mocked_request

        transport = SSETransport(app, auth_token="valid-token", api_key="valid-api-key")

        # 两种认证都错误
        request = make_mocked_request(
            "POST",
            "/sse",
            headers={
                "Authorization": "Bearer wrong-token",
                "X-API-Key": "wrong-api-key",
            },
        )

        async def mock_handler(req):
            return web.Response(status=200, text="Success")

        # 获取认证中间件
        web_app = web.Application()
        transport._setup_auth(web_app)
        auth_middleware = web_app.middlewares[0]

        # 调用中间件
        response = await auth_middleware(request, mock_handler)

        # 验证403错误（Token先检查失败）
        assert response.status == 403


class TestSSEModuleLogging:
    """SSE模块日志测试"""

    def test_sse_module_logging(self):
        """测试sse模块有正确的日志配置"""
        from deep_thinking.transports import sse

        # 验证logger存在
        assert hasattr(sse, "logger")

        # 验证run_sse函数存在
        assert callable(sse.run_sse)

        # 验证SSETransport类存在
        assert sse.SSETransport is not None
