"""
模板加载工具

提供模板的加载、解析和管理功能。
"""

import json
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class TemplateLoader:
    """
    模板加载器

    负责从文件系统加载和管理思考模板。
    """

    def __init__(self, templates_dir: Path | None = None):
        """
        初始化模板加载器

        Args:
            templates_dir: 模板目录路径，默认为包内 templates 目录
        """
        if templates_dir is None:
            # 使用包内的 templates 目录
            import deep_thinking.templates as templates_module

            self.templates_dir = Path(templates_module.__file__).parent
        else:
            self.templates_dir = Path(templates_dir)

        logger.debug(f"模板加载器初始化，目录: {self.templates_dir}")

    def load_template(self, template_id: str) -> dict[str, Any]:
        """
        加载指定模板

        Args:
            template_id: 模板ID（不含文件扩展名）

        Returns:
            模板数据字典

        Raises:
            FileNotFoundError: 模板文件不存在
            ValueError: 模板格式无效
        """
        # 构建文件路径
        template_file = self.templates_dir / f"{template_id}.json"

        if not template_file.exists():
            # 尝试搜索所有模板文件
            available = self.list_available_templates()
            raise FileNotFoundError(f"模板不存在: {template_id}。可用模板: {', '.join(available)}")

        try:
            with template_file.open("r", encoding="utf-8") as f:
                template_data: dict[str, Any] = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"模板文件格式错误 ({template_file}): {e}") from e

        # 验证模板格式
        self._validate_template(template_data)

        logger.debug(f"成功加载模板: {template_id}")
        return template_data

    def list_available_templates(self) -> list[str]:
        """
        列出所有可用的模板ID

        Returns:
            模板ID列表
        """
        if not self.templates_dir.exists():
            logger.warning(f"模板目录不存在: {self.templates_dir}")
            return []

        template_ids: list[str] = []
        for json_file in self.templates_dir.glob("*.json"):
            template_ids.append(json_file.stem)

        logger.debug(f"找到 {len(template_ids)} 个模板: {template_ids}")
        return sorted(template_ids)

    def get_template_info(self, template_id: str) -> dict[str, Any]:
        """
        获取模板的基本信息

        Args:
            template_id: 模板ID

        Returns:
            模板信息字典（包含 name, description, metadata 等）

        Raises:
            FileNotFoundError: 模板不存在
        """
        template = self.load_template(template_id)

        return {
            "template_id": template.get("template_id", template_id),
            "name": template.get("name", ""),
            "description": template.get("description", ""),
            "category": template.get("category", ""),
            "metadata": template.get("metadata", {}),
        }

    def list_templates(self) -> list[dict[str, Any]]:
        """
        列出所有模板及其基本信息

        Returns:
            模板信息列表
        """
        templates: list[dict[str, Any]] = []

        for template_id in self.list_available_templates():
            try:
                info: dict[str, Any] = self.get_template_info(template_id)
                templates.append(info)
            except Exception as e:
                logger.error(f"获取模板信息失败 ({template_id}): {e}")

        return templates

    def iter_templates(self) -> Iterator[dict[str, Any]]:
        """
        迭代所有模板

        Yields:
            模板数据字典
        """
        for template_id in self.list_available_templates():
            try:
                yield self.load_template(template_id)
            except Exception as e:
                logger.error(f"加载模板失败 ({template_id}): {e}")

    def _validate_template(self, template_data: dict[str, Any]) -> None:
        """
        验证模板格式

        Args:
            template_data: 模板数据

        Raises:
            ValueError: 模板格式无效
        """
        required_fields = ["template_id", "name", "description", "structure"]

        for field in required_fields:
            if field not in template_data:
                raise ValueError(f"模板缺少必需字段: {field}")

        # 验证 structure 格式
        structure = template_data.get("structure", {})
        if not isinstance(structure, dict):
            raise ValueError("template.structure 必须是字典类型")

        steps = structure.get("steps", [])
        if not isinstance(steps, list):
            raise ValueError("template.structure.steps 必须是列表类型")

        # 验证每个步骤
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                raise ValueError(f"步骤 {i} 必须是字典类型")

            if "step_number" not in step:
                raise ValueError(f"步骤 {i} 缺少 step_number 字段")

            if "prompt" not in step:
                raise ValueError(f"步骤 {i} 缺少 prompt 字段")

            if "type" not in step:
                raise ValueError(f"步骤 {i} 缺少 type 字段")

            # 验证 type 值
            valid_types = ["regular", "revision", "branch"]
            if step["type"] not in valid_types:
                raise ValueError(f"步骤 {i} 的 type 必须是: {', '.join(valid_types)}")


__all__ = [
    "TemplateLoader",
]
