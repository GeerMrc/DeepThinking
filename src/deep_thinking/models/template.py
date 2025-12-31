"""
思考模板模型

定义预设思考模板的数据结构。
模板提供标准化的思考框架，帮助用户更好地组织思考过程。
"""

from typing import Any, cast
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class Template(BaseModel):
    """
    思考模板模型

    表示一个预设的思考框架或模板。

    Attributes:
        template_id: 模板唯一标识符（UUID格式）
        name: 模板名称
        description: 模板描述
        category: 模板分类
        structure: 模板结构定义
        is_builtin: 是否为内置模板
        metadata: 元数据字典
    """

    template_id: str = Field(
        default_factory=lambda: str(uuid4()),
        min_length=1,
        max_length=100,
        description="模板唯一标识符",
    )

    name: str = Field(..., min_length=1, max_length=100, description="模板名称")

    description: str = Field(default="", max_length=500, description="模板描述")

    category: str = Field(
        default="general",
        pattern="^(problem_solving|decision_making|analysis|planning|creative|general)$",
        description="模板分类",
    )

    structure: dict[str, Any] = Field(
        ...,
        description="模板结构定义，包含步骤、提示等",
    )

    is_builtin: bool = Field(default=False, description="是否为内置模板")

    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据字典")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        验证模板名称

        Raises:
            ValueError: 如果名称为空或只有空格
        """
        if not v.strip():
            raise ValueError("模板名称不能为空或只有空格")
        return v.strip()

    @field_validator("structure")
    @classmethod
    def validate_structure(cls, v: dict[str, Any]) -> dict[str, Any]:
        """
        验证模板结构

        Raises:
            ValueError: 如果结构缺少必需字段
        """
        # 至少需要包含steps或phases之一
        if "steps" not in v and "phases" not in v:
            raise ValueError("模板结构必须包含'steps'或'phases'字段")

        return v

    def get_step_count(self) -> int:
        """
        获取模板步骤数量

        Returns:
            步骤数量
        """
        if "steps" in self.structure:
            return len(self.structure["steps"])
        elif "phases" in self.structure:
            return len(self.structure["phases"])
        return 0

    def get_steps(self) -> list[dict[str, Any]]:
        """
        获取模板步骤列表

        Returns:
            步骤列表
        """
        if "steps" in self.structure:
            return cast(list[dict[str, Any]], self.structure["steps"])
        elif "phases" in self.structure:
            return cast(list[dict[str, Any]], self.structure["phases"])
        return []

    def to_dict(self) -> dict[str, Any]:
        """
        转换为字典格式

        Returns:
            包含所有字段的字典
        """
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "step_count": self.get_step_count(),
            "structure": self.structure,
            "is_builtin": self.is_builtin,
            "metadata": self.metadata,
        }


class TemplateCreate(BaseModel):
    """
    创建模板的输入模型

    用于创建新模板时的输入验证。
    """

    name: str = Field(..., min_length=1, max_length=100, description="模板名称")

    description: str = Field(default="", max_length=500, description="模板描述")

    category: str = Field(
        default="general",
        pattern="^(problem_solving|decision_making|analysis|planning|creative|general)$",
        description="模板分类",
    )

    structure: dict[str, Any] = Field(..., description="模板结构定义")

    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")

    def to_template(self) -> Template:
        """
        转换为Template模型

        Returns:
            Template实例
        """
        return Template(
            name=self.name,
            description=self.description,
            category=self.category,
            structure=self.structure,
            metadata=self.metadata,
        )


class TemplateUpdate(BaseModel):
    """
    更新模板的输入模型

    用于更新现有模板时的输入验证。
    所有字段都是可选的。
    """

    name: str | None = Field(None, min_length=1, max_length=100, description="模板名称")

    description: str | None = Field(None, max_length=500, description="模板描述")

    category: str | None = Field(
        None,
        pattern="^(problem_solving|decision_making|analysis|planning|creative|general)$",
        description="模板分类",
    )

    structure: dict[str, Any] | None = Field(None, description="模板结构定义")

    metadata: dict[str, Any] | None = Field(None, description="元数据")
