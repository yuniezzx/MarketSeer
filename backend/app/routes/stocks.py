"""
股票相关路由
"""
from flask import jsonify, request
from app.routes import api_bp
from app.models import StockInfo, db
from app.services.stock_service import StockService


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
        
        return jsonify({
            'status': 'success',
            'data': stocks,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@api_bp.route('/stocks/<code>', methods=['GET'])
def get_stock(code):
    """
    获取单只股票详情
    """
    try:
        stock = StockInfo.query.filter_by(code=code).first()
        
        if not stock:
            return jsonify({
                'status': 'error',
                'message': f'股票代码 {code} 不存在'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': stock.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@api_bp.route('/update/stocks', methods=['POST'])
def update_stocks():
    """
    更新股票数据
    从 AkShare、eFinance 等数据源更新数据库
    """
    try:
        # 获取请求参数
        data = request.get_json() or {}
        source = data.get('source', 'all')  # 指定数据源或全部更新
        
        # 调用服务层更新数据
        service = StockService()
        result = service.update_stock_info(source=source)
        
        return jsonify({
            'status': 'success',
            'message': 'stock_info updated successfully',
            'updated_rows': result.get('updated_rows', 0),
            'source': result.get('source', source)
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@api_bp.route('/stocks/search', methods=['GET'])
def search_stocks():
    """
    搜索股票
    支持按代码、名称搜索
    """
    try:
        keyword = request.args.get('keyword', '')
        
        if not keyword:
            return jsonify({
                'status': 'error',
                'message': '请提供搜索关键词'
            }), 400
        
        # 搜索股票代码或名称
        stocks = StockInfo.query.filter(
            db.or_(
                StockInfo.code.like(f'%{keyword}%'),
                StockInfo.name.like(f'%{keyword}%')
            )
        ).limit(20).all()
        
        return jsonify({
            'status': 'success',
            'data': [stock.to_dict() for stock in stocks]
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    """
    return jsonify({
        'status': 'success',
        'message': 'MarketSeer API is running'
    }), 200
