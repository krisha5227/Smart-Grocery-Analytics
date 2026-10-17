# Smart Grocery Store Sales & Inventory Analytics System

A full-stack, real-world Data Analytics web application built using Python, Flask, Pandas, NumPy, SQLite, SQLAlchemy, Bootstrap 5, and Chart.js.

The system helps supermarket and grocery store owners monitor sales transactions, track real-time inventory health, detect dead stock, calculate inventory turnover, manage reorder levels, and gain deep business insights through an interactive dashboard.

---

## 1. Problem Statement
Traditional retail grocery stores often struggle with:
- Stockouts of popular daily essentials, resulting in lost revenue.
- Capital tied up in overstocked or dead stock items that do not sell.
- Manual billing without profit calculation or historical analytics.
- Lack of data-driven decisions on product performance and reordering.

This project solves these issues by combining a Point of Sale (POS) transaction recorder with a Python Pandas analytics engine.

---

## 2. Objectives
- **Record Sales**: Enable instant multi-item checkout with automatic invoice generation and stock deduction.
- **Track Inventory**: Monitor stock levels, flag low-stock items, and recommend exact reorder quantities.
- **Identify Dead Stock**: Automatically flag products with no sales over a configurable period (e.g., 30+ days).
- **Calculate Business Metrics**: Compute Inventory Turnover Ratios (`COGS / Avg Inventory`), total revenue, net profit, and average basket value.
- **Data Visualization**: Provide dynamic charts powered by Chart.js for monthly trends, category revenue shares, and top-selling SKUs.
- **Export Data**: Enable CSV exports for Sales, Inventory, and Performance reports.

---

## 3. Technology Stack

### Backend
- **Python 3.x**: Primary language for server logic and analytics engine.
- **Flask**: Lightweight Web Framework for routing, REST endpoints, and template rendering.
- **Pandas**: Advanced data manipulation, groupbys, aggregation, time series analysis, and CSV exports.
- **NumPy**: Vectorized numerical calculations for fast metric computing.
- **SQLite & SQLAlchemy**: Relational database with ORM models.
- **ReportLab**: PDF invoice generation.

### Frontend & Visualization
- **HTML5 & Vanilla CSS3**: Custom responsive layout with sleek dark/light sidebar design system.
- **JavaScript (ES6+)**: Async POS cart handling and dynamic API fetch calls.
- **Bootstrap 5 & Icons**: Modern UI components, responsive grids, and clean tables.
- **Chart.js v4**: Interactive data visualization (Line, Bar, Doughnut).

---

## 4. Database Schema

The SQLite database (`grocery_analytics.db`) consists of 4 main relational tables:

```
+----------------+       +-------------------+       +---------------+
|   categories   |       |     products      |       |  sale_items   |
+----------------+       +-------------------+       +---------------+
| id (PK)        |<----->| id (PK)           |<----->| id (PK)       |
| category_name  |       | product_name      |       | sale_id (FK)  |
+----------------+       | category_id (FK)  |       | product_id(FK)|
                         | unit              |       | quantity      |
                         | selling_price     |       | selling_price |
                         | cost_price        |       | cost_price    |
                         | stock_quantity    |       | subtotal      |
                         | reorder_level     |       | profit        |
                         | supplier_name     |       +---------------+
                         | created_at        |               ^
                         +-------------------+               |
                                                             v
                                                     +---------------+
                                                     |     sales     |
                                                     +---------------+
                                                     | id (PK)       |
                                                     | invoice_number|
                                                     | sale_date     |
                                                     | customer_name |
                                                     | total_amount  |
                                                     | total_profit  |
                                                     +---------------+
```

---

## 5. Folder Structure

```
smart_grocery_analytics/
│
├── app.py                      # Application entry point & blueprint registration
├── config.py                   # Configuration settings & defaults
├── requirements.txt            # Python dependencies
├── seed_database.py            # Database seeder (35+ products, 120+ sales)
├── database.db                 # SQLite database (auto-generated)
│
├── models/                     # SQLAlchemy Database Models
│   ├── __init__.py
│   ├── category.py
│   ├── product.py
│   ├── sale.py
│   └── sale_item.py
│
├── analytics/                  # Python Pandas & NumPy Analytics Engine
│   ├── __init__.py
│   ├── sales_analysis.py       # Revenue, profit, monthly & daily trends, category contributions
│   ├── inventory_analysis.py   # Stock status, dead stock, turnover ratio, reorder calculation
│   └── product_analysis.py     # Top products ranking & product performance DataFrames
│
├── routes/                     # Flask Route Blueprints
│   ├── __init__.py
│   ├── dashboard.py
│   ├── products.py
│   ├── categories.py
│   ├── sales.py
│   ├── inventory.py
│   ├── analytics.py
│   └── reports.py
│
├── static/                     # Static CSS & JS Assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── dashboard.js
│       ├── sales.js
│       └── analytics.js
│
└── templates/                  # Jinja2 HTML Templates
    ├── base.html
    ├── dashboard.html
    ├── products.html
    ├── categories.html
    ├── new_sale.html
    ├── sales_history.html
    ├── invoice.html
    ├── inventory.html
    ├── analytics.html
    └── reports.html
```

---

## 6. Installation & Setup Instructions

### Prerequisites
- Python 3.8+ installed on Windows.

### Step 1: Clone / Navigate to directory
```cmd
cd C:\Users\DELL\OneDrive\Desktop\smart_grocery_analytics
```

### Step 2: Create a Virtual Environment
```cmd
python -m venv venv
```

### Step 3: Activate Virtual Environment
```cmd
venv\Scripts\activate
```

### Step 4: Install Dependencies
```cmd
pip install -r requirements.txt
```

### Step 5: Seed Sample Database
```cmd
python seed_database.py
```

### Step 6: Run Application
```cmd
python app.py
```

### Step 7: Open Browser
Open `http://127.0.0.1:5000` in your web browser.

---

## 7. How Python & Pandas Are Used for Data Analytics

Instead of running slow SQL aggregations repeatedly in Flask view functions, all business analytics are handled in a dedicated `analytics/` package using Pandas DataFrames:

1. **DataFrame Loading (`get_sales_dataframe`)**: Joined SQL tables are converted into a Pandas DataFrame using SQLAlchemy queries.
2. **Aggregations & GroupBy**: `df.groupby('year_month')` and `df.groupby('category_name')` aggregate subtotal and profit data for time-series and categorical charts.
3. **Data Slicing & Filtering**: Pandas vector logic filters transactions dynamically by date range, category, or product without rewriting complex SQL queries.
4. **Dead Stock Analysis**: Time differences between `datetime.utcnow()` and `last_sale_date` calculate days inactive per product.
5. **Inventory Turnover Ratio**: `COGS / Average Inventory` is computed per SKU to measure inventory velocity.
6. **CSV Exporting**: `df.to_csv()` exports clean datasets instantly.

---

## 8. Interview Talking Points

If asked to present this project in a Data Science or Analytics interview:

- **Business Understanding**: "I built a supermarket analytics platform to bridge operational POS transactions with strategic inventory control."
- **Data Architecture**: "I designed an ORM schema with strict relationships between products, categories, sales, and line items, ensuring data integrity during purchases."
- **Analytics Engine**: "I implemented a modular Python package leveraging Pandas and NumPy. We load joined relational data into DataFrames to execute groupbys, time-series resampling, turnover ratio calculations, and dead stock detection."
- **Stock Management Logic**: "Purchases do not delete product records; stock decreases while sales history is preserved for trend forecasting."
- **Data Visualization**: "I built REST JSON endpoints that pipe Pandas aggregations into dynamic Chart.js visualizations."
