# PyPI 发布指南

> 📅 版本: 1.0.0
> 🎯 目的: 指导开发者将 Deep-Thinking-MCP 发布到 PyPI

---

## 📋 前置条件

### 1. PyPI 账号

- 注册 PyPI 账号: https://pypi.org/account/register/
- 启用双因素认证（2FA）
- 验证电子邮件地址

### 2. 包名检查

```bash
# 检查包名是否可用
pip search Deep-Thinking-MCP

# 或访问 PyPI 搜索
# https://pypi.org/search/?q=Deep-Thinking-MCP
```

**重要提示**: 包名必须是全局唯一的，建议使用前先确认。

### 3. 准备工具

```bash
# 安装构建工具
pip install build twine

# 或使用 uv
pip install uv
```

---

## 🔧 准备发布

### 第一步: 检查项目配置

确保 `pyproject.toml` 包含所有必需信息：

```toml
[project]
name = "Deep-Thinking-MCP"           # 包名
version = "0.1.0"                      # 版本号（遵循PEP 440）
description = "高级深度思考MCP服务器"   # 简短描述
readme = "README.md"                   # README文件
license = {text = "MIT"}               # 许可证
requires-python = ">=3.10"            # Python版本要求
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]

# 关键: 项目URL
[project.urls]
Homepage = "https://github.com/your-org/Deep-Thinking-MCP"
Repository = "https://github.com/your-org/Deep-Thinking-MCP"
Issues = "https://github.com/your-org/Deep-Thinking-MCP/issues"

# 关键: 包分类
[project.optional-dependencies]
dev = ["pytest>=7.0", "ruff>=0.1.0", "mypy>=1.0.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**必需检查清单:**

- [ ] `name` - 包名（小写，连字符分隔）
- [ ] `version` - 版本号（当前: 0.1.0）
- [ ] `description` - 简短描述
- [ ] `readme` - README文件路径
- [ ] `license` - 开源许可证
- [ ] `requires-python` - Python版本要求
- [ ] `authors` - 作者信息
- [ ] `urls` - 项目链接
- [ ] `build-system` - 构建系统配置

### 第二步: 准备 README.md

PyPI 会渲染 README.md 作为项目主页，确保：

```markdown
# DeepThinking MCP

一个强大的MCP服务器，提供深度思考能力。

## 功能特性

- 🔍 顺序思考工具
- 💾 会话管理
- 📊 数据导出
- 🎨 可视化
- 📋 模板系统

## 安装

```bash
pip install Deep-Thinking-MCP
```

## 使用示例

...

## 许可证

MIT License
```

### 第三步: 验证版本号

版本号必须遵循 [PEP 440](https://peps.python.org/pep/pep-0440/) 规范：

```bash
# 检查当前版本
grep "version = " pyproject.toml

# 示例正确版本号:
0.1.0      ✅ 初始发布
0.2.0      ✅ 次要版本（新功能，向后兼容）
1.0.0      ✅ 主要版本（破坏性变更）
0.1.1      ✅ 补丁版本（bug修复）
0.1.0a1    ✅ Alpha版本
0.1.0b1    ✅ Beta版本
0.1.0rc1   ✅ Release Candidate

# 错误示例:
v0.1.0     ❌ 不要带v前缀
0.1        ❌ 三个部分都要有
1.0        ❌ 三个部分都要有
```

---

## 🏗️ 构建发布包

### 清理旧构建文件

```bash
# 清理旧的构建产物
rm -rf dist/ build/ *.egg-info .venv __pycache__

# 清理Python缓存
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### 使用传统方式构建

```bash
# 使用 build 模块
python -m build

# 这将在 dist/ 目录下创建:
# - deep_thinking_mcp-0.1.0.tar.gz  (源码包)
# - deep_thinking_mcp-0.1.0-py3-none-any.whl  (wheel包)
```

### 使用 uv 构建（推荐）

```bash
# uv 构建更快
uv build

# 输出相同，但速度更快
```

### 验证构建包

```bash
# 检查dist目录
ls -lh dist/

# 应该看到:
# deep_thinking_mcp-0.1.0.tar.gz
# deep_thinking_mcp-0.1.0-py3-none-any.whl
```

---

## 🧪 测试发布包

### 在测试PyPI上测试

在正式发布前，强烈建议先在 TestPyPI 上测试：

#### 安装 TestPyPI 工具

```bash
pip install twine
```

#### 发布到 TestPyPI

