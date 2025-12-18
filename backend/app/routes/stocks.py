from flask import Blueprint, request, jsonify
from app.services import StocksService

stocks_bp = Blueprint('stocks', __name__, url_prefix='/api/stocks')


# 获取所有股票
@stocks_bp.route('', methods=['GET'])
def list_stocks():
    """
    Query Parameters:
    - offset: int (default: 0) - 分页偏移量
    - limit: int (optional) - 返回数量限制
    - order_by: str (optional) - 排序字段
    - desc: bool (default: false) - 是否降序
    """
    try:
        offset = request.args.get('offset', 0, type=int)
        limit = request.args.get('limit', type=int)
        order_by = request.args.get('order_by', type=str)
        desc = request.args.get('desc', 'false').lower() == 'true'
        
        service = StocksService()
        stocks = service.list_stocks(offset=offset, limit=limit, order_by=order_by, desc=desc)
        
        return jsonify({
            'status': 'success',
            'message': 'Stocks retrieved successfully',
            'data': stocks
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


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
