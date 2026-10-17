from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.category import Category
from models.product import Product

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')

@categories_bp.route('/')
def list_categories():
    categories = Category.query.order_by(Category.category_name.asc()).all()
    return render_template('categories.html', categories=categories)

@categories_bp.route('/add', methods=['POST'])
def add_category():
    name = request.form.get('category_name', '').strip()
    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('categories.list_categories'))

    existing = Category.query.filter(Category.category_name.ilike(name)).first()
    if existing:
        flash(f'Category "{name}" already exists.', 'warning')
        return redirect(url_for('categories.list_categories'))

    try:
        category = Category(category_name=name)
        db.session.add(category)
        db.session.commit()
        flash(f'Category "{name}" added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding category: {str(e)}', 'danger')

    return redirect(url_for('categories.list_categories'))

@categories_bp.route('/edit/<int:id>', methods=['POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    name = request.form.get('category_name', '').strip()

    if not name:
        flash('Category name cannot be empty.', 'danger')
        return redirect(url_for('categories.list_categories'))

    try:
        category.category_name = name
        db.session.commit()
        flash('Category updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating category: {str(e)}', 'danger')

    return redirect(url_for('categories.list_categories'))

@categories_bp.route('/view/<int:id>')
def view_category_products(id):
    category = Category.query.get_or_404(id)
    products = Product.query.filter_by(category_id=id).order_by(Product.product_name.asc()).all()
    return render_template('categories.html', categories=Category.query.all(), viewing_category=category, products=products)
