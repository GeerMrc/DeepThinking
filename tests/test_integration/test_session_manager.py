"""
集成测试 - 会话管理工具
"""

import pytest

from deep_thinking import server
from deep_thinking.storage.storage_manager import StorageManager
from deep_thinking.tools import session_manager


@pytest.mark.asyncio
class TestSessionManagerIntegration:
    """会话管理工具集成测试"""

    @pytest.fixture
    async def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager

        yield manager

        server._storage_manager = None

    async def test_create_and_get_session(self, storage_manager):
        """测试创建和获取会话"""
        result = session_manager.create_session(
            name="测试会话",
            description="这是一个测试会话",
        )

        assert "会话已创建" in result
        assert "测试会话" in result

        # 提取会话ID（支持Markdown格式）
        import re

        session_id = re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", result)
        assert session_id is not None
        session_id = session_id.group(1)

        # 获取会话详情
        session_result = session_manager.get_session(session_id)
        assert "测试会话" in session_result
        assert "这是一个测试会话" in session_result

    async def test_list_sessions(self, storage_manager):
        """测试列出会话"""
        # 创建多个会话
        session_manager.create_session(name="会话1", description="第一个会话")
        session_manager.create_session(name="会话2", description="第二个会话")
        session_manager.create_session(name="会话3", description="第三个会话")

        # 列出所有会话
        result = session_manager.list_sessions()
        assert "会话列表" in result
        assert "会话1" in result
        assert "会话2" in result
        assert "会话3" in result
        assert "**总数**: 3" in result

    async def test_list_sessions_with_status_filter(self, storage_manager):
        """测试按状态过滤会话"""
        # 创建会话
        r1 = session_manager.create_session(name="活跃会话", description="活跃")
        r2 = session_manager.create_session(name="完成会话", description="完成")

        # 提取会话ID（支持Markdown格式）
        import re

        re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", r1).group(1)
        session_id2 = re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", r2).group(1)

        # 将第二个会话标记为已完成
        session_manager.update_session_status(session_id2, "completed")

        # 按状态过滤
        active_result = session_manager.list_sessions(status="active")
        assert "活跃会话" in active_result
        assert "完成会话" not in active_result

        completed_result = session_manager.list_sessions(status="completed")
        assert "完成会话" in completed_result
        assert "活跃会话" not in completed_result

    async def test_update_session_status(self, storage_manager):
        """测试更新会话状态"""
        # 创建会话
        result = session_manager.create_session(name="状态测试会话")
        import re

        session_id = re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", result).group(1)

        # 标记为已完成
        update_result = session_manager.update_session_status(session_id, "completed")
        assert "会话状态已更新" in update_result
        assert "completed" in update_result

        # 验证状态已更新
        session = storage_manager.get_session(session_id)
        assert session.is_completed()

    async def test_delete_session(self, storage_manager):
        """测试删除会话"""
        # 创建会话
        result = session_manager.create_session(name="待删除会话")
        import re

        session_id = re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", result).group(1)

        # 删除会话
        delete_result = session_manager.delete_session(session_id)
        assert "会话已删除" in delete_result

        # 验证会话已删除
        session = storage_manager.get_session(session_id)
        assert session is None

    async def test_session_with_thoughts(self, storage_manager):
        """测试包含思考步骤的会话"""
        from deep_thinking.tools import sequential_thinking

        # 通过顺序思考工具创建会话
        sequential_thinking.sequential_thinking(
            thought="这是第一个思考",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=2,
            session_id="thoughts-test",
        )

        # 获取会话详情
        result = session_manager.get_session("thoughts-test")
        assert "**思考步骤数**: 1" in result
        assert "这是第一个思考" in result

        # 再添加一个思考
        sequential_thinking.sequential_thinking(
            thought="这是第二个思考",
            nextThoughtNeeded=False,
            thoughtNumber=2,
            totalThoughts=2,
            session_id="thoughts-test",
        )

        # 再次获取会话详情
        result = session_manager.get_session("thoughts-test")
        assert "**思考步骤数**: 2" in result
        assert "这是第二个思考" in result

    async def test_create_with_metadata(self, storage_manager):
        """测试创建带元数据的会话"""
        import json

        metadata = json.dumps({"author": "test", "tags": ["demo", "test"]})
        result = session_manager.create_session(
            name="元数据测试会话",
            metadata=metadata,
        )

        assert "会话已创建" in result

        # 验证元数据已保存
        import re

        session_id = re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", result).group(1)
        session = storage_manager.get_session(session_id)
        assert session is not None
        assert session.metadata["author"] == "test"
        assert session.metadata["tags"] == ["demo", "test"]

    async def test_invalid_status_update(self, storage_manager):
        """测试无效的状态更新"""
        result = session_manager.create_session(name="测试会话")
        import re

        session_id = re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", result).group(1)

        # 尝试使用无效状态
        with pytest.raises(ValueError, match="无效的状态值"):
            session_manager.update_session_status(session_id, "invalid_status")

    async def test_get_nonexistent_session(self, storage_manager):
        """测试获取不存在的会话"""
        with pytest.raises(ValueError, match="会话不存在"):
            session_manager.get_session("nonexistent-session-id")

    async def test_create_with_invalid_json_metadata(self, storage_manager):
        """测试创建带无效JSON元数据的会话"""
        with pytest.raises(ValueError, match="元数据JSON格式错误"):
            session_manager.create_session(
                name="无效元数据会话",
                metadata="{invalid json}",
            )

    async def test_list_sessions_invalid_status(self, storage_manager):
        """测试列出会话时使用无效状态值"""
        session_manager.create_session(name="测试会话")

        with pytest.raises(ValueError, match="无效的状态值"):
            session_manager.list_sessions(status="invalid_status")

    async def test_list_sessions_with_limit(self, storage_manager):
        """测试限制返回数量的会话列表"""
        # 创建5个会话
        for i in range(5):
            session_manager.create_session(name=f"会话{i}", description=f"第{i}个会话")

        # 限制返回3个
        result = session_manager.list_sessions(limit=3)
        assert "**总数**: 3" in result

    async def test_list_empty_sessions(self, storage_manager):
        """测试列出空会话列表"""
        result = session_manager.list_sessions()
        assert "暂无会话" in result

    async def test_delete_nonexistent_session(self, storage_manager):
        """测试删除不存在的会话"""
        result = session_manager.delete_session("nonexistent-session-id")
        assert "删除失败" in result
        assert "会话不存在" in result

    async def test_update_nonexistent_session_status(self, storage_manager):
        """测试更新不存在会话的状态"""
        with pytest.raises(ValueError, match="会话不存在"):
            session_manager.update_session_status("nonexistent-session-id", "completed")

    async def test_update_session_to_archived(self, storage_manager):
        """测试将会话状态更新为archived"""
        result = session_manager.create_session(name="归档测试会话")
        import re

        session_id = re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", result).group(1)

        # 标记为已归档
        update_result = session_manager.update_session_status(session_id, "archived")
        assert "会话状态已更新" in update_result
        assert "archived" in update_result

        # 验证状态已更新
        session = storage_manager.get_session(session_id)
        assert session.is_archived()

    async def test_update_session_to_active(self, storage_manager):
        """测试将会话状态更新回active"""
        result = session_manager.create_session(name="重新激活测试会话")
        import re

        session_id = re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", result).group(1)

        # 先标记为已完成
        session_manager.update_session_status(session_id, "completed")

        # 再标记为活跃
        update_result = session_manager.update_session_status(session_id, "active")
        assert "会话状态已更新" in update_result
        assert "active" in update_result

        # 验证状态已更新
        session = storage_manager.get_session(session_id)
        assert session.is_active()

    async def test_resume_session_with_thoughts(self, storage_manager):
        """测试恢复有思考步骤的会话"""
        from deep_thinking.tools import sequential_thinking

        # 创建有思考步骤的会话
        sequential_thinking.sequential_thinking(
            thought="第一个思考步骤",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="resume-test",
        )

        # 恢复会话
        result = session_manager.resume_session("resume-test")
        assert "会话恢复成功" in result
        assert "resume-test" in result
        assert "上一个思考步骤" in result
        assert "第一个思考步骤" in result
        assert "继续思考" in result

    async def test_resume_completed_session(self, storage_manager):
        """测试恢复已完成的会话"""
        from deep_thinking.tools import sequential_thinking

        # 创建并完成会话
        sequential_thinking.sequential_thinking(
            thought="测试思考",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
            session_id="completed-resume-test",
        )

        # 标记为完成
        session = storage_manager.get_session("completed-resume-test")
        session.mark_completed()
        storage_manager.update_session(session)

        # 尝试恢复
        result = session_manager.resume_session("completed-resume-test")
        assert "会话已完成" in result
        assert "已经标记为完成" in result

    async def test_resume_empty_session(self, storage_manager):
        """测试恢复没有思考步骤的会话"""
        # 创建空会话
        result = session_manager.create_session(name="空会话", description="没有思考步骤")
        import re

        session_id = re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", result).group(1)

        # 恢复空会话
        resume_result = session_manager.resume_session(session_id)
        assert "会话恢复成功" in resume_result
        assert "尚未包含任何思考步骤" in resume_result
        assert "可以直接开始思考" in resume_result

    async def test_resume_nonexistent_session(self, storage_manager):
        """测试恢复不存在的会话"""
        with pytest.raises(ValueError, match="会话不存在"):
            session_manager.resume_session("nonexistent-session-id")

    async def test_resume_session_with_total_thoughts_history(self, storage_manager):
        """测试恢复有total_thoughts历史的会话"""
        from deep_thinking.models.thought import Thought

        # 创建会话并添加历史记录
        session = storage_manager.create_session(name="历史记录会话", description="测试历史记录")
        session.metadata["total_thoughts_history"] = [
            {"timestamp": "2025-01-01T00:00:00", "old_total": 5, "new_total": 10}
        ]
        storage_manager.update_session(session)

        # 添加思考步骤
        thought = Thought(
            thought_number=1,
            content="测试思考",
            type="regular",
            timestamp="2025-01-01T00:00:00",
        )
        session.add_thought(thought)
        storage_manager.update_session(session)

        # 恢复会话
        result = session_manager.resume_session(session.session_id)
        assert "思考步骤调整历史" in result
        assert "**当前总数**: 10" in result
        assert "**调整次数**: 1" in result
