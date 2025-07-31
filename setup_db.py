from app import app, db

def setup_database():
    with app.app_context():
        db.create_all()
        print("Database and tables created (if they didn't exist).")

if __name__ == "__main__":
    setup_database()
