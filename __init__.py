import os

from flask import Flask

from .admin_routes import admin_bp
from .auth_routes import auth_bp
from .company_routes import company_bp
from .extensions import db, login_manager
from .models import User
from .student_routes import student_bp


def create_app():
    app = Flask(__name__)
    base_dir = os.path.abspath(os.path.dirname(__file__))

    app.config["SECRET_KEY"] = "placement-portal-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(base_dir, 'placement_portal.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(base_dir, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    with app.app_context():
        db.create_all()
        seed_admin()

    return app


def seed_admin():
    admin = User.query.filter_by(email="admin@placement.local").first()
    if admin:
        return

    admin = User(email="admin@placement.local", role="admin")
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()