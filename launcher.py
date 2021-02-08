from lib.bot import bot
from utils.jsons import write_json, read_json
from utils.tools import manage_version


import logging
import contextlib


@contextlib.contextmanager
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    try:
        dt_fmt = '%A | %Y/%m/%d %H:%M:%S'
        fmt = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}', dt_fmt, style='{')
        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.INFO)

        file_hdlr = logging.FileHandler(
            filename='data/logs/log.txt',
            encoding="utf-8",
            mode='w')
        file_hdlr.setFormatter(fmt)
        logger.addHandler(file_hdlr)

        yield
    finally:
        handlers = logger.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            logger.removeHandler(hdlr)


with setup_logging():
    version = manage_version()
    bot.run(version)
