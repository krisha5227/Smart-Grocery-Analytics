from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db
from models.product import Product
from models.category import Category
from models.sale_item import SaleItem

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
def list_products():
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category_id', type=int)

    query = Product.query.join(Category)

    if search_query:
        query = query.filter(Product.product_name.ilike(f'%{search_query}%'))
    if category_filter:
        query = query.filter(Product.category_id == category_filter)

    products = query.order_by(Product.product_name.asc()).all()
    categories = Category.query.order_by(Category.category_name.asc()).all()

    return render_template(
        'products.html',
        products=products,
        categories=categories,
        search_query=search_query,
        selected_category=category_filter
    )

@products_bp.route('/add', methods=['POST'])
def add_product():
    try:
        name = request.form.get('product_name', '').strip()
        category_id = request.form.get('category_id', type=int)
        unit = request.form.get('unit', 'pc').strip()
        selling_price = request.form.get('selling_price', type=float)
        cost_price = request.form.get('cost_price', type=float)
        stock_quantity = request.form.get('stock_quantity', type=int, default=0)
        reorder_level = request.form.get('reorder_level', type=int, default=10)
        supplier_name = request.form.get('supplier_name', '').strip()

        # Basic Form Validation
        if not name or not category_id or selling_price is None or cost_price is None:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('products.list_products'))

        if selling_price < 0 or cost_price < 0 or stock_quantity < 0 or reorder_level < 0:
            flash('Prices and quantities cannot be negative values.', 'danger')
            return redirect(url_for('products.list_products'))

        product = Product(
            product_name=name,
            category_id=category_id,
            unit=unit,
            selling_price=selling_price,
            cost_price=cost_price,
            stock_quantity=stock_quantity,
            reorder_level=reorder_level,
            supplier_name=supplier_name
        )
        db.session.add(product)
        db.session.commit()
        flash(f'Product "{name}" added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding product: {str(e)}', 'danger')

    return redirect(url_for('products.list_products'))

@products_bp.route('/edit/<int:id>', methods=['POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    try:
        product.product_name = request.form.get('product_name', product.product_name).strip()
        product.category_id = request.form.get('category_id', type=int, default=product.category_id)
        product.unit = request.form.get('unit', product.unit).strip()
        product.selling_price = request.form.get('selling_price', type=float, default=product.selling_price)
        product.cost_price = request.form.get('cost_price', type=float, default=product.cost_price)
        product.stock_quantity = request.form.get('stock_quantity', type=int, default=product.stock_quantity)
        product.reorder_level = request.form.get('reorder_level', type=int, default=product.reorder_level)
        product.supplier_name = request.form.get('supplier_name', product.supplier_name).strip()

        if product.selling_price < 0 or product.cost_price < 0 or product.stock_quantity < 0:
            flash('Values cannot be negative.', 'danger')
            return redirect(url_for('products.list_products'))

        db.session.commit()
        flash(f'Product "{product.product_name}" updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating product: {str(e)}', 'danger')

    return redirect(url_for('products.list_products'))

@products_bp.route('/update-stock/<int:id>', methods=['POST'])
def update_stock(id):
    product = Product.query.get_or_404(id)
    try:
        added_stock = request.form.get('added_stock', type=int, default=0)
        if added_stock <= 0:
            flash('Stock update quantity must be greater than zero.', 'warning')
        else:
            product.stock_quantity += added_stock
            db.session.commit()
            flash(f'Added {added_stock} {product.unit} to stock for "{product.product_name}". New Stock: {product.stock_quantity}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating stock: {str(e)}', 'danger')

    return redirect(url_for('products.list_products'))

@products_bp.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    try:
        # Check if product has historical sales
        has_sales = SaleItem.query.filter_by(product_id=id).first() is not None
        if has_sales:
            flash(f'Cannot delete "{product.product_name}" because historical transactions exist for analytics integrity. Set stock to 0 or edit details instead.', 'warning')
        else:
            db.session.delete(product)
            db.session.commit()
            flash(f'Discontinued product "{product.product_name}" deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'danger')

    return redirect(url_for('products.list_products'))
