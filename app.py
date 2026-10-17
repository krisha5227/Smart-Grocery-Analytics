import os
from flask import Flask, render_template
from config import Config
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    from routes.dashboard import dashboard_bp
    from routes.products import products_bp
    from routes.categories import categories_bp
    from routes.sales import sales_bp
    from routes.inventory import inventory_bp
    from routes.analytics import analytics_bp
    from routes.reports import reports_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(reports_bp)

    # Custom Jinja Template Filters
    @app.template_filter('currency')
    def currency_filter(value):
        try:
            return f"₹{float(value):,.2f}"
        except (ValueError, TypeError):
            return "₹0.00"

    # Context processors
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_message="Page Not Found (404)"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_message="Internal Server Error (500). Please check logs."), 500

    # Ensure tables exist
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    print("=========================================================")
    print(" Smart Grocery Store Sales & Inventory Analytics System")
    print(" Running locally on: http://127.0.0.1:5000")
    print("=========================================================")
    app.run(host='127.0.0.1', port=5000, debug=True)
