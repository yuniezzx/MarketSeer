from flask import Blueprint

stock_bp = Blueprint('stock', __name__, url_prefix='/stocks')


@stock_bp.route('/', methods=['GET'])
def list_stocks():
    return "List of stocks"
