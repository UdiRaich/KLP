from flask import Flask


from .routes import bp as routes_bp

def create_app():
    app = Flask(__name__)

    # ייבוא ה־routes
    app.register_blueprint(routes_bp)

    return app