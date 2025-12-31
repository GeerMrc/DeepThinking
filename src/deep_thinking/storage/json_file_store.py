"""
JSON文件存储模块

提供原子写入、文件锁、自动备份的JSON文件存储功能。
关键特性:
- 原子写入：临时文件+重命名机制
- 文件锁：跨平台文件锁（fcntl/msvcrt）
- 自动备份：每次写入前自动备份
- 异常安全：操作失败自动清理
"""

import contextlib
import fcntl
import json
import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, TypeVar, cast

# Windows专用模块，仅在Windows系统导入
if sys.platform == "win32":
    import msvcrt  # noqa: F401

logger = logging.getLogger(__name__)

T = TypeVar("T")


class JsonFileStore:
    """
    JSON文件存储类

    提供线程安全的JSON文件读写操作，支持原子写入和自动备份。

    Attributes:
        base_dir: 基础目录路径
        backup_dir: 备份目录路径
        enable_backup: 是否启用自动备份
        enable_lock: 是否启用文件锁
    """

    def __init__(
        self,
        base_dir: str | Path,
        backup_dir: str | Path | None = None,
        enable_backup: bool = True,
        enable_lock: bool = True,
    ):
        """
        初始化JSON文件存储

        Args:
            base_dir: 基础目录路径
            backup_dir: 备份目录路径（默认为base_dir/.backups）
            enable_backup: 是否启用自动备份
            enable_lock: 是否启用文件锁
        """
        self.base_dir = Path(base_dir)
        self.enable_backup = enable_backup
        self.enable_lock = enable_lock

        # 创建基础目录
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # 设置备份目录
        if backup_dir is None:
            self.backup_dir = self.base_dir / ".backups"
        else:
            self.backup_dir = Path(backup_dir)

        if enable_backup:
            self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, key: str) -> Path:
        """
        获取文件路径

        Args:
            key: 文件键名

        Returns:
            文件完整路径
        """
        return self.base_dir / f"{key}.json"

    def _get_backup_path(self, key: str) -> Path:
        """
        获取备份文件路径

        Args:
            key: 文件键名

        Returns:
            备份文件完整路径
        """
        return self.backup_dir / f"{key}.json"

    def _acquire_lock(self, file_obj: Any) -> None:
        """
        获取文件锁

        Args:
            file_obj: 文件对象
        """
        if not self.enable_lock:
            return

        try:
            # Unix-like系统使用fcntl
            fcntl.flock(file_obj.fileno(), fcntl.LOCK_EX)
        except (AttributeError, OSError):
            # Windows系统使用msvcrt
            if sys.platform == "win32" and "msvcrt" in sys.modules:
                try:
                    msvcrt.locking(file_obj.fileno(), msvcrt.LK_LOCK, 1)  # type: ignore[attr-defined]
                except (AttributeError, OSError):
                    logger.warning("无法获取文件锁，继续操作")
            else:
                logger.warning("无法获取文件锁，继续操作")

    def _release_lock(self, file_obj: Any) -> None:
        """
        释放文件锁

        Args:
            file_obj: 文件对象
        """
        if not self.enable_lock:
            return

        try:
            # Unix-like系统使用fcntl
            fcntl.flock(file_obj.fileno(), fcntl.LOCK_UN)
        except (AttributeError, OSError):
            # Windows系统使用msvcrt
            if sys.platform == "win32" and "msvcrt" in sys.modules:
                with contextlib.suppress(AttributeError, OSError):
                    msvcrt.locking(file_obj.fileno(), msvcrt.LK_UNLOCK, 1)  # type: ignore[attr-defined]

    def _create_backup(self, key: str) -> None:
        """
        创建备份文件

        Args:
            key: 文件键名
        """
        if not self.enable_backup:
            return

        source_path = self._get_file_path(key)
        backup_path = self._get_backup_path(key)

        if source_path.exists():
            try:
                shutil.copy2(source_path, backup_path)
                logger.debug(f"已创建备份: {backup_path}")
            except OSError as e:
                logger.warning(f"创建备份失败: {e}")

    def _atomic_write(self, file_path: Path, data: str) -> None:
        """
        原子写入文件

        使用临时文件+重命名机制确保写入原子性。

        Args:
            file_path: 目标文件路径
            data: 要写入的数据
        """
        # 创建临时文件
        temp_fd, temp_path = tempfile.mkstemp(dir=self.base_dir, prefix=".tmp_", suffix=".json")

        try:
            # 写入数据到临时文件
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())

            # 原子重命名
            os.replace(temp_path, file_path)

        except Exception:
            # 清理临时文件
            with contextlib.suppress(OSError):
                os.unlink(temp_path)
            raise

    def read(self, key: str) -> dict[str, Any] | None:
        """
        读取JSON文件

        Args:
            key: 文件键名

        Returns:
            JSON数据，如果文件不存在则返回None

        Raises:
            OSError: 读取失败
            ValueError: JSON解析失败
        """
        file_path = self._get_file_path(key)

        if not file_path.exists():
            return None

        try:
            with open(file_path, encoding="utf-8") as f:
                self._acquire_lock(f)
                try:
                    data: dict[str, Any] = cast(dict[str, Any], json.load(f))
                    return data
                finally:
                    self._release_lock(f)

        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {e}") from e
        except OSError as e:
            logger.error(f"读取文件失败: {e}")
            raise

    def write(self, key: str, data: dict[str, Any] | list[Any]) -> None:
        """
        写入JSON文件（原子写入）

        Args:
            key: 文件键名
            data: 要写入的数据

        Raises:
            OSError: 写入失败
            TypeError: 数据不可序列化
        """
        file_path = self._get_file_path(key)

        # 创建备份
        self._create_backup(key)

        # 序列化数据
        try:
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
        except (TypeError, ValueError) as e:
            raise TypeError(f"数据序列化失败: {e}") from e

        # 原子写入
        try:
            self._atomic_write(file_path, json_str)
            logger.debug(f"写入文件成功: {file_path}")
        except OSError as e:
            logger.error(f"写入文件失败: {e}")
            raise

    def delete(self, key: str) -> bool:
        """
        删除JSON文件

        Args:
            key: 文件键名

        Returns:
            是否成功删除
        """
        file_path = self._get_file_path(key)

        if not file_path.exists():
            return False

        try:
            # 创建备份
            self._create_backup(key)

            # 删除文件
            file_path.unlink()
            logger.debug(f"删除文件成功: {file_path}")
            return True

        except OSError as e:
            logger.error(f"删除文件失败: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        检查文件是否存在

        Args:
            key: 文件键名

        Returns:
            文件是否存在
        """
        return self._get_file_path(key).exists()

    def list_keys(self) -> list[str]:
        """
        列出所有文件键名

        Returns:
            文件键名列表
        """
        keys = []
        for file_path in self.base_dir.glob("*.json"):
            # 跳过备份目录
            if file_path.is_file() and self.backup_dir not in file_path.parents:
                keys.append(file_path.stem)
        return sorted(keys)

    def restore_backup(self, key: str) -> bool:
        """
        从备份恢复文件

        Args:
            key: 文件键名

        Returns:
            是否成功恢复
        """
        backup_path = self._get_backup_path(key)
        file_path = self._get_file_path(key)

        if not backup_path.exists():
            return False

        try:
            shutil.copy2(backup_path, file_path)
            logger.info(f"从备份恢复: {key}")
            return True
        except OSError as e:
            logger.error(f"恢复备份失败: {e}")
            return False

    def clear_backups(self, older_than_days: int = 30) -> int:
        """
        清理旧备份文件

        Args:
            older_than_days: 清理多少天前的备份

        Returns:
            清理的文件数量
        """
        import time

        cutoff_time = time.time() - (older_than_days * 86400)
        cleared = 0

        for backup_path in self.backup_dir.glob("*.json"):
            try:
                if backup_path.stat().st_mtime < cutoff_time:
                    backup_path.unlink()
                    cleared += 1
            except OSError as e:
                logger.warning(f"清理备份失败 {backup_path}: {e}")

        if cleared > 0:
            logger.info(f"清理了 {cleared} 个旧备份文件")

        return cleared
