"""
Fix database column types to prevent OCR text truncation
Run this script to update existing PostgreSQL tables
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_database_columns():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Fix String columns that should have explicit lengths
        queries = [
            "ALTER TABLE users ALTER COLUMN username TYPE VARCHAR(255);",
            "ALTER TABLE users ALTER COLUMN email TYPE VARCHAR(255);",
            "ALTER TABLE users ALTER COLUMN hashed_password TYPE VARCHAR(255);",
            "ALTER TABLE chat_sessions ALTER COLUMN session_id TYPE VARCHAR(255);",
            "ALTER TABLE chat_history ALTER COLUMN role TYPE VARCHAR(50);",
            "ALTER TABLE documents ALTER COLUMN filename TYPE VARCHAR(500);",
            "ALTER TABLE documents ALTER COLUMN embedding_id TYPE VARCHAR(255);",
        ]
        
        for query in queries:
            try:
                conn.execute(text(query))
                print(f"✓ Executed: {query}")
            except Exception as e:
                print(f"✗ Error executing {query}: {e}")
        
        conn.commit()
        print("\n✓ Database columns updated successfully!")
        print("OCR text should now store properly in PostgreSQL.")

if __name__ == "__main__":
    fix_database_columns()
