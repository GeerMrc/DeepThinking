"""
思考配置模型单元测试
"""

import os

import pytest
from pydantic import ValidationError

from deep_thinking.models.config import ThinkingConfig, get_global_config, set_global_config


class TestThinkingConfig:
    """思考配置模型测试"""

    def test_default_values(self):
        """测试默认值"""
        config = ThinkingConfig()
        assert config.max_thoughts == 50
        assert config.min_thoughts == 3
        assert config.thoughts_increment == 10

    def test_custom_values(self):
        """测试自定义值"""
        config = ThinkingConfig(
            max_thoughts=500,
            min_thoughts=5,
            thoughts_increment=20,
        )
        assert config.max_thoughts == 500
        assert config.min_thoughts == 5
        assert config.thoughts_increment == 20

    def test_max_thoughts_validation(self):
        """测试最大思考步骤数验证"""
        # 有效值
        config = ThinkingConfig(max_thoughts=100)
        assert config.max_thoughts == 100

        # 无效值：太小
        with pytest.raises(ValidationError):
            ThinkingConfig(max_thoughts=0)

        # 无效值：太大
        with pytest.raises(ValidationError):
            ThinkingConfig(max_thoughts=10001)

    def test_min_thoughts_validation(self):
        """测试最小思考步骤数验证"""
        # 有效值
        config = ThinkingConfig(min_thoughts=5)
        assert config.min_thoughts == 5

        # 无效值：太小
        with pytest.raises(ValidationError):
            ThinkingConfig(min_thoughts=0)

        # 无效值：大于 max_thoughts
        with pytest.raises(ValidationError) as exc_info:
            ThinkingConfig(min_thoughts=2000, max_thoughts=1000)
        assert "min_thoughts" in str(exc_info.value).lower()

    def test_thoughts_increment_validation(self):
        """测试思考步骤增量验证"""
        # 有效值
        config = ThinkingConfig(thoughts_increment=5)
        assert config.thoughts_increment == 5

        # 无效值：太小
        with pytest.raises(ValidationError):
            ThinkingConfig(thoughts_increment=0)

        # 无效值：太大
        with pytest.raises(ValidationError):
            ThinkingConfig(thoughts_increment=101)

    def test_validate_bounds(self):
        """测试边界验证"""
        config = ThinkingConfig(
            max_thoughts=100,
            min_thoughts=1,
            thoughts_increment=10,
        )

        # 在范围内
        assert config.validate_bounds(current=50, total=100)
        assert config.validate_bounds(current=1, total=50)

        # 超出最大值
        assert not config.validate_bounds(current=101, total=100)
        assert not config.validate_bounds(current=50, total=101)

        # 小于最小值
        assert not config.validate_bounds(current=0, total=50)

    def test_get_incremented_total(self):
        """测试获取增加后的总思考步骤数"""
        config = ThinkingConfig(
            max_thoughts=100,
            thoughts_increment=10,
        )

        # 正常增加
        assert config.get_incremented_total(50) == 60
        assert config.get_incremented_total(90) == 100

        # 已达到最大值
        assert config.get_incremented_total(100) == 100

    def test_from_env(self):
        """测试从环境变量创建配置"""
        # 设置环境变量
        os.environ["DEEP_THINKING_MAX_THOUGHTS"] = "500"
        os.environ["DEEP_THINKING_MIN_THOUGHTS"] = "5"
        os.environ["DEEP_THINKING_THOUGHTS_INCREMENT"] = "20"

        config = ThinkingConfig.from_env()

        assert config.max_thoughts == 500
        assert config.min_thoughts == 5
        assert config.thoughts_increment == 20

        # 清理环境变量
        del os.environ["DEEP_THINKING_MAX_THOUGHTS"]
        del os.environ["DEEP_THINKING_MIN_THOUGHTS"]
        del os.environ["DEEP_THINKING_THOUGHTS_INCREMENT"]

    def test_from_env_defaults(self):
        """测试从环境变量创建配置（使用默认值）"""
        # 确保环境变量未设置
        env_vars = [
            "DEEP_THINKING_MAX_THOUGHTS",
            "DEEP_THINKING_MIN_THOUGHTS",
            "DEEP_THINKING_THOUGHTS_INCREMENT",
        ]
        for var in env_vars:
            os.environ.pop(var, None)

        config = ThinkingConfig.from_env()

        assert config.max_thoughts == 50
        assert config.min_thoughts == 3
        assert config.thoughts_increment == 10


class TestGlobalConfig:
    """全局配置实例测试"""

    def setup_method(self):
        """每个测试前重置全局配置"""
        import deep_thinking.models.config as config_module
        config_module._global_config = None

    def test_get_global_config_initializes_from_env(self):
        """测试获取全局配置（从环境变量初始化）"""
        config = get_global_config()
        assert isinstance(config, ThinkingConfig)
        assert config.max_thoughts == 50  # 默认值

    def test_set_global_config(self):
        """测试设置全局配置"""
        custom_config = ThinkingConfig(max_thoughts=200)
        set_global_config(custom_config)

        config = get_global_config()
        assert config.max_thoughts == 200

    def test_global_config_singleton(self):
        """测试全局配置单例"""
        config1 = get_global_config()
        config2 = get_global_config()

        # 应该是同一个实例
        assert config1 is config2
