import logging
from os import getenv
from os import environ

from fsd_utils import configclass
from fsd_utils import CommonConfig


@configclass
class DefaultConfig(object):
    # Logging
    FSD_LOG_LEVEL = logging.WARNING

    SECRET_KEY = CommonConfig.SECRET_KEY

    FAB_HOST = getenv("FAB_HOST", "fab:8080/")
    FAB_SAVE_PER_PAGE = getenv("FAB_SAVE_PER_PAGE", "dev/save")
    FORM_RUNNER_URL = getenv("FORM_RUNNER_INTERNAL_HOST", "http://form-runner:3009")
    FORM_RUNNER_URL_REDIRECT = getenv("FORM_RUNNER_EXTERNAL_HOST", "http://localhost:3009")
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")
