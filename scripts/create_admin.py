from app import app, bcrypt
from models.user import User
from models.db import mongo

def create_admin():
    with app.app_context():
        # Check if admin already exists
        existing_admin = mongo.db.users.find_one({"email": "admin@meldpharm.com"})
        
        if existing_admin:
            print("Admin user already exists!")
            return

        # Create Admin User
        hashed_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
        
        admin_data = {
            "username": "Admin",
            "email": "admin@meldpharm.com",
            "password": hashed_password,
            "is_admin": True
        }
        
        mongo.db.users.insert_one(admin_data)
        print("Admin user created successfully!")
        print("Email: admin@meldpharm.com")
        print("Password: admin123")

if __name__ == "__main__":
    create_admin()