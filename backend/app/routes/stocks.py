"""
股票相关路由
"""

from flask import jsonify, request
from app.routes import api_bp
from app.models import StockInfo, db
from app.services.stock_service import StockInfoService


@api_bp.route('/stocks', methods=['GET'])
def get_stocks():
    """
    获取股票列表
    支持分页和筛选
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        market = request.args.get('market', None)
        industry = request.args.get('industry', None)

        # 构建查询
        query = StockInfo.query

        if market:
            query = query.filter_by(market=market)
        if industry:
            query = query.filter_by(industry=industry)

        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        stocks = [stock.to_dict() for stock in pagination.items]

        return (
            jsonify(
                {
                    'status': 'success',
                    'data': stocks,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/stocks/<string:code>', methods=['GET'])
def get_stock_detail(code):
    """
    获取指定股票的详细信息
    """
    try:
        stock = StockInfo.query.filter_by(code=code).first()
        if not stock:
            return jsonify({'status': 'error', 'message': f'未找到股票代码 {code} 的信息'}), 404

        return jsonify({'status': 'success', 'data': stock.to_dict()}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/stocks/AddStock', methods=['POST'])
def add_stock():
    """
    添加新股票
    请求体应包含股票代码
    """
    try:
        data = request.get_json()
        code = data.get('code')['code']
        print('code:', code)
        if not code:
            return jsonify({'status': 'error', 'message': '股票代码不能为空'}), 400

        # 使用 StockInfoService 添加股票
        stock_service = StockInfoService()
        stock_info = stock_service.add_stock_by_code(code)

        if not stock_info:
            return jsonify({'status': 'error', 'message': f'无法获取股票代码 {code} 的信息'}), 404

        return jsonify({'status': 'success', 'data': stock_info.to_dict()}), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
