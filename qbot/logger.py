import logging
from logging.handlers import RotatingFileHandler


formatter = logging.Formatter(
    "{asctime} | {filename}:{funcName} | {levelname} | {message}",
    "%Y-%m-%d %H:%M:%S",
    style="{"
)

# Пишется лог со всех модулей с severity DEBUG и выше в quotebeholder_debug.log
debuging = logging.getLogger()
debuging.setLevel(logging.DEBUG)
all_log = RotatingFileHandler(
    "/var/log/quotebeholder/quotebeholder_debug.log", maxBytes=1000000, backupCount=10
)
all_log.setLevel(logging.DEBUG)
all_log.setFormatter(formatter)
debuging.addHandler(all_log)

# Логи самого приложения пишутся в quotebeholder.log
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logfile = logging.FileHandler("/var/log/quotebeholder/quotebeholder.log")
logfile.setLevel(logging.INFO)
logfile.setFormatter(formatter)
logger.addHandler(logfile)