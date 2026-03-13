import secrets
import os
from pathlib import Path

print("=" * 50)
print("Configuration Generator & Validator")
print("=" * 50)
print()

# 1. Generate SECRET_KEY
print("[1/4] Generating SECRET_KEY...")
secret_key = secrets.token_hex(32)
print(f"✅ SECRET_KEY: {secret_key}")
print()

# 2. Create VECTOR_DB_PATH
print("[2/4] Creating VECTOR_DB_PATH...")
vector_path = Path("./data/vector_store")
vector_path.mkdir(parents=True, exist_ok=True)
print(f"✅ Created: {vector_path.absolute()}")
print()

# 3. Test PostgreSQL
print("[3/4] Testing PostgreSQL...")
try:
    import psycopg2
    conn = psycopg2.connect(
        dbname="Multi_Agent",
        user="postgres",
        password="YourNewSecurePassword",
        host="localhost",
        port="5432"
    )
    print("✅ PostgreSQL: Connected!")
    conn.close()
except Exception as e:
    print(f"⚠️  PostgreSQL: {str(e)}")
    print("   Run: psql -U postgres -c 'CREATE DATABASE \"Multi_Agent\";'")
print()

# 4. Test Redis
print("[4/4] Testing Redis...")
try:
    import redis
    r = redis.from_url("redis://localhost:6379/0")
    r.ping()
    print("✅ Redis: Connected!")
except Exception as e:
    print(f"⚠️  Redis: {str(e)}")
    print("   Install: https://www.memurai.com/get-memurai")
    print("   Or set: USE_REDIS=false in .env")
print()

# Generate .env content
print("=" * 50)
print("Complete .env Configuration")
print("=" * 50)
env_content = f"""# LLM Configuration
USE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama2

# PostgreSQL Database
DB_USER=postgres
DB_PASSWORD=YourNewSecurePassword
DB_HOST=localhost
DB_PORT=5432
DB_NAME=Multi_Agent
DATABASE_URL=postgresql://postgres:YourNewSecurePassword@localhost:5432/Multi_Agent

# Redis
USE_REDIS=true
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY={secret_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Vector Database (FAISS)
VECTOR_DB_PATH=./data/vector_store
MAX_CONTEXT_LENGTH=5

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
TEMPERATURE=0.7
"""

print(env_content)

# Save to file
with open(".env.generated", "w") as f:
    f.write(env_content)

print("=" * 50)
print("✅ Configuration saved to: .env.generated")
print("Copy this to .env file to use it!")
print("=" * 50)
