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
        result = await session_manager.create_session(
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
        session_result = await session_manager.get_session(session_id)
        assert "测试会话" in session_result
        assert "这是一个测试会话" in session_result

    async def test_list_sessions(self, storage_manager):
        """测试列出会话"""
        # 创建多个会话
        await session_manager.create_session(name="会话1", description="第一个会话")
        await session_manager.create_session(name="会话2", description="第二个会话")
        await session_manager.create_session(name="会话3", description="第三个会话")

        # 列出所有会话
        result = await session_manager.list_sessions()
        assert "会话列表" in result
        assert "会话1" in result
        assert "会话2" in result
        assert "会话3" in result
        assert "**总数**: 3" in result

    async def test_list_sessions_with_status_filter(self, storage_manager):
        """测试按状态过滤会话"""
        # 创建会话
        r1 = await session_manager.create_session(name="活跃会话", description="活跃")
        r2 = await session_manager.create_session(name="完成会话", description="完成")

        # 提取会话ID（支持Markdown格式）
        import re
        re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", r1).group(1)
        session_id2 = re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", r2).group(1)

        # 将第二个会话标记为已完成
        await session_manager.update_session_status(session_id2, "completed")

        # 按状态过滤
        active_result = await session_manager.list_sessions(status="active")
        assert "活跃会话" in active_result
        assert "完成会话" not in active_result

        completed_result = await session_manager.list_sessions(status="completed")
        assert "完成会话" in completed_result
        assert "活跃会话" not in completed_result

    async def test_update_session_status(self, storage_manager):
        """测试更新会话状态"""
        # 创建会话
        result = await session_manager.create_session(name="状态测试会话")
        import re
        session_id = re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", result).group(1)

        # 标记为已完成
        update_result = await session_manager.update_session_status(session_id, "completed")
        assert "会话状态已更新" in update_result
        assert "completed" in update_result

        # 验证状态已更新
        session = storage_manager.get_session(session_id)
        assert session.is_completed()

    async def test_delete_session(self, storage_manager):
        """测试删除会话"""
        # 创建会话
        result = await session_manager.create_session(name="待删除会话")
        import re
        session_id = re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", result).group(1)

        # 删除会话
        delete_result = await session_manager.delete_session(session_id)
        assert "会话已删除" in delete_result

        # 验证会话已删除
        session = storage_manager.get_session(session_id)
        assert session is None

    async def test_session_with_thoughts(self, storage_manager):
        """测试包含思考步骤的会话"""
        from deep_thinking.tools import sequential_thinking

        # 通过顺序思考工具创建会话
        await sequential_thinking.sequential_thinking(
            thought="这是第一个思考",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=2,
            session_id="thoughts-test",
        )

        # 获取会话详情
        result = await session_manager.get_session("thoughts-test")
        assert "**思考步骤数**: 1" in result
        assert "这是第一个思考" in result

        # 再添加一个思考
        await sequential_thinking.sequential_thinking(
            thought="这是第二个思考",
            nextThoughtNeeded=False,
            thoughtNumber=2,
            totalThoughts=2,
            session_id="thoughts-test",
        )

        # 再次获取会话详情
        result = await session_manager.get_session("thoughts-test")
        assert "**思考步骤数**: 2" in result
        assert "这是第二个思考" in result

    async def test_create_with_metadata(self, storage_manager):
        """测试创建带元数据的会话"""
        import json

        metadata = json.dumps({"author": "test", "tags": ["demo", "test"]})
        result = await session_manager.create_session(
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
        result = await session_manager.create_session(name="测试会话")
        import re
        session_id = re.search(r"\*\*会话ID\*\*: ([a-f0-9-]+)", result).group(1)

        # 尝试使用无效状态
        with pytest.raises(ValueError, match="无效的状态值"):
            await session_manager.update_session_status(session_id, "invalid_status")

    async def test_get_nonexistent_session(self, storage_manager):
        """测试获取不存在的会话"""
        with pytest.raises(ValueError, match="会话不存在"):
            await session_manager.get_session("nonexistent-session-id")
