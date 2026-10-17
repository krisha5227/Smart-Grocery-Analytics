import os
import random
from datetime import datetime, timedelta
from app import app
from models import db
from models.category import Category
from models.product import Product
from models.sale import Sale
from models.sale_item import SaleItem

def seed_database():
    with app.app_context():
        print("Cleaning existing database tables...")
        db.drop_all()
        db.create_all()

        print("Seeding Categories...")
        categories_data = [
            'Fruits & Vegetables',
            'Grains & Staples',
            'Dairy Products',
            'Personal Care',
            'Household Items'
        ]
        
        category_map = {}
        for cat_name in categories_data:
            cat = Category(category_name=cat_name)
            db.session.add(cat)
            db.session.flush()
            category_map[cat_name] = cat.id

        print("Seeding Products (35+ products across 5 categories)...")
        products_data = [
            # Fruits & Vegetables
            {'name': 'Apple (Kashmiri)', 'cat': 'Fruits & Vegetables', 'unit': 'kg', 'sp': 180, 'cp': 130, 'stock': 120, 'reorder': 20, 'supplier': 'Fresh Farm Supplies'},
            {'name': 'Banana (Robusta)', 'cat': 'Fruits & Vegetables', 'unit': 'kg', 'sp': 60, 'cp': 40, 'stock': 150, 'reorder': 25, 'supplier': 'Green Orchard Co.'},
            {'name': 'Kiwi (Imported)', 'cat': 'Fruits & Vegetables', 'unit': 'pack', 'sp': 140, 'cp': 95, 'stock': 8, 'reorder': 10, 'supplier': 'Global Produce Imports'}, # Low Stock
            {'name': 'Orange (Nagpur)', 'cat': 'Fruits & Vegetables', 'unit': 'kg', 'sp': 90, 'cp': 60, 'stock': 80, 'reorder': 15, 'supplier': 'Fresh Farm Supplies'},
            {'name': 'Tomato (Hybrid)', 'cat': 'Fruits & Vegetables', 'unit': 'kg', 'sp': 40, 'cp': 25, 'stock': 0, 'reorder': 30, 'supplier': 'Local Farmers Co-op'}, # Out of Stock
            {'name': 'Potato (Jyoti)', 'cat': 'Fruits & Vegetables', 'unit': 'kg', 'sp': 30, 'cp': 18, 'stock': 200, 'reorder': 40, 'supplier': 'Local Farmers Co-op'},
            {'name': 'Onion (Nashik)', 'cat': 'Fruits & Vegetables', 'unit': 'kg', 'sp': 45, 'cp': 28, 'stock': 180, 'reorder': 35, 'supplier': 'Nashik Agri Trading'},
            {'name': 'Dragon Fruit', 'cat': 'Fruits & Vegetables', 'unit': 'pc', 'sp': 110, 'cp': 80, 'stock': 45, 'reorder': 10, 'supplier': 'Exotic Fruits Traders'}, # Dead stock candidate

            # Grains & Staples
            {'name': 'Basmati Rice (Premium)', 'cat': 'Grains & Staples', 'unit': 'kg', 'sp': 130, 'cp': 95, 'stock': 250, 'reorder': 30, 'supplier': 'Royal Grains Traders'},
            {'name': 'Whole Wheat Atta', 'cat': 'Grains & Staples', 'unit': 'kg', 'sp': 55, 'cp': 40, 'stock': 300, 'reorder': 50, 'supplier': 'Golden Harvest Mills'},
            {'name': 'Toor Dal (Unpolished)', 'cat': 'Grains & Staples', 'unit': 'kg', 'sp': 160, 'cp': 120, 'stock': 110, 'reorder': 20, 'supplier': 'Desi Pulses Ltd.'},
            {'name': 'Refined Sugar', 'cat': 'Grains & Staples', 'unit': 'kg', 'sp': 48, 'cp': 36, 'stock': 140, 'reorder': 25, 'supplier': 'Sweetland Refineries'},
            {'name': 'Maida (All-Purpose Flour)', 'cat': 'Grains & Staples', 'unit': 'kg', 'sp': 42, 'cp': 28, 'stock': 70, 'reorder': 15, 'supplier': 'Golden Harvest Mills'},
            {'name': 'Moong Dal', 'cat': 'Grains & Staples', 'unit': 'kg', 'sp': 140, 'cp': 105, 'stock': 5, 'reorder': 15, 'supplier': 'Desi Pulses Ltd.'}, # Low stock
            {'name': 'Organic Oats', 'cat': 'Grains & Staples', 'unit': 'pack', 'sp': 195, 'cp': 140, 'stock': 35, 'reorder': 10, 'supplier': 'Health & Grain Inc.'}, # Dead stock candidate

            # Dairy Products
            {'name': 'Full Cream Milk (1L)', 'cat': 'Dairy Products', 'unit': 'liter', 'sp': 66, 'cp': 52, 'stock': 90, 'reorder': 30, 'supplier': 'Amul Fresh Dairy'},
            {'name': 'Fresh Curd (500g)', 'cat': 'Dairy Products', 'unit': 'pack', 'sp': 38, 'cp': 28, 'stock': 65, 'reorder': 20, 'supplier': 'Mother Dairy Corp'},
            {'name': 'Cheddar Cheese Slice', 'cat': 'Dairy Products', 'unit': 'pack', 'sp': 150, 'cp': 110, 'stock': 40, 'reorder': 10, 'supplier': 'Amul Fresh Dairy'},
            {'name': 'Salted Butter (500g)', 'cat': 'Dairy Products', 'unit': 'pack', 'sp': 275, 'cp': 225, 'stock': 35, 'reorder': 12, 'supplier': 'Amul Fresh Dairy'},
            {'name': 'Fresh Paneer (200g)', 'cat': 'Dairy Products', 'unit': 'pack', 'sp': 95, 'cp': 72, 'stock': 0, 'reorder': 15, 'supplier': 'Local Dairy Farms'}, # Out of stock
            {'name': 'Greek Yogurt (Blueberry)', 'cat': 'Dairy Products', 'unit': 'pack', 'sp': 80, 'cp': 55, 'stock': 18, 'reorder': 5, 'supplier': 'Epigamia Dairy'},

            # Personal Care
            {'name': 'Anti-Dandruff Shampoo (350ml)', 'cat': 'Personal Care', 'unit': 'pc', 'sp': 240, 'cp': 175, 'stock': 60, 'reorder': 15, 'supplier': 'FMCG Distributors'},
            {'name': 'Neem Bathing Soap (4x125g)', 'cat': 'Personal Care', 'unit': 'pack', 'sp': 160, 'cp': 115, 'stock': 85, 'reorder': 20, 'supplier': 'Hindustan Care Products'},
            {'name': 'Herbal Toothpaste (200g)', 'cat': 'Personal Care', 'unit': 'pc', 'sp': 115, 'cp': 82, 'stock': 95, 'reorder': 15, 'supplier': 'Colgate-Palmolive Distribution'},
            {'name': 'Gentle Face Wash (150ml)', 'cat': 'Personal Care', 'unit': 'pc', 'sp': 190, 'cp': 135, 'stock': 7, 'reorder': 10, 'supplier': 'FMCG Distributors'}, # Low stock
            {'name': 'Charcoal Peel-off Mask', 'cat': 'Personal Care', 'unit': 'pc', 'sp': 299, 'cp': 180, 'stock': 25, 'reorder': 5, 'supplier': 'Beauty Care Alliance'}, # Dead stock candidate
            {'name': 'Moisturizing Body Lotion (400ml)', 'cat': 'Personal Care', 'unit': 'pc', 'sp': 350, 'cp': 245, 'stock': 50, 'reorder': 10, 'supplier': 'Hindustan Care Products'},

            # Household Items
            {'name': 'Washing Powder Detergent (2kg)', 'cat': 'Household Items', 'unit': 'pack', 'sp': 360, 'cp': 260, 'stock': 75, 'reorder': 15, 'supplier': 'Surf & Clean Logistics'},
            {'name': 'Dishwash Liquid Gel (750ml)', 'cat': 'Household Items', 'unit': 'pc', 'sp': 155, 'cp': 110, 'stock': 90, 'reorder': 20, 'supplier': 'Vim Hygiene Ltd.'},
            {'name': 'Disinfectant Floor Cleaner (1L)', 'cat': 'Household Items', 'unit': 'pc', 'sp': 185, 'cp': 130, 'stock': 65, 'reorder': 15, 'supplier': 'Lysol Supply Chain'},
            {'name': 'Facial Tissue Box (200 pulls)', 'cat': 'Household Items', 'unit': 'pack', 'sp': 99, 'cp': 65, 'stock': 120, 'reorder': 25, 'supplier': 'Paper Soft Corp'},
            {'name': 'Garbage Bags (30 count)', 'cat': 'Household Items', 'unit': 'pack', 'sp': 120, 'cp': 80, 'stock': 3, 'reorder': 10, 'supplier': 'CleanHome Essentials'}, # Low stock
            {'name': 'Microfiber Cleaning Cloth (4 pack)', 'cat': 'Household Items', 'unit': 'pack', 'sp': 220, 'cp': 140, 'stock': 30, 'reorder': 5, 'supplier': 'CleanHome Essentials'} # Dead stock candidate
        ]

        products_list = []
        for pd in products_data:
            product = Product(
                product_name=pd['name'],
                category_id=category_map[pd['cat']],
                unit=pd['unit'],
                selling_price=pd['sp'],
                cost_price=pd['cp'],
                stock_quantity=pd['stock'],
                reorder_level=pd['reorder'],
                supplier_name=pd['supplier'],
                created_at=datetime.utcnow() - timedelta(days=180)
            )
            db.session.add(product)
            products_list.append(product)

        db.session.flush()

        print("Seeding 120+ Historical Sales Transactions over the past 6 months...")
        
        # We will separate active products vs dead stock products
        dead_stock_names = ['Dragon Fruit', 'Organic Oats', 'Charcoal Peel-off Mask', 'Microfiber Cleaning Cloth (4 pack)']
        active_products = [p for p in products_list if p.product_name not in dead_stock_names]
        
        sample_customers = [
            'Ramesh Kumar', 'Priya Sharma', 'Anit Patel', 'Sunita Rao', 'Vikram Singh',
            'Neha Gupta', 'Amit Verma', 'Kavita Joshi', 'Rajesh Nair', 'Meena Sen',
            'Walk-in Customer', 'Walk-in Customer', 'Walk-in Customer', 'Walk-in Customer'
        ]

        # Generate transactions over the past 150 days
        base_date = datetime.utcnow()
        invoice_counter = 1001

        # Build transactions
        for i in range(130):
            # Pick a date within the last 150 days (with higher frequency in recent days)
            days_ago = int(random.triangular(0, 150, 15))
            sale_dt = base_date - timedelta(days=days_ago, hours=random.randint(8, 20), minutes=random.randint(0, 59))
            
            # Select 1 to 5 random products for this transaction
            num_items = random.randint(1, 5)
            selected_prods = random.sample(active_products, num_items)

            total_amount = 0.0
            total_profit = 0.0
            sale_items = []

            for prod in selected_prods:
                qty = random.randint(1, 4)
                sp = prod.selling_price
                cp = prod.cost_price
                subtotal = sp * qty
                profit = (sp - cp) * qty

                total_amount += subtotal
                total_profit += profit

                item = SaleItem(
                    product_id=prod.id,
                    quantity=qty,
                    selling_price=sp,
                    cost_price=cp,
                    subtotal=subtotal,
                    profit=profit
                )
                sale_items.append(item)

            sale = Sale(
                invoice_number=f"INV-{invoice_counter}",
                sale_date=sale_dt,
                customer_name=random.choice(sample_customers),
                total_amount=round(total_amount, 2),
                total_profit=round(total_profit, 2)
            )
            db.session.add(sale)
            db.session.flush()

            for item in sale_items:
                item.sale_id = sale.id
                db.session.add(item)

            invoice_counter += 1

        db.session.commit()
        print("Database Seeding Completed Successfully!")
        print(f"Categories: {Category.query.count()}")
        print(f"Products: {Product.query.count()}")
        print(f"Sales Transactions: {Sale.query.count()}")
        print(f"Sale Items: {SaleItem.query.count()}")

if __name__ == '__main__':
    seed_database()
