import logging
from fastapi import FastAPI
from qual.core import xyapi

logger = logging.getLogger(__name__)


@xyapi.register(__name__)
def install(app: FastAPI):
    logger.debug(f"安装 {__package__}")
