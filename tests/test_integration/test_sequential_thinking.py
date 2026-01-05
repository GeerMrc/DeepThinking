"""
集成测试 - 顺序思考工具
"""

import pytest

from deep_thinking import server
from deep_thinking.storage.storage_manager import StorageManager
from deep_thinking.tools import sequential_thinking


@pytest.mark.asyncio(loop_scope="class")
class TestSequentialThinkingIntegration:
    """顺序思考工具集成测试"""

    @pytest.fixture
    async def storage_manager(self, tmp_path):
        """创建存储管理器"""
        manager = StorageManager(tmp_path)
        server._storage_manager = manager

        yield manager

        # 清理
        server._storage_manager = None

    async def test_regular_thinking(self, storage_manager):
        """测试常规思考"""
        result = sequential_thinking.sequential_thinking(
            thought="这是第一个思考步骤",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-regular",
        )

        assert "思考步骤 1/3" in result
        assert "常规思考" in result
        assert "这是第一个思考步骤" in result
        assert "继续下一步思考" in result

        # 验证会话已创建
        session = storage_manager.get_session("test-regular")
        assert session is not None
        assert session.thought_count() == 1
        assert session.thoughts[0].content == "这是第一个思考步骤"

    async def test_revision_thinking(self, storage_manager):
        """测试修订思考"""
        # 先创建一个常规思考
        sequential_thinking.sequential_thinking(
            thought="原始思考",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-revision",
        )

        # 然后创建修订思考
        result = sequential_thinking.sequential_thinking(
            thought="这是修订后的思考",
            nextThoughtNeeded=False,
            thoughtNumber=2,
            totalThoughts=3,
            session_id="test-revision",
            isRevision=True,
            revisesThought=1,
        )

        assert "修订思考" in result
        assert "修订思考步骤 1" in result
        assert "这是修订后的思考" in result
        assert "思考完成" in result

        # 验证修订信息
        session = storage_manager.get_session("test-revision")
        assert session is not None
        assert session.thought_count() == 2
        assert session.thoughts[1].type == "revision"
        assert session.thoughts[1].revises_thought == 1

    async def test_branch_thinking(self, storage_manager):
        """测试分支思考"""
        # 先创建一个常规思考
        sequential_thinking.sequential_thinking(
            thought="主线思考",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=5,
            session_id="test-branch",
        )

        # 然后创建分支思考
        result = sequential_thinking.sequential_thinking(
            thought="这是一个分支思考",
            nextThoughtNeeded=True,
            thoughtNumber=2,
            totalThoughts=5,
            session_id="test-branch",
            branchFromThought=1,
            branchId="branch-0-1",
        )

        assert "分支思考" in result
        assert "从步骤 1 分支" in result
        assert "这是一个分支思考" in result

        # 验证分支信息
        session = storage_manager.get_session("test-branch")
        assert session is not None
        assert session.thought_count() == 2
        assert session.thoughts[1].type == "branch"
        assert session.thoughts[1].branch_from_thought == 1
        assert session.thoughts[1].branch_id == "branch-0-1"

    async def test_completion(self, storage_manager):
        """测试思考完成"""
        result = sequential_thinking.sequential_thinking(
            thought="最后一个思考",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
            session_id="test-complete",
        )

        assert "思考完成" in result
        assert "✅" in result

        # 验证会话已标记为完成
        session = storage_manager.get_session("test-complete")
        assert session is not None
        assert session.is_completed()

    async def test_multiple_thoughts_same_session(self, storage_manager):
        """测试同一会话中的多个思考步骤"""
        session_id = "test-multiple"

        # 添加三个思考步骤
        sequential_thinking.sequential_thinking(
            thought="步骤1：分析问题",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
            session_id=session_id,
        )

        sequential_thinking.sequential_thinking(
            thought="步骤2：制定方案",
            nextThoughtNeeded=True,
            thoughtNumber=2,
            totalThoughts=3,
            session_id=session_id,
        )

        sequential_thinking.sequential_thinking(
            thought="步骤3：执行方案",
            nextThoughtNeeded=False,
            thoughtNumber=3,
            totalThoughts=3,
            session_id=session_id,
        )

        # 验证所有思考都已保存
        session = storage_manager.get_session(session_id)
        assert session is not None
        assert session.thought_count() == 3
        assert session.thoughts[0].content == "步骤1：分析问题"
        assert session.thoughts[1].content == "步骤2：制定方案"
        assert session.thoughts[2].content == "步骤3：执行方案"

    async def test_default_session_creation(self, storage_manager):
        """测试默认会话自动创建"""
        result = sequential_thinking.sequential_thinking(
            thought="使用默认会话",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=1,
        )

        assert "思考步骤 1/1" in result

        # 验证默认会话已创建
        session = storage_manager.get_session("default")
        assert session is not None
        assert session.thought_count() == 1

    async def test_comparison_thinking(self, storage_manager):
        """测试对比思考类型"""
        result = sequential_thinking.sequential_thinking(
            thought="比较三种数据库方案",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=3,
            session_id="test-comparison",
            comparisonItems=[
                "MySQL: 成熟稳定，社区活跃",
                "PostgreSQL: 功能丰富，扩展性强",
                "MongoDB: 灵活文档存储"
            ],
            comparisonDimensions=["性能", "可靠性", "成本"],
            comparisonResult="PostgreSQL在功能和扩展性上最优",
        )

        assert "思考步骤 1/3" in result
        assert "对比思考 ⚖️" in result
        assert "比较三种数据库方案" in result
        assert "比较项" in result
        assert "性能, 可靠性, 成本" in result
        assert "PostgreSQL" in result

        # 验证对比思考数据
        session = storage_manager.get_session("test-comparison")
        assert session is not None
        assert session.thought_count() == 1
        assert session.thoughts[0].type == "comparison"
        assert session.thoughts[0].comparison_items is not None
        assert len(session.thoughts[0].comparison_items) == 3
        assert session.thoughts[0].comparison_result == "PostgreSQL在功能和扩展性上最优"

    async def test_reverse_thinking(self, storage_manager):
        """测试逆向思考类型"""
        result = sequential_thinking.sequential_thinking(
            thought="反推微服务架构决策的前提条件",
            nextThoughtNeeded=False,
            thoughtNumber=3,
            totalThoughts=5,
            session_id="test-reverse",
            reverseFrom=2,
            reverseTarget="验证'采用微服务架构'结论的前提条件",
            reverseSteps=[
                "前提1: 团队规模超过20人",
                "前提2: 业务模块边界清晰",
                "验证结果: 前提3不成立"
            ],
        )

        assert "思考步骤 3/5" in result
        assert "逆向思考 🔙" in result
        assert "反推微服务架构" in result
        assert "反推起点" in result
        assert "思考步骤 2" in result
        assert "反推目标" in result
        assert "反推步骤" in result

        # 验证逆向思考数据
        session = storage_manager.get_session("test-reverse")
        assert session is not None
        assert session.thought_count() == 1
        assert session.thoughts[0].type == "reverse"
        assert session.thoughts[0].reverse_from == 2
        assert session.thoughts[0].reverse_target == "验证'采用微服务架构'结论的前提条件"
        assert session.thoughts[0].reverse_steps is not None
        assert len(session.thoughts[0].reverse_steps) == 3

    async def test_hypothetical_thinking(self, storage_manager):
        """测试假设思考类型"""
        result = sequential_thinking.sequential_thinking(
            thought="探索用户增长10倍的影响",
            nextThoughtNeeded=False,
            thoughtNumber=1,
            totalThoughts=2,
            session_id="test-hypothetical",
            hypotheticalCondition="如果用户数量从10万增长到100万",
            hypotheticalImpact="服务器负载增加10倍，需要：1.数据库分库分表 2.引入缓存层",
            hypotheticalProbability="可能性：高",
        )

        assert "思考步骤 1/2" in result
        assert "假设思考 🤔" in result
        assert "探索用户增长10倍的影响" in result
        assert "假设条件" in result
        assert "如果用户数量从10万增长到100万" in result
        assert "影响分析" in result
        assert "服务器负载增加10倍" in result
        assert "可能性" in result

        # 验证假设思考数据
        session = storage_manager.get_session("test-hypothetical")
        assert session is not None
        assert session.thought_count() == 1
        assert session.thoughts[0].type == "hypothetical"
        assert session.thoughts[0].hypothetical_condition == "如果用户数量从10万增长到100万"
        assert session.thoughts[0].hypothetical_impact == "服务器负载增加10倍，需要：1.数据库分库分表 2.引入缓存层"
        assert session.thoughts[0].hypothetical_probability == "可能性：高"
