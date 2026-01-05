"""
Pytest配置和共享fixtures

这个文件包含所有测试用例共享的配置和fixtures。
"""

import logging
import os
import sys
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp.server import FastMCP

# 延迟导入deep_thinking模块以避免CoverageWarning
_setup_logging = None


def _get_setup_logging():
    """延迟导入setup_logging以避免CoverageWarning"""
    global _setup_logging
    if _setup_logging is None:
        from deep_thinking.utils.logger import setup_logging  # type: ignore[import-untyped]

        _setup_logging = setup_logging
    return _setup_logging


# =============================================================================
# 测试配置
# =============================================================================


def pytest_configure(config):
    """Pytest配置钩子"""
    config.addinivalue_line("markers", "unit: 单元测试标记")
    config.addinivalue_line("markers", "integration: 集成测试标记")
    config.addinivalue_line("markers", "transport: 传输层测试标记")
    config.addinivalue_line("markers", "slow: 慢速测试标记")


# =============================================================================
# 日志配置
# =============================================================================


@pytest.fixture(autouse=True)
def configure_logging_for_tests():
    """
    自动配置测试日志

    所有测试都会使用这个日志配置
    """
    # 使用延迟导入的setup_logging
    setup_logging = _get_setup_logging()
    # 使用stderr输出日志，避免干扰测试输出
    setup_logging("stdio")
    logging.getLogger().setLevel(logging.DEBUG)


# =============================================================================
# 临时目录fixtures
# =============================================================================


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """
    临时目录fixture

    每个测试都会获得一个独立的临时目录
    """
    with tempfile.TemporaryDirectory() as temp_path:
        yield Path(temp_path)


@pytest.fixture
def temp_sessions_dir(temp_dir: Path) -> Generator[Path, None, None]:
    """
    临时会话目录fixture

    在temp_dir下创建sessions目录
    """
    sessions_dir = temp_dir / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    yield sessions_dir


# =============================================================================
# MCP服务器fixtures
# =============================================================================


@pytest.fixture
def mcp_server() -> FastMCP:
    """
    FastMCP服务器fixture

    提供一个用于测试的MCP服务器实例
    """
    app = FastMCP("test-server")
    return app


@pytest.fixture
def mock_storage_manager():
    """
    Mock存储管理器fixture

    用于需要mock存储的测试
    """
    storage = AsyncMock()
    storage.create_session = AsyncMock()
    storage.get_session = AsyncMock()
    storage.update_session = AsyncMock()
    storage.delete_session = AsyncMock()
    storage.list_sessions = AsyncMock()
    return storage


# =============================================================================
# 异步事件循环fixtures
# =============================================================================
#
# 注意：自定义event_loop fixture已被pytest-asyncio弃用
# 现在使用@pytest.mark.asyncio(loop_scope="session")来实现session级别事件循环
# 参考文档：https://pytest-asyncio.readthedocs.io/en/latest/reference.html#pytest-asyncio-event-loop-policy-overrides



# =============================================================================
# 测试数据fixtures
# =============================================================================


@pytest.fixture
def sample_thought_data():
    """示例思考步骤数据"""
    return {
        "thought_number": 1,
        "content": "这是一个测试思考",
        "type": "regular",
        "is_revision": False,
        "revises_thought": None,
        "branch_from_thought": None,
        "branch_id": None,
        "timestamp": "2025-12-31T00:00:00Z",
    }


@pytest.fixture
def sample_session_data():
    """示例会话数据"""
    return {
        "session_id": "test-session-123",
        "name": "测试会话",
        "description": "这是一个测试会话",
        "created_at": "2025-12-31T00:00:00Z",
        "updated_at": "2025-12-31T00:00:00Z",
        "status": "active",
        "thoughts": [],
        "metadata": {},
    }


@pytest.fixture
def sample_thought_input():
    """示例思考输入数据"""
    return {
        "thought": "这是一个测试思考",
        "nextThoughtNeeded": True,
        "thoughtNumber": 1,
        "totalThoughts": 5,
        "session_id": "test-session-123",
    }


# =============================================================================
# Mock fixtures
# =============================================================================


@pytest.fixture
def mock_aiohttp_response():
    """Mock aiohttp响应"""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/event-stream"}
    mock_response.text = AsyncMock(return_value="OK")
    return mock_response


@pytest.fixture
def mock_aiohttp_session(mock_aiohttp_response):
    """Mock aiohttp会话"""
    mock_session = AsyncMock()
    mock_session.post = AsyncMock(return_value=mock_aiohttp_response)
    mock_session.get = AsyncMock(return_value=mock_aiohttp_response)
    return mock_session


# =============================================================================
# 环境变量fixtures
# =============================================================================


@pytest.fixture
def clean_env():
    """清洁的环境变量fixture"""
    original_env = os.environ.copy()

    yield

    # 恢复原始环境变量
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def stdio_env(clean_env):
    """STDIO模式环境变量"""
    os.environ["DEEP_THINKING_TRANSPORT"] = "stdio"


@pytest.fixture
def sse_env(clean_env):
    """SSE模式环境变量"""
    os.environ["DEEP_THINKING_TRANSPORT"] = "sse"
    os.environ["DEEP_THINKING_HOST"] = "localhost"
    os.environ["DEEP_THINKING_PORT"] = "8000"


# =============================================================================
# 性能测试fixtures
# =============================================================================


@pytest.fixture
def benchmark_timer():
    """基准测试计时器"""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.elapsed = None

        def start(self):
            self.start_time = time.perf_counter()
            return self

        def stop(self):
            self.end_time = time.perf_counter()
            self.elapsed = self.end_time - self.start_time
            return self.elapsed

    return Timer()


# =============================================================================
# 跳过条件fixtures
# =============================================================================


@pytest.fixture
def skip_slow_tests(request):
    """当运行快速测试时跳过慢速测试"""
    if request.config.getoption("--runslow", default=False) is False:
        pytest.skip("需要--runslow选项来运行慢速测试")


# =============================================================================
# 辅助函数
# =============================================================================


def assert_valid_uuid(uuid_string: str) -> bool:
    """验证UUID格式"""
    import re

    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return re.match(uuid_pattern, uuid_string, re.IGNORECASE) is not None


def assert_log_contains(caplog, level: int, message: str):
    """断言日志包含特定消息"""
    assert any(
        record.levelno == level and message in record.message for record in caplog.records
    ), f"日志中没有找到: {logging.getLevelName(level)} - {message}"
