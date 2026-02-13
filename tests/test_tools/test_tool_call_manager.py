"""
工具调用管理器单元测试 (Interleaved Thinking)
"""

from deep_thinking.models.tool_call import (
    ToolCallData,
    ToolCallError,
    ToolResultData,
)
from deep_thinking.tools.tool_call_manager import (
    ToolCallManager,
    ToolCallStatistics,
)


class TestToolCallStatistics:
    """ToolCallStatistics 测试"""

    def test_create_statistics_with_defaults(self):
        """测试使用默认值创建统计"""
        stats = ToolCallStatistics()
        assert stats.total_calls == 0
        assert stats.successful_calls == 0
        assert stats.failed_calls == 0
        assert stats.cached_hits == 0
        assert stats.cache_misses == 0
        assert stats.total_execution_time_ms == 0.0

    def test_statistics_to_dict(self):
        """测试转换为字典"""
        stats = ToolCallStatistics(
            total_calls=10,
            successful_calls=8,
            failed_calls=2,
            cached_hits=5,
            cache_misses=5,
            total_execution_time_ms=1000.0,
        )
        data = stats.to_dict()

        assert data["total_calls"] == 10
        assert data["successful_calls"] == 8
        assert data["failed_calls"] == 2
        assert data["cached_hits"] == 5
        assert data["cache_misses"] == 5
        assert data["total_execution_time_ms"] == 1000.0
        assert data["avg_execution_time_ms"] == 100.0

    def test_statistics_avg_execution_time_zero_calls(self):
        """测试零调用时的平均执行时间"""
        stats = ToolCallStatistics()
        data = stats.to_dict()
        assert data["avg_execution_time_ms"] == 0.0


class TestToolCallManager:
    """ToolCallManager 基础测试"""

    def test_create_manager_with_defaults(self):
        """测试使用默认值创建管理器"""
        manager = ToolCallManager()
        assert manager.max_calls == 100
        assert manager.cache_size == 50
        assert manager.timeout_ms == 30000.0

    def test_create_manager_with_custom_values(self):
        """测试使用自定义值创建管理器"""
        manager = ToolCallManager(max_calls=50, cache_size=20, timeout_ms=10000.0)
        assert manager.max_calls == 50
        assert manager.cache_size == 20
        assert manager.timeout_ms == 10000.0


class TestToolCallManagerCallLimit:
    """ToolCallManager 调用次数限制测试"""

    def test_can_execute_initially_true(self):
        """测试初始时可以执行"""
        manager = ToolCallManager(max_calls=5)
        assert manager.can_execute() is True

    def test_can_execute_after_calls(self):
        """测试调用后检查是否可执行"""
        manager = ToolCallManager(max_calls=3)

        # 前3次可以执行
        for _ in range(3):
            assert manager.can_execute() is True
            manager.register_call()

        # 第4次不能执行
        assert manager.can_execute() is False

    def test_get_remaining_calls(self):
        """测试获取剩余调用次数"""
        manager = ToolCallManager(max_calls=10)
        assert manager.get_remaining_calls() == 10

        manager.register_call()
        assert manager.get_remaining_calls() == 9

        manager.register_call()
        manager.register_call()
        assert manager.get_remaining_calls() == 7


