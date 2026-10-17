import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models import db
from models.product import Product
from models.category import Category
from models.sale_item import SaleItem
from models.sale import Sale
from config import Config

def get_inventory_status_counts():
    """
    Returns counts of Healthy Stock (In Stock), Low Stock, and Out of Stock products.
    """
    products = Product.query.all()
    if not products:
        return {'in_stock': 0, 'low_stock': 0, 'out_of_stock': 0}

    in_stock = sum(1 for p in products if p.stock_quantity > p.reorder_level)
    low_stock = sum(1 for p in products if 0 < p.stock_quantity <= p.reorder_level)
    out_of_stock = sum(1 for p in products if p.stock_quantity == 0)

    return {
        'in_stock': in_stock,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock
    }

def get_dead_stock_analysis(days_threshold=Config.DEFAULT_DEAD_STOCK_DAYS):
    """
    Dead Stock Detection using Pandas:
    Products with no sale in the last `days_threshold` days (or never sold).
    Calculates: Product, Category, Current Stock, Last Sale Date, Days Since Last Sale.
    """
    products = Product.query.join(Category).all()
    if not products:
        return []

    # Get last sale date per product via DB query / pandas
    sale_items = db.session.query(
        SaleItem.product_id,
        db.func.max(Sale.sale_date).label('last_sale')
    ).join(Sale, SaleItem.sale_id == Sale.id).group_by(SaleItem.product_id).all()

    last_sale_dict = {item.product_id: item.last_sale for item in sale_items}
    
    # Reference datetime: now or latest sale date in DB
    latest_db_sale = db.session.query(db.func.max(Sale.sale_date)).scalar()
    current_time = latest_db_sale if latest_db_sale else datetime.utcnow()

    dead_stock_list = []

    for p in products:
        last_sale = last_sale_dict.get(p.id)
        if last_sale:
            days_inactive = (current_time - last_sale).days
        else:
            days_inactive = 999  # Never sold

        if days_inactive >= days_threshold:
            dead_stock_list.append({
                'product_id': p.id,
                'product_name': p.product_name,
                'category_name': p.category.category_name,
                'unit': p.unit,
                'stock_quantity': p.stock_quantity,
                'cost_price': p.cost_price,
                'tied_up_capital': round(p.stock_quantity * p.cost_price, 2),
                'last_sale_date': last_sale.strftime('%Y-%m-%d') if last_sale else 'Never Sold',
                'days_since_last_sale': days_inactive if days_inactive != 999 else 'N/A'
            })

    # Sort by days inactive descending using Pandas
    if dead_stock_list:
        df_dead = pd.DataFrame(dead_stock_list)
        df_dead = df_dead.sort_values(by=['stock_quantity'], ascending=False)
        return df_dead.to_dict(orient='records')

    return []

def get_inventory_turnover_analysis():
    """
    Inventory Turnover Ratio = Cost of Goods Sold (COGS) / Average Inventory Value
    Average Inventory Value = ((Current Stock Value) + (Beginning Stock Value)) / 2
    Approximated using historical sales data & current stock.
    """
    query = db.session.query(
        Product.id.label('product_id'),
        Product.product_name,
        Category.category_name,
        Product.stock_quantity,
        Product.cost_price,
        db.func.coalesce(db.func.sum(SaleItem.quantity), 0).label('total_units_sold'),
        db.func.coalesce(db.func.sum(SaleItem.quantity * SaleItem.cost_price), 0.0).label('cogs')
    ).join(Category, Product.category_id == Category.id)\
     .outerjoin(SaleItem, Product.id == SaleItem.product_id)\
     .group_by(Product.id)

    records = query.all()
    if not records:
        return []

    data = []
    for r in records:
        current_stock_val = r.stock_quantity * r.cost_price
        cogs = float(r.cogs)
        
        # Average inventory estimate: (Current Stock + COGS_units) / 2 * cost_price
        avg_inv_val = (current_stock_val + (cogs / 2.0)) if cogs > 0 else current_stock_val
        if avg_inv_val <= 0:
            avg_inv_val = r.cost_price  # Avoid zero division

        turnover_ratio = round(cogs / avg_inv_val, 2)

        data.append({
            'product_id': r.product_id,
            'product_name': r.product_name,
            'category_name': r.category_name,
            'cogs': round(cogs, 2),
            'units_sold': int(r.total_units_sold),
            'current_stock': r.stock_quantity,
            'avg_inventory_val': round(avg_inv_val, 2),
            'turnover_ratio': turnover_ratio
        })

    df = pd.DataFrame(data)
    df = df.sort_values('turnover_ratio', ascending=False)
    return df.to_dict(orient='records')

def get_reorder_recommendations(max_stock_level=Config.DEFAULT_MAX_STOCK_LEVEL):
    """
    Identifies products where Current Stock <= Reorder Level.
    Calculates Suggested Reorder Quantity = Maximum Stock Level - Current Stock.
    """
    products = Product.query.join(Category).filter(Product.stock_quantity <= Product.reorder_level).all()

    recommendations = []
    for p in products:
        suggested_reorder = max(0, max_stock_level - p.stock_quantity)
        est_cost = round(suggested_reorder * p.cost_price, 2)

        recommendations.append({
            'product_id': p.id,
            'product_name': p.product_name,
            'category_name': p.category.category_name,
            'unit': p.unit,
            'current_stock': p.stock_quantity,
            'reorder_level': p.reorder_level,
            'stock_status': p.stock_status,
            'suggested_reorder_qty': suggested_reorder,
            'supplier_name': p.supplier_name or 'N/A',
            'estimated_reorder_cost': est_cost
        })

    if recommendations:
        df_reorder = pd.DataFrame(recommendations)
        df_reorder = df_reorder.sort_values(by=['current_stock', 'suggested_reorder_qty'], ascending=[True, False])
        return df_reorder.to_dict(orient='records')

    return []
