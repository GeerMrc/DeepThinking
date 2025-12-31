"""
FastMCP服务器实例

提供MCP工具注册和生命周期管理。
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from mcp.server import FastMCP  # type: ignore[import-not-found]

from deep_thinking.storage.storage_manager import StorageManager

logger = logging.getLogger(__name__)

# 全局存储管理器实例
_storage_manager: StorageManager | None = None


def get_storage_manager() -> StorageManager:
    """
    获取全局存储管理器实例

    Returns:
        StorageManager实例

    Raises:
        RuntimeError: 如果存储管理器未初始化
    """
    global _storage_manager
    if _storage_manager is None:
        raise RuntimeError("存储管理器未初始化")
    return _storage_manager


@asynccontextmanager
async def server_lifespan(_server: FastMCP) -> AsyncGenerator[None, None]:
    """
    服务器生命周期管理

    处理服务器的初始化和清理。

    Args:
        _server: FastMCP服务器实例（未使用，保留用于API兼容性）
    """
    global _storage_manager

    # 数据存储目录
    data_dir = Path.home() / ".deep-thinking-mcp"
    data_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"初始化数据目录: {data_dir}")

    # 初始化存储管理器
    _storage_manager = StorageManager(data_dir)
    logger.info("存储管理器已初始化")

    try:
        yield
    finally:
        # 清理资源
        logger.info("清理服务器资源")
        _storage_manager = None


# 创建FastMCP服务器实例
app = FastMCP(
    name="deep-thinking",
    instructions="深度思考MCP服务器 - 提供顺序思考、会话管理和状态持久化功能",
    lifespan=server_lifespan,
)


# 导出工具模块
from deep_thinking.tools import (  # noqa: E402, F401
    export,
    sequential_thinking,
    session_manager,
    template,
    visualization,
)
