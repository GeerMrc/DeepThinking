"""
思考会话模型单元测试
"""

import pytest
from pydantic import ValidationError

from deep_thinking.models.thinking_session import (
    SessionCreate,
    SessionStatistics,
    SessionUpdate,
    ThinkingSession,
)
from deep_thinking.models.thought import Thought
from deep_thinking.models.tool_call import (
    ToolCallData,
    ToolCallRecord,
    ToolResultData,
)


class TestThinkingSession:
    """ThinkingSession模型测试"""

    def test_create_session_with_defaults(self):
        """测试使用默认值创建会话"""
        session = ThinkingSession(name="测试会话")
        assert session.name == "测试会话"
        assert session.description == ""
        assert session.status == "active"
        assert session.is_active() is True
        assert session.thoughts == []
        assert session.metadata == {}
        assert isinstance(session.session_id, str)
        assert len(session.session_id) > 0

    def test_create_session_full(self):
        """测试创建完整会话"""
        session_id = "550e8400-e29b-41d4-a716-446655440000"
        session = ThinkingSession(
            session_id=session_id,
            name="完整会话",
            description="这是一个完整的会话",
            status="completed",
            metadata={"key": "value"},
        )
        assert session.session_id == session_id
        assert session.name == "完整会话"
        assert session.description == "这是一个完整的会话"
        assert session.status == "completed"
        assert session.is_completed() is True
        assert session.metadata == {"key": "value"}

    def test_name_validation(self):
        """测试名称验证"""
        # 空名称
        with pytest.raises(ValidationError):
            ThinkingSession(name="")

        # 只有空格的名称
        with pytest.raises(ValidationError):
            ThinkingSession(name="   ")

        # 名称应该被strip
        session = ThinkingSession(name="  测试会话  ")
        assert session.name == "测试会话"

    def test_name_length_validation(self):
        """测试名称长度验证"""
        with pytest.raises(ValidationError):
            ThinkingSession(name="x" * 101)  # 超过100字符

    def test_description_length_validation(self):
        """测试描述长度验证"""
        with pytest.raises(ValidationError):
            ThinkingSession(
                name="会话",
                description="x" * 2001,  # 超过2000字符
            )

    def test_status_validation(self):
        """测试状态验证"""
        with pytest.raises(ValidationError):
            ThinkingSession(name="会话", status="invalid")

        # 有效状态
        for status in ["active", "completed", "archived"]:
            session = ThinkingSession(name="会话", status=status)
            assert session.status == status

    def test_session_id_validation(self):
        """测试会话ID验证（UUID格式）"""
        # 测试无效的UUID格式（36字符但内容无效）
        with pytest.raises(ValidationError):
            ThinkingSession(name="会话", session_id="12345678-1234-1234-1234-invalid-uuid")

    def test_add_thought(self):
        """测试添加思考步骤"""
        session = ThinkingSession(name="测试会话")
        thought = Thought(thought_number=1, content="第一个思考")

        session.add_thought(thought)

        assert session.thought_count() == 1
        assert session.thoughts[0].content == "第一个思考"

    def test_remove_thought(self):
        """测试移除思考步骤"""
        session = ThinkingSession(name="测试会话")
        thought1 = Thought(thought_number=1, content="思考1")
        thought2 = Thought(thought_number=2, content="思考2")

        session.add_thought(thought1)
        session.add_thought(thought2)

        assert session.thought_count() == 2

        # 移除存在的思考
        result = session.remove_thought(1)
        assert result is True
        assert session.thought_count() == 1

        # 移除不存在的思考
        result = session.remove_thought(999)
        assert result is False

    def test_get_thought(self):
        """测试获取思考步骤"""
        session = ThinkingSession(name="测试会话")
        thought1 = Thought(thought_number=1, content="思考1")
        thought2 = Thought(thought_number=2, content="思考2")

        session.add_thought(thought1)
        session.add_thought(thought2)

        # 获取存在的思考
        retrieved = session.get_thought(1)
        assert retrieved is not None
        assert retrieved.content == "思考1"

        # 获取不存在的思考
        retrieved = session.get_thought(999)
        assert retrieved is None

    def test_get_latest_thought(self):
        """测试获取最后一个思考步骤"""
        session = ThinkingSession(name="测试会话")

        # 空会话
        assert session.get_latest_thought() is None

        # 添加思考后
        thought1 = Thought(thought_number=1, content="思考1")
        thought2 = Thought(thought_number=2, content="思考2")
        session.add_thought(thought1)
        session.add_thought(thought2)

        latest = session.get_latest_thought()
        assert latest is not None
        assert latest.thought_number == 2
        assert latest.content == "思考2"

    def test_mark_completed(self):
        """测试标记会话为已完成"""
        session = ThinkingSession(name="测试会话")
        assert session.is_active() is True

        session.mark_completed()
        assert session.is_completed() is True
        assert session.status == "completed"

    def test_mark_archived(self):
        """测试标记会话为已归档"""
        session = ThinkingSession(name="测试会话")

        session.mark_archived()
        assert session.is_archived() is True
        assert session.status == "archived"

    def test_mark_active(self):
        """测试标记会话为活跃"""
        session = ThinkingSession(name="测试会话", status="completed")

        session.mark_active()
        assert session.is_active() is True

    def test_updated_at_changes(self):
        """测试updated_at随操作更新"""
        session = ThinkingSession(name="测试会话")
        original_time = session.updated_at

        # 等待一小段时间确保时间戳变化
        import time

        time.sleep(0.01)

        # 添加思考应该更新updated_at
        thought = Thought(thought_number=1, content="思考")
        session.add_thought(thought)

        assert session.updated_at > original_time

    def test_to_dict(self):
        """测试转换为字典"""
        session = ThinkingSession(
            name="测试会话",
            description="测试描述",
            status="active",
            metadata={"key": "value"},
        )
        thought = Thought(thought_number=1, content="思考")
        session.add_thought(thought)

        data = session.to_dict()

        assert data["name"] == "测试会话"
        assert data["description"] == "测试描述"
        assert data["status"] == "active"
        assert data["thought_count"] == 1
        assert "thoughts" in data
        assert len(data["thoughts"]) == 1
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)

    def test_get_summary(self):
        """测试获取会话摘要"""
        session = ThinkingSession(
            name="测试会话",
            description="测试描述",
        )
        thought1 = Thought(thought_number=1, content="思考1")
        thought2 = Thought(thought_number=2, content="思考2")
        session.add_thought(thought1)
        session.add_thought(thought2)

        summary = session.get_summary()

        assert summary["name"] == "测试会话"
        assert summary["thought_count"] == 2
        assert summary["latest_thought"] is not None
        assert summary["latest_thought"]["thought_number"] == 2


