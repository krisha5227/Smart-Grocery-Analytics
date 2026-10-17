from flask import Blueprint, render_template, jsonify
from analytics.sales_analysis import (
    get_overall_kpis,
    get_monthly_sales_trend,
    get_category_revenue_and_profit
)
from analytics.inventory_analysis import get_inventory_status_counts
from analytics.product_analysis import get_top_selling_products
from models.sale import Sale

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    kpis = get_overall_kpis()
    recent_transactions = Sale.query.order_by(Sale.sale_date.desc()).limit(10).all()
    return render_template('dashboard.html', kpis=kpis, recent_transactions=recent_transactions)

@dashboard_bp.route('/api/dashboard-charts')
def dashboard_charts_api():
    monthly_trend = get_monthly_sales_trend()
    category_data = get_category_revenue_and_profit()
    top_products = get_top_selling_products(limit=10)
    inventory_status = get_inventory_status_counts()

    return jsonify({
        'monthly_trend': monthly_trend,
        'category_data': category_data,
        'top_products': top_products,
        'inventory_status': inventory_status
    })
