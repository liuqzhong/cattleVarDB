"""
Test database connection
测试数据库连接
"""
import sys
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://cattle_user:cattle_pass@localhost:5432/cattle_snp_db"

print(f"Testing connection to: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("OK - Database connection successful!")
        print(f"Result: {result.fetchone()}")

except Exception as e:
    print(f"ERROR - Database connection failed: {e}")
    sys.exit(1)
