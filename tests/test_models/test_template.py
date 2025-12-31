"""
思考模板模型单元测试
"""

import pytest
from pydantic import ValidationError

from deep_thinking.models.template import (
    Template,
    TemplateCreate,
    TemplateUpdate,
)


class TestTemplate:
    """Template模型测试"""

    def test_create_template_with_defaults(self):
        """测试使用默认值创建模板"""
        template = Template(
            name="测试模板",
            structure={"steps": [{"step": 1, "prompt": "第一步"}]},
        )
        assert template.name == "测试模板"
        assert template.description == ""
        assert template.category == "general"
        assert template.is_builtin is False
        assert template.metadata == {}
        assert isinstance(template.template_id, str)

    def test_create_template_full(self):
        """测试创建完整模板"""
        template_id = "550e8400-e29b-41d4-a716-446655440000"
        template = Template(
            template_id=template_id,
            name="完整模板",
            description="这是一个完整的模板",
            category="problem_solving",
            structure={
                "steps": [
                    {"step": 1, "prompt": "分析问题"},
                    {"step": 2, "prompt": "寻找解决方案"},
                ]
            },
            is_builtin=True,
            metadata={"author": "系统"},
        )
        assert template.template_id == template_id
        assert template.name == "完整模板"
        assert template.description == "这是一个完整的模板"
        assert template.category == "problem_solving"
        assert template.is_builtin is True
        assert template.metadata == {"author": "系统"}

    def test_name_validation(self):
        """测试名称验证"""
        # 空名称
        structure = {"steps": []}
        with pytest.raises(ValidationError):
            Template(name="", structure=structure)

        # 只有空格的名称
        with pytest.raises(ValidationError):
            Template(name="   ", structure=structure)

        # 名称应该被strip
        template = Template(name="  测试模板  ", structure=structure)
        assert template.name == "测试模板"

    def test_structure_validation(self):
        """测试结构验证"""
        # 结构必须包含steps或phases
        with pytest.raises(ValidationError) as exc_info:
            Template(name="模板", structure={})
        assert "steps" in str(exc_info.value) or "phases" in str(exc_info.value)

    def test_structure_with_steps(self):
        """测试包含steps的结构"""
        structure = {
            "steps": [
                {"step": 1, "prompt": "第一步"},
                {"step": 2, "prompt": "第二步"},
            ]
        }
        template = Template(name="模板", structure=structure)
        assert template.get_step_count() == 2
        assert len(template.get_steps()) == 2

    def test_structure_with_phases(self):
        """测试包含phases的结构"""
        structure = {
            "phases": [
                {"phase": 1, "name": "准备阶段"},
                {"phase": 2, "name": "执行阶段"},
                {"phase": 3, "name": "总结阶段"},
            ]
        }
        template = Template(name="模板", structure=structure)
        assert template.get_step_count() == 3
        assert len(template.get_steps()) == 3

    def test_get_step_count(self):
        """测试获取步骤数量"""
        template = Template(
            name="模板",
            structure={
                "steps": [
                    {"step": 1},
                    {"step": 2},
                    {"step": 3},
                ]
            },
        )
        assert template.get_step_count() == 3

    def test_get_steps(self):
        """测试获取步骤列表"""
        steps = [
            {"step": 1, "prompt": "第一步"},
            {"step": 2, "prompt": "第二步"},
        ]
        template = Template(name="模板", structure={"steps": steps})

        retrieved_steps = template.get_steps()
        assert len(retrieved_steps) == 2
        assert retrieved_steps[0]["step"] == 1
        assert retrieved_steps[1]["step"] == 2

    def test_category_validation(self):
        """测试分类验证"""
        structure = {"steps": []}

        # 有效分类
        valid_categories = [
            "problem_solving",
            "decision_making",
            "analysis",
            "planning",
            "creative",
            "general",
        ]
        for category in valid_categories:
            template = Template(name="模板", structure=structure, category=category)
            assert template.category == category

        # 无效分类
        with pytest.raises(ValidationError):
            Template(name="模板", structure=structure, category="invalid")

    def test_to_dict(self):
        """测试转换为字典"""
        template = Template(
            name="测试模板",
            description="测试描述",
            category="problem_solving",
            structure={
                "steps": [
                    {"step": 1, "prompt": "第一步"},
                    {"step": 2, "prompt": "第二步"},
                ]
            },
            metadata={"version": "1.0"},
        )

        data = template.to_dict()

        assert data["name"] == "测试模板"
        assert data["description"] == "测试描述"
        assert data["category"] == "problem_solving"
        assert data["step_count"] == 2
        assert "structure" in data
        assert data["metadata"] == {"version": "1.0"}


class TestTemplateCreate:
    """TemplateCreate模型测试"""

    def test_to_template(self):
        """测试转换为Template模型"""
        create_data = TemplateCreate(
            name="新模板",
            description="模板描述",
            category="analysis",
            structure={"steps": [{"step": 1}]},
            metadata={"author": "user"},
        )
        template = create_data.to_template()

        assert isinstance(template, Template)
        assert template.name == "新模板"
        assert template.description == "模板描述"
        assert template.category == "analysis"
        assert template.metadata == {"author": "user"}

    def test_default_values(self):
        """测试默认值"""
        create_data = TemplateCreate(
            name="模板",
            structure={"steps": []},
        )
        template = create_data.to_template()

        assert template.description == ""
        assert template.category == "general"
        assert template.metadata == {}


class TestTemplateUpdate:
    """TemplateUpdate模型测试"""

    def test_update_name_only(self):
        """测试只更新名称"""
        update_data = TemplateUpdate(name="新名称")
        assert update_data.name == "新名称"
        assert update_data.description is None

    def test_update_multiple_fields(self):
        """测试更新多个字段"""
        update_data = TemplateUpdate(
            name="新名称",
            description="新描述",
            category="creative",
        )
        assert update_data.name == "新名称"
        assert update_data.description == "新描述"
        assert update_data.category == "creative"

    def test_invalid_category(self):
        """测试无效分类"""
        with pytest.raises(ValidationError):
            TemplateUpdate(category="invalid")

    def test_all_fields_optional(self):
        """测试所有字段都是可选的"""
        update_data = TemplateUpdate()
        assert update_data.name is None
        assert update_data.description is None
        assert update_data.category is None
        assert update_data.structure is None
