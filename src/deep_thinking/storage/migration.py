"""
数据迁移模块

提供从旧存储位置（./.deepthinking/）迁移到新位置（~/.deepthinking/）的功能。
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def get_old_data_dir() -> Path:
    """
    获取旧数据目录位置（项目本地目录）

    Returns:
        旧数据目录路径
    """
    return Path.cwd() / ".deepthinking"


# 旧数据目录位置
OLD_DATA_DIR = get_old_data_dir()

# 迁移状态文件
MIGRATION_MARKER = ".migration_completed"


def detect_old_data() -> bool:
    """
    检测是否存在旧数据目录

    Returns:
        如果存在旧数据目录且包含会话数据，返回True
    """
    if not OLD_DATA_DIR.exists():
        return False

    # 检查是否包含会话目录或索引文件
    sessions_dir = OLD_DATA_DIR / "sessions"
    index_file = OLD_DATA_DIR / "sessions" / ".index.json"

    return sessions_dir.exists() or index_file.exists()


def create_migration_backup(backup_dir: Path | None = None) -> Path | None:
    """
    创建迁移前备份

    Args:
        backup_dir: 备份目录路径，默认为 ~/.deepthinking/backups/migration_backup_<timestamp>

    Returns:
        备份目录路径，失败返回None
    """
    if not OLD_DATA_DIR.exists():
        logger.warning("旧数据目录不存在，跳过备份")
        return None

    if backup_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = OLD_DATA_DIR / "backups" / f"migration_backup_{timestamp}"

    try:
        # 创建备份目录
        backup_dir.mkdir(parents=True, exist_ok=True)

        # 备份会话目录
        sessions_src = OLD_DATA_DIR / "sessions"
        if sessions_src.exists():
            shutil.copytree(sessions_src, backup_dir / "sessions")

        # 备份索引文件
        index_src = OLD_DATA_DIR / "sessions" / ".index.json"
        if index_src.exists():
            backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(index_src, backup_dir / "index.json")

        logger.info(f"创建迁移备份: {backup_dir}")
        return backup_dir

    except Exception as e:
        logger.error(f"创建备份失败: {e}")
        return None


def migrate_data(target_dir: Path, force: bool = False) -> bool:
    """
    迁移数据到新位置

    Args:
        target_dir: 目标目录路径
        force: 是否强制迁移（覆盖已有数据）

    Returns:
        是否成功迁移
    """
    # 检查旧数据是否存在
    if not detect_old_data():
        logger.info("未检测到旧数据，跳过迁移")
        return False

    # 检查是否已完成迁移
    migration_marker = target_dir / MIGRATION_MARKER
    if migration_marker.exists() and not force:
        logger.info("迁移已完成，跳过")
        return False

    # 检查目标目录是否已有数据
    if target_dir.exists() and (target_dir / "sessions").exists() and not force:
        logger.warning(f"目标目录已存在数据: {target_dir}")
        logger.warning("使用 --force 强制迁移或手动清理目标目录")
        return False

    logger.info(f"开始迁移数据: {OLD_DATA_DIR} -> {target_dir}")

    try:
        # 创建目标目录
        target_dir.mkdir(parents=True, exist_ok=True)

        # 迁移会话目录
        sessions_src = OLD_DATA_DIR / "sessions"
        if sessions_src.exists():
            sessions_dst = target_dir / "sessions"
            if sessions_dst.exists():
                shutil.rmtree(sessions_dst)
            shutil.copytree(sessions_src, sessions_dst)

        # 迁移索引文件
        index_src = OLD_DATA_DIR / "sessions" / ".index.json"
        if index_src.exists():
            index_dst = target_dir / "sessions" / ".index.json"
            shutil.copy2(index_src, index_dst)

        # 创建迁移标记
        migration_marker.write_text(
            f"migration_date: {datetime.now().isoformat()}\n"
            f"source: {OLD_DATA_DIR}\n"
            f"target: {target_dir}\n",
            encoding="utf-8",
        )

        logger.info(f"数据迁移完成: {target_dir}")
        return True

    except Exception as e:
        logger.error(f"数据迁移失败: {e}")
        return False


def rollback_migration(target_dir: Path) -> bool:
    """
    回滚迁移（删除新位置的数据）

    注意：此操作仅删除新位置的数据，不会恢复旧位置的数据。

    Args:
        target_dir: 目标目录路径

    Returns:
        是否成功回滚
    """
    migration_marker = target_dir / MIGRATION_MARKER
    if not migration_marker.exists():
        logger.warning("未检测到迁移标记，跳过回滚")
        return False

    try:
        # 删除迁移标记
        migration_marker.unlink()

        # 删除会话目录
        sessions_dir = target_dir / "sessions"
        if sessions_dir.exists():
            shutil.rmtree(sessions_dir)

        # 删除索引文件
        index_file = target_dir / "sessions" / ".index.json"
        if index_file.exists():
            index_file.unlink()

        logger.info(f"迁移回滚完成: {target_dir}")
        return True

    except Exception as e:
        logger.error(f"回滚失败: {e}")
        return False


def get_migration_info(target_dir: Path) -> dict[str, str] | None:
    """
    获取迁移信息

    Args:
        target_dir: 目标目录路径

    Returns:
        迁移信息字典，未迁移返回None
    """
    migration_marker = target_dir / MIGRATION_MARKER
    if not migration_marker.exists():
        return None

    try:
        content = migration_marker.read_text(encoding="utf-8")
        info = {}
        for line in content.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info
    except Exception:
        return None


def should_migrate(target_dir: Path) -> bool:
    """
    判断是否需要迁移

    Args:
        target_dir: 目标目录路径

    Returns:
        是否需要迁移
    """
    # 如果旧数据不存在，不需要迁移
    if not detect_old_data():
        return False

    # 如果迁移已完成，不需要迁移
    return not (target_dir / MIGRATION_MARKER).exists()
