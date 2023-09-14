import logging
from .config import settings

log_level = logging.DEBUG if settings.DEBUG else logging.INFO

logging.basicConfig(level=log_level)

# TODO: 这只是个十分简陋的logger配置还有以下工作要完成
# [ ]: 日志格式配置
# [ ]: 日志文件输出
# [ ]: 日志输出目录配置
# [ ]: 控制台日志输出
# [ ]: 日志等级开关
