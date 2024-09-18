import logging
from os import getenv

from fsd_utils import configclass

from config.envs.default import DefaultConfig as Config


@configclass
class UnitTestConfig(Config):

    # Logging
    FSD_LOG_LEVEL = logging.DEBUG

    SECRET_KEY = "unit_test"

    SQLALCHEMY_DATABASE_URI = getenv(
        "DATABASE_URL_UNIT_TEST",
        "postgresql://postgres:postgres@127.0.0.1:5432/fab_unit_test",  # pragma: allowlist secret
    )
