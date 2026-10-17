from . import db

class SaleItem(db.Model):
    __tablename__ = 'sale_items'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    profit = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'product_id': self.product_id,
            'product_name': self.product.product_name if self.product else 'Unknown',
            'unit': self.product.unit if self.product else '',
            'quantity': self.quantity,
            'selling_price': round(self.selling_price, 2),
            'cost_price': round(self.cost_price, 2),
            'subtotal': round(self.subtotal, 2),
            'profit': round(self.profit, 2)
        }
