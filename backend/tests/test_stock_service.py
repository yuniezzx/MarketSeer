import pytest
from app.services.stock_service import StockService

class DummyAkShare:
    def stock_info_a_code_name(self):
        return DummyDF()

class DummyDF:
    def to_dict(self, orient=None):
        return [
            {'code': '000001', 'name': '平安银行'},
            {'code': '000002', 'name': '万科A'}
        ]

def test_fetch_from_akshare(monkeypatch):
    service = StockService()
    # mock akshare
    monkeypatch.setattr('app.services.stock_service.__import__', lambda name, *args: DummyAkShare() if name == 'akshare' else __import__(name, *args))
    monkeypatch.setattr('app.services.stock_service.getattr', lambda obj, name, default=None: getattr(DummyAkShare(), name, default))
    result = service._fetch_from_akshare('stock_info_a_code_name')
    assert isinstance(result, list)
    assert result[0]['code'] == '000001'
    assert result[1]['name'] == '万科A'
