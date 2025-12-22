from flask import Blueprint, request, jsonify
from app.services import DragonTigerService, ActiveBrokerageService

dragon_tiger_bp = Blueprint("dragon_tiger", __name__, url_prefix="/api/dragon-tiger")


# 获取每日龙虎榜数据（最近N天）
@dragon_tiger_bp.route("/daily", methods=["GET"])
def get_daily_dragon_tiger():
    """
    获取最近N天的龙虎榜数据

    Query Parameters:
    - daysBack: int (default: 7) - 查询最近几天的数据

    Response:
    {
        "status": "success",
        "message": "查询成功",
        "data": [...],
        "meta": {
            "daysBack": 7,
            "count": 150,
        }
    }
    """
    try:
        # 获取查询参数
        days_back = request.args.get("daysBack", 7, type=int)

        # 参数验证
        if days_back < 1 or days_back > 365:
            return jsonify({"status": "error", "message": "daysBack 必须在 1-365 之间"}), 400

        # 调用服务层
        service = DragonTigerService()
        data = service.get_daily_dragon_tiger(days_back=days_back)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"成功获取最近 {days_back} 天的龙虎榜数据",
                    "data": data,
                    "meta": {
                        "daysBack": days_back,
                        "count": len(data),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 获取每日活跃营业部数据（最近N天）
@dragon_tiger_bp.route("/daily-brokerage", methods=["GET"])
def get_daily_active_brokerage():
    """
    获取最近N天的活跃营业部数据

    Query Parameters:
    - daysBack: int (default: 7) - 查询最近几天的数据

    Response:
    {
        "status": "success",
        "message": "查询成功",
        "data": [...],
        "meta": {
            "daysBack": 7,
            "count": 150,
        }
    }
    """
    try:
        # 获取查询参数
        days_back = request.args.get("daysBack", 7, type=int)

        # 参数验证
        if days_back < 1 or days_back > 365:
            return jsonify({"status": "error", "message": "daysBack 必须在 1-365 之间"}), 400

        # 调用服务层
        service = ActiveBrokerageService()
        data = service.get_daily_active_brokerage(days_back=days_back)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"成功获取最近 {days_back} 天的活跃营业部数据",
                    "data": data,
                    "meta": {
                        "daysBack": days_back,
                        "count": len(data),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 获取指定日期范围的龙虎榜数据
@dragon_tiger_bp.route("/range", methods=["GET"])
def get_dragon_tiger_by_range():
    """
    获取指定日期范围的龙虎榜数据

    Query Parameters:
    - startDate: str (required) - 开始日期 YYYYMMDD
    - endDate: str (required) - 结束日期 YYYYMMDD
    """
    try:
        start_date = request.args.get("startDate", type=str)
        end_date = request.args.get("endDate", type=str)

        if not start_date or not end_date:
            return jsonify({"status": "error", "message": "startDate 和 endDate 是必填参数"}), 400

        service = DragonTigerService()
        data = service.get_dragon_tiger_by_date_range(start_date=start_date, end_date=end_date)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"成功获取 {start_date} 到 {end_date} 的龙虎榜数据",
                    "data": data,
                    "meta": {
                        "startDate": start_date,
                        "endDate": end_date,
                        "count": len(data),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
