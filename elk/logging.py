import logging


def _get_logger():
    return logging.getLogger('app')


class logger():
    @staticmethod
    def warning(*args, **kwargs):
        kwargs['exc_info'] = True
        _get_logger().warning(*args, **kwargs)

    @staticmethod
    def error(*args, **kwargs):
        kwargs['exc_info'] = True
        _get_logger().error(*args, **kwargs)