class TestToolCallManagerCache:
    """ToolCallManager 缓存功能测试"""

    def test_cache_miss(self):
        """测试缓存未命中"""
        manager = ToolCallManager()
        call_data = ToolCallData(tool_name="search", arguments={"q": "test"})

        result = manager.get_cached_result(call_data)
        assert result is None
        assert manager.get_statistics()["cache_misses"] == 1

    def test_cache_hit(self):
        """测试缓存命中"""
        manager = ToolCallManager()
        call_data = ToolCallData(tool_name="search", arguments={"q": "test"})

        # 缓存结果
        cached_result = ToolResultData(
            call_id="test-id",
            success=True,
            result={"data": "value"},
        )
        manager.cache_result(call_data, cached_result)

        # 获取缓存
        result = manager.get_cached_result(call_data)
        assert result is not None
        assert result.success is True
        assert result.from_cache is True
        assert manager.get_statistics()["cached_hits"] == 1

    def test_cache_with_different_arguments(self):
        """测试不同参数使用不同缓存"""
        manager = ToolCallManager()

        call_data1 = ToolCallData(tool_name="search", arguments={"q": "test1"})
        call_data2 = ToolCallData(tool_name="search", arguments={"q": "test2"})

        result1 = ToolResultData(call_id="id1", success=True, result={"data": "value1"})
        result2 = ToolResultData(call_id="id2", success=True, result={"data": "value2"})

        manager.cache_result(call_data1, result1)
        manager.cache_result(call_data2, result2)

        cached1 = manager.get_cached_result(call_data1)
        cached2 = manager.get_cached_result(call_data2)

        assert cached1 is not None
        assert cached1.result == {"data": "value1"}
        assert cached2 is not None
        assert cached2.result == {"data": "value2"}

    def test_cache_key_stability(self):
        """测试缓存键的稳定性（相同参数生成相同键）"""
        manager = ToolCallManager()

        # 参数顺序不同但内容相同
        call_data1 = ToolCallData(tool_name="search", arguments={"a": 1, "b": 2})
        call_data2 = ToolCallData(tool_name="search", arguments={"b": 2, "a": 1})

        result = ToolResultData(call_id="test-id", success=True, result={"data": "value"})
        manager.cache_result(call_data1, result)

        # 应该能命中缓存
        cached = manager.get_cached_result(call_data2)
        assert cached is not None


class TestToolCallManagerLRU:
    """ToolCallManager LRU 淘汰策略测试"""

    def test_lru_eviction(self):
        """测试 LRU 淘汰"""
        manager = ToolCallManager(cache_size=3)

        # 添加3个缓存条目
        for i in range(3):
            call_data = ToolCallData(tool_name="search", arguments={"q": f"test{i}"})
            result = ToolResultData(call_id=f"id{i}", success=True, result={"index": i})
            manager.cache_result(call_data, result)

        assert manager.get_cache_size() == 3

        # 添加第4个，应该淘汰第1个
        call_data4 = ToolCallData(tool_name="search", arguments={"q": "test3"})
        result4 = ToolResultData(call_id="id3", success=True, result={"index": 3})
        manager.cache_result(call_data4, result4)

        assert manager.get_cache_size() == 3

        # 第1个应该被淘汰
        call_data1 = ToolCallData(tool_name="search", arguments={"q": "test0"})
        cached1 = manager.get_cached_result(call_data1)
        assert cached1 is None

        # 第4个应该存在
        call_data4_check = ToolCallData(tool_name="search", arguments={"q": "test3"})
        cached4 = manager.get_cached_result(call_data4_check)
        assert cached4 is not None

    def test_lru_access_order_update(self):
        """测试 LRU 访问顺序更新"""
        manager = ToolCallManager(cache_size=3)

        # 添加3个缓存条目
        for i in range(3):
            call_data = ToolCallData(tool_name="search", arguments={"q": f"test{i}"})
            result = ToolResultData(call_id=f"id{i}", success=True, result={"index": i})
            manager.cache_result(call_data, result)

        # 访问第1个，使其移到最后
        call_data1 = ToolCallData(tool_name="search", arguments={"q": "test0"})
        manager.get_cached_result(call_data1)

        # 添加第4个，应该淘汰第2个（因为第1个已被访问）
        call_data4 = ToolCallData(tool_name="search", arguments={"q": "test3"})
        result4 = ToolResultData(call_id="id3", success=True, result={"index": 3})
        manager.cache_result(call_data4, result4)

        # 第1个应该还在
        cached1 = manager.get_cached_result(call_data1)
        assert cached1 is not None

        # 第2个应该被淘汰
        call_data2 = ToolCallData(tool_name="search", arguments={"q": "test1"})
        cached2 = manager.get_cached_result(call_data2)
        assert cached2 is None

    def test_cache_update_existing_key(self):
        """测试更新已存在的缓存键"""
        manager = ToolCallManager(cache_size=2)

        call_data = ToolCallData(tool_name="search", arguments={"q": "test"})

        # 第一次缓存
        result1 = ToolResultData(call_id="id1", success=True, result={"version": 1})
        manager.cache_result(call_data, result1)

        # 更新缓存
        result2 = ToolResultData(call_id="id2", success=True, result={"version": 2})
        manager.cache_result(call_data, result2)

        # 缓存大小应该还是1
        assert manager.get_cache_size() == 1

        # 获取的应该是新版本
        cached = manager.get_cached_result(call_data)
        assert cached is not None
        assert cached.result == {"version": 2}


