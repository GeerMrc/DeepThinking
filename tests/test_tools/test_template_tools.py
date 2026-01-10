"""
模板工具单元测试

测试 template.py 中的模板功能。
"""

from unittest.mock import MagicMock, patch

import pytest

from deep_thinking.tools import template
from deep_thinking.utils.template_loader import TemplateLoader

# =============================================================================
# TemplateLoader 测试
# =============================================================================


class TestTemplateLoader:
    """测试模板加载器"""

    def test_load_template_problem_solving(self, temp_dir):
        """测试加载问题求解模板"""
        # 创建测试模板文件
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)
        template_file = templates_dir / "test_template.json"
        template_file.write_text(
            """
{
    "template_id": "test_template",
    "name": "测试模板",
    "description": "这是一个测试模板",
    "category": "test",
    "structure": {
        "steps": [
            {
                "step_number": 1,
                "prompt": "第一步",
                "type": "regular"
            }
        ]
    },
    "metadata": {
        "version": "1.0"
    }
}
""",
            encoding="utf-8",
        )

        loader = TemplateLoader(templates_dir)
        result = loader.load_template("test_template")

        assert result["template_id"] == "test_template"
        assert result["name"] == "测试模板"
        assert result["category"] == "test"
        assert len(result["structure"]["steps"]) == 1

    def test_load_template_not_found(self, temp_dir):
        """测试加载不存在的模板"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)

        loader = TemplateLoader(templates_dir)

        with pytest.raises(FileNotFoundError, match="模板不存在"):
            loader.load_template("nonexistent")

    def test_load_template_invalid_json(self, temp_dir):
        """测试加载格式错误的模板"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)
        template_file = templates_dir / "invalid.json"
        template_file.write_text("{invalid json}", encoding="utf-8")

        loader = TemplateLoader(templates_dir)

        with pytest.raises(ValueError, match="格式错误"):
            loader.load_template("invalid")

    def test_load_template_missing_fields(self, temp_dir):
        """测试加载缺少必需字段的模板"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)
        template_file = templates_dir / "incomplete.json"
        template_file.write_text('{"name": "测试"}', encoding="utf-8")

        loader = TemplateLoader(templates_dir)

        with pytest.raises(ValueError, match="缺少必需字段"):
            loader.load_template("incomplete")

    def test_list_available_templates(self, temp_dir):
        """测试列出可用模板"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)

        # 创建多个模板文件
        (templates_dir / "template1.json").write_text(
            '{"template_id": "t1", "name": "T1", "description": "", "category": "", "structure": {"steps": []}}'
        )
        (templates_dir / "template2.json").write_text(
            '{"template_id": "t2", "name": "T2", "description": "", "category": "", "structure": {"steps": []}}'
        )

        loader = TemplateLoader(templates_dir)
        result = loader.list_available_templates()

        assert set(result) == {"template1", "template2"}

    def test_list_available_templates_empty_dir(self, temp_dir):
        """测试空模板目录"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)

        loader = TemplateLoader(templates_dir)
        result = loader.list_available_templates()

        assert result == []

    def test_get_template_info(self, temp_dir):
        """测试获取模板信息"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)
        (templates_dir / "test.json").write_text(
            """
{
    "template_id": "test",
    "name": "测试模板",
    "description": "测试描述",
    "category": "test_category",
    "structure": {"steps": []},
    "metadata": {"tags": ["test"]}
}
""",
            encoding="utf-8",
        )

        loader = TemplateLoader(templates_dir)
        result = loader.get_template_info("test")

        assert result["template_id"] == "test"
        assert result["name"] == "测试模板"
        assert result["description"] == "测试描述"
        assert result["category"] == "test_category"
        assert result["metadata"]["tags"] == ["test"]

    def test_list_templates(self, temp_dir):
        """测试列出所有模板信息"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)

        (templates_dir / "t1.json").write_text(
            '{"template_id": "t1", "name": "模板1", "description": "描述1", "category": "c1", "structure": {"steps": []}, "metadata": {}}'
        )
        (templates_dir / "t2.json").write_text(
            '{"template_id": "t2", "name": "模板2", "description": "描述2", "category": "c2", "structure": {"steps": []}, "metadata": {}}'
        )

        loader = TemplateLoader(templates_dir)
        result = loader.list_templates()

        assert len(result) == 2
        assert any(t["template_id"] == "t1" for t in result)
        assert any(t["template_id"] == "t2" for t in result)

    def test_list_templates_with_invalid_template(self, temp_dir):
        """测试列出模板时跳过无效模板（异常处理）"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)

        # 创建有效模板
        (templates_dir / "valid.json").write_text(
            '{"template_id": "valid", "name": "有效模板", "description": "", "category": "", "structure": {"steps": []}, "metadata": {}}'
        )
        # 创建无效模板（缺少必需字段）
        (templates_dir / "invalid.json").write_text('{"name": "无效"}', encoding="utf-8")

        loader = TemplateLoader(templates_dir)
        result = loader.list_templates()

        # 应该只返回有效模板
        assert len(result) == 1
        assert result[0]["template_id"] == "valid"

    def test_list_templates_with_nonexistent_dir(self, temp_dir):
        """测试列出模板时目录不存在（异常处理）"""
        # 使用不存在的目录
        templates_dir = temp_dir / "nonexistent"
        loader = TemplateLoader(templates_dir)

        result = loader.list_templates()

        # 目录不存在时应返回空列表
        assert result == []

    def test_iter_templates_with_invalid_template(self, temp_dir):
        """测试迭代模板时跳过无效模板"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)

        # 创建有效模板
        (templates_dir / "valid.json").write_text(
            '{"template_id": "valid", "name": "有效模板", "description": "", "category": "", "structure": {"steps": []}, "metadata": {}}'
        )
        # 创建无效模板（格式错误）
        (templates_dir / "invalid.json").write_text("{invalid json}", encoding="utf-8")

        loader = TemplateLoader(templates_dir)
        result = list(loader.iter_templates())

        # 应该只返回有效模板
        assert len(result) == 1
        assert result[0]["template_id"] == "valid"

    def test_validate_template_missing_structure(self, temp_dir):
        """测试模板缺少structure字段"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)
        template_file = templates_dir / "no_structure.json"
        template_file.write_text(
            '{"template_id": "test", "name": "测试", "description": "", "category": ""}',
            encoding="utf-8",
        )

        loader = TemplateLoader(templates_dir)

        with pytest.raises(ValueError, match="缺少必需字段.*structure"):
            loader.load_template("no_structure")

    def test_validate_template_structure_not_dict(self, temp_dir):
        """测试structure字段不是字典类型"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)
        template_file = templates_dir / "bad_structure.json"
        template_file.write_text(
            '{"template_id": "test", "name": "测试", "description": "", "category": "", "structure": "not_a_dict"}',
            encoding="utf-8",
        )

        loader = TemplateLoader(templates_dir)

        with pytest.raises(ValueError, match="structure.*必须是字典类型"):
            loader.load_template("bad_structure")

    def test_validate_template_steps_not_list(self, temp_dir):
        """测试steps字段不是列表类型"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)
        template_file = templates_dir / "bad_steps.json"
        template_file.write_text(
            '{"template_id": "test", "name": "测试", "description": "", "category": "", "structure": {"steps": "not_a_list"}}',
            encoding="utf-8",
        )

        loader = TemplateLoader(templates_dir)

        with pytest.raises(ValueError, match="steps.*必须是列表类型"):
            loader.load_template("bad_steps")

    def test_validate_template_step_not_dict(self, temp_dir):
        """测试步骤不是字典类型"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)
        template_file = templates_dir / "bad_step.json"
        template_file.write_text(
            '{"template_id": "test", "name": "测试", "description": "", "category": "", "structure": {"steps": ["not_a_dict"]}}',
            encoding="utf-8",
        )

        loader = TemplateLoader(templates_dir)

        with pytest.raises(ValueError, match="步骤 0.*必须是字典类型"):
            loader.load_template("bad_step")

    def test_validate_template_step_missing_number(self, temp_dir):
        """测试步骤缺少step_number字段"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)
        template_file = templates_dir / "no_number.json"
        template_file.write_text(
            '{"template_id": "test", "name": "测试", "description": "", "category": "", "structure": {"steps": [{"prompt": "测试", "type": "regular"}]}}',
            encoding="utf-8",
        )

        loader = TemplateLoader(templates_dir)

        with pytest.raises(ValueError, match="步骤 0.*缺少 step_number"):
            loader.load_template("no_number")

    def test_validate_template_step_missing_prompt(self, temp_dir):
        """测试步骤缺少prompt字段"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)
        template_file = templates_dir / "no_prompt.json"
        template_file.write_text(
            '{"template_id": "test", "name": "测试", "description": "", "category": "", "structure": {"steps": [{"step_number": 1, "type": "regular"}]}}',
            encoding="utf-8",
        )

        loader = TemplateLoader(templates_dir)

        with pytest.raises(ValueError, match="步骤 0.*缺少 prompt"):
            loader.load_template("no_prompt")

    def test_validate_template_step_missing_type(self, temp_dir):
        """测试步骤缺少type字段"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)
        template_file = templates_dir / "no_type.json"
        template_file.write_text(
            '{"template_id": "test", "name": "测试", "description": "", "category": "", "structure": {"steps": [{"step_number": 1, "prompt": "测试"}]}}',
            encoding="utf-8",
        )

        loader = TemplateLoader(templates_dir)

        with pytest.raises(ValueError, match="步骤 0.*缺少 type"):
            loader.load_template("no_type")

    def test_validate_template_step_invalid_type(self, temp_dir):
        """测试步骤type字段值无效"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir(parents=True)
        template_file = templates_dir / "invalid_type.json"
        template_file.write_text(
            '{"template_id": "test", "name": "测试", "description": "", "category": "", "structure": {"steps": [{"step_number": 1, "prompt": "测试", "type": "invalid_type"}]}}',
            encoding="utf-8",
        )

        loader = TemplateLoader(templates_dir)

        with pytest.raises(ValueError, match="步骤 0.*type.*必须是"):
            loader.load_template("invalid_type")


# =============================================================================
# apply_template MCP 工具测试
# =============================================================================


@pytest.mark.asyncio
class TestApplyTemplateTool:
    """测试 apply_template MCP 工具"""

    async def test_apply_template_basic(self, clean_env):
        """测试基本模板应用"""
        mock_manager = MagicMock()
        mock_session = MagicMock()
        mock_session.session_id = "test-session-123"
        mock_session.name = "测试会话"
        mock_session.thought_count.return_value = 2
        mock_manager.create_session.return_value = mock_session
        mock_manager.update_session.return_value = True

        with (
            patch("deep_thinking.tools.template.get_storage_manager", return_value=mock_manager),
            patch("deep_thinking.tools.template.TemplateLoader") as MockLoader,
        ):
            # Mock模板
            mock_template = {
                "template_id": "test",
                "name": "测试模板",
                "description": "测试描述",
                "structure": {
                    "steps": [
                        {"step_number": 1, "prompt": "第一步", "type": "regular"},
                        {"step_number": 2, "prompt": "第二步", "type": "regular"},
                    ]
                },
            }
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_template.return_value = mock_template
            MockLoader.return_value = mock_loader_instance

            result = await template.apply_template("test")

        assert "测试模板 已应用" in result
        assert "test-session-123" in result
        assert "第一步" in result
        assert "第二步" in result

    async def test_apply_template_with_context(self, clean_env):
        """测试带上下文的模板应用"""
        mock_manager = MagicMock()
        mock_session = MagicMock()
        mock_session.session_id = "test-session-123"
        mock_session.name = "测试会话"
        mock_session.thought_count.return_value = 1
        mock_manager.create_session.return_value = mock_session
        mock_manager.update_session.return_value = True

        with (
            patch("deep_thinking.tools.template.get_storage_manager", return_value=mock_manager),
            patch("deep_thinking.tools.template.TemplateLoader") as MockLoader,
        ):
            mock_template = {
                "template_id": "test",
                "name": "测试模板",
                "description": "测试描述",
                "structure": {"steps": [{"step_number": 1, "prompt": "第一步", "type": "regular"}]},
            }
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_template.return_value = mock_template
            MockLoader.return_value = mock_loader_instance

            result = await template.apply_template("test", "我的问题上下文")

        assert "我的问题上下文" in result

    async def test_apply_template_not_found(self, clean_env):
        """测试模板不存在时的错误处理"""
        mock_manager = MagicMock()

        with (
            patch("deep_thinking.tools.template.get_storage_manager", return_value=mock_manager),
            patch("deep_thinking.tools.template.TemplateLoader") as MockLoader,
        ):
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_template.side_effect = FileNotFoundError("模板不存在")
            mock_loader_instance.list_available_templates.return_value = ["t1", "t2"]
            MockLoader.return_value = mock_loader_instance

            with pytest.raises(ValueError, match="模板不存在"):
                await template.apply_template("nonexistent")


# =============================================================================
# list_templates MCP 工具测试
# =============================================================================


class TestListTemplatesTool:
    """测试 list_templates MCP 工具"""

    async def test_list_templates_all(self, clean_env):
        """测试列出所有模板"""
        with patch("deep_thinking.tools.template.TemplateLoader") as MockLoader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.list_templates.return_value = [
                {
                    "template_id": "problem_solving",
                    "name": "问题求解",
                    "description": "系统分析问题",
                    "category": "problem_solving",
                    "metadata": {"tags": ["问题"]},
                },
                {
                    "template_id": "decision_making",
                    "name": "决策",
                    "description": "做出决策",
                    "category": "decision",
                    "metadata": {"tags": ["决策"]},
                },
            ]
            MockLoader.return_value = mock_loader_instance

            result = await template.list_templates()

        assert "可用思考模板" in result
        assert "问题求解" in result
        assert "决策" in result
        assert "problem_solving" in result
        assert "decision_making" in result

    async def test_list_templates_with_category(self, clean_env):
        """测试按类别过滤模板"""
        with patch("deep_thinking.tools.template.TemplateLoader") as MockLoader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.list_templates.return_value = [
                {
                    "template_id": "decision_making",
                    "name": "决策",
                    "description": "做出决策",
                    "category": "decision",
                    "metadata": {},
                }
            ]
            MockLoader.return_value = mock_loader_instance

            result = await template.list_templates("decision")

        assert "类别过滤" in result
        assert "决策" in result

    async def test_list_templates_empty(self, clean_env):
        """测试空模板列表"""
        with patch("deep_thinking.tools.template.TemplateLoader") as MockLoader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.list_templates.return_value = []
            MockLoader.return_value = mock_loader_instance

            result = await template.list_templates()

        assert "没有找到匹配的模板" in result


# =============================================================================
# 辅助函数测试
# =============================================================================


class TestHelperFunctions:
    """测试辅助函数"""

    def test_normalize_format(self):
        """测试格式标准化"""
        from deep_thinking.tools.template import _normalize_format

        assert _normalize_format("json") == "json"
        assert _normalize_format("md") == "markdown"
        assert _normalize_format("markdown") == "markdown"
        assert _normalize_format("txt") == "text"
        assert _normalize_format("text") == "text"

        with pytest.raises(ValueError, match="不支持的格式"):
            _normalize_format("invalid")
