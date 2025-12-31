"""
参数验证工具模块

提供Pydantic模型和验证函数，用于输入数据验证。

使用示例:
    from deep_thinking.utils.validators import ThoughtInput
    from pydantic import ValidationError

    try:
        data = ThoughtInput(
            thought="这是一个思考",
            thoughtNumber=1,
            totalThoughts=5,
            nextThoughtNeeded=True
        )
    except ValidationError as e:
        print(f"验证失败: {e}")
"""

from typing import TYPE_CHECKING, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from pydantic import ValidationInfo as _ValidationInfo
else:
    _ValidationInfo = object


class ThoughtInput(BaseModel):
    """
    思考步骤输入验证模型

    用于验证sequential_thinking工具的输入参数
    """

    thought: str = Field(..., min_length=1, max_length=10000, description="思考内容，1-10000个字符")

    nextThoughtNeeded: bool = Field(..., description="是否需要更多思考")

    thoughtNumber: int = Field(..., ge=1, description="当前思考步骤编号，从1开始")

    totalThoughts: int = Field(..., ge=1, description="总思考步骤数")

    session_id: str = Field(
        default="default", min_length=1, max_length=100, description="会话标识符"
    )

    isRevision: bool = Field(default=False, description="是否为修订思考")

    revisesThought: int | None = Field(default=None, ge=1, description="修订的思考步骤编号")

    branchFromThought: int | None = Field(default=None, ge=1, description="分支起始思考步骤编号")

    branchId: str | None = Field(
        default=None, min_length=1, max_length=50, description="分支标识符"
    )

    needsMoreThoughts: bool = Field(default=False, description="是否需要扩展totalThoughts")

    @field_validator("thoughtNumber")
    @classmethod
    def validate_thought_number(cls, v: int, info: _ValidationInfo) -> int:
        """
        验证思考编号不超过总数

        Raises:
            ValueError: 如果thoughtNumber超过totalThoughts
        """
        if "totalThoughts" in info.data and v > info.data["totalThoughts"]:
            raise ValueError(
                f"thoughtNumber ({v}) 不能超过 totalThoughts ({info.data['totalThoughts']})"
            )
        return v

    @field_validator("revisesThought")
    @classmethod
    def validate_revises_thought(cls, v: int | None, info: _ValidationInfo) -> int | None:
        """
        验证修订思考参数

        Raises:
            ValueError: 如果isRevision为False但提供了revisesThought
        """
        if v is not None:
            if "isRevision" in info.data and not info.data["isRevision"]:
                raise ValueError("revisesThought 只能在 isRevision=True 时使用")
            if "thoughtNumber" in info.data and v >= info.data["thoughtNumber"]:
                raise ValueError(
                    f"revisesThought ({v}) 必须小于当前 thoughtNumber "
                    f"({info.data['thoughtNumber']})"
                )
        return v

    @field_validator("branchFromThought")
    @classmethod
    def validate_branch_from(cls, v: int | None, info: _ValidationInfo) -> int | None:
        """
        验证分支起始思考参数

        Raises:
            ValueError: 如果branchFromThought设置不合理
        """
        if v is not None and "thoughtNumber" in info.data and v >= info.data["thoughtNumber"]:
            raise ValueError(
                f"branchFromThought ({v}) 必须小于当前 thoughtNumber ({info.data['thoughtNumber']})"
            )
        return v

    @field_validator("branchId")
    @classmethod
    def validate_branch_id(cls, v: str | None, info: _ValidationInfo) -> str | None:
        """
        验证分支标识符

        Raises:
            ValueError: 如果提供了branchId但没有branchFromThought
        """
        if (
            v is not None
            and "branchFromThought" in info.data
            and info.data["branchFromThought"] is None
        ):
            raise ValueError("branchId 需要配合 branchFromThought 使用")
        return v


class SessionInput(BaseModel):
    """
    会话创建输入验证模型
    """

    name: str = Field(..., min_length=1, max_length=100, description="会话名称")

    description: str = Field(default="", max_length=500, description="会话描述")

    metadata: dict = Field(default_factory=dict, description="元数据")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证会话名称不包含特殊字符"""
        if not v.strip():
            raise ValueError("会话名称不能为空或只有空格")
        return v.strip()


class ExportInput(BaseModel):
    """
    导出输入验证模型
    """

    session_id: str = Field(..., min_length=1, description="会话标识符")

    format: Literal["json", "markdown", "html", "text"] = Field(..., description="导出格式")

    output_path: str | None = Field(default=None, description="输出文件路径（可选）")


class VisualizationInput(BaseModel):
    """
    可视化输入验证模型
    """

    session_id: str = Field(..., min_length=1, description="会话标识符")

    format: Literal["mermaid", "ascii"] = Field(..., description="可视化格式")


def generate_session_id() -> str:
    """
    生成唯一的会话ID

    Returns:
        UUID格式的会话ID
    """
    return str(uuid4())


def validate_session_id(session_id: str) -> bool:
    """
    验证会话ID格式

    Args:
        session_id: 会话ID

    Returns:
        是否为有效的UUID格式
    """
    try:
        from uuid import UUID

        UUID(session_id)
        return True
    except ValueError:
        return False