class TestToolCallManagerStatistics:
    """ToolCallManager 统计功能测试"""

    def test_get_statistics_initial(self):
        """测试初始统计信息"""
        manager = ToolCallManager()
        stats = manager.get_statistics()

        assert stats["total_calls"] == 0
        assert stats["successful_calls"] == 0
        assert stats["failed_calls"] == 0

    def test_record_successful_result(self):
        """测试记录成功结果"""
        manager = ToolCallManager()
        manager.register_call()

        result = ToolResultData(call_id="test-id", success=True, execution_time_ms=100.0)
        manager.record_result(result)

        stats = manager.get_statistics()
        assert stats["successful_calls"] == 1
        assert stats["failed_calls"] == 0
        assert stats["total_execution_time_ms"] == 100.0

    def test_record_failed_result(self):
        """测试记录失败结果"""
        manager = ToolCallManager()
        manager.register_call()

        error = ToolCallError(error_type="ValueError", error_message="Invalid input")
        result = ToolResultData(call_id="test-id", success=False, error=error)
        manager.record_result(result)

        stats = manager.get_statistics()
        assert stats["successful_calls"] == 0
        assert stats["failed_calls"] == 1


class TestToolCallManagerReset:
    """ToolCallManager 重置功能测试"""

    def test_reset_clears_all_state(self):
        """测试重置清除所有状态"""
        manager = ToolCallManager(max_calls=5, cache_size=10)

        # 执行一些操作
        for _ in range(3):
            manager.register_call()

        call_data = ToolCallData(tool_name="search", arguments={"q": "test"})
        result = ToolResultData(call_id="test-id", success=True)
        manager.cache_result(call_data, result)
        manager.record_result(result)

        # 重置
        manager.reset()

        # 验证状态已清除
        assert manager.can_execute() is True
        assert manager.get_remaining_calls() == 5
        assert manager.get_cache_size() == 0

        stats = manager.get_statistics()
        assert stats["total_calls"] == 0
        assert stats["successful_calls"] == 0


class TestToolCallManagerIntegration:
    """ToolCallManager 集成测试"""

    def test_full_workflow(self):
        """测试完整工作流程"""
        manager = ToolCallManager(max_calls=10, cache_size=5)

        # 模拟多次工具调用
        for i in range(5):
            call_data = ToolCallData(tool_name="search", arguments={"q": f"query{i}"})

            # 检查缓存
            cached = manager.get_cached_result(call_data)
            if cached is not None:
                continue

            # 检查是否可执行
            if not manager.can_execute():
                break

            # 注册并执行
            manager.register_call()

            # 模拟执行
            result = ToolResultData(
                call_id=f"call-{i}",
                success=True,
                result={"items": [f"item{i}"]},
                execution_time_ms=50.0 + i * 10,
            )

            # 缓存并记录
            manager.cache_result(call_data, result)
            manager.record_result(result)

        # 验证统计
        stats = manager.get_statistics()
        assert stats["total_calls"] == 5
        assert stats["successful_calls"] == 5
        assert stats["cache_misses"] == 5  # 首次都是未命中

        # 再次调用相同查询应该命中缓存
        call_data = ToolCallData(tool_name="search", arguments={"q": "query0"})
        cached = manager.get_cached_result(call_data)
        assert cached is not None
        assert cached.from_cache is True
