"""
工具调用管理器 (Interleaved Thinking)

管理工具调用的执行、缓存和统计。
提供调用次数限制、结果缓存（LRU策略）和统计信息收集功能。
"""

import json
from collections import OrderedDict
from dataclasses import dataclass
from hashlib import md5
from typing import Any

from deep_thinking.models.tool_call import (
    ToolCallData,
    ToolResultData,
)


@dataclass
class ToolCallStatistics:
    """
    工具调用统计信息

    记录工具调用的统计数据，用于监控和分析。

    Attributes:
        total_calls: 总调用次数
        successful_calls: 成功的调用次数
        failed_calls: 失败的调用次数
        cached_hits: 缓存命中次数
        cache_misses: 缓存未命中次数
        total_execution_time_ms: 总执行时间（毫秒）
    """

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    cached_hits: int = 0
    cache_misses: int = 0
    total_execution_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """
        转换为字典格式

        Returns:
            包含所有统计字段的字典
        """
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "cached_hits": self.cached_hits,
            "cache_misses": self.cache_misses,
            "total_execution_time_ms": self.total_execution_time_ms,
            "avg_execution_time_ms": (
                self.total_execution_time_ms / self.total_calls if self.total_calls > 0 else 0.0
            ),
        }


class ToolCallManager:
    """
    工具调用管理器

    管理工具调用的执行、缓存和统计。

    Features:
        - 调用次数限制：防止无限调用
        - 结果缓存：LRU策略缓存工具调用结果
        - 统计信息：收集调用统计数据

    Attributes:
        max_calls: 最大调用次数限制
        cache_size: 缓存大小限制
        timeout_ms: 调用超时时间（毫秒）

    Example:
        >>> manager = ToolCallManager(max_calls=100, cache_size=50)
        >>> if manager.can_execute():
        ...     manager.register_call()
        ...     # 执行工具调用
    """

    def __init__(
        self,
        max_calls: int = 100,
        cache_size: int = 50,
        timeout_ms: float = 30000.0,
    ):
        """
        初始化工具调用管理器

        Args:
            max_calls: 最大调用次数限制，默认100
            cache_size: 缓存大小限制，默认50
            timeout_ms: 调用超时时间（毫秒），默认30000
        """
        self.max_calls = max_calls
        self.cache_size = cache_size
        self.timeout_ms = timeout_ms

        # 内部状态
        self._call_count: int = 0
        self._cache: OrderedDict[str, ToolResultData] = OrderedDict()
        self._statistics: ToolCallStatistics = ToolCallStatistics()

    def can_execute(self) -> bool:
        """
        检查是否还可以执行工具调用

        Returns:
            True 如果还可以执行，False 如果已达到限制
        """
        return self._call_count < self.max_calls

    def register_call(self) -> None:
        """
        注册一次工具调用

        增加调用计数。应在执行工具调用前调用。
        """
        self._call_count += 1
        self._statistics.total_calls += 1

    def _generate_cache_key(self, call_data: ToolCallData) -> str:
        """
        生成缓存键

        使用工具名称和参数生成唯一键。

        Args:
            call_data: 工具调用数据

        Returns:
            缓存键字符串
        """
        # 将参数序列化为稳定排序的 JSON 字符串
        args_str = json.dumps(call_data.arguments, sort_keys=True)
        args_hash = md5(args_str.encode(), usedforsecurity=False).hexdigest()
        return f"{call_data.tool_name}:{args_hash}"

    def get_cached_result(self, call_data: ToolCallData) -> ToolResultData | None:
        """
        获取缓存的结果

        如果缓存命中，将结果移到 OrderedDict 末尾（LRU策略）。

        Args:
            call_data: 工具调用数据

        Returns:
            缓存的结果，如果不存在则返回 None
        """
        key = self._generate_cache_key(call_data)
        if key in self._cache:
            # LRU: 移到末尾表示最近使用
            self._cache.move_to_end(key)
            self._statistics.cached_hits += 1
            # 标记结果来自缓存
            result = self._cache[key]
            result.from_cache = True
            return result

        self._statistics.cache_misses += 1
        return None

    def cache_result(self, call_data: ToolCallData, result: ToolResultData) -> None:
        """
        缓存工具调用结果

        使用 LRU 策略管理缓存大小。

        Args:
            call_data: 工具调用数据
            result: 工具调用结果
        """
        key = self._generate_cache_key(call_data)

        # 如果键已存在，先删除（更新位置）
        if key in self._cache:
            del self._cache[key]

        # LRU 淘汰：如果缓存已满，删除最久未使用的条目
        while len(self._cache) >= self.cache_size:
            self._cache.popitem(last=False)

        # 添加新条目
        self._cache[key] = result

    def record_result(self, result: ToolResultData) -> None:
        """
        记录工具调用结果到统计

        Args:
            result: 工具调用结果
        """
        if result.success:
            self._statistics.successful_calls += 1
        else:
            self._statistics.failed_calls += 1

        if result.execution_time_ms is not None:
            self._statistics.total_execution_time_ms += result.execution_time_ms

    def get_statistics(self) -> dict[str, Any]:
        """
        获取统计信息

        Returns:
            包含统计信息的字典
        """
        return self._statistics.to_dict()

    def reset(self) -> None:
        """
        重置管理器状态

        清空调用计数、缓存和统计信息。
        """
        self._call_count = 0
        self._cache.clear()
        self._statistics = ToolCallStatistics()

    def get_cache_size(self) -> int:
        """
        获取当前缓存大小

        Returns:
            缓存中的条目数
        """
        return len(self._cache)

    def get_remaining_calls(self) -> int:
        """
        获取剩余可调用次数

        Returns:
            剩余可调用次数
        """
        return max(0, self.max_calls - self._call_count)


__all__ = [
    "ToolCallManager",
    "ToolCallStatistics",
]
