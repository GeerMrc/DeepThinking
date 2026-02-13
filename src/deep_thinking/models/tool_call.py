"""
工具调用数据模型 (Interleaved Thinking)

定义工具调用相关的数据结构和验证规则。
用于追踪和管理思考过程中的工具调用。
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ToolCallData(BaseModel):
    """
    工具调用数据模型

    表示一个工具调用的请求数据。

    Attributes:
        call_id: 调用唯一标识符
        tool_name: 工具名称
        arguments: 工具调用参数
        timestamp: 调用时间戳
    """

    call_id: str = Field(
        default_factory=lambda: str(uuid4()),
        min_length=1,
        description="调用唯一标识符",
    )

    tool_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="工具名称",
    )

    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="工具调用参数",
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="调用时间戳",
    )

    def to_dict(self) -> dict[str, Any]:
        """
        转换为字典格式

        Returns:
            包含所有字段的字典，timestamp转为ISO格式字符串
        """
        return {
            "call_id": self.call_id,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "timestamp": self.timestamp.isoformat(),
        }


class ToolCallError(BaseModel):
    """
    工具调用错误模型

    表示工具调用过程中的错误信息。

    Attributes:
        error_type: 错误类型
        error_message: 错误消息
        error_code: 错误代码（可选）
        stack_trace: 堆栈跟踪（可选）
    """

    error_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="错误类型",
    )

    error_message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="错误消息",
    )

    error_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="错误代码",
    )

    stack_trace: str | None = Field(
        default=None,
        max_length=10000,
        description="堆栈跟踪",
    )

    def to_dict(self) -> dict[str, Any]:
        """
        转换为字典格式

        Returns:
            包含所有字段的字典
        """
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "stack_trace": self.stack_trace,
        }


class ToolResultData(BaseModel):
    """
    工具调用结果模型

    表示工具调用的返回结果。

    Attributes:
        call_id: 对应的调用ID
        success: 是否成功
        result: 返回结果（成功时）
        error: 错误信息（失败时）
        execution_time_ms: 执行时间（毫秒）
        timestamp: 结果时间戳
        from_cache: 是否来自缓存
    """

    call_id: str = Field(
        ...,
        min_length=1,
        description="对应的调用ID",
    )

    success: bool = Field(
        default=True,
        description="是否成功",
    )

    result: Any = Field(
        default=None,
        description="返回结果",
    )

    error: ToolCallError | None = Field(
        default=None,
        description="错误信息",
    )

    execution_time_ms: float | None = Field(
        default=None,
        ge=0,
        description="执行时间（毫秒）",
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="结果时间戳",
    )

    from_cache: bool = Field(
        default=False,
        description="是否来自缓存",
    )

    def to_dict(self) -> dict[str, Any]:
        """
        转换为字典格式

        Returns:
            包含所有字段的字典
        """
        return {
            "call_id": self.call_id,
            "success": self.success,
            "result": self.result,
            "error": self.error.to_dict() if self.error else None,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "from_cache": self.from_cache,
        }


class ToolCallRecord(BaseModel):
    """
    工具调用记录模型

    表示完整的工具调用记录，包含调用请求和结果。

    Attributes:
        record_id: 记录唯一标识符
        thought_number: 关联的思考步骤编号
        call_data: 调用数据
        result_data: 结果数据（可选，异步调用时可能为空）
        status: 调用状态（pending/completed/failed/timeout）
        created_at: 创建时间
        updated_at: 更新时间
    """

    record_id: str = Field(
        default_factory=lambda: str(uuid4()),
        min_length=1,
        description="记录唯一标识符",
    )

    thought_number: int = Field(
        ...,
        ge=1,
        description="关联的思考步骤编号",
    )

    call_data: ToolCallData = Field(
        ...,
        description="调用数据",
    )

    result_data: ToolResultData | None = Field(
        default=None,
        description="结果数据",
    )

    status: str = Field(
        default="pending",
        pattern="^(pending|running|completed|failed|timeout|cancelled)$",
        description="调用状态",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="创建时间",
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="更新时间",
    )

    def is_completed(self) -> bool:
        """判断调用是否已完成（成功或失败）"""
        return self.status in ("completed", "failed", "timeout", "cancelled")

    def is_successful(self) -> bool:
        """判断调用是否成功"""
        return self.status == "completed" and (
            self.result_data is not None and self.result_data.success
        )

    def set_result(self, result: ToolResultData, status: str = "completed") -> None:
        """
        设置调用结果

        Args:
            result: 结果数据
            status: 状态（默认completed）
        """
        self.result_data = result
        self.status = status
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """
        转换为字典格式

        Returns:
            包含所有字段的字典
        """
        return {
            "record_id": self.record_id,
            "thought_number": self.thought_number,
            "call_data": self.call_data.to_dict(),
            "result_data": self.result_data.to_dict() if self.result_data else None,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


__all__ = [
    "ToolCallData",
    "ToolCallError",
    "ToolResultData",
    "ToolCallRecord",
]
