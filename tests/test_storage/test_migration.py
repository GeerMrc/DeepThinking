"""
数据迁移模块单元测试
"""

import json
from pathlib import Path
from unittest import mock

import pytest

from deep_thinking.storage.migration import (
    MIGRATION_MARKER,
    create_migration_backup,
    detect_old_data,
    get_migration_info,
    migrate_data,
    rollback_migration,
    should_migrate,
)


@pytest.fixture
def temp_old_data_dir(tmp_path: Path):
    """创建临时旧数据目录"""
    old_dir = tmp_path / ".deepthinking"
    old_dir.mkdir(parents=True, exist_ok=True)

    # 创建会话目录和索引文件
    sessions_dir = old_dir / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # 创建索引文件
    index_file = sessions_dir / ".index.json"
    index_file.write_text(
        json.dumps(
            {
                "test-session-1": {
                    "name": "Test Session 1",
                    "status": "completed",
                    "updated_at": "2026-01-01T00:00:00",
                }
            }
        ),
        encoding="utf-8",
    )

    # 创建测试会话文件
    session_file = sessions_dir / "test-session-1.json"
    session_file.write_text(
        json.dumps(
            {
                "session_id": "test-session-1",
                "name": "Test Session 1",
                "description": "Test Description",
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-01T00:00:00",
                "status": "completed",
                "thoughts": [],
            }
        ),
        encoding="utf-8",
    )

    return old_dir


class TestDetectOldData:
    """测试旧数据检测功能"""

    def test_no_old_data_dir(self, tmp_path: Path):
        """测试：旧数据目录不存在"""
        with mock.patch("deep_thinking.storage.migration.OLD_DATA_DIR", tmp_path / "nonexistent"):
            assert not detect_old_data()

    def test_old_data_dir_exists_empty(self, tmp_path: Path):
        """测试：旧数据目录存在但为空"""
        old_dir = tmp_path / ".deepthinking"
        old_dir.mkdir(parents=True, exist_ok=True)

        with mock.patch("deep_thinking.storage.migration.OLD_DATA_DIR", old_dir):
            assert not detect_old_data()

    def test_old_data_dir_with_sessions(self, temp_old_data_dir: Path):
        """测试：旧数据目录存在且包含会话数据"""
        with mock.patch("deep_thinking.storage.migration.OLD_DATA_DIR", temp_old_data_dir):
            assert detect_old_data()

    def test_old_data_dir_with_index_only(self, tmp_path: Path):
        """测试：旧数据目录存在且只有索引文件"""
        old_dir = tmp_path / ".deepthinking"
        old_dir.mkdir(parents=True, exist_ok=True)

        sessions_dir = old_dir / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)

        index_file = sessions_dir / ".index.json"
        index_file.write_text('{"test": "data"}', encoding="utf-8")

        with mock.patch("deep_thinking.storage.migration.OLD_DATA_DIR", old_dir):
            assert detect_old_data()


class TestCreateMigrationBackup:
    """测试备份创建功能"""

    def test_create_backup_success(self, temp_old_data_dir: Path):
        """测试：成功创建备份"""
        with mock.patch("deep_thinking.storage.migration.OLD_DATA_DIR", temp_old_data_dir):
            backup_dir = create_migration_backup()

            assert backup_dir is not None
            assert backup_dir.exists()
            assert (backup_dir / "sessions").exists()
            assert (backup_dir / "index.json").exists()

    def test_create_backup_custom_path(self, temp_old_data_dir: Path, tmp_path: Path):
        """测试：指定备份路径"""
        custom_backup = tmp_path / "custom_backup"

        with mock.patch("deep_thinking.storage.migration.OLD_DATA_DIR", temp_old_data_dir):
            backup_dir = create_migration_backup(custom_backup)

            assert backup_dir == custom_backup
            assert backup_dir.exists()

    def test_create_backup_no_old_data(self, tmp_path: Path):
        """测试：旧数据不存在时创建备份"""
        with mock.patch("deep_thinking.storage.migration.OLD_DATA_DIR", tmp_path / "nonexistent"):
            backup_dir = create_migration_backup()
            assert backup_dir is None


