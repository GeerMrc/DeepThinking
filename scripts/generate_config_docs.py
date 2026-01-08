#!/usr/bin/env python3
"""
配置参数文档生成脚本

从代码中提取环境变量定义，生成标准化的Markdown配置参考文档。

功能：
- 扫描源代码文件，提取环境变量定义
- 解析环境变量的默认值和描述
- 生成标准化的Markdown配置参考表格
- 支持检查模式，验证文档与代码的一致性

使用方式：
    # 生成配置文档
    python scripts/generate_config_docs.py

    # 检查文档与代码的一致性
    python scripts/generate_config_docs.py --check

    # 输出到指定文件
    python scripts/generate_config_docs.py --output docs/configuration.md
"""

import argparse
import ast
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


class EnvVarExtractor:
    """环境变量提取器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.env_vars: Dict[str, Dict] = {}

    def extract_from_file(self, file_path: Path) -> None:
        """
        从Python文件中提取环境变量定义

        Args:
            file_path: Python文件路径
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 解析AST
            tree = ast.parse(content)

            # 遍历AST节点
            for node in ast.walk(tree):
                # 查找 os.getenv() 调用
                if isinstance(node, ast.Call):
                    if self._is_os_getenv(node):
                        var_name, default_value, context = self._parse_os_getenv(node, content)
                        if var_name:
                            self._add_env_var(var_name, default_value, context, file_path)

        except Exception as e:
            print(f"警告: 解析文件 {file_path} 失败: {e}", file=sys.stderr)

    def _is_os_getenv(self, node: ast.Call) -> bool:
        """检查是否为 os.getenv() 调用"""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return node.func.value.id == "os" and node.func.attr == "getenv"
        return False

    def _parse_os_getenv(
        self, node: ast.Call, source: str
    ) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        解析 os.getenv() 调用

        Returns:
            (变量名, 默认值, 上下文描述)
        """
        try:
            # 获取变量名（第一个参数）
            if node.args and isinstance(node.args[0], ast.Constant):
                var_name = node.args[0].value
            else:
                return None, None, None

            # 获取默认值（第二个参数或关键字参数）
            default_value = None
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                default_value = node.args[1].value
            elif len(node.args) >= 2 and isinstance(node.args[1], ast.Call):
                # 处理 int() 包装的情况
                if isinstance(node.args[1].func, ast.Name) and node.args[1].func.id == "int":
                    if node.args[1].args and isinstance(node.args[1].args[0], ast.Constant):
                        default_value = node.args[1].args[0].value

            # 获取上下文行（用于提取描述）
            line_num = node.lineno
            lines = source.split("\n")
            context = ""
            if 0 <= line_num - 1 < len(lines):
                context = lines[line_num - 1].strip()

            return var_name, str(default_value) if default_value is not None else None, context

        except Exception:
            return None, None, None

    def _add_env_var(
        self, name: str, default: Optional[str], context: str, file_path: Path
    ) -> None:
        """添加或更新环境变量"""
        if name not in self.env_vars:
            self.env_vars[name] = {
                "name": name,
                "default": default,
                "description": "",
                "file": str(file_path.relative_to(self.project_root)),
                "contexts": [],
            }

        if context:
            self.env_vars[name]["contexts"].append(context)

    def extract_from_env_example(self, file_path: Path) -> None:
        """
        从 .env.example 文件中提取环境变量定义

        Args:
            file_path: .env.example 文件路径
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 解析环境变量定义
            for line in content.split("\n"):
                line = line.strip()

                # 跳过注释和空行
                if not line or line.startswith("#"):
                    continue

                # 解析变量定义
                match = re.match(r"^([A-Z_]+)=(.*)$", line)
                if match:
                    var_name = match.group(1)
                    default_value = match.group(2)

                    # 提取前面的注释作为描述
                    description = self._extract_description(content, line, var_name)

                    if var_name not in self.env_vars:
                        self.env_vars[var_name] = {
                            "name": var_name,
                            "default": default_value if default_value else None,
                            "description": description,
                            "file": str(file_path.relative_to(self.project_root)),
                            "contexts": [],
                        }
                    else:
                        if description:
                            self.env_vars[var_name]["description"] = description
                        if default_value:
                            self.env_vars[var_name]["default"] = default_value

        except Exception as e:
            print(f"警告: 解析文件 {file_path} 失败: {e}", file=sys.stderr)

    def _extract_description(self, content: str, line: str, var_name: str) -> str:
        """提取环境变量的描述（从注释中）"""
        line_pos = content.find(line)
        if line_pos == -1:
            return ""

        # 向前查找注释
        before = content[:line_pos]
        lines = before.split("\n")

        description = ""
        for comment_line in reversed(lines):
            comment_line = comment_line.strip()
            if comment_line.startswith("#"):
                desc_text = comment_line[1:].strip()
                # 跳过特殊标记
                if desc_text and not desc_text.startswith("="):
                    description = desc_text + " " + description
            else:
                break

        return description.strip()

    def get_sorted_vars(self) -> List[Dict]:
        """获取排序后的环境变量列表"""
        # 按类别分组
        categories = {
            "传输模式配置": [],
            "SSE模式配置": [],
            "日志配置": [],
            "存储配置": [],
            "思考配置": [],
            "服务器配置": [],
            "开发选项": [],
            "其他": [],
        }

        for var in self.env_vars.values():
            name = var["name"]

            if "TRANSPORT" in name:
                categories["传输模式配置"].append(var)
            elif name in ["HOST", "PORT", "AUTH_TOKEN", "API_KEY"]:
                categories["SSE模式配置"].append(var)
            elif "LOG_LEVEL" in name:
                categories["日志配置"].append(var)
            elif "DATA_DIR" in name or "BACKUP" in name:
                categories["存储配置"].append(var)
            elif "THOUGHT" in name or "THINKING" in name:
                if "MAX" in name or "MIN" in name or "INCREMENT" in name:
                    categories["思考配置"].append(var)
                else:
                    categories["服务器配置"].append(var)
            elif "DEV" in name or "PROFILE" in name:
                categories["开发选项"].append(var)
            else:
                categories["其他"].append(var)

        # 展平为列表（跳过空类别）
        result = []
        for category, vars_list in categories.items():
            if vars_list:
                result.append({"category": category, "vars": vars_list})

        return result


