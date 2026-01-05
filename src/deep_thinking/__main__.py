"""
DeepThinking CLI入口

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

from mcp.server import FastMCP

# 导入 server.py 中的 app 实例（已注册所有工具）
# 这必须在使用前导入，以确保工具装饰器执行
from deep_thinking.server import app  # noqa: E402
from deep_thinking.transports.sse import run_sse

# 导入传输层模块
from deep_thinking.transports.stdio import run_stdio
from deep_thinking.utils.logger import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def server_lifespan(_app: FastMCP) -> AsyncGenerator[None, None]:
    """
    服务器生命周期管理

    注意：实际的资源初始化和清理在 server.py 的 server_lifespan 中实现，
    包括存储管理器的初始化和会话数据的持久化。

    Args:
        app: FastMCP服务器实例（未使用，保留用于API兼容性）

    Yields:
        None
    """
    logger.info("DeepThinking服务器正在初始化...")

    yield

    logger.info("DeepThinking服务器正在关闭...")


def create_server() -> FastMCP:
    """
    创建FastMCP服务器实例

    注意：实际的MCP服务器和工具注册在 server.py 中实现。
    各个工具模块通过导入 server.py 中的 app 实例自动注册。

    Returns:
        FastMCP服务器实例（基础实例，实际使用 server.py 中的全局实例）
    """
    app = FastMCP(name="DeepThinking", lifespan=server_lifespan)

    # 工具通过导入 server.py 自动注册：
    # - sequential_thinking (顺序思考)
    # - session_manager (会话管理)
    # - export (导出工具)
    # - visualization (可视化)
    # - template (模板系统)

    return app


def parse_args() -> argparse.Namespace:
    """
    解析命令行参数

    Returns:
        解析后的参数命名空间
    """
    parser = argparse.ArgumentParser(
        prog="deepthinking", description="DeepThinking MCP - 高级深度思考MCP服务器"
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

    # 存储目录参数
    parser.add_argument(
        "--data-dir",
        type=str,
        default=os.getenv("DEEP_THINKING_DATA_DIR"),
        help="数据存储目录路径（默认: ./.deepthinking/）",
    )

    # 日志级别
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=os.getenv("DEEP_THINKING_LOG_LEVEL", "INFO"),
        help="日志级别（默认: INFO）",
    )

    # 思考配置参数
    parser.add_argument(
        "--max-thoughts",
        type=int,
        default=int(os.getenv("DEEP_THINKING_MAX_THOUGHTS", "50")),
        help="最大思考步骤数（默认: 50，支持 1-10000）",
    )

    parser.add_argument(
        "--min-thoughts",
        type=int,
        default=int(os.getenv("DEEP_THINKING_MIN_THOUGHTS", "3")),
        help="最小思考步骤数（默认: 3，支持 1-10000）",
    )

    parser.add_argument(
        "--thoughts-increment",
        type=int,
        default=int(os.getenv("DEEP_THINKING_THOUGHTS_INCREMENT", "10")),
        help="思考步骤增量（默认: 10，支持 1-100）",
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

    # 如果指定了 --data-dir，设置环境变量
    if args.data_dir:
        os.environ["DEEP_THINKING_DATA_DIR"] = args.data_dir

    # 初始化思考配置（从 CLI 参数或环境变量）
    from deep_thinking.models.config import ThinkingConfig, set_global_config

    thinking_config = ThinkingConfig(
        max_thoughts=args.max_thoughts,
        min_thoughts=args.min_thoughts,
        thoughts_increment=args.thoughts_increment,
    )
    set_global_config(thinking_config)

    logger.info(
        f"思考配置: max={args.max_thoughts}, min={args.min_thoughts}, "
        f"increment={args.thoughts_increment}"
    )

    # 配置日志（传输感知）
    log_level = getattr(logging, args.log_level)
    setup_logging(args.transport)
    logging.getLogger().setLevel(log_level)

    logger.info(f"传输模式: {args.transport}")

    # 使用 server.py 中已配置工具的 app 实例
    # 该实例已通过工具模块导入注册了所有 MCP 工具
    # app = create_server()  # 不再需要创建新实例

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
