"""
工具调用数据模型单元测试 (Interleaved Thinking)
"""

import pytest
from pydantic import ValidationError

from deep_thinking.models.tool_call import (
    ToolCallData,
    ToolCallError,
    ToolCallRecord,
    ToolResultData,
)


class TestToolCallData:
    """ToolCallData模型测试"""

    def test_create_tool_call_data_valid(self):
        """测试创建有效的工具调用数据"""
        call_data = ToolCallData(
            tool_name="search",
            arguments={"query": "test"},
        )
        assert call_data.tool_name == "search"
        assert call_data.arguments == {"query": "test"}
        assert call_data.call_id is not None
        assert call_data.timestamp is not None

    def test_tool_call_data_with_custom_call_id(self):
        """测试自定义调用ID"""
        call_data = ToolCallData(
            call_id="custom-id-123",
            tool_name="read",
            arguments={"path": "/test"},
        )
        assert call_data.call_id == "custom-id-123"

    def test_tool_call_data_empty_arguments(self):
        """测试空参数"""
        call_data = ToolCallData(tool_name="noop")
        assert call_data.arguments == {}

    def test_tool_call_data_tool_name_required(self):
        """测试工具名称必填"""
        with pytest.raises(ValidationError):
            ToolCallData()

    def test_tool_call_data_tool_name_validation(self):
        """测试工具名称验证"""
        # 空名称
        with pytest.raises(ValidationError):
            ToolCallData(tool_name="")

        # 名称过长
        with pytest.raises(ValidationError):
            ToolCallData(tool_name="x" * 101)

    def test_tool_call_data_to_dict(self):
        """测试转换为字典"""
        call_data = ToolCallData(
            call_id="test-id",
            tool_name="search",
            arguments={"query": "test"},
        )
        data = call_data.to_dict()

        assert data["call_id"] == "test-id"
        assert data["tool_name"] == "search"
        assert data["arguments"] == {"query": "test"}
        assert isinstance(data["timestamp"], str)


class TestToolCallError:
    """ToolCallError模型测试"""

    def test_create_tool_call_error_valid(self):
        """测试创建有效的工具调用错误"""
        error = ToolCallError(
            error_type="ValueError",
            error_message="Invalid input",
        )
        assert error.error_type == "ValueError"
        assert error.error_message == "Invalid input"
        assert error.error_code is None
        assert error.stack_trace is None

    def test_tool_call_error_with_all_fields(self):
        """测试包含所有字段的错误"""
        error = ToolCallError(
            error_type="RuntimeError",
            error_message="Execution failed",
            error_code="E001",
            stack_trace="line 1\nline 2",
        )
        assert error.error_code == "E001"
        assert error.stack_trace == "line 1\nline 2"

    def test_tool_call_error_required_fields(self):
        """测试必填字段"""
        with pytest.raises(ValidationError):
            ToolCallError()

        with pytest.raises(ValidationError):
            ToolCallError(error_type="Error")

    def test_tool_call_error_length_validation(self):
        """测试长度验证"""
        # 错误类型过长
        with pytest.raises(ValidationError):
            ToolCallError(
                error_type="x" * 101,
                error_message="msg",
            )

        # 错误消息过长
        with pytest.raises(ValidationError):
            ToolCallError(
                error_type="Error",
                error_message="x" * 5001,
            )

    def test_tool_call_error_to_dict(self):
        """测试转换为字典"""
        error = ToolCallError(
            error_type="ValueError",
            error_message="Invalid input",
            error_code="E001",
        )
        data = error.to_dict()

        assert data["error_type"] == "ValueError"
        assert data["error_message"] == "Invalid input"
        assert data["error_code"] == "E001"
        assert data["stack_trace"] is None


class TestToolResultData:
    """ToolResultData模型测试"""

    def test_create_tool_result_success(self):
        """测试创建成功的结果"""
        result = ToolResultData(
            call_id="call-123",
            success=True,
            result={"data": "value"},
        )
        assert result.call_id == "call-123"
        assert result.success is True
        assert result.result == {"data": "value"}
        assert result.error is None
        assert result.from_cache is False

    def test_create_tool_result_with_error(self):
        """测试创建带错误的结果"""
        error = ToolCallError(
            error_type="ValueError",
            error_message="Invalid input",
        )
        result = ToolResultData(
            call_id="call-123",
            success=False,
            error=error,
        )
        assert result.success is False
        assert result.error is not None
        assert result.error.error_type == "ValueError"

    def test_tool_result_with_execution_time(self):
        """测试包含执行时间的结果"""
        result = ToolResultData(
            call_id="call-123",
            success=True,
            execution_time_ms=150.5,
        )
        assert result.execution_time_ms == 150.5

    def test_tool_result_from_cache(self):
        """测试缓存结果标记"""
        result = ToolResultData(
            call_id="call-123",
            success=True,
            from_cache=True,
        )
        assert result.from_cache is True

    def test_tool_result_call_id_required(self):
        """测试调用ID必填"""
        with pytest.raises(ValidationError):
            ToolResultData()

    def test_tool_result_execution_time_validation(self):
        """测试执行时间验证"""
        # 负数执行时间
        with pytest.raises(ValidationError):
            ToolResultData(
                call_id="call-123",
                execution_time_ms=-1,
            )

    def test_tool_result_to_dict(self):
        """测试转换为字典"""
        error = ToolCallError(
            error_type="Error",
            error_message="msg",
        )
        result = ToolResultData(
            call_id="call-123",
            success=False,
            error=error,
            execution_time_ms=100.0,
            from_cache=True,
        )
        data = result.to_dict()

        assert data["call_id"] == "call-123"
        assert data["success"] is False
        assert data["error"] is not None
        assert data["execution_time_ms"] == 100.0
        assert data["from_cache"] is True
        assert isinstance(data["timestamp"], str)


