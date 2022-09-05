import qbot.config.config as config
from os import getenv


def test_file_paths():
    assert config.path_config.exists(), "Configuration file is not exist"
    assert config.auth_path.exists(), "Authentication file is not exist"
    assert config.path_db.exists(), "DB file is not exist"
    assert config.path_tests_db.exists(), "Test DB file is not exist"
    assert config.path_scheme.exists(), "Scheme file for DB is not exist"


def test_auth_credentials():
    assert getenv("TELE_TOKEN"), "TELE_TOKEN is not exist in auth.env"
    assert getenv("TINKOFF_TOKEN"), "TINKOFF_TOKEN is not exist in auth.env"
    assert getenv("TINKOFF_ACCOUNT_ID"), "TINKOFF_ACCOUNT_ID is not exist in auth.env"

