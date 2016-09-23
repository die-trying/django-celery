import logging


def _get_logger():
    return logging.getLogger('app')


class logger():
    @staticmethod
    def warning(*args, **kwargs):
        _get_logger().warning(*args, **kwargs)

    @staticmethod
    def error(*args, **kwargs):
        _get_logger().error(*args, **kwargs)
