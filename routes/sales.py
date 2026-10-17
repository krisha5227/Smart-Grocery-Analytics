import os
import io
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from models import db
from models.product import Product
from models.category import Category
from models.sale import Sale
from models.sale_item import SaleItem
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

@sales_bp.route('/new')
def new_sale():
    products = Product.query.order_by(Product.product_name.asc()).all()
    categories = Category.query.order_by(Category.category_name.asc()).all()

    # Convert products to dict list for POS frontend JS
    products_json = [p.to_dict() for p in products]

    return render_template('new_sale.html', products=products, products_json=products_json, categories=categories)

@sales_bp.route('/create', methods=['POST'])
def create_sale():
    try:
        data = request.get_json()
        if not data or 'items' not in data or not data['items']:
            return jsonify({'success': False, 'message': 'No items selected in cart.'}), 400

        customer_name = data.get('customer_name', '').strip() or 'Walk-in Customer'
        cart_items = data['items']

        total_amount = 0.0
        total_profit = 0.0
        sale_items_to_create = []

        # Validate stock for all items first
        for item in cart_items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)

            if not product_id or quantity <= 0:
                return jsonify({'success': False, 'message': 'Invalid product or quantity specified.'}), 400

            product = Product.query.get(product_id)
            if not product:
                return jsonify({'success': False, 'message': f'Product ID {product_id} not found.'}), 404

            if product.stock_quantity < quantity:
                return jsonify({
                    'success': False,
                    'message': f'Insufficient stock for "{product.product_name}". Available: {product.stock_quantity} {product.unit}, Requested: {quantity}'
                }), 400

            sp = product.selling_price
            cp = product.cost_price
            subtotal = round(sp * quantity, 2)
            profit = round((sp - cp) * quantity, 2)

            total_amount += subtotal
            total_profit += profit

            sale_items_to_create.append({
                'product': product,
                'quantity': quantity,
                'selling_price': sp,
                'cost_price': cp,
                'subtotal': subtotal,
                'profit': profit
            })

        # Generate unique Invoice Number (e.g. INV-1001)
        last_sale = Sale.query.order_by(Sale.id.desc()).first()
        next_id = (last_sale.id + 1001) if last_sale else 1001
        invoice_num = f"INV-{next_id}"

        new_sale = Sale(
            invoice_number=invoice_num,
            sale_date=datetime.utcnow(),
            customer_name=customer_name,
            total_amount=round(total_amount, 2),
            total_profit=round(total_profit, 2)
        )
        db.session.add(new_sale)
        db.session.flush()

        # Update stock and record sale items
        for entry in sale_items_to_create:
            product = entry['product']
            product.stock_quantity -= entry['quantity']  # Stock Reduction

            s_item = SaleItem(
                sale_id=new_sale.id,
                product_id=product.id,
                quantity=entry['quantity'],
                selling_price=entry['selling_price'],
                cost_price=entry['cost_price'],
                subtotal=entry['subtotal'],
                profit=entry['profit']
            )
            db.session.add(s_item)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Sale completed successfully!',
            'invoice_id': new_sale.id,
            'invoice_number': new_sale.invoice_number
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Server Error: {str(e)}'}), 500

@sales_bp.route('/history')
def sales_history():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()

    query = Sale.query.order_by(Sale.sale_date.desc())
    if search:
        query = query.filter(
            (Sale.invoice_number.ilike(f'%{search}%')) |
            (Sale.customer_name.ilike(f'%{search}%'))
        )

    pagination = query.paginate(page=page, per_page=15, error_out=False)
    sales = pagination.items

    return render_template('sales_history.html', sales=sales, pagination=pagination, search=search)

@sales_bp.route('/invoice/<int:id>')
def view_invoice(id):
    sale = Sale.query.get_or_404(id)
    return render_template('invoice.html', sale=sale)

@sales_bp.route('/invoice/<int:id>/pdf')
def download_invoice_pdf(id):
    """
    Generates a simple, clean PDF invoice using ReportLab.
    """
    sale = Sale.query.get_or_404(id)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='TitleStyle', fontName='Helvetica-Bold', fontSize=18, leading=22, alignment=1, textColor=colors.HexColor('#1E293B'))
    header_style = ParagraphStyle(name='HeaderStyle', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#475569'))
    normal_style = ParagraphStyle(name='NormalStyle', fontName='Helvetica', fontSize=10, leading=14)

    elements = []

    # Store Header
    elements.append(Paragraph("SMART GROCERY STORE", title_style))
    elements.append(Paragraph("123 Supermarket Avenue, Cityville | Contact: +91 98765 43210", ParagraphStyle('Sub', alignment=1, fontName='Helvetica', fontSize=9, textColor=colors.gray)))
    elements.append(Spacer(1, 15))

    # Invoice Details
    elements.append(Paragraph(f"<b>Invoice No:</b> {sale.invoice_number}", normal_style))
    elements.append(Paragraph(f"<b>Date:</b> {sale.sale_date.strftime('%d-%m-%Y %H:%M')}", normal_style))
    elements.append(Paragraph(f"<b>Customer:</b> {sale.customer_name}", normal_style))
    elements.append(Spacer(1, 15))

    # Items Table
    table_data = [['Product', 'Unit', 'Qty', 'Price (₹)', 'Amount (₹)']]
    for item in sale.items:
        table_data.append([
            item.product.product_name if item.product else 'Product',
            item.product.unit if item.product else '',
            str(item.quantity),
            f"₹{item.selling_price:.2f}",
            f"₹{item.subtotal:.2f}"
        ])

    table_data.append(['', '', '', 'Total:', f"₹{sale.total_amount:.2f}"])

    t = Table(table_data, colWidths=[220, 60, 50, 90, 90])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#CBD5E1')),
        ('LINEBELOW', (0,-1), (-1,-1), 1.5, colors.HexColor('#0F172A')),
        ('FONTNAME', (3,-1), (-1,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))

    elements.append(t)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>Thank you for shopping with Smart Grocery Store!</b>", ParagraphStyle('Thanks', alignment=1, fontName='Helvetica-Oblique', fontSize=10, textColor=colors.HexColor('#475569'))))

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Invoice_{sale.invoice_number}.pdf",
        mimetype='application/pdf'
    )
