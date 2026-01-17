"""
============================================
Cattle SNP Effect Value Database - Data Import Script
牛变异效应值数据库 - 数据导入脚本
============================================

This script imports TSV data into the PostgreSQL database.
支持从TSV文件导入SNP和效应值数据

Usage:
    python import_data.py --file ./SNP-disease/variant_sad_all_targets.tsv
    python import_data.py --file ./SNP-disease/variant_sad_all_targets.tsv --batch-size 1000
"""

import argparse
import csv
import os
import sys
import logging
from datetime import datetime
from typing import List, Tuple
from tqdm import tqdm

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import psycopg2.extras

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# Configuration
# ============================================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cattle_user:cattle_pass@localhost:5432/cattle_snp_db"
)

TSV_FILE_PATH = "./SNP-disease/variant_sad_all_targets.tsv"
BATCH_SIZE = 1000  # Number of records to insert per batch

# ============================================
# Logging Setup
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_data.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ============================================
# Database Connection
# ============================================
def get_db_connection():
    """获取数据库连接"""
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session, engine
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise


# ============================================
# TSV File Parser
# ============================================
def parse_tsv_header(file_path: str) -> Tuple[List[str], List[str]]:
    """
    解析TSV文件头，识别SNP基础列和效应值列

    Returns:
        (snp_columns, effect_columns): SNP基础列名和效应值列名列表
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)

    # First 6 columns are SNP basic info
    snp_columns = header[:6]
    # Remaining columns are effect values (targets)
    effect_columns = header[6:]

    logger.info(f"Found {len(snp_columns)} SNP columns: {snp_columns}")
    logger.info(f"Found {len(effect_columns)} effect value columns (targets)")

    return snp_columns, effect_columns


def read_tsv_data(file_path: str) -> List[dict]:
    """
    读取TSV文件数据

    Returns:
        List of dictionaries containing row data
    """
    logger.info(f"Reading TSV file: {file_path}")

    data_rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            data_rows.append(row)

    logger.info(f"Read {len(data_rows)} data rows from TSV file")
    return data_rows


# ============================================
# Data Import Functions
# ============================================
def import_targets(session, effect_columns: List[str]) -> dict:
    """
    导入靶点（组织/细胞类型）数据

    Args:
        session: SQLAlchemy session
        effect_columns: List of target names from TSV header

    Returns:
        Dictionary mapping target_name -> target_id
    """
    logger.info("Importing targets...")

    target_name_to_id = {}
    imported_count = 0

    for idx, target_name in enumerate(effect_columns, start=1):
        # Remove .norRPKM suffix if present
        clean_name = target_name.replace('.norRPKM', '')

        # Check if target already exists
        from backend.main import TargetModel
        existing = session.query(TargetModel).filter(
            TargetModel.name == clean_name
        ).first()

        if existing:
            target_name_to_id[target_name] = existing.id
        else:
            # Create new target
            target = TargetModel(
                name=clean_name,
                category="tissue_cell",
                description=f"Imported from TSV column {idx}"
            )
            session.add(target)
            session.flush()
            target_name_to_id[target_name] = target.id
            imported_count += 1

    session.commit()
    logger.info(f"Imported {imported_count} new targets, total targets: {len(target_name_to_id)}")

    return target_name_to_id


def import_snps_and_effects(
    session,
    data_rows: List[dict],
    target_name_to_id: dict,
    batch_size: int = BATCH_SIZE
) -> dict:
    """
    导入SNP和效应值数据

    Args:
        session: SQLAlchemy session
        data_rows: List of data rows from TSV
        target_name_to_id: Mapping of target names to IDs
        batch_size: Batch size for bulk insert

    Returns:
        Dictionary with import statistics
    """
    from backend.main import SNPModel, SNPEffectModel

    logger.info(f"Importing SNPs and effects (batch_size={batch_size})...")

    stats = {
        "snps_imported": 0,
        "snps_skipped": 0,
        "effects_imported": 0,
        "effects_skipped": 0,
        "errors": []
    }

    # Use raw connection for faster bulk inserts
    connection = session.connection().connection
    cursor = connection.cursor()

    for row_idx, row in enumerate(tqdm(data_rows, desc="Importing rows"), start=1):
        try:
            # Extract SNP basic info
            chrom = row.get('chrom', '')
            pos = int(row.get('pos', 0)) if row.get('pos', '').isdigit() else 0
            rs_id = row.get('id', '')
            ref_allele = row.get('ref', '')
            alt_allele = row.get('alt', '')
            max_abs_sad = float(row.get('max_abs_sad', 0))

            # Validate required fields
            if not all([chrom, pos, ref_allele, alt_allele]):
                logger.warning(f"Row {row_idx}: Missing required SNP fields, skipping")
                stats["snps_skipped"] += 1
                continue

            # Insert SNP (or get existing ID)
            cursor.execute("""
                INSERT INTO snps (chrom, pos, rs_id, ref_allele, alt_allele, max_abs_sad)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (chrom, pos, ref_allele, alt_allele)
                DO UPDATE SET rs_id = EXCLUDED.rs_id, max_abs_sad = EXCLUDED.max_abs_sad
                RETURNING id
            """, (chrom, pos, rs_id if rs_id else None, ref_allele, alt_allele, max_abs_sad))

            snp_id = cursor.fetchone()[0]
            stats["snps_imported"] += 1

            # Insert effect values
            for target_name, target_id in target_name_to_id.items():
                effect_value_str = row.get(target_name, '0')
                try:
                    effect_value = float(effect_value_str) if effect_value_str else 0.0

                    cursor.execute("""
                        INSERT INTO snp_effects (snp_id, target_id, effect_value)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (snp_id, target_id)
                        DO UPDATE SET effect_value = EXCLUDED.effect_value
                    """, (snp_id, target_id, effect_value))

                    stats["effects_imported"] += 1

                except (ValueError, TypeError) as e:
                    logger.debug(f"Invalid effect value for SNP {snp_id}, target {target_name}: {e}")
                    stats["effects_skipped"] += 1

            # Commit periodically
            if row_idx % batch_size == 0:
                connection.commit()
                logger.info(f"Processed {row_idx} rows...")

        except Exception as e:
            logger.error(f"Error processing row {row_idx}: {str(e)}")
            stats["errors"].append(f"Row {row_idx}: {str(e)}")
            connection.rollback()

    # Final commit
    connection.commit()
    cursor.close()

    return stats


def create_import_log(session, stats: dict, file_path: str):
    """创建导入日志记录"""
    try:
        session.execute(text("""
            INSERT INTO data_import_log (import_type, source_file, records_processed, status, error_message, completed_at)
            VALUES (:import_type, :source_file, :records_processed, :status, :error_message, :completed_at)
        """), {
            'import_type': 'TSV_IMPORT',
            'source_file': file_path,
            'records_processed': stats.get('snps_imported', 0),
            'status': 'completed' if not stats.get('errors') else 'completed_with_errors',
            'error_message': '; '.join(stats.get('errors', []))[:1000] if stats.get('errors') else None,
            'completed_at': datetime.utcnow()
        })
        session.commit()
    except Exception as e:
        logger.warning(f"Failed to create import log: {str(e)}")


def refresh_materialized_views(session):
    """刷新物化视图"""
    try:
        logger.info("Refreshing materialized views...")
        session.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY SNP_EFFECT_SUMMARY"))
        session.commit()
        logger.info("Materialized views refreshed successfully")
    except Exception as e:
        logger.warning(f"Failed to refresh materialized views: {str(e)}")


# ============================================
# Main Import Function
# ============================================
def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Import SNP effect value data from TSV file'
    )
    parser.add_argument(
        '--file',
        type=str,
        default=TSV_FILE_PATH,
        help=f'Path to TSV file (default: {TSV_FILE_PATH})'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=BATCH_SIZE,
        help=f'Batch size for inserts (default: {BATCH_SIZE})'
    )
    parser.add_argument(
        '--skip-targets',
        action='store_true',
        help='Skip target import if targets already exist'
    )
    parser.add_argument(
        '--refresh-views',
        action='store_true',
        help='Refresh materialized views after import'
    )

    args = parser.parse_args()

    # Validate file path
    if not os.path.exists(args.file):
        logger.error(f"TSV file not found: {args.file}")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("Starting TSV data import...")
    logger.info(f"File: {args.file}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info("=" * 60)

    start_time = datetime.now()

    try:
        # Get database connection
        session, engine = get_db_connection()

        # Parse TSV header
        snp_columns, effect_columns = parse_tsv_header(args.file)

        # Import targets
        if not args.skip_targets:
            target_name_to_id = import_targets(session, effect_columns)
        else:
            # Load existing targets
            from backend.main import TargetModel
            existing_targets = session.query(TargetModel).all()
            target_name_to_id = {t.name: t.id for t in existing_targets}
            logger.info(f"Using {len(target_name_to_id)} existing targets")

        # Read TSV data
        data_rows = read_tsv_data(args.file)

        # Import SNPs and effects
        stats = import_snps_and_effects(
            session,
            data_rows,
            target_name_to_id,
            args.batch_size
        )

        # Create import log
        create_import_log(session, stats, args.file)

        # Refresh materialized views
        if args.refresh_views:
            refresh_materialized_views(session)

        session.close()

        # Print summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("=" * 60)
        logger.info("Import completed successfully!")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"SNPs imported: {stats['snps_imported']}")
        logger.info(f"SNPs skipped: {stats['snps_skipped']}")
        logger.info(f"Effects imported: {stats['effects_imported']}")
        logger.info(f"Effects skipped: {stats['effects_skipped']}")
        if stats['errors']:
            logger.info(f"Errors: {len(stats['errors'])}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
