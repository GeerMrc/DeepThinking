"""
传输感知的日志配置模块

根据传输模式（STDIO/SSE）配置日志系统，确保日志不会干扰JSON-RPC通信。

关键规则:
- STDIO模式: 日志必须输出到stderr，严禁使用print()
- SSE模式: 日志可以输出到stdout或文件

使用示例:
    from deep_thinking.utils.logger import setup_logging
    import logging

    # STDIO模式
    logger = setup_logging("stdio")
    logger.info("这会输出到stderr")

    # SSE模式
    logger = setup_logging("sse")
    logger.info("这会输出到stdout")
"""

import logging
import sys
from typing import Literal


def setup_logging(
    transport_mode: Literal["stdio", "sse"] = "stdio", level: int = logging.INFO
) -> logging.Logger:
    """
    配置传输感知的日志系统

    Args:
        transport_mode: 传输模式，"stdio" 或 "sse"
        level: 日志级别

    Returns:
        配置好的根logger实例

    注意:
        STDIO模式: 日志输出到stderr（stdout用于JSON-RPC）
        SSE模式: 日志输出到stdout（或可配置到文件）

    严禁:
        - 在STDIO模式下使用print()函数
        - 任何模式下将日志输出到stdio模式的stdout
    """
    # 获取根logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 清除现有handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    if transport_mode == "stdio":
        # STDIO模式：强制输出到stderr
        # stdout用于JSON-RPC通信，任何输出到stdout的内容都会破坏协议
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)
        root_logger.info("STDIO模式: 日志输出到stderr，严禁使用print()")

    else:
        # SSE模式：可以使用stdout或文件
        # 默认使用stdout，方便在终端查看
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        root_logger.info("SSE模式: 日志输出到stdout")

    # 设置格式化器
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    # 添加handler
    root_logger.addHandler(handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    获取命名logger

    Args:
        name: logger名称，通常使用__name__

    Returns:
        Logger实例

    Example:
        from deep_thinking.utils.logger import get_logger

        logger = get_logger(__name__)
        logger.info("这是一条日志")
    """
    return logging.getLogger(name)


class LoggingContext:
    """
    日志上下文管理器

    用于临时修改日志级别

    Example:
        with LoggingContext(logging.DEBUG):
            logger.debug("这条调试日志会被显示")
    """

    def __init__(self, level: int, logger: logging.Logger | None = None):
        self.level = level
        self.logger = logger or logging.getLogger()
        self.old_level: int = 0

    def __enter__(self) -> "LoggingContext":
        self.old_level = self.logger.level
        self.logger.setLevel(self.level)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        self.logger.setLevel(self.old_level)
