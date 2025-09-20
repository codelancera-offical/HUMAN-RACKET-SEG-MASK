# logger_config.py

import logging
import sys

def setup_logger():
    """
    配置一个全局的、格式化的日志记录器。
    """
    # 获取根日志记录器
    logger = logging.getLogger()
    
    # 设置日志级别为 INFO，这意味着 INFO, WARNING, ERROR, CRITICAL 都会被记录
    logger.setLevel(logging.INFO)

    # 如果已经存在 handlers，则不再重复添加，避免日志重复输出
    if logger.hasHandlers():
        return logger

    # 创建一个日志格式器
    # 格式: [时间] - [日志级别] - [消息]
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 创建一个流处理器 (StreamHandler)，用于将日志输出到控制台 (stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    # 将处理器添加到日志记录器中
    logger.addHandler(stream_handler)

    return logger