class TestMigrateData:
    """测试数据迁移功能"""

    def test_migrate_success(self, temp_old_data_dir: Path, tmp_path: Path):
        """测试：成功迁移数据"""
        target_dir = tmp_path / ".deepthinking-new"

        with mock.patch("deep_thinking.storage.migration.OLD_DATA_DIR", temp_old_data_dir):
            success = migrate_data(target_dir)

            assert success
            assert (target_dir / "sessions" / ".index.json").exists()
            assert (target_dir / "sessions" / "test-session-1.json").exists()
            assert (target_dir / MIGRATION_MARKER).exists()

    def test_migrate_no_old_data(self, tmp_path: Path):
        """测试：旧数据不存在时迁移"""
        target_dir = tmp_path / ".deepthinking"

        with mock.patch("deep_thinking.storage.migration.OLD_DATA_DIR", tmp_path / "nonexistent"):
            success = migrate_data(target_dir)
            assert not success

    def test_migrate_already_completed(self, temp_old_data_dir: Path, tmp_path: Path):
        """测试：已完成的迁移不再重复"""
        target_dir = tmp_path / ".deepthinking"
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / MIGRATION_MARKER).write_text("migration_date: 2026-01-01")

        with mock.patch("deep_thinking.storage.migration.OLD_DATA_DIR", temp_old_data_dir):
            success = migrate_data(target_dir)
            assert not success

    def test_migrate_force_overwrite(self, temp_old_data_dir: Path, tmp_path: Path):
        """测试：强制迁移覆盖已有数据"""
        target_dir = tmp_path / ".deepthinking-force"
        target_dir.mkdir(parents=True, exist_ok=True)

        # 创建旧会话文件
        (target_dir / "sessions").mkdir(parents=True, exist_ok=True)
        (target_dir / "sessions" / "old.json").write_text("{}", encoding="utf-8")

        with mock.patch("deep_thinking.storage.migration.OLD_DATA_DIR", temp_old_data_dir):
            success = migrate_data(target_dir, force=True)
            assert success
            # 验证新数据已迁移
            assert (target_dir / "sessions" / ".index.json").exists()


class TestRollbackMigration:
    """测试迁移回滚功能"""

    def test_rollback_success(self, temp_old_data_dir: Path, tmp_path: Path):
        """测试：成功回滚迁移"""
        target_dir = tmp_path / ".deepthinking"
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / MIGRATION_MARKER).write_text("migration_date: 2026-01-01")

        sessions_dir = target_dir / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        (sessions_dir / "test.json").write_text("{}", encoding="utf-8")

        success = rollback_migration(target_dir)

        assert success
        assert not (target_dir / MIGRATION_MARKER).exists()
        assert not (target_dir / "sessions").exists()

    def test_rollback_no_marker(self, tmp_path: Path):
        """测试：没有迁移标记时回滚"""
        target_dir = tmp_path / ".deepthinking"
        target_dir.mkdir(parents=True, exist_ok=True)

        success = rollback_migration(target_dir)
        assert not success


class TestGetMigrationInfo:
    """测试获取迁移信息功能"""

    def test_get_migration_info_exists(self, tmp_path: Path):
        """测试：成功获取迁移信息"""
        target_dir = tmp_path / ".deepthinking"
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / MIGRATION_MARKER).write_text(
            "migration_date: 2026-01-01T00:00:00\n"
            "source: ~/.deepthinking/\n"
            "target: ./.deepthinking/\n",
            encoding="utf-8",
        )

        info = get_migration_info(target_dir)

        assert info is not None
        assert info["migration_date"] == "2026-01-01T00:00:00"
        assert info["source"] == "~/.deepthinking/"
        assert info["target"] == "./.deepthinking/"

    def test_get_migration_info_not_exists(self, tmp_path: Path):
        """测试：迁移标记不存在时返回 None"""
        target_dir = tmp_path / ".deepthinking"
        target_dir.mkdir(parents=True, exist_ok=True)

        info = get_migration_info(target_dir)
        assert info is None


class TestShouldMigrate:
    """测试是否需要迁移功能"""

    def test_should_migrate_yes(self, temp_old_data_dir: Path, tmp_path: Path):
        """测试：需要迁移"""
        target_dir = tmp_path / ".deepthinking"
        target_dir.mkdir(parents=True, exist_ok=True)

        with mock.patch("deep_thinking.storage.migration.OLD_DATA_DIR", temp_old_data_dir):
            assert should_migrate(target_dir)

    def test_should_migrate_no_old_data(self, tmp_path: Path):
        """测试：没有旧数据，不需要迁移"""
        target_dir = tmp_path / ".deepthinking"
        target_dir.mkdir(parents=True, exist_ok=True)

        with mock.patch("deep_thinking.storage.migration.OLD_DATA_DIR", tmp_path / "nonexistent"):
            assert not should_migrate(target_dir)

    def test_should_migrate_already_done(self, temp_old_data_dir: Path, tmp_path: Path):
        """测试：已完成迁移，不需要再迁移"""
        target_dir = tmp_path / ".deepthinking"
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / MIGRATION_MARKER).write_text("migration_date: 2026-01-01")

        with mock.patch("deep_thinking.storage.migration.OLD_DATA_DIR", temp_old_data_dir):
            assert not should_migrate(target_dir)
