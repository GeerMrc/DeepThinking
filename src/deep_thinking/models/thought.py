"""
思考步骤模型

定义单个思考步骤的数据结构和验证规则。
支持常规思考、修订思考、分支思考、对比思考、逆向思考、假设思考六种类型。
"""

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

# 定义思考类型的联合类型
ThoughtType = Literal["regular", "revision", "branch", "comparison", "reverse", "hypothetical"]

# 定义执行阶段的联合类型 (Interleaved Thinking)
ExecutionPhase = Literal["thinking", "tool_call", "analysis"]


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
        phase: 执行阶段（thinking/tool_call/analysis，Interleaved Thinking）
        tool_calls: 关联的工具调用记录列表（Interleaved Thinking）
    """

    thought_number: int = Field(..., ge=1, description="思考步骤编号，从1开始")

    content: str = Field(..., min_length=1, max_length=10000, description="思考内容，1-10000个字符")

    type: ThoughtType = Field(default="regular", description="思考类型")

    is_revision: bool = Field(default=False, description="是否为修订思考")

    revises_thought: int | None = Field(default=None, ge=1, description="修订的思考步骤编号")

    branch_from_thought: int | None = Field(default=None, ge=1, description="分支起始思考步骤编号")

    branch_id: str | None = Field(
        default=None, min_length=1, max_length=50, description="分支标识符"
    )

    # Comparison类型专属字段
    comparison_items: list[str] | None = Field(
        default=None,
        min_length=2,
        description="对比思考的比较项列表，至少2个",
    )

    comparison_dimensions: list[str] | None = Field(
        default=None,
        max_length=10,
        description="对比思考的比较维度列表，最多10个",
    )

    comparison_result: str | None = Field(
        default=None,
        min_length=1,
        max_length=10000,
        description="对比思考的比较结论",
    )

    # Reverse类型专属字段
    reverse_from: int | None = Field(
        default=None,
        ge=1,
        description="逆向思考的反推起点思考编号",
    )

    reverse_target: str | None = Field(
        default=None,
        min_length=1,
        max_length=2000,
        description="逆向思考的反推目标描述",
    )

    reverse_steps: list[str] | None = Field(
        default=None,
        max_length=20,
        description="逆向思考的反推步骤列表，最多20个",
    )

    # Hypothetical类型专属字段
    hypothetical_condition: str | None = Field(
        default=None,
        min_length=1,
        max_length=2000,
        description="假设思考的假设条件描述",
    )

    hypothetical_impact: str | None = Field(
        default=None,
        min_length=1,
        max_length=10000,
        description="假设思考的影响分析",
    )

    hypothetical_probability: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="假设思考的可能性评估",
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="思考时间戳"
    )

    # Interleaved Thinking 扩展字段
    phase: ExecutionPhase = Field(
        default="thinking",
        description="执行阶段（thinking/tool_call/analysis）",
    )

    tool_calls: list[Any] = Field(
        default_factory=list,
        description="关联的工具调用记录ID列表",
    )

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

        elif self.type == "comparison":
            # 对比思考必须指定comparison_items
            if self.comparison_items is None or len(self.comparison_items) < 2:
                raise ValueError("comparison类型必须指定至少2个comparison_items")
            # comparison_items不能有重复项
            if len(self.comparison_items) != len(set(self.comparison_items)):
                raise ValueError("comparison_items不能有重复项")
            # 每个comparison_item长度1-500字符
            for item in self.comparison_items:
                if not 1 <= len(item) <= 500:
                    raise ValueError("每个comparison_item必须在1-500字符之间")
            # comparison_dimensions最多10个维度
            if self.comparison_dimensions and len(self.comparison_dimensions) > 10:
                raise ValueError("comparison_dimensions最多10个维度")
            # 每个dimension长度1-50字符
            if self.comparison_dimensions:
                for dim in self.comparison_dimensions:
                    if not 1 <= len(dim) <= 50:
                        raise ValueError("每个comparison_dimension必须在1-50字符之间")

        elif self.type == "reverse":
            # 逆向思考必须指定reverse_target
            if self.reverse_target is None or not 1 <= len(self.reverse_target) <= 2000:
                raise ValueError("reverse类型必须指定reverse_target(1-2000字符)")
            # reverse_from必须小于当前thought_number
            if self.reverse_from is not None and self.reverse_from >= self.thought_number:
                raise ValueError(
                    f"reverse_from ({self.reverse_from}) 必须小于 "
                    f"thought_number ({self.thought_number})"
                )
            # reverse_steps最多20个步骤
            if self.reverse_steps and len(self.reverse_steps) > 20:
                raise ValueError("reverse_steps最多20个步骤")
            # 每个step长度1-500字符
            if self.reverse_steps:
                for step in self.reverse_steps:
                    if not 1 <= len(step) <= 500:
                        raise ValueError("每个reverse_step必须在1-500字符之间")

        elif self.type == "hypothetical":
            # 假设思考必须指定hypothetical_condition
            if (
                self.hypothetical_condition is None
                or not 1 <= len(self.hypothetical_condition) <= 2000
            ):
                raise ValueError("hypothetical类型必须指定hypothetical_condition(1-2000字符)")
            # hypothetical_impact长度1-10000字符
            if (
                self.hypothetical_impact is not None
                and not 1 <= len(self.hypothetical_impact) <= 10000
            ):
                raise ValueError("hypothetical_impact必须在1-10000字符之间")
            # hypothetical_probability长度1-50字符
            if (
                self.hypothetical_probability is not None
                and not 1 <= len(self.hypothetical_probability) <= 50
            ):
                raise ValueError("hypothetical_probability必须在1-50字符之间")

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

    def is_comparison_thought(self) -> bool:
        """判断是否为对比思考"""
        return self.type == "comparison"

    def is_reverse_thought(self) -> bool:
        """判断是否为逆向思考"""
        return self.type == "reverse"

    def is_hypothetical_thought(self) -> bool:
        """判断是否为假设思考"""
        return self.type == "hypothetical"

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
            "comparison": "⚖️",
            "reverse": "🔙",
            "hypothetical": "🤔",
        }
        return type_symbols.get(self.type, "❓")

    def to_dict(self) -> dict[str, Any]:
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

    type: ThoughtType = Field(default="regular", description="思考类型")

    is_revision: bool = Field(default=False, description="是否为修订思考")

    revises_thought: int | None = Field(default=None, ge=1, description="修订的思考步骤编号")

    branch_from_thought: int | None = Field(default=None, ge=1, description="分支起始思考步骤编号")

    branch_id: str | None = Field(
        default=None, min_length=1, max_length=50, description="分支标识符"
    )

    # Comparison类型字段
    comparison_items: list[str] | None = Field(
        default=None,
        min_length=2,
        description="对比思考的比较项列表，至少2个",
    )

    comparison_dimensions: list[str] | None = Field(
        default=None,
        max_length=10,
        description="对比思考的比较维度列表，最多10个",
    )

    comparison_result: str | None = Field(
        default=None,
        min_length=1,
        max_length=10000,
        description="对比思考的比较结论",
    )

    # Reverse类型字段
    reverse_from: int | None = Field(
        default=None,
        ge=1,
        description="逆向思考的反推起点思考编号",
    )

    reverse_target: str | None = Field(
        default=None,
        min_length=1,
        max_length=2000,
        description="逆向思考的反推目标描述",
    )

    reverse_steps: list[str] | None = Field(
        default=None,
        max_length=20,
        description="逆向思考的反推步骤列表，最多20个",
    )

    # Hypothetical类型字段
    hypothetical_condition: str | None = Field(
        default=None,
        min_length=1,
        max_length=2000,
        description="假设思考的假设条件描述",
    )

    hypothetical_impact: str | None = Field(
        default=None,
        min_length=1,
        max_length=10000,
        description="假设思考的影响分析",
    )

    hypothetical_probability: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="假设思考的可能性评估",
    )

    # Interleaved Thinking 扩展字段
    phase: ExecutionPhase = Field(
        default="thinking",
        description="执行阶段",
    )

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
            comparison_items=self.comparison_items,
            comparison_dimensions=self.comparison_dimensions,
            comparison_result=self.comparison_result,
            reverse_from=self.reverse_from,
            reverse_target=self.reverse_target,
            reverse_steps=self.reverse_steps,
            hypothetical_condition=self.hypothetical_condition,
            hypothetical_impact=self.hypothetical_impact,
            hypothetical_probability=self.hypothetical_probability,
            phase=self.phase,
        )


class ThoughtUpdate(BaseModel):
    """
    更新思考步骤的输入模型

    用于更新现有思考步骤时的输入验证。
    所有字段都是可选的。
    """

    content: str | None = Field(None, min_length=1, max_length=10000, description="思考内容")

    type: ThoughtType | None = Field(None, description="思考类型")

    is_revision: bool | None = Field(None, description="是否为修订思考")

    revises_thought: int | None = Field(None, ge=1, description="修订的思考步骤编号")

    branch_from_thought: int | None = Field(None, ge=1, description="分支起始思考步骤编号")

    branch_id: str | None = Field(None, min_length=1, max_length=50, description="分支标识符")

    # Comparison类型字段
    comparison_items: list[str] | None = Field(
        None, min_length=2, description="对比思考的比较项列表"
    )

    comparison_dimensions: list[str] | None = Field(
        None, max_length=10, description="对比思考的比较维度列表"
    )

    comparison_result: str | None = Field(
        None, min_length=1, max_length=10000, description="对比思考的比较结论"
    )

    # Reverse类型字段
    reverse_from: int | None = Field(None, ge=1, description="逆向思考的反推起点思考编号")

    reverse_target: str | None = Field(
        None, min_length=1, max_length=2000, description="逆向思考的反推目标描述"
    )

    reverse_steps: list[str] | None = Field(
        None, max_length=20, description="逆向思考的反推步骤列表"
    )

    # Hypothetical类型字段
    hypothetical_condition: str | None = Field(
        None, min_length=1, max_length=2000, description="假设思考的假设条件描述"
    )

    hypothetical_impact: str | None = Field(
        None, min_length=1, max_length=10000, description="假设思考的影响分析"
    )

    hypothetical_probability: str | None = Field(
        None, min_length=1, max_length=50, description="假设思考的可能性评估"
    )

    # Interleaved Thinking 扩展字段
    phase: ExecutionPhase | None = Field(
        None, description="执行阶段"
    )
