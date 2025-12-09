from flask import Blueprint, request, jsonify
from app.services import StocksService

stocks_bp = Blueprint('stocks', __name__, url_prefix='/api/stocks')


# 获取所有股票
@stocks_bp.route('', methods=['GET'])
def list_stocks():
    return "List of stocks"


# 添加新股票
@stocks_bp.route('', methods=['POST'])
def add_stock():
    """
    Query Parameters:
    {
        "symbol": "AAPL"
    }
    """
    try:
        data = request.get_json()
        symbol = data.get("symbol")

        if not symbol:
            return {"error": "symbol is required"}, 400

        service = StocksService()
        result = service.add_stock(symbol)

        return (
            jsonify({'status': 'success', 'message': 'Stock added successfully', 'data': result}),
            201,
        )

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
