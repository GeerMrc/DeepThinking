"""
STDIO传输模块

使用标准输入/输出流进行进程间通信，适用于Claude Desktop本地集成。

关键特性:
- 使用stdin接收JSON-RPC请求
- 使用stdout发送JSON-RPC响应
- 日志必须输出到stderr（严禁使用print）
- 最佳性能，无网络开销
"""

import logging

from mcp.server import FastMCP

logger = logging.getLogger(__name__)


async def run_stdio(app: FastMCP) -> None:
    """
    使用STDIO传输运行MCP服务器

    Args:
        app: FastMCP服务器实例

    注意:
        - STDIO模式下，stdout用于JSON-RPC通信
        - 所有日志必须输出到stderr
        - 严禁使用print()函数，会破坏JSON-RPC协议
    """
    logger.info("启动STDIO传输模式 - 日志输出到stderr")
    logger.debug("开始监听stdin的JSON-RPC请求")

    # 直接调用底层的异步方法，避免 asyncio 事件循环冲突
    # 使用当前的 asyncio 事件循环而不是创建新的
    await app.run_stdio_async()

    logger.info("STDIO传输模式已关闭")
