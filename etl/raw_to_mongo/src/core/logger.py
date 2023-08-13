"""Logger with colored format."""

import logging


class CustomFormatter(logging.Formatter):

    default ="\x1b[49m"
    blue = "\x1b[34m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: default + format + reset,
        logging.INFO: blue + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger() -> logging.Logger:
    """Returns .logger with colored format.

    :return logging.Logger
    """
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
    return logger


# logger.debug("debug message, color — white")
# logger.info("info message, color — blue")
# logger.warning("warning message, color — orange")
# logger.error("error message, color — red")
# logger.critical("criticalerror message, color — red")
logger = get_logger()