class TestToolCallRecord:
    """ToolCallRecord模型测试"""

    def test_create_tool_call_record_valid(self):
        """测试创建有效的工具调用记录"""
        call_data = ToolCallData(
            tool_name="search",
            arguments={"query": "test"},
        )
        record = ToolCallRecord(
            thought_number=1,
            call_data=call_data,
        )
        assert record.thought_number == 1
        assert record.call_data.tool_name == "search"
        assert record.status == "pending"
        assert record.result_data is None
        assert record.record_id is not None

    def test_tool_call_record_set_result(self):
        """测试设置结果"""
        call_data = ToolCallData(tool_name="search", arguments={})
        record = ToolCallRecord(
            thought_number=1,
            call_data=call_data,
        )

        result = ToolResultData(
            call_id=record.call_data.call_id,
            success=True,
            result={"data": "value"},
        )
        record.set_result(result)

        assert record.status == "completed"
        assert record.result_data is not None
        assert record.result_data.success is True

    def test_tool_call_record_set_failed_result(self):
        """测试设置失败结果"""
        call_data = ToolCallData(tool_name="search", arguments={})
        record = ToolCallRecord(
            thought_number=1,
            call_data=call_data,
        )

        error = ToolCallError(
            error_type="TimeoutError",
            error_message="Request timed out",
        )
        result = ToolResultData(
            call_id=record.call_data.call_id,
            success=False,
            error=error,
        )
        record.set_result(result, status="failed")

        assert record.status == "failed"
        assert record.result_data.success is False

    def test_tool_call_record_is_completed(self):
        """测试判断是否完成"""
        call_data = ToolCallData(tool_name="test", arguments={})
        record = ToolCallRecord(thought_number=1, call_data=call_data)

        # pending状态
        assert record.is_completed() is False

        # completed状态
        record.status = "completed"
        assert record.is_completed() is True

        # failed状态
        record.status = "failed"
        assert record.is_completed() is True

        # timeout状态
        record.status = "timeout"
        assert record.is_completed() is True

    def test_tool_call_record_is_successful(self):
        """测试判断是否成功"""
        call_data = ToolCallData(tool_name="test", arguments={})
        record = ToolCallRecord(thought_number=1, call_data=call_data)

        # 无结果时
        assert record.is_successful() is False

        # 有成功结果
        result = ToolResultData(
            call_id=record.call_data.call_id,
            success=True,
        )
        record.set_result(result)
        assert record.is_successful() is True

        # 有失败结果
        result_failed = ToolResultData(
            call_id=record.call_data.call_id,
            success=False,
        )
        record.set_result(result_failed, status="failed")
        assert record.is_successful() is False

    def test_tool_call_record_status_validation(self):
        """测试状态验证"""
        call_data = ToolCallData(tool_name="test", arguments={})

        # 有效状态
        for status in ["pending", "running", "completed", "failed", "timeout", "cancelled"]:
            record = ToolCallRecord(
                thought_number=1,
                call_data=call_data,
                status=status,
            )
            assert record.status == status

        # 无效状态
        with pytest.raises(ValidationError):
            ToolCallRecord(
                thought_number=1,
                call_data=call_data,
                status="invalid_status",
            )

    def test_tool_call_record_thought_number_validation(self):
        """测试思考编号验证"""
        call_data = ToolCallData(tool_name="test", arguments={})

        # 有效编号
        record = ToolCallRecord(thought_number=1, call_data=call_data)
        assert record.thought_number == 1

        # 无效编号
        with pytest.raises(ValidationError):
            ToolCallRecord(thought_number=0, call_data=call_data)

        with pytest.raises(ValidationError):
            ToolCallRecord(thought_number=-1, call_data=call_data)

    def test_tool_call_record_to_dict(self):
        """测试转换为字典"""
        call_data = ToolCallData(
            call_id="call-123",
            tool_name="search",
            arguments={"query": "test"},
        )
        result = ToolResultData(
            call_id="call-123",
            success=True,
            result={"items": []},
        )
        record = ToolCallRecord(
            record_id="record-123",
            thought_number=5,
            call_data=call_data,
            status="completed",
        )
        record.set_result(result)

        data = record.to_dict()

        assert data["record_id"] == "record-123"
        assert data["thought_number"] == 5
        assert data["call_data"]["call_id"] == "call-123"
        assert data["status"] == "completed"
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