```bash
# 使用 twine 上传到 TestPyPI
python -m twine upload --repository testpypi dist/*
```

#### 从 TestPyPI 安装测试

```bash
# 创建临时虚拟环境测试
python -m venv test_env
source test_env/bin/activate

# 从 TestPyPI 安装
pip install --index-url https://test.pypi.org/simple/ Deep-Thinking-MCP

# 验证安装
python -c "import deep_thinking; print('✅ TestPyPI安装成功')"

# 清理测试环境
deactivate
rm -rf test_env
```

---

## 🚀 正式发布到 PyPI

### 方法1: 使用 Twine（推荐）

#### 配置 ~/.pypirc

创建 `~/.pypirc` 文件（简化上传流程）：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = <your-api-token>

[testpypi]
username = __token__
password = <your-testpypi-api-token>
```

**获取 API Token:**

1. 登录 PyPI: https://pypi.org/manage/account/token/
2. 创建新的 API token
3. 选择范围: "Entire account" 或 "Project: Deep-Thinking-MCP"
4. 复制 token（只显示一次！）

#### 上传到 PyPI

```bash
# 使用 twine 上传
python -m twine upload dist/*
```

**上传参数说明:**

```bash
# 跳过已有文件检查
python -m twine upload --skip-existing dist/*

# 签名发布（高级）
python -m twine upload --sign dist/*
```

### 方法2: 使用 UV 发布

```bash
# 使用 uv 直接发布
uv publish dist/*

# 或指定仓库
uv publish --repository pypi dist/*
```

---

## 📦 发布后验证

### 1. 检查 PyPI 页面

访问: https://pypi.org/project/Deep-Thinking-MCP/

确认:
- [ ] 包信息正确显示
- [ ] README 正确渲染
- [ ] 版本号正确
- [ ] 项目链接有效

### 2. 测试从 PyPI 安装

```bash
# 创建新的虚拟环境
python -m venv verify_env
source verify_env/bin/activate

# 从 PyPI 安装
pip install Deep-Thinking-MCP

# 验证功能
python -c "import deep_thinking; print(deep_thinking.__version__)"

# 清理
deactivate
rm -rf verify_env
```

### 3. 验证不同安装方式

```bash
# 测试 pip 安装
pip install Deep-Thinking-MCP

# 测试 uv 安装
uv pip install Deep-Thinking-MCP

# 测试可编辑模式（如果需要）
pip install -e .
```

---

## 📝 发布新版本

### 版本号更新流程

#### 1. 更新版本号

编辑 `pyproject.toml`:

```toml
version = "0.2.0"  # 从 0.1.0 升级
```

#### 2. 更新 CHANGELOG.md

```markdown
## [0.2.0] - 2025-12-31

### 新增
- 添加XXX功能

### 修复
- 修复XXX问题

### 变更
- XXX行为变更
```

#### 3. 创建 Git 标签

```bash
# 创建版本标签
git tag v0.2.0

# 推送标签到远程
git push origin v0.2.0
```

#### 4. 构建和发布

```bash
# 清理旧构建
rm -rf dist/ build/

# 构建新版本
uv build

# 发布到 PyPI
uv publish dist/*
```

---

## 🛡️ 安全最佳实践

### 1. 使用 API Token

✅ **推荐**:
```bash
# 使用 API Token（存储在 ~/.pypirc）
password = <pypi-token>
```

❌ **不推荐**:
```bash
# 使用账号密码（已弃用）
# twine 会提示输入用户名和密码
```

### 2. 使用 TestPyPI 测试

```bash
# 总是先在 TestPyPI 测试
python -m twine upload --repository testpypi dist/*

# 确认无误后再发布到 PyPI
python -m twine upload dist/*
```

### 3. 验证包内容

```bash
# 检查wheel包内容
python -m zipfile -l dist/deep_thinking_mcp-0.1.0-py3-none-any.whl

# 检查源码包内容
tar -tzf dist/deep_thinking_mcp-0.1.0.tar.gz
```

---

## ⚠️ 常见问题

### 问题1: 包名已存在

**错误**:
```
HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
File already exists
```

**解决方案**:
- 更换包名
- 或使用新版本号

---

### 问题2: 版本号已存在

**错误**:
```
File already exists
deep_thinking_mcp-0.1.0.tar.gz
```

**解决方案**:
```bash
# 更新版本号
# 0.1.0 -> 0.1.1 或 0.2.0

# 重新构建
uv build

# 发布新版本
uv publish dist/*
```

---

### 问题3: README 格式错误

**错误**:
```
400 Bad Request
The description failed to render in the default formats.
```

**解决方案**:
- 确保 README.md 是有效的 Markdown
- 检查特殊字符是否正确转义
- 使用在线 Markdown 验证器检查

---

### 问题4: 无效的元数据

**错误**:
```
400 Bad Request
Invalid value for requires_python
```

**解决方案**:
```toml
# 确保版本号格式正确
requires-python = ">=3.10"    # ✅ 正确
requires-python = "3.10+"      # ❌ 错误
requires-python = ">=3.10,<4.0" # ✅ 正确
```

---

### 问题5: 构建系统错误

**错误**:
```
Error: Build backend is not available
```

**解决方案**:
```bash
# 确保构建后端已安装
pip install hatchling

# 或更新 build
pip install --upgrade build
```

---

## 📋 发布检查清单

### 发布前

- [ ] PyPI 账号已创建并验证
- [ ] 包名已检查且可用
- [ ] 版本号已更新（遵循PEP 440）
- [ ] README.md 完整且格式正确
- [ ] pyproject.toml 包含所有必需字段
- [ ] 所有依赖已声明
- [ ] License 已明确
- [ ] CHANGELOG.md 已更新
- [ ] Git 标签已创建
- [ ] 代码已提交到 Git
- [ ] 在 TestPyPI 上测试通过

### 发布中

- [ ] 旧构建文件已清理
- [ ] 新构建包已生成
- [ ] 构建包内容已验证
- [ ] 使用 Twine 或 UV 上传
- [ ] 上传成功无错误

### 发布后

- [ ] PyPI 页面信息正确
- [ ] 从 PyPI 安装测试通过
- [ ] 基本功能验证通过
- [ ] Release 已在 GitHub 创建
- [ ] 用户已通知新版本发布

---

## 🔄 自动化发布脚本

### 创建发布脚本

创建 `scripts/publish.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 开始发布 Deep-Thinking-MCP 到 PyPI"

# 检查是否在正确的分支
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ 错误: 请在 main 分支发布"
    exit 1
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ 错误: 有未提交的更改"
    exit 1
fi

# 获取版本号
VERSION=$(grep "^version = " pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "📦 发布版本: $VERSION"

# 清理旧构建
echo "🧹 清理旧构建..."
rm -rf dist/ build/ *.egg-info

# 构建
echo "🏗️ 构建发布包..."
uv build

# 检查构建产物
echo "✅ 验证构建产物..."
ls -lh dist/

# 询问确认
read -p "确认发布版本 $VERSION 到 PyPI? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 发布已取消"
    exit 1
fi

# 先发布到 TestPyPI
echo "🧪 发布到 TestPyPI..."
python -m twine upload --repository testpypi dist/*

read -p "TestPyPI 测试通过? 继续发布到 PyPI? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 发布已取消"
    exit 1
fi

# 发布到 PyPI
echo "🚀 发布到 PyPI..."
uv publish dist/*

# 创建 Git 标签
echo "🏷️ 创建 Git 标签 v$VERSION..."
git tag -a "v$VERSION" -m "Release version $VERSION"
git push origin "v$VERSION"

echo "✅ 发布完成！"
echo "📦 PyPI: https://pypi.org/project/Deep-Thinking-MCP/"
```

**使用脚本:**

```bash
# 添加执行权限
chmod +x scripts/publish.sh

# 运行发布脚本
./scripts/publish.sh
```

---

## 📚 参考资源

### 官方文档
- [PyPI - Packaging Tutorial](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [PEP 440 - Version Identification](https://peps.python.org/pep/pep-0440/)
- [PyPI Upload](https://pypi.org/help/#uploading)

### 工具
- [build](https://pypi.org/project/build/) - 构建工具
- [twine](https://pypi.org/project/twine/) - 上传工具
- [uv](https://github.com/astral-sh/uv) - 现代包管理器

### 验证工具
- [PyPI README Renderer](https://pypi.org/manage/project/<project-name>/rendering/)
- [Check Project Name Availability](https://pypi.org/search/)

---

## 📞 支持

如果遇到问题:

1. 查看 [PyPI FAQ](https://pypi.org/help/)
2. 搜索 [GitHub Issues](https://github.com/your-org/Deep-Thinking-MCP/issues)
3. 提交新的 Issue

---

> ✅ **更新日期**: 2025-12-31
> 📋 **文档版本**: 1.0.0
> 🎯 **适用项目**: Deep-Thinking-MCP
