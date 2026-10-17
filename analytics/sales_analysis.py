import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models import db
from models.sale import Sale
from models.sale_item import SaleItem
from models.product import Product
from models.category import Category

def get_sales_dataframe():
    """
    Load all sales and sale items joined with products and categories into a Pandas DataFrame.
    """
    query = db.session.query(
        Sale.id.label('sale_id'),
        Sale.invoice_number,
        Sale.sale_date,
        Sale.customer_name,
        SaleItem.id.label('sale_item_id'),
        SaleItem.product_id,
        Product.product_name,
        Product.unit,
        Category.id.label('category_id'),
        Category.category_name,
        SaleItem.quantity,
        SaleItem.selling_price,
        SaleItem.cost_price,
        SaleItem.subtotal,
        SaleItem.profit
    ).join(SaleItem, Sale.id == SaleItem.sale_id)\
     .join(Product, SaleItem.product_id == Product.id)\
     .join(Category, Product.category_id == Category.id)

    records = query.all()
    if not records:
        return pd.DataFrame(columns=[
            'sale_id', 'invoice_number', 'sale_date', 'customer_name',
            'sale_item_id', 'product_id', 'product_name', 'unit',
            'category_id', 'category_name', 'quantity', 'selling_price',
            'cost_price', 'subtotal', 'profit'
        ])

    df = pd.DataFrame(records)
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    return df

def get_overall_kpis():
    """
    Compute KPI summary using Pandas & NumPy.
    """
    df = get_sales_dataframe()
    total_products = Product.query.count()
    
    if df.empty:
        return {
            'total_revenue': 0.0,
            'total_profit': 0.0,
            'total_products': total_products,
            'total_units_sold': 0,
            'low_stock_products': Product.query.filter(Product.stock_quantity <= Product.reorder_level).count(),
            'total_transactions': 0,
            'avg_transaction_value': 0.0
        }

    total_revenue = float(np.sum(df['subtotal']))
    total_profit = float(np.sum(df['profit']))
    total_units_sold = int(np.sum(df['quantity']))
    total_transactions = int(df['sale_id'].nunique())
    avg_tx_value = float(total_revenue / total_transactions) if total_transactions > 0 else 0.0
    low_stock_count = Product.query.filter(Product.stock_quantity <= Product.reorder_level).count()

    return {
        'total_revenue': round(total_revenue, 2),
        'total_profit': round(total_profit, 2),
        'total_products': total_products,
        'total_units_sold': total_units_sold,
        'low_stock_products': low_stock_count,
        'total_transactions': total_transactions,
        'avg_transaction_value': round(avg_tx_value, 2)
    }

def get_monthly_sales_trend(df=None):
    """
    Group sales by Month (YYYY-MM) and calculate total revenue and profit using Pandas.
    """
    if df is None:
        df = get_sales_dataframe()

    if df.empty:
        return {'labels': [], 'revenue': [], 'profit': []}

    df_copy = df.copy()
    df_copy['year_month'] = df_copy['sale_date'].dt.to_period('M').astype(str)

    monthly_grp = df_copy.groupby('year_month').agg({
        'subtotal': 'sum',
        'profit': 'sum'
    }).reset_index().sort_values('year_month')

    return {
        'labels': monthly_grp['year_month'].tolist(),
        'revenue': [round(x, 2) for x in monthly_grp['subtotal'].tolist()],
        'profit': [round(x, 2) for x in monthly_grp['profit'].tolist()]
    }

def get_daily_sales_trend(df=None, days=30):
    """
    Group sales by Date (YYYY-MM-DD) for recent days.
    """
    if df is None:
        df = get_sales_dataframe()

    if df.empty:
        return {'labels': [], 'revenue': [], 'profit': [], 'units_sold': []}

    df_copy = df.copy()
    df_copy['date_str'] = df_copy['sale_date'].dt.strftime('%Y-%m-%d')

    daily_grp = df_copy.groupby('date_str').agg({
        'subtotal': 'sum',
        'profit': 'sum',
        'quantity': 'sum'
    }).reset_index().sort_values('date_str')

    if days and len(daily_grp) > days:
        daily_grp = daily_grp.tail(days)

    return {
        'labels': daily_grp['date_str'].tolist(),
        'revenue': [round(x, 2) for x in daily_grp['subtotal'].tolist()],
        'profit': [round(x, 2) for x in daily_grp['profit'].tolist()],
        'units_sold': [int(x) for x in daily_grp['quantity'].tolist()]
    }

