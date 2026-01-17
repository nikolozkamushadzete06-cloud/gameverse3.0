from app import app
from models import db, User
from werkzeug.security import generate_password_hash

with app.app_context():

    existing_admin = User.query.filter_by(username="admin").first()
    if existing_admin:
        print("Admin user already exists.")
    else:
        admin = User(
            username="admin",
            password=generate_password_hash("admin123"),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully.")