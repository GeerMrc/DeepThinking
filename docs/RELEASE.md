# PyPI 发布指南

> 📦 本文档描述如何将 DeepThinking MCP 发布到 PyPI

## 目录

- [快速配置](#快速配置-推荐)
- [发布前准备](#发布前准备)
- [发布方式](#发布方式)
- [安全注意事项](#安全注意事项)
- [未来项目复用](#未来项目复用)
- [发布检查清单](#发布检查清单)
- [版本管理](#版本管理)
- [Makefile 命令参考](#makefile-命令参考)
- [环境变量配置](#环境变量配置)
- [常见问题](#常见问题)
- [发布后验证](#发布后验证)
- [常见报错及处理](#常见报错及处理)
- [回滚](#回滚)
- [相关链接](#相关链接)

---

## 快速配置（推荐）

### 一键配置所有环境

首次发布时，运行以下命令配置全局环境（**仅需配置一次，所有项目通用**）：

```bash
# 一键配置：全局 Token + GitHub Secret
make setup-all TOKEN=pypi-AgEIcHlwaS5vcmcC...
```

配置完成后：
- ✅ 所有项目都可以直接使用 `make publish` 发布
- ✅ 推送 git tag 自动触发 GitHub Actions 发布
- ✅ 无需重复输入 Token

### 分步配置

如果需要分步配置：

```bash
# 1. 配置全局 PyPI Token（所有项目通用）
make setup-token TOKEN=pypi-AgEIcHlwaS5vcmcC...

# 2. 配置当前项目的 GitHub Secret（用于自动化发布）
make setup-github TOKEN=pypi-AgEIcHlwaS5vcmcC...
```

### 配置说明

| 配置项 | 作用 | 范围 | 是否必需 |
|--------|------|------|----------|
| 全局 Token | 本地发布认证 | 所有项目 | 推荐配置 |
| GitHub Secret | 自动化发布认证 | 单个仓库 | 可选 |

---

## 发布前准备

### 1. PyPI 账户配置

确保你已：
- 注册 [PyPI 账户](https://pypi.org/account/register/)
- 创建 API Token（推荐）或配置密码认证
- 验证邮箱地址

### 2. 创建 PyPI API Token

1. 访问 https://pypi.org/manage/account/token/
2. 点击 "Add API Token"
3. 选择 "Entire account" 范围
4. 输入描述（如 "Development - All Projects"）
5. **立即复制 Token**（只显示一次！）

### 3. 本地工具安装

```bash
# 安装发布工具
pip install build twine

# 或使用 uv
uv pip install build twine

# 安装 gh CLI（用于配置 GitHub Secrets）
brew install gh  # macOS
# 或访问 https://cli.github.com/
```

---

## 发布方式

### 方式一：GitHub Actions 自动发布（推荐）⭐

#### 工作原理

GitHub Actions 会在推送 `v*` 格式的 tag 时自动触发发布流程：

```
推送 tag → 运行测试 → 代码检查 → 构建包 → 发布 PyPI → 创建 Release
```

#### 配置说明

| 配置项 | 是否每个项目需要 | 说明 |
|--------|-----------------|------|
| `.github/workflows/publish.yml` | ✅ 是 | 每个项目需要自己的工作流文件 |
| GitHub Secret `PYPI_API_TOKEN` | ✅ 是 | **每个仓库单独配置**（仓库级别隔离） |
| 全局 Token | ❌ 否 | 本地发布时使用，与 GitHub Actions 无关 |

> **重要提示**：GitHub Secret 是**仓库级别**的隔离，不是全局的！每个项目仓库需要单独配置 Secret。

#### 配置步骤

**1. 复制工作流文件到新项目**

```bash
# 复制 GitHub Actions 配置
cp -r /path/to/DeepThinking/.github/workflows /path/to/new-project/.github/
```

**2. 配置 GitHub Secret**

```bash
# 方法A：使用脚本自动配置（推荐）
cd /path/to/new-project
make setup-github TOKEN=pypi-AgEIcHlwaS5vcmcC...

# 方法B：手动配置
# 1. 访问仓库 Settings → Secrets and variables → Actions
# 2. 点击 "New repository secret"
# 3. Name: PYPI_API_TOKEN
# 4. Value: 你的 PyPI Token
```

#### 发布流程

```bash
# 1. 更新版本号
vim pyproject.toml  # version = "0.2.4"

# 2. 更新 CHANGELOG.md
vim CHANGELOG.md

# 3. 提交更改
git add -A
git commit -m "chore: prepare for release v0.2.4"

# 4. 创建 tag 并推送（触发自动发布）
git tag v0.2.4
git push origin v0.2.4
```

#### 查看发布状态

- **GitHub Actions**：访问仓库的 Actions 标签页
- **自动创建 GitHub Release**：发布成功后会自动创建
- **PyPI 包**：自动发布到 https://pypi.org/project/DeepThinking/

### 方式二：Makefile 本地发布

**前提**：已运行 `make setup-token` 配置全局 Token

```bash
# 完整发布流程（检查 + 构建 + 发布）
make release

# 分步执行
make release-check  # 发布前检查
make build          # 构建分发包
make verify         # 验证分发包
make publish        # 发布到 PyPI（无需输入 Token）
```

### 方式三：手动发布

```bash
# 1. 运行测试
pytest

# 2. 代码格式化
ruff format src/ tests/
ruff check src/ tests/

# 3. 类型检查
mypy src/deep_thinking/

# 4. 构建分发包
python -m build

# 5. 检查分发包
twine check dist/*

# 6. 发布到 PyPI
twine upload dist/* --username __token__ --password YOUR_API_TOKEN
```

---

## 安全注意事项

### 🔒 Token 安全最佳实践

#### 1. 永远不要将 Token 提交到代码仓库

```bash
# ❌ 错误：Token 会被提交到 Git
export PYPI_TOKEN="pypi-..."  # 不要在代码中写死
echo "pypi-..." > config.txt  # 不要提交到仓库

# ✅ 正确：使用环境变量或配置文件（已加入 .gitignore）
make setup-token TOKEN=pypi-...
```

#### 2. 确保 .gitignore 包含敏感文件

```bash
# .gitignore 应包含
.pypirc
.env
*.token
```

#### 3. Token 权限管理

| Token 用途 | 推荐范围 | 说明 |
|------------|----------|------|
| 个人开发 | Entire account | 所有项目通用 |
| 单一项目 | Single project | 仅限一个项目 |
| CI/CD | Entire account | 需要发布权限 |

#### 4. 定期轮换 Token

```bash
# 每 3-6 个月更新一次 Token
# 1. 在 PyPI 网站删除旧 Token
# 2. 创建新 Token
# 3. 更新配置
make setup-token TOKEN=新Token
```

#### 5. 泄露处理

如果 Token 不慎泄露：

1. **立即撤销**：访问 PyPI → Account settings → API tokens → 删除泄露的 Token
2. **创建新 Token**：生成新的 Token
3. **更新配置**：重新运行 `make setup-token`
4. **检查日志**：查看是否有异常发布活动

### 配置文件安全

#### ~/.pypirc 安全

```bash
# 文件权限检查
ls -la ~/.pypirc
# 应该是 -rw------- (600)

# 如果权限过于开放，修复权限
chmod 600 ~/.pypirc
```

#### GitHub Secret 安全

```bash
# Secret 会自动加密存储
# 查看已配置的 Secret
gh secret list --repo your-username/your-repo

# 删除 Secret（如果泄露）
gh secret remove PYPI_API_TOKEN --repo your-username/your-repo
```

---

## 未来项目复用

### 配置概述

| 配置类型 | 配置范围 | 配置频率 | 说明 |
|---------|---------|---------|------|
| **全局 PyPI Token** | 机器级别 | 每台机器一次 | 用于本地发布，所有项目通用 |
| **GitHub Secret** | 仓库级别 | 每个项目一次 | 用于 GitHub Actions 自动发布 |

### 全局 Token 配置（每台机器一次）

```bash
# 配置全局 PyPI Token（所有项目通用）
make setup-token TOKEN=pypi-AgEIcHlwaS5vcmcC...
```

配置后会自动创建：
- `~/.zshrc` - 环境变量
- `~/.pypirc` - twine 配置

### 新项目发布流程

#### 1. 复制发布配置

```bash
# 将以下文件复制到新项目
cp -r /path/to/DeepThinking/.github/workflows /path/to/new-project/.github/
cp /path/to/DeepThinking/Makefile /path/to/new-project/
cp /path/to/DeepThinking/scripts/setup-*.sh /path/to/new-project/scripts/
```

#### 2. 配置 GitHub Secret（可选）

```bash
cd /path/to/new-project
make setup-github TOKEN=pypi-AgEIcHlwaS5vcmcC...
```

#### 3. 发布

```bash
# 本地发布
make release

# 或自动化发布
git tag v1.0.0
git push origin v1.0.0
```

### 配置验证

```bash
# 验证全局 Token 是否配置成功
echo $PYPI_API_TOKEN

# 验证 ~/.pypirc 是否存在
cat ~/.pypirc

# 验证 GitHub Secret 是否配置成功
gh secret list --repo your-username/your-repo
```

---

## 发布检查清单

发布前请确认：

- [ ] 更新 `CHANGELOG.md` 发布说明
- [ ] 确认版本号（`pyproject.toml` 中的 `version`）
- [ ] 运行完整测试套件：`pytest`
- [ ] 代码格式检查：`ruff format` + `ruff check`
- [ ] 类型检查：`mypy src/deep_thinking/`
- [ ] 构建成功：`python -m build`
- [ ] 验证分发包：`twine check dist/*`
- [ ] 测试 TestPyPI（可选）：`twine upload --repository testpypi dist/*`

---

## 版本管理

### 语义化版本

遵循 [Semantic Versioning 2.0.0](https://semver.org/)：

- **主版本 (MAJOR)**：不兼容的 API 变更
- **次版本 (MINOR)**：向后兼容的功能新增
- **补丁版本 (PATCH)**：向后兼容的问题修复

### 版本号示例

```
0.2.3  -> 0.2.4  # 补丁版本（bug 修复）
0.2.3  -> 0.3.0  # 次版本（新功能）
0.2.3  -> 1.0.0  # 主版本（重大变更）
```

### Makefile 版本管理

```bash
make version-patch   # 增加补丁版本
make version-minor   # 增加次版本
make version-major   # 增加主版本
```

---

## Makefile 命令参考

### 开发命令

| 命令 | 说明 |
|------|------|
| `make help` | 显示所有可用命令 |
| `make install` | 安装项目依赖 |
| `make dev` | 开发模式安装 |
| `make test` | 运行测试套件 |
| `make lint` | 运行代码检查 |
| `make format` | 格式化代码 |
| `make typecheck` | 运行类型检查 |
| `make check` | 运行所有检查 |
| `make all` | 格式化 + 检查 + 测试 + 构建 |

### 发布命令

| 命令 | 说明 |
|------|------|
| `make clean` | 清理构建产物 |
| `make build` | 构建 PyPI 分发包 |
| `make verify` | 验证分发包 |
| `make publish` | 发布到 PyPI |
| `make release` | 完整发布流程 |
| `make release-check` | 发布前检查 |

### 配置命令

| 命令 | 说明 |
|------|------|
| `make setup-token` | 配置全局 PyPI Token |
| `make setup-github` | 配置 GitHub Secret |
| `make setup-all` | 一键配置所有环境 |

---

## 环境变量配置

### 环境变量方式

运行 `make setup-token` 后，会自动在 `~/.zshrc` 添加：

```bash
# PyPI API Token (用于发布 Python 包到 PyPI)
export PYPI_API_TOKEN="pypi-..."
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="${PYPI_API_TOKEN}"
```

### ~/.pypirc 配置

运行 `make setup-token` 后，会自动创建 `~/.pypirc`：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-...

[testpypi]
username = __token__
password = pypi-...
repository = https://test.pypi.org/legacy/
```

---

## 常见问题

> 💡 **提示**: 本章节提供快速解决方案。如需详细的错误分析和排查步骤，请参考[常见报错及处理](#常见报错及处理)章节。

### 1. 认证失败 (403 Forbidden)

**错误信息**：`HTTPError: 403 Forbidden`

**解决方案**：
- 确认 API Token 格式正确（不要有空格）
- 确认 Token 有发布权限（Entire account）
- 检查用户名是否为 `__token__`
- 重新生成 Token 并配置

### 2. 包名已存在

**错误信息**：`File already exists`

**解决方案**：
- 检查包名是否已被占用
- 更换包名或联系原作者

### 3. 版本号冲突

**错误信息**：`File already exists`

**解决方案**：
- 更新 `pyproject.toml` 中的版本号
- 不能发布已存在的版本

### 4. Token 配置后仍然提示输入密码

**原因**：环境变量未生效或配置文件未正确创建

**解决方案**：
```bash
# 重新加载 Shell 配置
source ~/.zshrc

# 验证环境变量
echo $PYPI_API_TOKEN

# 验证 ~/.pypirc
cat ~/.pypirc
```

---

## 发布后验证

发布成功后，使用以下方法验证包是否正确发布到 PyPI：

### 方法一：使用 pip 验证

#### 基础验证

```bash
# 1. 清除本地缓存（确保获取最新版本）
pip cache purge

# 2. 查看远程包信息
pip index versions DeepThinking

# 3. 安装指定版本验证
pip install DeepThinking==0.2.3

# 4. 验证安装的版本
python -c "import deep_thinking; print(deep_thinking.__version__)"
```

#### 完整验证流程

```bash
# 1. 创建临时虚拟环境
python -m venv test_install_venv
source test_install_venv/bin/activate  # Windows: test_install_venv\Scripts\activate

# 2. 安装包
pip install DeepThinking==0.2.3

# 3. 运行基本功能测试
python -m deep_thinking --help

# 4. 检查安装的文件
pip show -f DeepThinking

# 5. 清理测试环境
deactivate
rm -rf test_install_venv
```

### 方法二：使用 uv pip 验证

#### 快速验证

```bash
# 1. 查看 PyPI 上的可用版本
uv pip index versions DeepThinking

# 2. 安装并验证
uv pip install DeepThinking==0.2.3
python -c "import deep_thinking; print(deep_thinking.__version__)"
```

#### 完整验证流程

```bash
# 1. 创建临时虚拟环境
uv venv test_uv_venv
source test_uv_venv/bin/activate

# 2. 安装包
uv pip install DeepThinking==0.2.3

# 3. 验证安装
uv pip show DeepThinking
python -c "import deep_thinking; print(deep_thinking.__version__)"

# 4. 运行功能测试
python -m deep_thinking --help

# 5. 清理
deactivate
rm -rf test_uv_venv
```

### 方法三：PyPI 网页验证

访问 PyPI 项目页面验证：

- **包主页**: https://pypi.org/project/DeepThinking/
- **版本历史**: https://pypi.org/project/DeepThinking/#history
- **文件下载**: https://pypi.org/project/DeepThinking/#files

验证项目：

- [ ] 版本号正确显示
- [ ] 发布时间正确
- [ ] 文件完整性（wheel + tar.gz）
- [ ] 包描述正确

### 版本号获取方法

#### 命令行方式

```bash
# 方法1: 使用 import
python -c "import deep_thinking; print(deep_thinking.__version__)"

# 方法2: 使用 pip show
pip show DeepThinking | grep Version

# 方法3: 使用 uv pip show
uv pip show DeepThinking | grep Version
```

#### Python 代码方式

```python
import deep_thinking
print(f"DeepThinking 版本: {deep_thinking.__version__}")

# 或者使用 importlib.metadata
from importlib.metadata import version
print(f"版本: {version('DeepThinking')}")
```

---

## 常见报错及处理

### 发布阶段报错

#### 1. 403 Forbidden - 认证失败

**错误信息**：

```
HTTPError: 403 Forbidden from https://upload.pypi.org/legacy/
Invalid or nonexistent authentication information
```

**原因分析**：

- API Token 格式错误
- Token 已过期或被撤销
- 使用了错误的用户名（应使用 `__token__`）

**解决方案**：

```bash
# 1. 验证 Token 格式
echo $PYPI_API_TOKEN
# 应输出: pypi-xxxxx...

# 2. 检查 ~/.pypirc 配置
cat ~/.pypirc
# 确认 username = __token__

# 3. 重新配置 Token
make setup-token TOKEN=pypi-xxx...

# 4. 如果使用 GitHub Actions，检查 Secret
gh secret list --repo your-org/your-repo
```

#### 2. 400 Bad Request - 文件已存在

**错误信息**：

```
HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
File already exists
```

**原因分析**：

- 尝试发布已存在的版本号
- dist/ 目录中有旧版本残留

**解决方案**：

```bash
# 1. 清理构建目录
make clean
# 或手动删除
rm -rf dist/ build/ *.egg-info

# 2. 确认版本号是否需要更新
grep version pyproject.toml

# 3. 重新构建
python -m build

# 4. 如果确实需要覆盖，联系 PyPI 支持撤销旧版本
```

#### 3. 构建失败 - 权限错误

**错误信息**：

```
PermissionError: [Errno 13] Permission denied
```

**解决方案**：

```bash
# 1. 清理缓存
rm -rf dist/ build/ *.egg-info

# 2. 检查文件权限
ls -la

# 3. 使用 sudo（不推荐）或修复权限
chmod -R u+w .
```

### 验证阶段报错

#### 1. 版本号不匹配

**错误现象**：

```bash
$ python -c "import deep_thinking; print(deep_thinking.__version__)"
0.2.2  # 但发布的是 0.2.3
```

**原因分析**：

- 本地安装的是旧版本
- PyPI 缓存未更新
- 代码中的 `__version__` 未更新

**解决方案**：

```bash
# 1. 清除 pip 缓存
pip cache purge

# 2. 卸载旧版本
pip uninstall DeepThinking -y

# 3. 强制重新安装
pip install DeepThinking==0.2.3 --no-cache-dir

# 4. 如果代码版本号未更新，检查源码
grep -r "__version__" src/deep_thinking/__init__.py
```

#### 2. 包无法导入

**错误信息**：

```
ModuleNotFoundError: No module named 'deep_thinking'
```

**解决方案**：

```bash
# 1. 确认包已安装
pip list | grep DeepThinking

# 2. 检查 Python 环境
which python
python --version

# 3. 重新安装
pip install DeepThinking==0.2.3 --force-reinstall
```

#### 3. 依赖冲突

**错误信息**：

```
ERROR: pip's dependency resolver does not currently take into account...
```

**解决方案**：

```bash
# 1. 使用虚拟环境
python -m venv clean_env
source clean_env/bin/activate
pip install DeepThinking==0.2.3

# 2. 或使用 uv（更好的依赖解析）
uv venv clean_env
source clean_env/bin/activate
uv pip install DeepThinking==0.2.3
```

### 安装阶段报错

#### 1. 网络超时

**错误信息**：

```
ERROR: Could not find a version that satisfies the requirement...
No matching distribution found for DeepThinking
```

**解决方案**：

```bash
# 1. 检查网络连接
ping pypi.org

# 2. 使用国内镜像（临时）
pip install DeepThinking==0.2.3 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 配置永久镜像（可选）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 2. SSL 证书错误

**错误信息**：

```
SSL: CERTIFICATE_VERIFY_FAILED
```

**解决方案**：

```bash
# 1. 更新 pip
python -m pip install --upgrade pip

# 2. 信任 PyPI（不推荐，仅用于调试）
pip install DeepThinking --trusted-host pypi.org --trusted-host files.pythonhosted.org

# 3. 检查系统证书
# macOS
brew install ca-certificates
```

#### 3. 平台不兼容

**错误信息**：

```
ERROR: Could not find a version that satisfies the requirement DeepThinking
```

**解决方案**：

```bash
# 1. 检查可用版本
pip index versions DeepThinking

# 2. 检查平台支持
python -c "import platform; print(f'{platform.system()} {platform.machine()}')"

# 3. 如果没有预编译 wheel，从源码安装
pip install DeepThinking==0.2.3 --no-binary=DeepThinking
```

### 快速诊断命令

```bash
# 一键诊断发布状态
echo "=== PyPI 版本检查 ==="
curl -s https://pypi.org/pypi/DeepThinking/json 2>/dev/null | grep -o '"version":"[^"]*"'

echo -e "\n=== 本地版本检查 ==="
python -c "import deep_thinking; print(f'本地版本: {deep_thinking.__version__}')" 2>/dev/null || echo "未安装"

echo -e "\n=== pip 检查 ==="
pip show DeepThinking 2>/dev/null || echo "未通过 pip 安装"

echo -e "\n=== 环境检查 ==="
python --version
which python
```

---

## 回滚

如果发布有严重问题：

1. **联系 PyPI 支持手动删除**
2. **发布新版本修复问题**（推荐）
3. **在 PyPI 上标记为已弃用**

---

## 相关链接

- [PyPI 官方文档](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine 文档](https://twine.readthedocs.io/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [GitHub CLI 文档](https://cli.github.com/)
- [Semantic Versioning](https://semver.org/)
- [PyPI 安全最佳实践](https://pypi.org/help/#managing-api-tokens)
