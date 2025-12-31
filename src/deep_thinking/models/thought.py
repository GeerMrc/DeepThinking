"""
思考步骤模型

定义单个思考步骤的数据结构和验证规则。
支持常规思考、修订思考和分支思考三种类型。
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Thought(BaseModel):
    """
    思考步骤模型

    表示顺序思考过程中的单个思考步骤。

    Attributes:
        thought_number: 思考步骤编号，从1开始
        content: 思考内容
        type: 思考类型（regular/revision/branch）
        is_revision: 是否为修订思考
        revises_thought: 修订的思考步骤编号
        branch_from_thought: 分支起始思考步骤编号
        branch_id: 分支标识符
        timestamp: 思考时间戳
    """

    thought_number: int = Field(..., ge=1, description="思考步骤编号，从1开始")

    content: str = Field(..., min_length=1, max_length=10000, description="思考内容，1-10000个字符")

    type: Literal["regular", "revision", "branch"] = Field(
        default="regular", description="思考类型"
    )

    is_revision: bool = Field(default=False, description="是否为修订思考")

    revises_thought: int | None = Field(default=None, ge=1, description="修订的思考步骤编号")

    branch_from_thought: int | None = Field(default=None, ge=1, description="分支起始思考步骤编号")

    branch_id: str | None = Field(
        default=None, min_length=1, max_length=50, description="分支标识符"
    )

    timestamp: datetime = Field(default_factory=datetime.utcnow, description="思考时间戳")

    @model_validator(mode="after")
    def validate_type_consistency(self) -> "Thought":
        """
        验证思考类型与其他字段的一致性

        Raises:
            ValueError: 如果类型与字段值不匹配
        """
        if self.type == "revision":
            # 修订思考必须设置is_revision=True
            if not self.is_revision:
                raise ValueError("修订思考必须设置is_revision=True")
            # 修订思考必须指定revises_thought
            if self.revises_thought is None:
                raise ValueError("修订思考必须指定revises_thought")
            # 修订编号必须小于当前编号
            if self.revises_thought >= self.thought_number:
                raise ValueError(
                    f"revises_thought ({self.revises_thought}) 必须小于当前 "
                    f"thought_number ({self.thought_number})"
                )

        elif self.type == "branch":
            # 分支思考必须指定branch_from_thought
            if self.branch_from_thought is None:
                raise ValueError("分支思考必须指定branch_from_thought")
            # 分支思考必须指定branch_id
            if self.branch_id is None:
                raise ValueError("分支思考必须指定branch_id")
            # 分支起始编号必须小于当前编号
            if self.branch_from_thought >= self.thought_number:
                raise ValueError(
                    f"branch_from_thought ({self.branch_from_thought}) 必须小于当前 "
                    f"thought_number ({self.thought_number})"
                )

        return self

    def is_regular_thought(self) -> bool:
        """判断是否为常规思考"""
        return self.type == "regular"

    def is_revision_thought(self) -> bool:
        """判断是否为修订思考"""
        return self.type == "revision"

    def is_branch_thought(self) -> bool:
        """判断是否为分支思考"""
        return self.type == "branch"

    def get_display_type(self) -> str:
        """
        获取思考类型的显示符号

        Returns:
            思考类型的符号表示（💭/🔄/🌿）
        """
        type_symbols = {
            "regular": "💭",
            "revision": "🔄",
            "branch": "🌿",
        }
        return type_symbols.get(self.type, "❓")

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            包含所有字段的字典，timestamp转为ISO格式字符串
        """
        data = self.model_dump()
        data["timestamp"] = self.timestamp.isoformat()
        data["display_type"] = self.get_display_type()
        return data


class ThoughtCreate(BaseModel):
    """
    创建思考步骤的输入模型

    用于创建新思考步骤时的输入验证。
    """

    thought_number: int = Field(..., ge=1, description="思考步骤编号")

    content: str = Field(..., min_length=1, max_length=10000, description="思考内容")

    type: Literal["regular", "revision", "branch"] = Field(
        default="regular", description="思考类型"
    )

    is_revision: bool = Field(default=False, description="是否为修订思考")

    revises_thought: int | None = Field(default=None, ge=1, description="修订的思考步骤编号")

    branch_from_thought: int | None = Field(default=None, ge=1, description="分支起始思考步骤编号")

    branch_id: str | None = Field(default=None, min_length=1, max_length=50, description="分支标识符")

    def to_thought(self) -> Thought:
        """
        转换为Thought模型

        Returns:
            Thought实例
        """
        return Thought(
            thought_number=self.thought_number,
            content=self.content,
            type=self.type,
            is_revision=self.is_revision,
            revises_thought=self.revises_thought,
            branch_from_thought=self.branch_from_thought,
            branch_id=self.branch_id,
        )


class ThoughtUpdate(BaseModel):
    """
    更新思考步骤的输入模型

    用于更新现有思考步骤时的输入验证。
    所有字段都是可选的。
    """

    content: str | None = Field(None, min_length=1, max_length=10000, description="思考内容")

    type: Literal["regular", "revision", "branch"] | None = Field(None, description="思考类型")

    is_revision: bool | None = Field(None, description="是否为修订思考")

    revises_thought: int | None = Field(None, ge=1, description="修订的思考步骤编号")

    branch_from_thought: int | None = Field(None, ge=1, description="分支起始思考步骤编号")

    branch_id: str | None = Field(None, min_length=1, max_length=50, description="分支标识符")
