from flask import Blueprint, render_template, request
from models.product import Product
from models.category import Category
from analytics.inventory_analysis import (
    get_inventory_status_counts,
    get_dead_stock_analysis,
    get_inventory_turnover_analysis,
    get_reorder_recommendations
)
from config import Config

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/')
def index():
    dead_stock_days = request.args.get('dead_days', type=int, default=Config.DEFAULT_DEAD_STOCK_DAYS)
    max_stock = request.args.get('max_stock', type=int, default=Config.DEFAULT_MAX_STOCK_LEVEL)

    # General Product Stock List
    products = Product.query.join(Category).order_by(Product.product_name.asc()).all()
    status_counts = get_inventory_status_counts()

    # Advanced Inventory Analytics via Pandas
    dead_stock = get_dead_stock_analysis(days_threshold=dead_stock_days)
    turnover = get_inventory_turnover_analysis()
    reorder_list = get_reorder_recommendations(max_stock_level=max_stock)

    return render_template(
        'inventory.html',
        products=products,
        status_counts=status_counts,
        dead_stock=dead_stock,
        turnover=turnover,
        reorder_list=reorder_list,
        dead_stock_days=dead_stock_days,
        max_stock=max_stock
    )
