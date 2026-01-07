"""
FastMCP服务器实例

提供MCP工具注册和生命周期管理。
"""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from mcp.server import FastMCP

from deep_thinking.storage.migration import (
    create_migration_backup,
    detect_old_data,
    get_migration_info,
    migrate_data,
)
from deep_thinking.storage.storage_manager import StorageManager

logger = logging.getLogger(__name__)


def get_default_data_dir() -> Path:
    """
    获取默认数据存储目录

    优先级：
    1. 环境变量 DEEP_THINKING_DATA_DIR（支持 ~ 和 $HOME 自动扩展）
    2. 项目本地目录 .deepthinking/
    3. 用户主目录 .deepthinking/ (向后兼容)

    Returns:
        数据存储目录路径
    """
    # 1. 检查环境变量（支持路径扩展）
    custom_dir = os.getenv("DEEP_THINKING_DATA_DIR")
    if custom_dir:
        # 先扩展环境变量（如 $HOME），再扩展 ~ 符号
        expanded = os.path.expandvars(custom_dir)
        return Path(expanded).expanduser()

    # 2. 默认使用项目本地目录
    local_dir = Path.cwd() / ".deepthinking"

    # 3. 向后兼容：如果本地目录不存在但旧目录存在，使用旧目录
    old_dir = Path.home() / ".deepthinking"
    if not local_dir.exists() and old_dir.exists():
        logger.info(f"检测到旧数据目录: {old_dir}")
        logger.info("建议迁移数据到项目本地目录")
        return old_dir

    return local_dir


def ensure_gitignore(data_dir: Path) -> None:
    """
    确保数据目录包含 .gitignore 文件

    防止敏感数据和临时文件被提交到版本控制。

    Args:
        data_dir: 数据目录路径
    """
    gitignore_path = data_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.parent.mkdir(parents=True, exist_ok=True)
        gitignore_path.write_text(
            "# 忽略所有会话数据\n"
            "sessions/\n"
            "# 忽略索引文件\n"
            ".index.json\n"
            "# 忽略备份数据\n"
            ".backups/\n"
            "backups/\n"
            "# 忽略迁移日志\n"
            "migration.log\n"
            "*.log\n",
            encoding="utf-8",
        )
        logger.debug(f"创建 .gitignore: {gitignore_path}")


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

    # 获取数据存储目录（支持环境变量和项目本地目录）
    data_dir = get_default_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"初始化数据目录: {data_dir}")

    # 确保 .gitignore 存在
    ensure_gitignore(data_dir)

    # 检查并执行数据迁移
    migration_info = get_migration_info(data_dir)
    if migration_info:
        logger.info(f"数据已迁移: {migration_info.get('target', data_dir)}")
    elif detect_old_data():
        logger.info("检测到旧数据目录，开始自动迁移...")
        backup_dir = create_migration_backup()
        if backup_dir:
            logger.info(f"迁移备份已创建: {backup_dir}")

        success = migrate_data(data_dir)
        if success:
            logger.info("数据迁移完成")
        else:
            logger.warning("数据迁移失败，将继续使用旧数据目录")

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
    name="DeepThinking",
    instructions="深度思考MCP服务器 - 提供顺序思考、会话管理和状态持久化功能",
    lifespan=server_lifespan,
)


# 导出工具模块
from deep_thinking.tools import (  # noqa: E402, F401
    export,
    sequential_thinking,
    session_manager,
    task_manager,
    template,
    visualization,
)
