from datetime import datetime
from . import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(150), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    unit = db.Column(db.String(50), nullable=False, default='pc')
    selling_price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, nullable=False, default=10)
    supplier_name = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with SaleItem
    sale_items = db.relationship('SaleItem', backref='product', lazy=True)

    @property
    def stock_status(self):
        if self.stock_quantity == 0:
            return "Out of Stock"
        elif self.stock_quantity <= self.reorder_level:
            return "Low Stock"
        else:
            return "In Stock"

    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'category_id': self.category_id,
            'category_name': self.category.category_name if self.category else '',
            'unit': self.unit,
            'selling_price': self.selling_price,
            'cost_price': self.cost_price,
            'profit_margin': round(self.selling_price - self.cost_price, 2),
            'stock_quantity': self.stock_quantity,
            'reorder_level': self.reorder_level,
            'stock_status': self.stock_status,
            'supplier_name': self.supplier_name or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
