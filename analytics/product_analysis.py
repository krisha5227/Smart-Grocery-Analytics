import pandas as pd
import numpy as np
from models import db
from models.product import Product
from models.category import Category
from models.sale_item import SaleItem
from models.sale import Sale

def get_top_selling_products(limit=10):
    """
    Ranks top products based on units sold and total revenue using Pandas.
    """
    query = db.session.query(
        Product.id.label('product_id'),
        Product.product_name,
        Category.category_name,
        db.func.coalesce(db.func.sum(SaleItem.quantity), 0).label('total_quantity'),
        db.func.coalesce(db.func.sum(SaleItem.subtotal), 0.0).label('total_revenue'),
        db.func.coalesce(db.func.sum(SaleItem.profit), 0.0).label('total_profit')
    ).join(Category, Product.category_id == Category.id)\
     .outerjoin(SaleItem, Product.id == SaleItem.product_id)\
     .group_by(Product.id)

    records = query.all()
    if not records:
        return {'labels': [], 'revenue': [], 'quantity': [], 'profit': []}

    df = pd.DataFrame(records)
    df_sorted = df.sort_values(by='total_revenue', ascending=False).head(limit)

    return {
        'labels': df_sorted['product_name'].tolist(),
        'revenue': [round(x, 2) for x in df_sorted['total_revenue'].tolist()],
        'quantity': [int(x) for x in df_sorted['total_quantity'].tolist()],
        'profit': [round(x, 2) for x in df_sorted['total_profit'].tolist()]
    }

def get_product_performance_df():
    """
    Creates a full Product Performance summary DataFrame for Reports & Export.
    Columns: Product, Category, Unit, Selling Price, Cost Price, Stock, Units Sold, Revenue, Profit, Last Sale Date
    """
    query = db.session.query(
        Product.id.label('product_id'),
        Product.product_name,
        Category.category_name,
        Product.unit,
        Product.selling_price,
        Product.cost_price,
        Product.stock_quantity,
        db.func.coalesce(db.func.sum(SaleItem.quantity), 0).label('units_sold'),
        db.func.coalesce(db.func.sum(SaleItem.subtotal), 0.0).label('revenue'),
        db.func.coalesce(db.func.sum(SaleItem.profit), 0.0).label('profit'),
        db.func.max(Sale.sale_date).label('last_sale_date')
    ).join(Category, Product.category_id == Category.id)\
     .outerjoin(SaleItem, Product.id == SaleItem.product_id)\
     .outerjoin(Sale, SaleItem.sale_id == Sale.id)\
     .group_by(Product.id)

    records = query.all()
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df['revenue'] = df['revenue'].round(2)
    df['profit'] = df['profit'].round(2)
    df['last_sale_date'] = df['last_sale_date'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and hasattr(x, 'strftime') else 'No Sales')
    return df
