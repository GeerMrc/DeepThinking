"""
思考配置模型

定义 MCP 服务器的思考行为配置参数。
"""

import os

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class ThinkingConfig(BaseModel):
    """
    思考配置模型

    定义思考步骤的数量限制和增量参数。

    Attributes:
        max_thoughts: 最大思考步骤数（防止无限循环）
        min_thoughts: 最小思考步骤数（确保合理范围）
        thoughts_increment: 每次增加的思考步骤数（needsMoreThoughts 功能使用）
    """

    max_thoughts: int = Field(
        default=50,
        ge=1,
        le=10000,
        description="最大思考步骤数（防止无限循环）",
    )
    min_thoughts: int = Field(
        default=3,
        ge=1,
        description="最小思考步骤数（确保合理范围）",
    )
    thoughts_increment: int = Field(
        default=10,
        ge=1,
        le=100,
        description="每次增加的思考步骤数（needsMoreThoughts 功能使用）",
    )

    @field_validator("min_thoughts")
    @classmethod
    def validate_min_thoughts(cls, v: int, info: ValidationInfo) -> int:
        """
        验证最小思考步骤数

        确保 min_thoughts 不超过 max_thoughts。

        Args:
            v: 最小思考步骤数
            info: 字段验证信息

        Returns:
            验证后的最小思考步骤数

        Raises:
            ValueError: 如果 min_thoughts > max_thoughts
        """
        max_thoughts = info.data.get("max_thoughts")
        if max_thoughts is not None and v > max_thoughts:
            raise ValueError(f"min_thoughts ({v}) 不能大于 max_thoughts ({max_thoughts})")
        return v

    @field_validator("thoughts_increment")
    @classmethod
    def validate_thoughts_increment(cls, v: int) -> int:
        """
        验证思考步骤增量

        确保 thoughts_increment 是合理的值。

        Args:
            v: 思考步骤增量

        Returns:
            验证后的思考步骤增量

        Raises:
            ValueError: 如果增量不合理
        """
        if v < 1:
            raise ValueError("thoughts_increment 必须大于等于 1")
        if v > 100:
            raise ValueError("thoughts_increment 不能大于 100")
        return v

    def validate_bounds(self, current: int, total: int) -> bool:
        """
        验证思考步骤是否在合理范围内

        Args:
            current: 当前思考步骤数
            total: 总思考步骤数

        Returns:
            是否在合理范围内
        """
        return self.min_thoughts <= current <= self.max_thoughts and total <= self.max_thoughts

    def get_incremented_total(self, current_total: int) -> int:
        """
        获取增加后的总思考步骤数

        Args:
            current_total: 当前总思考步骤数

        Returns:
            增加后的总思考步骤数（不超过 max_thoughts）
        """
        new_total = min(current_total + self.thoughts_increment, self.max_thoughts)
        return new_total

    @classmethod
    def from_env(cls) -> "ThinkingConfig":
        """
        从环境变量创建配置

        支持的环境变量：
        - DEEP_THINKING_MAX_THOUGHTS: 最大思考步骤数（默认：50）
        - DEEP_THINKING_MIN_THOUGHTS: 最小思考步骤数（默认：3）
        - DEEP_THINKING_THOUGHTS_INCREMENT: 思考步骤增量（默认：10）

        配置范围说明：
        - 最大思考步骤：支持配置 1-10000 步（推荐 50 步）
        - 最小思考步骤：支持配置 1-10000 步（推荐 3 步）
        - 思考步骤增量：支持配置 1-100 步（默认 10 步）

        Returns:
            思考配置实例
        """
        return cls(
            max_thoughts=int(os.getenv("DEEP_THINKING_MAX_THOUGHTS", "50")),
            min_thoughts=int(os.getenv("DEEP_THINKING_MIN_THOUGHTS", "3")),
            thoughts_increment=int(os.getenv("DEEP_THINKING_THOUGHTS_INCREMENT", "10")),
        )


# 全局配置实例（单例）
_global_config: ThinkingConfig | None = None


def get_global_config() -> ThinkingConfig:
    """
    获取全局思考配置实例

    Returns:
        全局思考配置实例

    Raises:
        RuntimeError: 如果配置未初始化
    """
    global _global_config
    if _global_config is None:
        # 如果未初始化，从环境变量创建
        _global_config = ThinkingConfig.from_env()
    return _global_config


def set_global_config(config: ThinkingConfig) -> None:
    """
    设置全局思考配置实例

    Args:
        config: 思考配置实例
    """
    global _global_config
    _global_config = config


__all__ = [
    "ThinkingConfig",
    "get_global_config",
    "set_global_config",
]