def get_category_revenue_and_profit(df=None):
    """
    Group sales by Category to compute revenue, profit, and percentage contribution.
    """
    if df is None:
        df = get_sales_dataframe()

    if df.empty:
        return {'labels': [], 'revenue': [], 'profit': [], 'units_sold': [], 'contributions': []}

    cat_grp = df.groupby('category_name').agg({
        'subtotal': 'sum',
        'profit': 'sum',
        'quantity': 'sum'
    }).reset_index().sort_values('subtotal', ascending=False)

    total_revenue = np.sum(cat_grp['subtotal'])
    cat_grp['contribution'] = (cat_grp['subtotal'] / total_revenue * 100) if total_revenue > 0 else 0

    return {
        'labels': cat_grp['category_name'].tolist(),
        'revenue': [round(x, 2) for x in cat_grp['subtotal'].tolist()],
        'profit': [round(x, 2) for x in cat_grp['profit'].tolist()],
        'units_sold': [int(x) for x in cat_grp['quantity'].tolist()],
        'contributions': [round(x, 2) for x in cat_grp['contribution'].tolist()]
    }

def get_filtered_analytics(start_date=None, end_date=None, category_id=None, product_id=None):
    """
    Apply dynamic filters (Date range, Category, Product) using Pandas data slicing.
    Returns filtered summary metrics & data payload for Chart.js.
    """
    df = get_sales_dataframe()

    if df.empty:
        return {
            'metrics': {'revenue': 0, 'profit': 0, 'units_sold': 0, 'avg_tx_value': 0, 'tx_count': 0},
            'monthly_trend': {'labels': [], 'revenue': [], 'profit': []},
            'daily_trend': {'labels': [], 'revenue': [], 'profit': []},
            'category_performance': {'labels': [], 'revenue': [], 'profit': [], 'units_sold': []},
            'top_products': {'labels': [], 'revenue': [], 'units_sold': []}
        }

    # Data Filtering using Pandas vector conditions
    if start_date:
        df = df[df['sale_date'] >= pd.to_datetime(start_date)]
    if end_date:
        # Include end of the day
        df = df[df['sale_date'] <= pd.to_datetime(end_date) + pd.Timedelta(days=1)]
    if category_id:
        df = df[df['category_id'] == int(category_id)]
    if product_id:
        df = df[df['product_id'] == int(product_id)]

    if df.empty:
        return {
            'metrics': {'revenue': 0, 'profit': 0, 'units_sold': 0, 'avg_tx_value': 0, 'tx_count': 0},
            'monthly_trend': {'labels': [], 'revenue': [], 'profit': []},
            'daily_trend': {'labels': [], 'revenue': [], 'profit': []},
            'category_performance': {'labels': [], 'revenue': [], 'profit': [], 'units_sold': []},
            'top_products': {'labels': [], 'revenue': [], 'units_sold': []}
        }

    rev = float(np.sum(df['subtotal']))
    prof = float(np.sum(df['profit']))
    units = int(np.sum(df['quantity']))
    tx_count = int(df['sale_id'].nunique())
    avg_tx = float(rev / tx_count) if tx_count > 0 else 0.0

    monthly_trend = get_monthly_sales_trend(df)
    daily_trend = get_daily_sales_trend(df, days=60)
    cat_perf = get_category_revenue_and_profit(df)

    # Top products in filtered view
    prod_grp = df.groupby('product_name').agg({
        'subtotal': 'sum',
        'quantity': 'sum'
    }).reset_index().sort_values('subtotal', ascending=False).head(10)

    top_products = {
        'labels': prod_grp['product_name'].tolist(),
        'revenue': [round(x, 2) for x in prod_grp['subtotal'].tolist()],
        'units_sold': [int(x) for x in prod_grp['quantity'].tolist()]
    }

    return {
        'metrics': {
            'revenue': round(rev, 2),
            'profit': round(prof, 2),
            'units_sold': units,
            'avg_tx_value': round(avg_tx, 2),
            'tx_count': tx_count
        },
        'monthly_trend': monthly_trend,
        'daily_trend': daily_trend,
        'category_performance': cat_perf,
        'top_products': top_products
    }