class TestSessionCreate:
    """SessionCreate模型测试"""

    def test_to_session(self):
        """测试转换为ThinkingSession"""
        create_data = SessionCreate(
            name="新会话",
            description="会话描述",
            metadata={"key": "value"},
        )
        session = create_data.to_session()

        assert isinstance(session, ThinkingSession)
        assert session.name == "新会话"
        assert session.description == "会话描述"
        assert session.metadata == {"key": "value"}

    def test_default_values(self):
        """测试默认值"""
        create_data = SessionCreate(name="会话")
        session = create_data.to_session()

        assert session.description == ""
        assert session.metadata == {}


class TestSessionUpdate:
    """SessionUpdate模型测试"""

    def test_update_name_only(self):
        """测试只更新名称"""
        update_data = SessionUpdate(name="新名称")
        assert update_data.name == "新名称"
        assert update_data.description is None

    def test_update_multiple_fields(self):
        """测试更新多个字段"""
        update_data = SessionUpdate(
            name="新名称",
            description="新描述",
            status="completed",
        )
        assert update_data.name == "新名称"
        assert update_data.description == "新描述"
        assert update_data.status == "completed"

    def test_invalid_status(self):
        """测试无效状态"""
        with pytest.raises(ValidationError):
            SessionUpdate(status="invalid")

    def test_all_fields_optional(self):
        """测试所有字段都是可选的"""
        update_data = SessionUpdate()
        assert update_data.name is None
        assert update_data.description is None
        assert update_data.status is None


