"""
存储模块

提供数据持久化和迁移功能。
"""

from deep_thinking.storage.json_file_store import JsonFileStore
from deep_thinking.storage.migration import (
    create_migration_backup,
    detect_old_data,
    get_migration_info,
    migrate_data,
    rollback_migration,
    should_migrate,
)
from deep_thinking.storage.storage_manager import StorageManager
from deep_thinking.storage.task_list_store import TaskListStore

__all__ = [
    # 存储管理
    "StorageManager",
    "JsonFileStore",
    "TaskListStore",
    # 数据迁移
    "detect_old_data",
    "migrate_data",
    "create_migration_backup",
    "rollback_migration",
    "get_migration_info",
    "should_migrate",
]
