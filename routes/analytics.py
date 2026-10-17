from flask import Blueprint, render_template, request, jsonify
from models.category import Category
from models.product import Product
from analytics.sales_analysis import get_filtered_analytics

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
def index():
    categories = Category.query.order_by(Category.category_name.asc()).all()
    products = Product.query.order_by(Product.product_name.asc()).all()
    return render_template('analytics.html', categories=categories, products=products)

@analytics_bp.route('/api/data')
def analytics_data_api():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id')
    product_id = request.args.get('product_id')

    data = get_filtered_analytics(
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None,
        category_id=category_id if category_id else None,
        product_id=product_id if product_id else None
    )

    return jsonify(data)
