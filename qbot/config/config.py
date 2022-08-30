from yaml import safe_load
from pathlib import Path
from dotenv import load_dotenv
from qbot.logger import logger


path_config = Path.home() / 'QuoteBeholderBot' / 'qbot' / 'config' / 'default-config.yml'
with open(path_config) as f:
    CONFIG = safe_load(f)

auth_path = Path.home() / 'QuoteBeholderBot' / 'auth.env'
if Path.exists(auth_path):
    load_dotenv(auth_path)
else:
    logger.error("auth.env not found in root folder!")
path_db = Path.home() / 'QuoteBeholderBot' / 'qbot' / 'db' / CONFIG['database_name']
path_tests_db = Path.home() / 'QuoteBeholderBot' / 'qbot' / 'tests' / 'data' / CONFIG['test_database_name']
path_scheme = Path.home() / 'QuoteBeholderBot' / 'qbot' / 'db' / CONFIG['db_scheme_name']