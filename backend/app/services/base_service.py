from logger import logger
from config import Config


class BaseService:
    def __init__(self):
        self.config = Config()
        self.logger = logger
