import efinance as ef
from .base import BaseClient


class EfinanceClient(BaseClient):
    def fetch(self, symbol: str) -> dict:
        """Fetch stock data using Efinance"""
        pass
