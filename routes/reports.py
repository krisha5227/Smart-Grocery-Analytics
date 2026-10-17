import io
import pandas as pd
from flask import Blueprint, render_template, request, Response, send_file, flash, redirect, url_for
from analytics.sales_analysis import get_sales_dataframe
from analytics.product_analysis import get_product_performance_df
from models.product import Product
from models.category import Category

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
def index():
    report_type = request.args.get('type', 'sales')

    sales_df = get_sales_dataframe()
    perf_df = get_product_performance_df()
    products = Product.query.join(Category).all()

    # Sales Report Preview Data
    sales_data = []
    if not sales_df.empty:
        sales_preview = sales_df.copy()
        sales_preview['sale_date'] = sales_preview['sale_date'].dt.strftime('%Y-%m-%d %H:%M')
        sales_data = sales_preview[['sale_date', 'invoice_number', 'product_name', 'category_name', 'quantity', 'subtotal', 'profit']].to_dict(orient='records')

    # Inventory Report Preview Data
    inventory_data = [{
        'product_name': p.product_name,
        'category_name': p.category.category_name if p.category else '',
        'stock_quantity': p.stock_quantity,
        'reorder_level': p.reorder_level,
        'status': p.stock_status,
        'supplier': p.supplier_name or 'N/A'
    } for p in products]

    # Performance Report Preview Data
    perf_data = perf_df.to_dict(orient='records') if not perf_df.empty else []

    return render_template(
        'reports.html',
        report_type=report_type,
        sales_data=sales_data[:50],  # Preview top 50
        inventory_data=inventory_data,
        perf_data=perf_data
    )

@reports_bp.route('/export/csv/<report_type>')
def export_csv(report_type):
    output = io.BytesIO()

    if report_type == 'sales':
        df = get_sales_dataframe()
        if df.empty:
            df = pd.DataFrame(columns=['Date', 'Invoice', 'Product', 'Category', 'Quantity', 'Revenue', 'Profit'])
        else:
            df['sale_date'] = df['sale_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            df = df[['sale_date', 'invoice_number', 'product_name', 'category_name', 'quantity', 'subtotal', 'profit']]
            df.columns = ['Date', 'Invoice', 'Product', 'Category', 'Quantity', 'Revenue', 'Profit']
        
        filename = "Sales_Report.csv"

    elif report_type == 'inventory':
        products = Product.query.join(Category).all()
        data = [{
            'Product': p.product_name,
            'Category': p.category.category_name,
            'Unit': p.unit,
            'Selling Price': p.selling_price,
            'Cost Price': p.cost_price,
            'Stock': p.stock_quantity,
            'Reorder Level': p.reorder_level,
            'Status': p.stock_status,
            'Supplier': p.supplier_name or 'N/A'
        } for p in products]
        df = pd.DataFrame(data)
        filename = "Inventory_Report.csv"

    elif report_type == 'performance':
        df = get_product_performance_df()
        if df.empty:
            df = pd.DataFrame()
        else:
            df = df[['product_name', 'category_name', 'unit', 'selling_price', 'cost_price', 'stock_quantity', 'units_sold', 'revenue', 'profit', 'last_sale_date']]
            df.columns = ['Product', 'Category', 'Unit', 'Selling Price', 'Cost Price', 'Stock', 'Units Sold', 'Revenue', 'Profit', 'Last Sale Date']
        filename = "Product_Performance_Report.csv"
    else:
        flash("Invalid report type specified.", "danger")
        return redirect(url_for('reports.index'))

    # Generate CSV using Pandas
    csv_str = df.to_csv(index=False)
    output.write(csv_str.encode('utf-8'))
    output.seek(0)

    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )
