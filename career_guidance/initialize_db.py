from app.database.session import init_db
from sqlalchemy import inspect
from app.database.session import engine

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    
    # Additional verification
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Database contains tables: {tables}")
    
    if not tables:
        print("\nERROR: No tables were created!")
        print("Possible solutions:")
        print("1. Check your model imports in session.py")
        print("2. Verify your model classes inherit from Base")
        print("3. Check for any silent errors during initialization")
    else:
        print("Database initialized successfully!")