class TestSessionStatistics:
    """SessionStatistics模型测试 (Interleaved Thinking)"""

    def test_create_statistics_with_defaults(self):
        """测试使用默认值创建统计信息"""
        stats = SessionStatistics()
        assert stats.total_thoughts == 0
        assert stats.total_tool_calls == 0
        assert stats.successful_tool_calls == 0
        assert stats.failed_tool_calls == 0
        assert stats.cached_tool_calls == 0
        assert stats.total_execution_time_ms == 0.0
        assert stats.avg_thought_length == 0.0
        assert stats.phase_distribution == {"thinking": 0, "tool_call": 0, "analysis": 0}

    def test_update_from_thoughts(self):
        """测试从思考步骤更新统计"""
        stats = SessionStatistics()
        thoughts = [
            Thought(thought_number=1, content="思考内容1"),
            Thought(thought_number=2, content="思考内容22"),
            Thought(thought_number=3, content="思考内容333"),
        ]

        stats.update_from_thoughts(thoughts)

        assert stats.total_thoughts == 3
        # 平均长度: (5 + 6 + 7) / 3 = 6
        assert stats.avg_thought_length == 6.0

    def test_update_from_thoughts_empty(self):
        """测试空思考列表更新统计"""
        stats = SessionStatistics()
        stats.update_from_thoughts([])
        assert stats.total_thoughts == 0
        assert stats.avg_thought_length == 0.0

    def test_update_from_tool_calls(self):
        """测试从工具调用记录更新统计"""
        stats = SessionStatistics()

        # 创建工具调用记录
        call_data1 = ToolCallData(tool_name="test", arguments={})
        record1 = ToolCallRecord(
            thought_number=1,
            call_data=call_data1,
            status="completed",
        )
        result1 = ToolResultData(
            call_id=call_data1.call_id,
            success=True,
            execution_time_ms=100.0,
        )
        record1.set_result(result1)

        call_data2 = ToolCallData(tool_name="test2", arguments={})
        record2 = ToolCallRecord(
            thought_number=2,
            call_data=call_data2,
            status="failed",
        )

        call_data3 = ToolCallData(tool_name="test3", arguments={})
        record3 = ToolCallRecord(
            thought_number=3,
            call_data=call_data3,
            status="completed",
        )
        result3 = ToolResultData(
            call_id=call_data3.call_id,
            success=True,
            execution_time_ms=50.0,
            from_cache=True,
        )
        record3.set_result(result3)

        tool_calls = [record1, record2, record3]
        stats.update_from_tool_calls(tool_calls)

        assert stats.total_tool_calls == 3
        assert stats.successful_tool_calls == 2
        assert stats.failed_tool_calls == 1
        assert stats.cached_tool_calls == 1
        assert stats.total_execution_time_ms == 150.0

    def test_statistics_to_dict(self):
        """测试统计信息转换为字典"""
        stats = SessionStatistics(
            total_thoughts=5,
            total_tool_calls=10,
            successful_tool_calls=8,
            failed_tool_calls=2,
        )
        data = stats.to_dict()

        assert data["total_thoughts"] == 5
        assert data["total_tool_calls"] == 10
        assert data["successful_tool_calls"] == 8
        assert data["failed_tool_calls"] == 2


class TestThinkingSessionInterleaved:
    """ThinkingSession Interleaved Thinking 功能测试"""

    def test_session_has_statistics_field(self):
        """测试会话包含统计字段"""
        session = ThinkingSession(name="测试会话")
        assert hasattr(session, "statistics")
        assert isinstance(session.statistics, SessionStatistics)

    def test_session_has_tool_call_history_field(self):
        """测试会话包含工具调用历史字段"""
        session = ThinkingSession(name="测试会话")
        assert hasattr(session, "tool_call_history")
        assert session.tool_call_history == []

    def test_add_tool_call_record(self):
        """测试添加工具调用记录"""
        session = ThinkingSession(name="测试会话")
        call_data = ToolCallData(tool_name="search", arguments={"query": "test"})
        record = ToolCallRecord(thought_number=1, call_data=call_data)

        session.add_tool_call_record(record)

        assert len(session.tool_call_history) == 1
        assert session.tool_call_history[0].call_data.tool_name == "search"

    def test_update_statistics(self):
        """测试更新统计信息"""
        session = ThinkingSession(name="测试会话")

        # 添加思考步骤
        thought = Thought(thought_number=1, content="测试思考内容")
        session.add_thought(thought)

        # 添加工具调用记录
        call_data = ToolCallData(tool_name="test", arguments={})
        record = ToolCallRecord(thought_number=1, call_data=call_data, status="completed")
        result = ToolResultData(call_id=call_data.call_id, success=True)
        record.set_result(result)
        session.add_tool_call_record(record)

        # 更新统计
        session.update_statistics()

        assert session.statistics.total_thoughts == 1
        assert session.statistics.total_tool_calls == 1
        assert session.statistics.successful_tool_calls == 1

    def test_to_dict_includes_statistics_and_tool_calls(self):
        """测试to_dict包含统计和工具调用"""
        session = ThinkingSession(name="测试会话")
        thought = Thought(thought_number=1, content="测试")
        session.add_thought(thought)

        call_data = ToolCallData(tool_name="test", arguments={})
        record = ToolCallRecord(thought_number=1, call_data=call_data)
        session.add_tool_call_record(record)

        data = session.to_dict()

        assert "statistics" in data
        assert "tool_call_history" in data
        assert len(data["tool_call_history"]) == 1

    def test_get_summary_includes_statistics(self):
        """测试get_summary包含统计信息"""
        session = ThinkingSession(name="测试会话")
        thought = Thought(thought_number=1, content="测试")
        session.add_thought(thought)

        summary = session.get_summary()

        assert "statistics" in summary
        assert "tool_call_count" in summary
        assert summary["tool_call_count"] == 0
