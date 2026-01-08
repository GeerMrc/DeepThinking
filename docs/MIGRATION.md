# DeepThinking MCP 数据迁移指南

> 版本: 0.2.3
> 更新日期: 2026-01-08

---

## 概述

从版本 0.2.2 开始，DeepThinking MCP 将默认存储位置从项目本地目录 (`./.deepthinking/`) 迁移到用户主目录 (`~/.deepthinking/`)。

本指南详细说明数据迁移的机制、流程和故障排除。

---

## 迁移动机

### 为什么改变存储位置？

1. **用户级数据管理**: 数据存储在用户主目录，更适合个人使用场景
2. **跨项目共享**: 多个项目可以共享同一套思考会话数据
3. **备份友好**: 用户主目录更容易纳入个人备份策略
4. **权限管理**: 更简单的权限控制和数据管理

### 存储位置对比

| 版本 | 存储位置 | 特点 |
|------|---------|------|
| 旧版本 (<0.2.2) | `./.deepthinking/` | 项目本地，团队协作 |
| 新版本 (≥0.2.2) | `~/.deepthinking/` | 用户主目录，个人使用 |

---

## 自动迁移流程

### 触发条件

服务器启动时会自动检查以下条件：

1. 旧数据目录存在：`./.deepthinking/`
2. 新数据目录不存在或为空：`~/.deepthinking/`

### 迁移步骤

```
1. 检测旧数据目录
   ↓
2. 创建自动备份
   ↓
3. 复制数据到新位置
   ↓
4. 创建迁移标记文件
   ↓
5. 继续使用新位置
```

### 迁移日志示例

```
INFO: 初始化数据目录: /home/user/.deepthinking
INFO: 检测到旧数据目录: /project/.deepthinking
INFO: 开始自动迁移...
INFO: 创建迁移备份: /project/.deepthinking/backups/migration_backup_20260108_120000
INFO: 迁移备份已创建: /project/.deepthinking/backups/migration_backup_20260108_120000
INFO: 数据迁移完成
```

---

## 手动迁移

### 使用 CLI 参数

```bash
# 指定新的存储位置
python -m deep_thinking --data-dir /path/to/new/location
```

### 使用环境变量

```bash
export DEEP_THINKING_DATA_DIR=/path/to/new/location
python -m deep_thinking
```

### 手动复制数据

```bash
# 1. 创建新目录
mkdir -p ~/.deepthinking/sessions

# 2. 复制会话数据
cp -r ./.deepthinking/sessions/* ~/.deepthinking/sessions/

# 3. 复制索引文件
cp ./.deepthinking/sessions/.index.json ~/.deepthinking/sessions/

# 4. 创建迁移标记
echo "migration_date: $(date -Iseconds)" > ~/.deepthinking/.migration_completed
echo "source: ./.deepthinking/" >> ~/.deepthinking/.migration_completed
echo "target: ~/.deepthinking/" >> ~/.deepthinking/.migration_completed
```

---

## 迁移验证

### 检查迁移状态

```bash
# 检查迁移标记文件
cat ~/.deepthinking/.migration_completed

# 验证会话数据
ls -la ~/.deepthinking/sessions/
```

### 验证数据完整性

```bash
# 启动服务器
python -m deep_thinking

# 列出所有会话
# 在 MCP Inspector 中执行: list_sessions()
```

---

## 回滚迁移

### 自动回滚

如果迁移失败，服务器会：
1. 记录错误日志
2. 继续使用旧数据目录
3. 不创建迁移标记

### 手动回滚

```bash
# 1. 删除新位置的数据
rm -rf ~/.deepthinking

# 2. 恢复备份
cp -r ./.deepthinking/backups/migration_backup_*/* ~/.deepthinking/sessions/

# 3. 使用旧位置
export DEEP_THINKING_DATA_DIR=./.deepthinking
python -m deep_thinking
```

---

## 故障排除

### 问题1: 迁移后找不到数据

**症状**: 服务器启动后没有显示旧的会话

**解决方案**:

1. 检查迁移是否成功：
   ```bash
   cat ~/.deepthinking/.migration_completed
   ```

2. 检查会话文件是否存在：
   ```bash
   ls -la ~/.deepthinking/sessions/
   ```

3. 手动指定旧数据目录：
   ```bash
   export DEEP_THINKING_DATA_DIR=./.deepthinking
   ```

---

### 问题2: 迁移失败

**症状**: 日志显示 `数据迁移失败`

**解决方案**:

1. 检查备份是否创建：
   ```bash
   ls -la ./.deepthinking/backups/
   ```

2. 查看详细错误日志：
   ```bash
   python -m deep_thinking --log-level DEBUG
   ```

3. 手动复制数据（见"手动迁移"章节）

---

### 问题3: 权限错误

**症状**: `PermissionError` 或权限被拒绝

**解决方案**:

```bash
# 检查目录权限
ls -la ~/.deepthinking/
ls -la ./.deepthinking/

# 修改权限
chmod 755 ~/.deepthinking/
chmod 755 ./.deepthinking/

# 使用有权限的目录
export DEEP_THINKING_DATA_DIR=/tmp/deep-thinking
```

---

## 多项目场景

### 共享旧数据

如果多个项目需要访问旧的思考数据：

**方案1: 每个项目独立迁移**

每个项目启动时会自动复制一份旧数据。

**方案2: 使用环境变量共享**

```bash
# 项目 A
export DEEP_THINKING_DATA_DIR=~/.Deep-Thinking-MCP
cd /project/a && python -m deep_thinking

# 项目 B
export DEEP_THINKING_DATA_DIR=~/.Deep-Thinking-MCP
cd /project/b && python -m deep_thinking
```

---

## 清理旧数据

### 迁移成功后

确认新位置数据正常后，可以清理旧数据：

```bash
# 1. 再次确认备份存在
ls -la ~/.Deep-Thinking-MCP/backups/

# 2. 删除旧数据（可选）
rm -rf ~/.Deep-Thinking-MCP/

# 3. 删除备份（可选）
rm -rf ~/.Deep-Thinking-MCP/backups/
```

⚠️ **警告**: 删除前请确保新位置数据完整！

---

## 最佳实践

### 1. 定期备份

```bash
# 定期备份新位置数据
cp -r .Deep-Thinking-MCP .Deep-Thinking-MCP.backup.$(date +%Y%m%d)
```

### 2. 版本控制

确保 `.Deep-Thinking-MCP/.gitignore` 存在：

```bash
cat .Deep-Thinking-MCP/.gitignore
```

应包含：
```
sessions/
.index.json
.backups/
*.log
```

### 3. CI/CD 集成

在 CI/CD 中使用固定的数据目录：

```yaml
env:
  DEEP_THINKING_DATA_DIR: /tmp/deep-thinking-ci
```

---

## 相关资源

- [API 文档](./api.md) - 数据存储接口说明
- [安装指南](./installation.md) - 配置存储目录
- [用户指南](./user_guide.md) - 会话管理功能

---

## 支持

如有迁移问题，请：
1. 查看 [故障排除](#故障排除) 章节
2. 启用 DEBUG 日志查看详细信息
3. 提交 [GitHub Issue](https://github.com/your-org/Deep-Thinking-MCP/issues)