def generate_markdown(env_vars_data: List[Dict]) -> str:
    """
    生成Markdown格式的配置参考文档

    Args:
        env_vars_data: 环境变量数据（按类别分组）

    Returns:
        Markdown文档
    """
    lines = [
        "# 配置参数参考",
        "",
        "> 本文档由 `scripts/generate_config_docs.py` 自动生成，请勿手动编辑。",
        "",
        "本文档提供所有环境变量的完整参考，确保配置参数与代码实现100%一致。",
        "",
        "## 📋 目录",
        "",
        "- [环境变量完整参考](#环境变量完整参考)",
        "  - [传输模式配置](#传输模式配置)",
        "  - [SSE模式配置](#sse模式配置)",
        "  - [日志配置](#日志配置)",
        "  - [存储配置](#存储配置)",
        "  - [思考配置](#思考配置)",
        "  - [服务器配置](#服务器配置)",
        "  - [开发选项](#开发选项)",
        "- [配置文件位置](#配置文件位置)",
        "- [传输模式配置](#传输模式配置-1)",
        "- [高级配置](#高级配置)",
        "",
        "## 环境变量完整参考",
        "",
    ]

    for category_data in env_vars_data:
        category = category_data["category"]
        vars_list = category_data["vars"]

        lines.append(f"### {category}")
        lines.append("")

        lines.append("| 环境变量 | 默认值 | 描述 |")
        lines.append("|---------|--------|------|")

        for var in vars_list:
            name = var["name"]
            default = var.get("default") or "未设置"
            description = var.get("description") or "从代码自动提取"
            lines.append(f"| `{name}` | {default} | {description} |")

        lines.append("")

    # 添加配置文件位置章节
    lines.extend([
        "## 配置文件位置",
        "",
        "### 默认存储路径",
        "",
        "数据存储目录：`~/.deepthinking/`",
        "",
        "目录结构：",
        "```",
        "~/.deepthinking/",
        "├── sessions/              # 会话数据目录",
        "│   ├── .index.json       # 会话索引文件",
        "│   └── *.json            # 各个会话的数据文件",
        "├── .backups/             # 自动备份目录",
        "│   └── sessions/         # 会话备份",
        "├── .gitignore            # 防止数据提交到版本控制",
        "└── tasks.json            # 任务列表存储",
        "```",
        "",
        "### 环境变量配置方式",
        "",
        "**方式1：使用 .env 文件**（推荐）",
        "",
        "在项目根目录创建 `.env` 文件：",
        "```bash",
        "# 复制示例配置",
        "cp .env.example .env",
        "",
        "# 编辑配置",
        "nano .env",
        "```",
        "",
        "**方式2：使用系统环境变量**",
        "",
        "在 `~/.bashrc` 或 `~/.zshrc` 中添加：",
        "```bash",
        "export DEEP_THINKING_DATA_DIR=/custom/path",
        "export DEEP_THINKING_LOG_LEVEL=DEBUG",
        "```",
        "",
        "**方式3：使用 CLI 参数**",
        "",
        "```bash",
        "python -m deep_thinking --data-dir /custom/path --log-level DEBUG",
        "```",
        "",
        "### 配置优先级",
        "",
        "``CLI 参数 > 环境变量 > 默认值```",
        "",
        "## 传输模式配置",
        "",
        "### STDIO 模式（本地）",
        "",
        "适用于本地开发场景，通过标准输入输出进行通信。",
        "",
        "**配置示例**：",
        "",
        "在 `.env` 文件中：",
        "```bash",
        "DEEP_THINKING_TRANSPORT=stdio",
        "```",
        "",
        "### SSE 模式（远程）",
        "",
        "适用于远程服务器部署，通过 HTTP Server-Sent Events 进行通信。",
        "",
        "**配置示例**：",
        "",
        "在 `.env` 文件中：",
        "```bash",
        "DEEP_THINKING_TRANSPORT=sse",
        "DEEP_THINKING_HOST=localhost",
        "DEEP_THINKING_PORT=8000",
        "```",
        "",
        "**认证配置**（可选）：",
        "",
        "```bash",
        "# Bearer Token 认证",
        "DEEP_THINKING_AUTH_TOKEN=your-secret-token-here",
        "",
        "# API Key 认证",
        "DEEP_THINKING_API_KEY=your-api-key-here",
        "```",
        "",
        "详细的 SSE 配置指南请参考：[SSE 配置指南](./sse-guide.md)",
        "",
        "## 高级配置",
        "",
        "### 思考参数配置",
        "",
        "DeepThinking MCP 支持配置思考步骤的限制范围，防止无限循环：",
        "",
        "| 参数 | 默认值 | 范围 | 推荐值 | 说明 |",
        "|------|--------|------|--------|------|",
        "| `DEEP_THINKING_MAX_THOUGHTS` | 50 | 1-10000 | 50 | 最大思考步骤数 |",
        "| `DEEP_THINKING_MIN_THOUGHTS` | 3 | 1-10000 | 3 | 最小思考步骤数 |",
        "| `DEEP_THINKING_THOUGHTS_INCREMENT` | 10 | 1-100 | 10 | 思考步骤增量 |",
        "",
        "**配置建议**：",
        "",
        "- **简单任务**：使用默认值即可",
        "- **复杂任务**：适当增加 `MAX_THOUGHTS` 到 100-200",
        "- **防止失控**：设置合理的 `MAX_THOUGHTS` 上限",
        "- **增量思考**：使用 `THOUGHTS_INCREMENT` 控制思考步骤的增量",
        "",
        "### 日志配置",
        "",
        "日志级别控制输出的详细程度：",
        "",
        "| 级别 | 输出内容 | 使用场景 |",
        "|------|---------|----------|",
        "| `DEBUG` | 所有调试信息 | 开发调试 |",
        "| `INFO` | 一般信息（默认） | 正常运行 |",
        "| `WARNING` | 警告信息 | 生产环境 |",
        "| `ERROR` | 仅错误信息 | 生产环境 |",
        "",
        "**配置示例**：",
        "",
        "```bash",
        "# 开发环境",
        "DEEP_THINKING_LOG_LEVEL=DEBUG",
        "",
        "# 生产环境",
        "DEEP_THINKING_LOG_LEVEL=INFO",
        "```",
        "",
        "### 存储配置",
        "",
        "自定义数据存储目录：",
        "",
        "```bash",
        "# 使用绝对路径",
        "DEEP_THINKING_DATA_DIR=/opt/deepthinking",
        "",
        "# 使用相对路径",
        "DEEP_THINKING_DATA_DIR=./data",
        "",
        "# 使用 ~ 路径（自动扩展）",
        "DEEP_THINKING_DATA_DIR=~/custom-deepthinking",
        "",
        "# 使用环境变量",
        "DEEP_THINKING_DATA_DIR=$HOME/data",
        "```",
        "",
        "**路径扩展支持**：",
        "",
        "- `~` 自动扩展为用户主目录",
        "- `$HOME` 等环境变量自动扩展",
        "- 相对路径相对于当前工作目录",
        "",
        "### 服务器描述配置",
        "",
        "自定义 MCP 服务器的描述（在 MCP 工具列表中显示）：",
        "",
        "```bash",
        'DEEP_THINKING_DESCRIPTION="我的 AI 助手服务器"',
        "```",
        "",
        "**说明**：",
        "- 如果不设置，使用默认描述",
        "- 默认值：`深度思考MCP服务器 - 高级思维编排引擎，提供顺序思考,适合处理多步骤、跨工具的复杂任务,会话管理和状态持久化功能`",
        "",
        "### 开发选项",
        "",
        "**启用开发模式**（暂未实现）：",
        "",
        "```bash",
        "DEEP_THINKING_DEV=true",
        "```",
        "",
        "**启用性能分析**（暂未实现）：",
        "",
        "```bash",
        "DEEP_THINKING_PROFILE=true",
        "```",
        "",
        "---",
        "",
        "## 相关文档",
        "",
        "- [安装指南](./installation.md) - 快速安装和配置",
        "- [IDE 集成配置](./ide-config.md) - 各种 IDE 的配置示例",
        "- [用户指南](./user_guide.md) - 使用指南和最佳实践",
        "- [API 参考](./api.md) - 完整的 API 文档",
        "",
        "---",
        "",
        "> **提示**：本文档由 `scripts/generate_config_docs.py` 自动生成，",
        "> 如需更新配置参数，请修改源代码中的 docstring 或 `.env.example` 文件，",
        "> 然后重新运行脚本生成文档。",
        "",
    ])

    return "\n".join(lines)


