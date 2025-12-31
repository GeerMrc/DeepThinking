"""
思考会话模型

定义思考会话的数据结构和验证规则。
一个会话包含多个思考步骤，支持会话状态管理和元数据。
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from deep_thinking.models.thought import Thought


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
    """

    session_id: str = Field(
        default_factory=lambda: str(uuid4()),
        min_length=1,
        max_length=100,
        description="会话唯一标识符",
    )

    name: str = Field(..., min_length=1, max_length=100, description="会话名称")

    description: str = Field(default="", max_length=500, description="会话描述")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="会话创建时间")

    updated_at: datetime = Field(default_factory=datetime.utcnow, description="会话最后更新时间")

    status: str = Field(
        default="active",
        pattern="^(active|completed|archived)$",
        description="会话状态",
    )

    thoughts: list[Thought] = Field(default_factory=list, description="思考步骤列表")

    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据字典")

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

        对于自动生成的UUID进行验证，自定义ID允许通过。

        Raises:
            ValueError: 如果ID为空或格式明显无效
        """
        if not v or not v.strip():
            raise ValueError("会话ID不能为空")

        v = v.strip()

        # 如果看起来像UUID格式，进行验证
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
        self.updated_at = datetime.utcnow()

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
                self.updated_at = datetime.utcnow()
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
        self.updated_at = datetime.utcnow()

    def mark_archived(self) -> None:
        """将会话标记为已归档"""
        self.status = "archived"
        self.updated_at = datetime.utcnow()

    def mark_active(self) -> None:
        """将会话标记为活跃"""
        self.status = "active"
        self.updated_at = datetime.utcnow()

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
        }


class SessionCreate(BaseModel):
    """
    创建会话的输入模型

    用于创建新会话时的输入验证。
    """

    name: str = Field(..., min_length=1, max_length=100, description="会话名称")

    description: str = Field(default="", max_length=500, description="会话描述")

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
