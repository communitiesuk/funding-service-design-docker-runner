import logging

from fsd_utils import configclass

from config.envs.default import DefaultConfig as Config


@configclass
class UnitTestConfig(Config):

    # Logging
    FSD_LOG_LEVEL = logging.DEBUG

    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:password@fab-db:5432/fab_unit_test"  # pragma: allowlist secret
