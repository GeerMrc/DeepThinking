"""
数据模型模块

包含所有 Pydantic 数据模型的导出。
"""

from deep_thinking.models.config import ThinkingConfig, get_global_config, set_global_config
from deep_thinking.models.task import TaskStatus, ThinkingTask
from deep_thinking.models.template import Template
from deep_thinking.models.thinking_session import ThinkingSession
from deep_thinking.models.thought import ExecutionPhase, Thought
from deep_thinking.models.tool_call import (
    ToolCallData,
    ToolCallError,
    ToolCallRecord,
    ToolResultData,
)

__all__ = [
    # 思考相关
    "Thought",
    "ExecutionPhase",
    "ThinkingSession",
    # 模板相关
    "Template",
    # 任务相关
    "ThinkingTask",
    "TaskStatus",
    # 配置相关
    "ThinkingConfig",
    "get_global_config",
    "set_global_config",
    # 工具调用相关 (Interleaved Thinking)
    "ToolCallData",
    "ToolCallError",
    "ToolResultData",
    "ToolCallRecord",
]
