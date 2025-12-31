"""
SSE传输模块

使用HTTP Server-Sent Events进行远程通信，适用于远程服务器部署。

关键特性:
- HTTP POST + Server-Sent Events
- 支持Bearer Token认证
- 支持API Key认证
- 可通过网络从任何位置访问
"""

import asyncio
import json
import logging

from aiohttp import web
from mcp.server import FastMCP  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)


class SSETransport:
    """SSE传输处理器"""

    def __init__(self, app: FastMCP, auth_token: str | None = None, api_key: str | None = None):
        """
        初始化SSE传输

        Args:
            app: FastMCP服务器实例
            auth_token: Bearer Token用于认证
            api_key: API Key用于认证
        """
        self.app = app
        self.auth_token = auth_token
        self.api_key = api_key
        self.web_app: web.Application | None = None
        self.runner: web.AppRunner | None = None

    def _setup_auth(self, app: web.Application) -> None:
        """设置认证中间件"""
        if not (self.auth_token or self.api_key):
            return

        @web.middleware
        async def auth(request: web.Request, handler):  # type: ignore[no-untyped-def]
            """检查认证信息"""
            # 检查Bearer Token
            if self.auth_token:
                auth_header = request.headers.get("Authorization", "")
                if not auth_header.startswith("Bearer "):
                    return web.Response(status=401, text="Missing Bearer token")
                token = auth_header[7:]  # 去掉"Bearer "前缀
                if token != self.auth_token:
                    return web.Response(status=403, text="Invalid Bearer token")

            # 检查API Key
            if self.api_key:
                api_key_header = request.headers.get("X-API-Key", "")
                if api_key_header != self.api_key:
                    return web.Response(status=403, text="Invalid API Key")

            return await handler(request)

        app.middlewares.append(auth)

    async def _sse_handler(self, request: web.Request) -> web.Response:
        """
        SSE端点处理器

        处理MCP的JSON-RPC请求并返回SSE响应
        """
        logger.debug("收到SSE连接请求")

        # 设置SSE响应头
        response = web.StreamResponse(
            status=200,
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            },
        )
        await response.prepare(request)

        # 发送连接建立消息
        await response.write(b"event: connected\n")
        await response.write(b'data: {"status":"connected"}\n\n')

        try:
            # 读取请求体
            request_data = await request.json()
            logger.info(f"收到MCP请求: {request_data.get('method', 'unknown')}")

            # TODO: 处理JSON-RPC请求
            # 这里需要实现MCP协议的请求处理逻辑
            # 暂时返回简单的响应
            response_data = {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "result": {"status": "ok"},
            }

            # 发送响应
            await response.write(b"event: message\n")
            await response.write(f"data: {json.dumps(response_data)}\n\n".encode())

            # 保持连接
            while True:
                await asyncio.sleep(1)
                # 发送心跳
                await response.write(b": heartbeat\n\n")

        except asyncio.CancelledError:
            logger.debug("SSE连接被取消")
        except Exception as e:
            logger.error(f"SSE处理错误: {e}", exc_info=True)
        finally:
            logger.debug("SSE连接已关闭")

        # SSE连接不会正常返回，始终通过异常结束
        raise NotImplementedError("SSE handler should never return")  # pragma: no cover

    async def _health_handler(self, _request: web.Request) -> web.Response:
        """健康检查端点"""
        return web.Response(status=200, text="OK")

    async def start(self, host: str = "localhost", port: int = 8000) -> None:
        """
        启动SSE服务器

        Args:
            host: 监听地址
            port: 监听端口
        """
        # 创建aiohttp应用
        self.web_app = web.Application()

        # 添加认证中间件（如果配置了）
        self._setup_auth(self.web_app)

        # 添加路由
        self.web_app.router.add_post("/sse", self._sse_handler)
        self.web_app.router.add_get("/health", self._health_handler)

        # 创建并启动runner
        self.runner = web.AppRunner(self.web_app)
        await self.runner.setup()

        site = web.TCPSite(self.runner, host, port)
        await site.start()

        logger.info(f"SSE服务器已启动: http://{host}:{port}")
        logger.info(f"SSE端点: http://{host}:{port}/sse")
        logger.info(f"健康检查: http://{host}:{port}/health")

        if self.auth_token or self.api_key:
            logger.info("认证已启用")

    async def stop(self) -> None:
        """停止SSE服务器"""
        if self.runner:
            await self.runner.cleanup()
            logger.info("SSE服务器已停止")


async def run_sse(
    app: FastMCP,
    host: str = "localhost",
    port: int = 8000,
    auth_token: str | None = None,
    api_key: str | None = None,
) -> None:
    """
    使用SSE传输运行MCP服务器

    Args:
        app: FastMCP服务器实例
        host: 监听地址
        port: 监听端口
        auth_token: Bearer Token用于认证
        api_key: API Key用于认证

    Example:
        # 启动SSE服务器（无认证）
        await run_sse(app, host="0.0.0.0", port=8000)

        # 启动带Bearer Token认证的服务器
        await run_sse(app, host="0.0.0.0", port=8000, auth_token="your-token")
    """
    logger.info("启动SSE传输模式")

    transport = SSETransport(app, auth_token=auth_token, api_key=api_key)

    try:
        await transport.start(host=host, port=port)

        # 保持运行
        stop_event = asyncio.Event()
        await stop_event.wait()

    finally:
        await transport.stop()
