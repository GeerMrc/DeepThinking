"""
Logger模块测试
"""

import logging
import sys

from deep_thinking.utils.logger import LoggingContext, get_logger, setup_logging


class TestSetupLogging:
    """setup_logging函数测试"""

    def test_setup_logging_stdio_mode(self):
        """测试STDIO模式日志配置"""
        logger = setup_logging("stdio")

        assert logger is not None
        assert logger.level == logging.INFO
        # STDIO模式应该使用stderr
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
        # 检查handler输出到stderr
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                assert handler.stream == sys.stderr

    def test_setup_logging_sse_mode(self):
        """测试SSE模式日志配置"""
        logger = setup_logging("sse")

        assert logger is not None
        assert logger.level == logging.INFO
        # SSE模式应该使用stdout
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                assert handler.stream == sys.stdout

    def test_setup_logging_custom_level(self):
        """测试自定义日志级别"""
        logger = setup_logging("stdio", level=logging.DEBUG)

        assert logger.level == logging.DEBUG
        for handler in logger.handlers:
            assert handler.level == logging.DEBUG

    def test_setup_logging_warning_level(self):
        """测试WARNING级别"""
        logger = setup_logging("sse", level=logging.WARNING)

        assert logger.level == logging.WARNING

    def test_setup_logging_error_level(self):
        """测试ERROR级别"""
        logger = setup_logging("stdio", level=logging.ERROR)

        assert logger.level == logging.ERROR

    def test_setup_logging_clears_existing_handlers(self):
        """测试清除现有handlers"""
        # 首次设置
        logger1 = setup_logging("stdio")
        initial_handler_count = len(logger1.handlers)

        # 再次设置，应该清除之前的handlers
        logger2 = setup_logging("sse")
        assert len(logger2.handlers) == initial_handler_count

    def test_setup_logging_formatter(self):
        """测试日志格式化器"""
        logger = setup_logging("stdio")

        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                assert handler.formatter is not None
                assert isinstance(handler.formatter, logging.Formatter)

    def test_setup_logging_creates_handlers(self):
        """测试setup_logging创建handlers"""
        logger = setup_logging("stdio", level=logging.INFO)

        # 验证handler被创建
        assert len(logger.handlers) > 0
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)


class TestGetLogger:
    """get_logger函数测试"""

    def test_get_logger_with_name(self):
        """测试获取命名logger"""
        logger = get_logger("test.logger")

        assert logger is not None
        assert logger.name == "test.logger"

    def test_get_logger_returns_same_instance(self):
        """测试返回相同的logger实例"""
        logger1 = get_logger("test.same")
        logger2 = get_logger("test.same")

        assert logger1 is logger2

    def test_get_logger_different_names(self):
        """测试不同名称返回不同logger"""
        logger1 = get_logger("test.first")
        logger2 = get_logger("test.second")

        assert logger1 is not logger2
        assert logger1.name == "test.first"
        assert logger2.name == "test.second"

    def test_get_logger_with_module_name(self):
        """测试使用__name__作为logger名称"""
        logger = get_logger(__name__)

        assert logger.name == __name__


class TestLoggingContext:
    """LoggingContext上下文管理器测试"""

    def test_logging_context_changes_level(self):
        """测试上下文管理器修改日志级别"""
        logger = logging.getLogger("test.context")
        original_level = logger.level

        with LoggingContext(logging.DEBUG, logger):
            assert logger.level == logging.DEBUG

        # 恢复原级别
        assert logger.level == original_level

    def test_logging_context_with_root_logger(self):
        """测试使用根logger"""
        root_logger = logging.getLogger()
        original_level = root_logger.level

        with LoggingContext(logging.WARNING):
            assert root_logger.level == logging.WARNING

        assert root_logger.level == original_level

    def test_logging_context_nested(self):
        """测试嵌套上下文"""
        logger = logging.getLogger("test.nested")
        logger.setLevel(logging.INFO)

        with LoggingContext(logging.DEBUG, logger):
            assert logger.level == logging.DEBUG
            with LoggingContext(logging.ERROR, logger):
                assert logger.level == logging.ERROR
            # 内层结束后恢复到DEBUG
            assert logger.level == logging.DEBUG

        # 外层结束后恢复到INFO
        assert logger.level == logging.INFO

    def test_logging_context_exception_handling(self):
        """测试异常处理"""
        logger = logging.getLogger("test.exception")
        original_level = logger.level

        try:
            with LoggingContext(logging.DEBUG, logger):
                assert logger.level == logging.DEBUG
                raise ValueError("Test exception")
        except ValueError:
            pass

        # 异常后应该恢复原级别
        assert logger.level == original_level

    def test_logging_context_returns_self(self):
        """测试上下文管理器返回自身"""
        context = LoggingContext(logging.INFO)
        result = context.__enter__()

        assert result is context

    def test_logging_context_preserves_handlers(self):
        """测试上下文不改变handlers"""
        logger = setup_logging("stdio")
        initial_handlers = list(logger.handlers)

        with LoggingContext(logging.DEBUG, logger):
            pass

        # handlers应该保持不变
        assert len(logger.handlers) == len(initial_handlers)


class TestLoggerIntegration:
    """Logger集成测试"""

    def test_logger_can_log_all_levels(self, caplog):
        """测试所有日志级别"""
        logger = get_logger("test.levels")
        logger.setLevel(logging.DEBUG)

        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")

        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text
        assert "Critical message" in caplog.text

    def test_logger_respects_level_filtering(self, caplog):
        """测试日志级别过滤"""
        logger = get_logger("test.filter")
        logger.setLevel(logging.WARNING)

        with caplog.at_level(logging.DEBUG):
            logger.debug("Should not appear")
            logger.info("Should not appear")
            logger.warning("Should appear")
            logger.error("Should appear")

        # DEBUG和INFO应该被过滤
        assert "Should not appear" not in caplog.text
        assert "Should appear" in caplog.text
