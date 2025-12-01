"""
龙虎榜相关路由
"""

from flask import jsonify, request
from app.routes import api_bp
from app.models import DailyLHB
from app.services.lhb_service import LhbService


@api_bp.route('/lhb/getLhbByDate', methods=['GET'])
def get_lhb_data():
    """
    获取龙虎榜数据
    支持按日期范围查询

    Query Parameters:
        startDate: 开始日期 (YYYY-MM-DD)
        endDate: 结束日期 (YYYY-MM-DD)
    """
    try:
        # 获取查询参数
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')

        if not start_date or not end_date:
            return jsonify({'status': 'error', 'message': '请提供开始日期和结束日期'}), 400

        # 使用 LhbService 查询数据
        lhb_service = LhbService()
        lhb_data = lhb_service.get_lhb_by_date_range(start_date, end_date)

        # 转换为字典格式
        data = [item.to_dict() for item in lhb_data]

        return jsonify({'status': 'success', 'data': data, 'count': len(data)}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/lhb/<string:code>', methods=['GET'])
def get_lhb_by_code(code):
    """
    获取指定股票的龙虎榜数据

    Path Parameters:
        code: 股票代码

    Query Parameters (optional):
        startDate: 开始日期 (YYYY-MM-DD)
        endDate: 结束日期 (YYYY-MM-DD)
    """
    try:
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')

        # 使用 LhbService 查询数据
        lhb_service = LhbService()
        lhb_data = lhb_service.get_lhb_by_code(code, start_date, end_date)

        if not lhb_data:
            return jsonify({'status': 'error', 'message': f'未找到股票代码 {code} 的龙虎榜数据'}), 404

        # 转换为字典格式
        data = [item.to_dict() for item in lhb_data]

        return jsonify({'status': 'success', 'data': data, 'count': len(data)}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/lhb/update', methods=['POST'])
def update_lhb_data():
    """
    更新龙虎榜数据
    从 AkShare 获取并保存到数据库

    Request Body:
        {
            "startDate": "YYYY-MM-DD",
            "endDate": "YYYY-MM-DD"
        }
    """
    try:
        data = request.get_json()
        start_date = data.get('startDate')
        end_date = data.get('endDate')

        if not start_date or not end_date:
            return jsonify({'status': 'error', 'message': '请提供开始日期和结束日期'}), 400

        # 使用 LhbService 更新数据
        lhb_service = LhbService()
        updated_count = lhb_service.fetch_and_update_lhb_data(start_date, end_date)

        return (
            jsonify(
                {
                    'status': 'success',
                    'message': f'成功更新 {updated_count} 条龙虎榜数据',
                    'count': updated_count,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/lhb/search', methods=['GET'])
def search_lhb():
    """
    搜索龙虎榜数据

    Query Parameters:
        keyword: 搜索关键词 (股票代码或名称)
    """
    try:
        keyword = request.args.get('keyword')

        if not keyword:
            return jsonify({'status': 'error', 'message': '请提供搜索关键词'}), 400

        # 使用 LhbService 搜索数据
        lhb_service = LhbService()
        lhb_data = lhb_service.search_lhb(keyword)

        # 转换为字典格式
        data = [item.to_dict() for item in lhb_data]

        return jsonify({'status': 'success', 'data': data, 'count': len(data)}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
