"""
存储管理器单元测试
"""

from pathlib import Path

import pytest

from deep_thinking.models.thought import Thought
from deep_thinking.storage.storage_manager import StorageManager


class TestStorageManager:
    """StorageManager测试"""

    @pytest.fixture
    def manager(self, temp_dir):
        """创建存储管理器实例"""
        return StorageManager(temp_dir)

    def test_init_creates_directories(self, manager):
        """测试初始化创建目录"""
        assert manager.sessions_dir.exists()
        assert manager.index_path.exists()

    def test_init_creates_index(self, manager):
        """测试初始化创建索引"""
        index = manager._read_index()
        assert index == {}

    def test_create_session(self, manager):
        """测试创建会话"""
        session = manager.create_session(
            name="测试会话",
            description="测试描述",
            metadata={"key": "value"},
        )

        assert session.name == "测试会话"
        assert session.description == "测试描述"
        assert session.metadata == {"key": "value"}
        assert isinstance(session.session_id, str)

    def test_get_session(self, manager):
        """测试获取会话"""
        created = manager.create_session(name="测试会话")
        retrieved = manager.get_session(created.session_id)

        assert retrieved is not None
        assert retrieved.session_id == created.session_id
        assert retrieved.name == "测试会话"

    def test_get_nonexistent_session(self, manager):
        """测试获取不存在的会话"""
        result = manager.get_session("nonexistent-id")
        assert result is None

    def test_update_session(self, manager):
        """测试更新会话"""
        session = manager.create_session(name="原始名称")
        session.name = "更新名称"
        session.mark_completed()

        result = manager.update_session(session)

        assert result is True
        updated = manager.get_session(session.session_id)
        assert updated.name == "更新名称"
        assert updated.is_completed()

    def test_update_nonexistent_session(self, manager):
        """测试更新不存在的会话"""
        from deep_thinking.models.thinking_session import ThinkingSession

        session = ThinkingSession(name="测试")
        result = manager.update_session(session)

        assert result is False

    def test_delete_session(self, manager):
        """测试删除会话"""
        session = manager.create_session(name="测试会话")
        result = manager.delete_session(session.session_id)

        assert result is True
        assert manager.get_session(session.session_id) is None

    def test_delete_nonexistent_session(self, manager):
        """测试删除不存在的会话"""
        result = manager.delete_session("nonexistent-id")
        assert result is False

    def test_list_sessions_all(self, manager):
        """测试列出所有会话"""
        manager.create_session(name="会话1")
        manager.create_session(name="会话2")
        manager.create_session(name="会话3")

        sessions = manager.list_sessions()
        assert len(sessions) == 3

        names = [s["name"] for s in sessions]
        assert "会话1" in names
        assert "会话2" in names
        assert "会话3" in names

    def test_list_sessions_with_status_filter(self, manager):
        """测试按状态过滤会话"""
        manager.create_session(name="活跃会话")
        session2 = manager.create_session(name="已完成会话")
        session2.mark_completed()
        manager.update_session(session2)

        active_sessions = manager.list_sessions(status="active")
        completed_sessions = manager.list_sessions(status="completed")

        assert len(active_sessions) == 1
        assert len(completed_sessions) == 1
        assert active_sessions[0]["name"] == "活跃会话"
        assert completed_sessions[0]["name"] == "已完成会话"

    def test_list_sessions_with_limit(self, manager):
        """测试限制返回数量"""
        for i in range(5):
            manager.create_session(name=f"会话{i}")

        sessions = manager.list_sessions(limit=3)
        assert len(sessions) == 3

    def test_list_sessions_sorted_by_updated_at(self, manager):
        """测试按更新时间排序"""
        manager.create_session(name="会话1")
        session2 = manager.create_session(name="会话2")

        # 更新session2使其更新时间更新
        session2.name = "更新会话2"
        manager.update_session(session2)

        sessions = manager.list_sessions()
        # 会话2应该在前面（更新时间更晚）
        assert sessions[0]["name"] == "更新会话2"
        assert sessions[1]["name"] == "会话1"

    def test_add_thought(self, manager):
        """测试添加思考步骤"""
        session = manager.create_session(name="测试会话")
        thought = Thought(thought_number=1, content="第一个思考")

        result = manager.add_thought(session.session_id, thought)

        assert result is True
        updated_session = manager.get_session(session.session_id)
        assert updated_session.thought_count() == 1
        assert updated_session.thoughts[0].content == "第一个思考"

    def test_add_thought_to_nonexistent_session(self, manager):
        """测试向不存在的会话添加思考"""
        thought = Thought(thought_number=1, content="思考")
        result = manager.add_thought("nonexistent-id", thought)
        assert result is False

    def test_get_latest_thought(self, manager):
        """测试获取最后一个思考步骤"""
        session = manager.create_session(name="测试会话")
        thought1 = Thought(thought_number=1, content="思考1")
        thought2 = Thought(thought_number=2, content="思考2")

        manager.add_thought(session.session_id, thought1)
        manager.add_thought(session.session_id, thought2)

        latest = manager.get_latest_thought(session.session_id)
        assert latest is not None
        assert latest.thought_number == 2
        assert latest.content == "思考2"

    def test_get_latest_thought_from_empty_session(self, manager):
        """测试从空会话获取最后思考"""
        session = manager.create_session(name="空会话")
        latest = manager.get_latest_thought(session.session_id)
        assert latest is None

    def test_create_backup(self, manager):
        """测试创建备份"""
        manager.create_session(name="会话1")
        manager.create_session(name="会话2")

        backup_path = manager.create_backup()
        assert backup_path is not None

        from pathlib import Path

        backup_dir = Path(backup_path)
        assert backup_dir.exists()
        assert (backup_dir / "sessions").exists()

    def test_restore_backup(self, manager):
        """测试恢复备份"""
        # 创建会话
        session = manager.create_session(name="原始会话")
        session_id = session.session_id

        # 创建备份
        backup_name = manager.create_backup()
        assert backup_name is not None
        backup_name = Path(backup_name).name

        # 删除会话
        manager.delete_session(session_id)
        assert manager.get_session(session_id) is None

        # 恢复备份
        result = manager.restore_backup(backup_name)
        assert result is True

        # 验证恢复
        restored = manager.get_session(session_id)
        assert restored is not None
        assert restored.name == "原始会话"

    def test_restore_nonexistent_backup(self, manager):
        """测试恢复不存在的备份"""
        result = manager.restore_backup("nonexistent-backup")
        assert result is False

    def test_list_backups(self, manager):
        """测试列出备份"""
        manager.create_session(name="会话1")
        manager.create_backup("backup1")

        backups = manager.list_backups()
        assert len(backups) >= 1

        # 检查第一个备份
        backup = backups[0]
        assert "name" in backup
        assert "created_at" in backup

    def test_get_stats(self, manager):
        """测试获取统计信息"""
        # 创建不同状态的会话
        session1 = manager.create_session(name="活跃")
        session2 = manager.create_session(name="已完成")
        session2.mark_completed()
        manager.update_session(session2)

        # 添加思考步骤
        thought = Thought(thought_number=1, content="思考")
        manager.add_thought(session1.session_id, thought)

        stats = manager.get_stats()
        assert stats["total_sessions"] == 2
        assert stats["status_counts"]["active"] == 1
        assert stats["status_counts"]["completed"] == 1
        assert stats["total_thoughts"] == 1
        assert "data_dir" in stats

    def test_persist_thoughts_across_sessions(self, manager):
        """测试思考步骤持久化"""
        session = manager.create_session(name="测试会话")

        # 添加多个思考
        for i in range(3):
            thought = Thought(thought_number=i + 1, content=f"思考{i + 1}")
            manager.add_thought(session.session_id, thought)

        # 重新加载会话
        reloaded = manager.get_session(session.session_id)

        assert reloaded.thought_count() == 3
        assert reloaded.thoughts[0].content == "思考1"
        assert reloaded.thoughts[1].content == "思考2"
        assert reloaded.thoughts[2].content == "思考3"

    def test_session_metadata_persistence(self, manager):
        """测试元数据持久化"""
        metadata = {"author": "user", "tags": ["test", "demo"]}
        session = manager.create_session(name="测试会话", metadata=metadata)

        # 重新加载
        reloaded = manager.get_session(session.session_id)
        assert reloaded.metadata == metadata

    def test_index_updated_on_operations(self, manager):
        """测试索引在操作时更新"""
        # 创建会话
        session = manager.create_session(name="测试会话")
        index = manager._read_index()
        assert session.session_id in index

        # 更新会话
        session.name = "新名称"
        manager.update_session(session)
        index = manager._read_index()
        assert index[session.session_id]["name"] == "新名称"

        # 删除会话
        manager.delete_session(session.session_id)
        index = manager._read_index()
        assert session.session_id not in index

    # =============================================================================
    # Interleaved Thinking 新字段持久化测试 (Phase 4.1/4.2/4.3/4.4)
    # =============================================================================

    def test_thought_phase_persistence(self, manager):
        """测试 Thought 的 phase 字段持久化 (Phase 4.1)"""
        from deep_thinking.models.thought import Thought

        session = manager.create_session(name="测试会话")

        # 添加带有 phase 字段的思考步骤
        thought = Thought(
            thought_number=1,
            content="工具调用阶段",
            phase="tool_call",
        )
        manager.add_thought(session.session_id, thought)

        # 重新加载
        reloaded = manager.get_session(session.session_id)
        assert reloaded is not None
        assert reloaded.thoughts[0].phase == "tool_call"

    def test_thought_tool_calls_persistence(self, manager):
        """测试 Thought 的 tool_calls 字段持久化 (Phase 4.1)"""
        from deep_thinking.models.thought import Thought

        session = manager.create_session(name="测试会话")

        # 添加带有 tool_calls 字段的思考步骤
        thought = Thought(
            thought_number=1,
            content="带有工具调用的思考",
            tool_calls=["record-id-1", "record-id-2"],
        )
        manager.add_thought(session.session_id, thought)

        # 重新加载
        reloaded = manager.get_session(session.session_id)
        assert reloaded is not None
        assert reloaded.thoughts[0].tool_calls == ["record-id-1", "record-id-2"]

    def test_thought_backward_compatibility(self, manager):
        """测试 Thought 向后兼容性 - 旧格式数据 (Phase 4.1)"""
        from deep_thinking.models.thought import Thought

        session = manager.create_session(name="测试会话")

        # 添加旧格式的思考步骤（没有 phase 和 tool_calls）
        thought = Thought(
            thought_number=1,
            content="旧格式思考",
        )
        manager.add_thought(session.session_id, thought)

        # 重新加载
        reloaded = manager.get_session(session.session_id)
        assert reloaded is not None
        # 验证默认值
        assert reloaded.thoughts[0].phase == "thinking"
        assert reloaded.thoughts[0].tool_calls == []

    def test_session_statistics_persistence(self, manager):
        """测试 ThinkingSession 的 statistics 字段持久化 (Phase 4.2/4.4)"""
        session = manager.create_session(name="测试会话")

        # 更新统计信息
        session.statistics.total_thoughts = 5
        session.statistics.total_tool_calls = 3
        session.statistics.successful_tool_calls = 2
        session.statistics.failed_tool_calls = 1
        manager.update_session(session)

        # 重新加载
        reloaded = manager.get_session(session.session_id)
        assert reloaded is not None
        assert reloaded.statistics.total_thoughts == 5
        assert reloaded.statistics.total_tool_calls == 3
        assert reloaded.statistics.successful_tool_calls == 2
        assert reloaded.statistics.failed_tool_calls == 1

    def test_session_tool_call_history_persistence(self, manager):
        """测试 ThinkingSession 的 tool_call_history 字段持久化 (Phase 4.3)"""
        from deep_thinking.models.tool_call import ToolCallData, ToolCallRecord

        session = manager.create_session(name="测试会话")

        # 添加工具调用记录
        record = ToolCallRecord(
            thought_number=1,
            call_data=ToolCallData(
                tool_name="search",
                arguments={"query": "test"},
            ),
            status="completed",
        )
        session.tool_call_history.append(record)
        manager.update_session(session)

        # 重新加载
        reloaded = manager.get_session(session.session_id)
        assert reloaded is not None
        assert len(reloaded.tool_call_history) == 1

        # 验证嵌套模型正确反序列化
        reloaded_record = reloaded.tool_call_history[0]
        assert reloaded_record.call_data.tool_name == "search"
        assert reloaded_record.call_data.arguments == {"query": "test"}
        assert reloaded_record.status == "completed"

    def test_session_backward_compatibility(self, manager):
        """测试 ThinkingSession 向后兼容性 - 旧格式数据 (Phase 4.2)"""
        session = manager.create_session(name="测试会话")

        # 旧格式会话不包含 statistics 和 tool_call_history
        reloaded = manager.get_session(session.session_id)
        assert reloaded is not None
        # 验证默认值
        assert reloaded.statistics.total_thoughts == 0
        assert reloaded.statistics.total_tool_calls == 0
        assert reloaded.tool_call_history == []

    def test_complex_nested_persistence(self, manager):
        """测试复杂嵌套结构持久化 (Phase 4.3/4.4)"""
        from deep_thinking.models.thought import Thought
        from deep_thinking.models.tool_call import (
            ToolCallData,
            ToolCallError,
            ToolCallRecord,
            ToolResultData,
        )

        session = manager.create_session(name="复杂测试会话")

        # 添加带有新字段的思考步骤
        thought = Thought(
            thought_number=1,
            content="分析阶段",
            phase="analysis",
            tool_calls=["rec-1"],
        )
        manager.add_thought(session.session_id, thought)

        # 重新获取会话并添加复杂的工具调用记录
        session = manager.get_session(session.session_id)
        assert session is not None

        # 添加带有错误信息的工具调用记录
        record = ToolCallRecord(
            thought_number=1,
            call_data=ToolCallData(tool_name="failing_tool", arguments={"x": 1}),
            result_data=ToolResultData(
                call_id="call-1",
                success=False,
                error=ToolCallError(
                    error_type="ValueError",
                    error_message="Invalid input",
                    error_code="E001",
                ),
                execution_time_ms=150.5,
            ),
            status="failed",
        )
        session.tool_call_history.append(record)
        session.statistics.update_from_tool_calls(session.tool_call_history)
        manager.update_session(session)

        # 重新加载并验证
        reloaded = manager.get_session(session.session_id)
        assert reloaded is not None

        # 验证 Thought
        assert reloaded.thoughts[0].phase == "analysis"
        assert reloaded.thoughts[0].tool_calls == ["rec-1"]

        # 验证 ToolCallRecord
        assert len(reloaded.tool_call_history) == 1
        rec = reloaded.tool_call_history[0]
        assert rec.call_data.tool_name == "failing_tool"
        assert rec.result_data is not None
        assert rec.result_data.success is False
        assert rec.result_data.error is not None
        assert rec.result_data.error.error_type == "ValueError"
        assert rec.result_data.execution_time_ms == 150.5

        # 验证 Statistics
        assert reloaded.statistics.total_tool_calls == 1
        assert reloaded.statistics.failed_tool_calls == 1
