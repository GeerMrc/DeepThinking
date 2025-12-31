"""
DeepThinking-MCP CLI入口

支持STDIO和SSE双传输模式的命令行接口。

使用示例:
    # STDIO模式（本地）
    python -m deep_thinking --transport stdio

    # SSE模式（远程）
    python -m deep_thinking --transport sse --port 8000 --host 0.0.0.0

    # SSE模式（带认证）
    python -m deep_thinking --transport sse --auth-token your-token
"""

import argparse
import asyncio
import logging
import os
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from mcp.server import FastMCP  # type: ignore[import-not-found]

from deep_thinking.transports.sse import run_sse

# 导入传输层模块
from deep_thinking.transports.stdio import run_stdio
from deep_thinking.utils.logger import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def server_lifespan(_app: FastMCP) -> AsyncGenerator[None, None]:
    """
    服务器生命周期管理

    在服务器启动时初始化资源，在关闭时清理资源

    Args:
        app: FastMCP服务器实例

    Yields:
        None
    """
    # TODO: 初始化存储管理器
    logger.info("DeepThinking-MCP服务器正在初始化...")

    yield

    # TODO: 清理资源
    logger.info("DeepThinking-MCP服务器正在关闭...")


def create_server() -> FastMCP:
    """
    创建FastMCP服务器实例

    Returns:
        FastMCP服务器实例
    """
    app = FastMCP(name="deep-thinking", lifespan=server_lifespan)

    # TODO: 添加工具注册
    # 这些将在后续阶段实现
    # @app.tool()
    # async def sequential_thinking(...) -> str:
    #     ...

    return app


def parse_args() -> argparse.Namespace:
    """
    解析命令行参数

    Returns:
        解析后的参数命名空间
    """
    parser = argparse.ArgumentParser(
        prog="deep-thinking", description="DeepThinking-MCP - 高级深度思考MCP服务器"
    )

    # 传输模式选择
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse"],
        default=os.getenv("DEEP_THINKING_TRANSPORT", "stdio"),
        help="传输模式: stdio（本地）或 sse（远程）",
    )

    # SSE模式参数
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("DEEP_THINKING_HOST", "localhost"),
        help="SSE模式监听地址（默认: localhost）",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("DEEP_THINKING_PORT", "8000")),
        help="SSE模式监听端口（默认: 8000）",
    )

    parser.add_argument(
        "--auth-token",
        type=str,
        default=os.getenv("DEEP_THINKING_AUTH_TOKEN"),
        help="Bearer Token用于SSE模式认证",
    )

    parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("DEEP_THINKING_API_KEY"),
        help="API Key用于SSE模式认证",
    )

    # 日志级别
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=os.getenv("DEEP_THINKING_LOG_LEVEL", "INFO"),
        help="日志级别（默认: INFO）",
    )

    return parser.parse_args()


async def main_async() -> int:
    """
    异步主函数

    Returns:
        退出码: 0表示成功，非0表示失败
    """
    # 解析命令行参数
    args = parse_args()

    # 配置日志（传输感知）
    log_level = getattr(logging, args.log_level)
    setup_logging(args.transport)
    logging.getLogger().setLevel(log_level)

    logger.info(f"传输模式: {args.transport}")

    # 创建MCP服务器
    app = create_server()

    try:
        if args.transport == "stdio":
            # STDIO模式
            logger.info("使用STDIO传输模式启动...")
            await run_stdio(app)

        elif args.transport == "sse":
            # SSE模式
            logger.info(f"使用SSE传输模式启动，监听: {args.host}:{args.port}")

            if args.auth_token or args.api_key:
                logger.info("认证已启用")

            await run_sse(
                app,
                host=args.host,
                port=args.port,
                auth_token=args.auth_token,
                api_key=args.api_key,
            )

        return 0

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
        return 0

    except Exception as e:
        logger.error(f"服务器错误: {e}", exc_info=True)
        return 1


def main() -> int:
    """
    CLI入口点

    Returns:
        退出码: 0表示成功，非0表示失败
    """
    try:
        return asyncio.run(main_async())
    except Exception as e:
        print(f"启动失败: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
