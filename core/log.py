import logging


class MyLogger:
    def __init__(self):
        # 定义Loggers
        self.logger = logging.getLogger('applog')
        # 一般设置为低于 handler 的日志级别
        self.logger.setLevel(logging.DEBUG)

        # 没有给 handler 指定日志级别，将使用绑定的logger级别
        console_handler = logging.StreamHandler()

        # 比logger的日志级别高，可以应用
        file_handler = logging.FileHandler(filename='logs/daily_check.log', mode='a')
        file_handler.setLevel(logging.WARNING)

        # 定义Formatters
        formatter = logging.Formatter("%(asctime)s|%(levelname)8s|%(lineno)s|%(message)s")
        # 里面的8，10实现了占位对齐，是字符串格式化的形式

        # 将formatter绑定到Handlers上面
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # 将Handlers与Loggers绑定
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

# 由于logger绑定了两个Handlers，这份日志会按照各自Handler的日志级别，输出到相应的地方（这里是控制台和文件）
# logger.debug("debug_msg")
# logger.info("info_msg")
# logger.warning("warning_msg")
# logger.error("error_msg")
# logger.critical("critical_msg")
