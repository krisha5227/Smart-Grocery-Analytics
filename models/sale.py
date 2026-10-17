from datetime import datetime
from . import db

class Sale(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    sale_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    customer_name = db.Column(db.String(100), nullable=True, default='Walk-in Customer')
    total_amount = db.Column(db.Float, nullable=False)
    total_profit = db.Column(db.Float, nullable=False)

    # Relationship to sale items
    items = db.relationship('SaleItem', backref='sale', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'sale_date': self.sale_date.strftime('%Y-%m-%d %H:%M:%S'),
            'customer_name': self.customer_name or 'Walk-in Customer',
            'total_amount': round(self.total_amount, 2),
            'total_profit': round(self.total_profit, 2),
            'item_count': len(self.items)
        }
