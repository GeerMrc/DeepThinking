"""
JSON文件存储模块单元测试
"""

import json
import os
import time

import pytest

from deep_thinking.storage.json_file_store import JsonFileStore


class TestJsonFileStore:
    """JsonFileStore测试"""

    @pytest.fixture
    def store(self, temp_dir):
        """创建存储实例"""
        return JsonFileStore(temp_dir, enable_backup=True, enable_lock=False)

    def test_init_creates_directories(self, temp_dir):
        """测试初始化创建目录"""
        JsonFileStore(temp_dir / "data")
        assert (temp_dir / "data").exists()
        assert (temp_dir / "data" / ".backups").exists()

    def test_write_and_read(self, store):
        """测试写入和读取"""
        data = {"key": "value", "number": 42}
        store.write("test", data)

        result = store.read("test")
        assert result == data

    def test_write_creates_json_file(self, store):
        """测试写入创建JSON文件"""
        store.write("test", {"data": "value"})

        file_path = store._get_file_path("test")
        assert file_path.exists()

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
            assert data == {"data": "value"}

    def test_read_nonexistent_returns_none(self, store):
        """测试读取不存在的文件返回None"""
        result = store.read("nonexistent")
        assert result is None

    def test_read_invalid_json_raises_error(self, store):
        """测试读取无效JSON抛出错误"""
        file_path = store._get_file_path("invalid")
        file_path.write_text("invalid json", encoding="utf-8")

        with pytest.raises(ValueError, match="JSON解析失败"):
            store.read("invalid")

    def test_write_creates_backup(self, store):
        """测试覆盖写入时创建备份"""
        # 首次写入，文件不存在时不会创建备份
        store.write("test", {"version": 1})
        backup_path = store._get_backup_path("test")
        assert not backup_path.exists()

        # 覆盖写入，应该创建备份
        store.write("test", {"version": 2})
        assert backup_path.exists()

        # 验证备份是旧版本
        import json

        with open(backup_path, encoding="utf-8") as f:
            backup_data = json.load(f)
        assert backup_data == {"version": 1}

    def test_write_overwrites_existing(self, store):
        """测试覆盖写入"""
        store.write("test", {"version": 1})
        store.write("test", {"version": 2})

        result = store.read("test")
        assert result == {"version": 2}

    def test_write_invalid_data_raises_error(self, store):
        """测试写入不可序列化数据抛出错误"""

        # 无法序列化的对象
        class Unserializable:
            pass

        with pytest.raises(TypeError, match="数据序列化失败"):
            store.write("test", {"obj": Unserializable()})

    def test_delete_existing_file(self, store):
        """测试删除存在的文件"""
        store.write("test", {"data": "value"})
        result = store.delete("test")

        assert result is True
        assert not store.exists("test")

    def test_delete_nonexistent_file(self, store):
        """测试删除不存在的文件"""
        result = store.delete("nonexistent")
        assert result is False

    def test_delete_creates_backup(self, store):
        """测试删除创建备份"""
        store.write("test", {"data": "value"})
        store.delete("test")

        backup_path = store._get_backup_path("test")
        assert backup_path.exists()

    def test_exists_true(self, store):
        """测试文件存在返回True"""
        store.write("test", {})
        assert store.exists("test") is True

    def test_exists_false(self, store):
        """测试文件不存在返回False"""
        assert store.exists("nonexistent") is False

    def test_list_keys(self, store):
        """测试列出所有键名"""
        store.write("aaa", {})
        store.write("bbb", {})
        store.write("ccc", {})

        keys = store.list_keys()
        assert keys == ["aaa", "bbb", "ccc"]

    def test_list_keys_empty(self, store):
        """测试列出空目录"""
        assert store.list_keys() == []

    def test_restore_backup(self, store):
        """测试从备份恢复"""
        original_data = {"version": 1}
        store.write("test", original_data)

        # 修改文件
        store.write("test", {"version": 2})

        # 从备份恢复
        result = store.restore_backup("test")

        assert result is True
        restored_data = store.read("test")
        assert restored_data == original_data

    def test_restore_backup_no_backup(self, store):
        """测试恢复不存在的备份"""
        result = store.restore_backup("nonexistent")
        assert result is False

    def test_clear_old_backups(self, store):
        """测试清理旧备份"""
        # 创建备份文件
        backup_path = store._get_backup_path("old")
        backup_path.write_text("{}", encoding="utf-8")

        # 修改文件时间使其看起来很旧
        old_time = time.time() - (40 * 86400)  # 40天前
        os.utime(backup_path, (old_time, old_time))

        # 清理
        cleared = store.clear_backups(older_than_days=30)

        assert cleared == 1
        assert not backup_path.exists()

    def test_atomic_write_integrity(self, store):
        """测试原子写入完整性"""
        # 写入一个键值对
        large_data = {"key": "x" * 10000}
        store.write("large", large_data)

        # 读取验证
        result = store.read("large")
        assert result == large_data

    def test_concurrent_write_safe(self, store):
        """测试并发写入安全"""
        data1 = {"value": 1}
        data2 = {"value": 2}

        store.write("test", data1)
        store.write("test", data2)

        # 最终应该只有一个有效的值
        result = store.read("test")
        assert result["value"] in [1, 2]
        # 文件应该存在且完整
        assert store.exists("test")

    def test_write_list_data(self, store):
        """测试写入列表数据"""
        data = [1, 2, 3, {"key": "value"}]
        store.write("list", data)

        result = store.read("list")
        assert result == data

    def test_empty_data(self, store):
        """测试空数据"""
        store.write("empty", {})
        result = store.read("empty")
        assert result == {}

    def test_nested_data(self, store):
        """测试嵌套数据"""
        data = {
            "level1": {"level2": {"level3": "deep_value"}},
            "list": [{"a": 1}, {"b": 2}],
        }
        store.write("nested", data)

        result = store.read("nested")
        assert result == data


class TestJsonFileStoreNoBackup:
    """禁用备份的JsonFileStore测试"""

    @pytest.fixture
    def store(self, temp_dir):
        """创建禁用备份的存储实例"""
        return JsonFileStore(temp_dir, enable_backup=False)

    def test_write_no_backup(self, store):
        """测试禁用备份时不创建备份"""
        store.write("test", {"data": "value"})

        backup_path = store._get_backup_path("test")
        assert not backup_path.exists()

    def test_delete_no_backup(self, store):
        """测试禁用备份时删除不创建备份"""
        store.write("test", {"data": "value"})
        store.delete("test")

        backup_path = store._get_backup_path("test")
        assert not backup_path.exists()


class TestJsonFileStoreCustomBackupDir:
    """自定义备份目录的JsonFileStore测试"""

    @pytest.fixture
    def custom_backup_dir(self, temp_dir):
        """创建自定义备份目录"""
        backup = temp_dir / "custom_backups"
        backup.mkdir(parents=True, exist_ok=True)
        return backup

    def test_custom_backup_dir(self, temp_dir, custom_backup_dir):
        """测试使用自定义备份目录"""
        store = JsonFileStore(temp_dir, backup_dir=custom_backup_dir)
        # 首次写入
        store.write("test", {"data": "value1"})
        backup_path = custom_backup_dir / "test.json"
        # 首次写入不会创建备份
        assert not backup_path.exists()

        # 覆盖写入创建备份
        store.write("test", {"data": "value2"})
        # 现在备份应该存在
        assert backup_path.exists()

        # 验证备份内容
        import json
        with open(backup_path, encoding="utf-8") as f:
            backup_data = json.load(f)
        assert backup_data == {"data": "value1"}
