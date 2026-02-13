"""
思考会话模型

定义思考会话的数据结构和验证规则。
一个会话包含多个思考步骤，支持会话状态管理和元数据。
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from deep_thinking.models.thought import Thought
from deep_thinking.models.tool_call import ToolCallRecord


class SessionStatistics(BaseModel):
    """
    会话统计信息模型 (Interleaved Thinking)

    记录会话的统计数据，包括思考步骤、工具调用等。

    Attributes:
        total_thoughts: 总思考步骤数
        total_tool_calls: 总工具调用次数
        successful_tool_calls: 成功的工具调用次数
        failed_tool_calls: 失败的工具调用次数
        cached_tool_calls: 缓存命中的工具调用次数
        total_execution_time_ms: 总执行时间（毫秒）
        avg_thought_length: 平均思考内容长度
        phase_distribution: 各阶段分布（thinking/tool_call/analysis的数量）
    """

    total_thoughts: int = Field(
        default=0,
        ge=0,
        description="总思考步骤数",
    )

    total_tool_calls: int = Field(
        default=0,
        ge=0,
        description="总工具调用次数",
    )

    successful_tool_calls: int = Field(
        default=0,
        ge=0,
        description="成功的工具调用次数",
    )

    failed_tool_calls: int = Field(
        default=0,
        ge=0,
        description="失败的工具调用次数",
    )

    cached_tool_calls: int = Field(
        default=0,
        ge=0,
        description="缓存命中的工具调用次数",
    )

    total_execution_time_ms: float = Field(
        default=0.0,
        ge=0,
        description="总执行时间（毫秒）",
    )

    avg_thought_length: float = Field(
        default=0.0,
        ge=0,
        description="平均思考内容长度",
    )

    phase_distribution: dict[str, int] = Field(
        default_factory=lambda: {"thinking": 0, "tool_call": 0, "analysis": 0},
        description="各阶段分布",
    )

    def update_from_thoughts(self, thoughts: list[Thought]) -> None:
        """
        根据思考步骤更新统计信息

        Args:
            thoughts: 思考步骤列表
        """
        self.total_thoughts = len(thoughts)
        if thoughts:
            total_length = sum(len(t.content) for t in thoughts)
            self.avg_thought_length = total_length / len(thoughts)
        else:
            self.avg_thought_length = 0.0

    def update_from_tool_calls(self, tool_call_history: list[ToolCallRecord]) -> None:
        """
        根据工具调用记录更新统计信息

        Args:
            tool_call_history: 工具调用记录列表
        """
        self.total_tool_calls = len(tool_call_history)
        self.successful_tool_calls = sum(1 for r in tool_call_history if r.is_successful())
        self.failed_tool_calls = sum(
            1 for r in tool_call_history if r.status in ("failed", "timeout")
        )
        self.cached_tool_calls = sum(
            1 for r in tool_call_history if r.result_data and r.result_data.from_cache
        )

        total_time = 0.0
        for record in tool_call_history:
            if record.result_data and record.result_data.execution_time_ms:
                total_time += record.result_data.execution_time_ms
        self.total_execution_time_ms = total_time

    def to_dict(self) -> dict[str, Any]:
        """
        转换为字典格式

        Returns:
            包含所有字段的字典
        """
        return {
            "total_thoughts": self.total_thoughts,
            "total_tool_calls": self.total_tool_calls,
            "successful_tool_calls": self.successful_tool_calls,
            "failed_tool_calls": self.failed_tool_calls,
            "cached_tool_calls": self.cached_tool_calls,
            "total_execution_time_ms": self.total_execution_time_ms,
            "avg_thought_length": self.avg_thought_length,
            "phase_distribution": self.phase_distribution,
        }


class ThinkingSession(BaseModel):
    """
    思考会话模型

    表示一个完整的思考会话，包含多个思考步骤。

    Attributes:
        session_id: 会话唯一标识符（UUID格式）
        name: 会话名称
        description: 会话描述
        created_at: 会话创建时间
        updated_at: 会话最后更新时间
        status: 会话状态（active/completed/archived）
        thoughts: 思考步骤列表
        metadata: 元数据字典（用于存储自定义信息）
        statistics: 会话统计信息（Interleaved Thinking）
        tool_call_history: 工具调用记录列表（Interleaved Thinking）
    """

    session_id: str = Field(
        default_factory=lambda: str(uuid4()),
        min_length=1,
        max_length=100,
        description="会话唯一标识符",
    )

    name: str = Field(..., min_length=1, max_length=100, description="会话名称")

    description: str = Field(default="", max_length=2000, description="会话描述")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="会话创建时间"
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="会话最后更新时间"
    )

    status: str = Field(
        default="active",
        pattern="^(active|completed|archived)$",
        description="会话状态",
    )

    thoughts: list[Thought] = Field(default_factory=list, description="思考步骤列表")

    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据字典")

    # Interleaved Thinking 扩展字段
    statistics: SessionStatistics = Field(
        default_factory=SessionStatistics,
        description="会话统计信息",
    )

    tool_call_history: list[ToolCallRecord] = Field(
        default_factory=list,
        description="工具调用记录列表",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        验证会话名称

        Raises:
            ValueError: 如果名称为空或只有空格
        """
        if not v.strip():
            raise ValueError("会话名称不能为空或只有空格")
        return v.strip()

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        """
        验证会话ID格式

        如果提供的ID看起来像UUID格式，进行严格验证。
        其他格式的ID也允许通过（支持测试环境和自定义ID）。

        Raises:
            ValueError: 如果ID为空或UUID格式明显无效
        """
        if not v or not v.strip():
            raise ValueError("会话ID不能为空")

        v = v.strip()

        # 如果看起来像UUID格式（长度36且包含"-"），进行严格验证
        if "-" in v and len(v) == 36:  # UUID格式特征
            try:
                from uuid import UUID

                UUID(v)
            except ValueError as e:
                raise ValueError(f"无效的UUID格式: {v}") from e

        return v

    def add_thought(self, thought: Thought) -> None:
        """
        添加思考步骤到会话

        Args:
            thought: 要添加的思考步骤
        """
        self.thoughts.append(thought)
        self.updated_at = datetime.now(timezone.utc)

    def remove_thought(self, thought_number: int) -> bool:
        """
        从会话中移除思考步骤

        Args:
            thought_number: 要移除的思考步骤编号

        Returns:
            是否成功移除
        """
        for i, thought in enumerate(self.thoughts):
            if thought.thought_number == thought_number:
                self.thoughts.pop(i)
                self.updated_at = datetime.now(timezone.utc)
                return True
        return False

    def get_thought(self, thought_number: int) -> Thought | None:
        """
        获取指定编号的思考步骤

        Args:
            thought_number: 思考步骤编号

        Returns:
            思考步骤对象，如果不存在则返回None
        """
        for thought in self.thoughts:
            if thought.thought_number == thought_number:
                return thought
        return None

    def get_latest_thought(self) -> Thought | None:
        """
        获取最后一个思考步骤

        Returns:
            最后一个思考步骤，如果会话为空则返回None
        """
        if self.thoughts:
            return self.thoughts[-1]
        return None

    def thought_count(self) -> int:
        """
        获取思考步骤数量

        Returns:
            思考步骤总数
        """
        return len(self.thoughts)

    def is_active(self) -> bool:
        """判断会话是否为活跃状态"""
        return self.status == "active"

    def is_completed(self) -> bool:
        """判断会话是否已完成"""
        return self.status == "completed"

    def is_archived(self) -> bool:
        """判断会话是否已归档"""
        return self.status == "archived"

    def mark_completed(self) -> None:
        """将会话标记为已完成"""
        self.status = "completed"
        self.updated_at = datetime.now(timezone.utc)

    def mark_archived(self) -> None:
        """将会话标记为已归档"""
        self.status = "archived"
        self.updated_at = datetime.now(timezone.utc)

    def mark_active(self) -> None:
        """将会话标记为活跃"""
        self.status = "active"
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """
        转换为字典格式

        Returns:
            包含所有字段的字典，datetime转为ISO格式字符串
        """
        return {
            "session_id": self.session_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status,
            "thought_count": self.thought_count(),
            "thoughts": [thought.to_dict() for thought in self.thoughts],
            "metadata": self.metadata,
            "statistics": self.statistics.to_dict(),
            "tool_call_history": [record.to_dict() for record in self.tool_call_history],
        }

    def get_summary(self) -> dict[str, Any]:
        """
        获取会话摘要（不包含完整的思考列表）

        Returns:
            会话摘要字典
        """
        latest_thought = self.get_latest_thought()
        return {
            "session_id": self.session_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status,
            "thought_count": self.thought_count(),
            "latest_thought": latest_thought.to_dict() if latest_thought else None,
            "metadata": self.metadata,
            "statistics": self.statistics.to_dict(),
            "tool_call_count": len(self.tool_call_history),
        }

    def add_tool_call_record(self, record: ToolCallRecord) -> None:
        """
        添加工具调用记录到会话

        Args:
            record: 要添加的工具调用记录
        """
        self.tool_call_history.append(record)
        self.updated_at = datetime.now(timezone.utc)

    def update_statistics(self) -> None:
        """
        更新会话统计信息

        根据当前的思考步骤和工具调用记录重新计算统计信息。
        """
        self.statistics.update_from_thoughts(self.thoughts)
        self.statistics.update_from_tool_calls(self.tool_call_history)
        self.updated_at = datetime.now(timezone.utc)


class SessionCreate(BaseModel):
    """
    创建会话的输入模型

    用于创建新会话时的输入验证。
    """

    name: str = Field(..., min_length=1, max_length=100, description="会话名称")

    description: str = Field(default="", max_length=2000, description="会话描述")

    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")

    def to_session(self) -> ThinkingSession:
        """
        转换为ThinkingSession模型

        Returns:
            ThinkingSession实例
        """
        return ThinkingSession(
            name=self.name,
            description=self.description,
            metadata=self.metadata,
        )


class SessionUpdate(BaseModel):
    """
    更新会话的输入模型

    用于更新现有会话时的输入验证。
    所有字段都是可选的。
    """

    name: str | None = Field(None, min_length=1, max_length=100, description="会话名称")

    description: str | None = Field(None, max_length=500, description="会话描述")

    status: str | None = Field(
        None, pattern="^(active|completed|archived)$", description="会话状态"
    )

    metadata: dict[str, Any] | None = Field(None, description="元数据")
