"""
============================================
Database Initialization Script
数据库初始化脚本
============================================
"""

import sys
import os
from sqlalchemy import create_engine, text, inspect
from logging import getLogger

logger = getLogger(__name__)

def get_database_url():
    """获取数据库连接URL"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://cattle_user:cattle_pass@localhost:5432/cattle_snp_db"
    )

def check_connection(engine):
    """检查数据库连接"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def check_tables_exist(engine):
    """检查表是否已存在"""
    required_tables = ['snps', 'targets', 'snp_effects']
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    missing_tables = [t for t in required_tables if t not in existing_tables]

    if missing_tables:
        logger.warning(f"⚠️  Missing tables: {', '.join(missing_tables)}")
        return False
    else:
        logger.info("✅ All required tables exist")
        return True

def init_database():
    """初始化数据库"""
    db_url = get_database_url()
    logger.info(f"Connecting to database: {db_url.split('@')[1] if '@' in db_url else db_url}")

    engine = create_engine(db_url)

    # 检查连接
    if not check_connection(engine):
        logger.error("Failed to connect to database. Please check:")
        logger.error("  1. PostgreSQL is running")
        logger.error("  2. Database credentials are correct")
        logger.error("  3. Database 'cattle_snp_db' exists")
        return False

    # 检查表是否存在
    if check_tables_exist(engine):
        logger.info("📊 Database already initialized")
        return True

    # 表不存在，需要运行 schema.sql
    logger.error("❌ Database tables do not exist!")
    logger.error("\nPlease run the schema.sql file to create tables:")
    logger.error("\nUsing psql:")
    logger.error("  psql -h localhost -U cattle_user -d cattle_snp_db -f database/schema.sql")
    logger.error("\nOr using Docker:")
    logger.error("  docker exec -i cattle_db psql -U cattle_user -d cattle_snp_db < database/schema.sql")

    return False

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    import logging

    success = init_database()
    sys.exit(0 if success else 1)