def check_consistency(
    generated_content: str, existing_file: Optional[Path]
) -> bool:
    """
    检查生成的文档与现有文档的一致性

    Args:
        generated_content: 生成的文档内容
        existing_file: 现有文档路径

    Returns:
        是否一致
    """
    if not existing_file or not existing_file.exists():
        print("现有文档不存在，跳过一致性检查")
        return True

    with open(existing_file, "r", encoding="utf-8") as f:
        existing_content = f.read()

    # 提取表格部分进行比较（忽略自动生成标记）
    gen_lines = [line for line in generated_content.split("\n")
                 if not line.strip().startswith("> 本文档由")]
    existing_lines = [line for line in existing_content.split("\n")
                     if not line.strip().startswith("> 本文档由")]

    if gen_lines == existing_lines:
        print("✅ 文档与代码一致")
        return True
    else:
        print("❌ 文档与代码不一致，需要更新")
        print("\n差异：")
        for i, (gen, ex) in enumerate(zip(gen_lines, existing_lines)):
            if gen != ex:
                print(f"  行 {i+1}:")
                print(f"    生成: {gen}")
                print(f"    现有: {ex}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="从代码生成配置参数文档"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="检查文档与代码的一致性（不写入文件）"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="输出文件路径（默认: docs/configuration.md）"
    )

    args = parser.parse_args()

    # 项目根目录
    project_root = Path(__file__).parent.parent

    # 输出文件路径
    output_file = args.output or project_root / "docs" / "configuration.md"

    # 创建提取器
    extractor = EnvVarExtractor(project_root)

    # 从源代码文件提取
    source_files = [
        project_root / "src" / "deep_thinking" / "__main__.py",
        project_root / "src" / "deep_thinking" / "server.py",
    ]

    for source_file in source_files:
        if source_file.exists():
            extractor.extract_from_file(source_file)

    # 从 .env.example 提取
    env_example = project_root / ".env.example"
    if env_example.exists():
        extractor.extract_from_env_example(env_example)

    # 获取排序后的环境变量
    env_vars_data = extractor.get_sorted_vars()

    # 生成 Markdown 文档
    markdown_content = generate_markdown(env_vars_data)

    # 检查模式
    if args.check:
        consistency = check_consistency(markdown_content, output_file)
        sys.exit(0 if consistency else 1)

    # 写入文件
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"✅ 配置文档已生成: {output_file}")
    print(f"   提取了 {len(extractor.env_vars)} 个环境变量")


if __name__ == "__main__":
    main()
