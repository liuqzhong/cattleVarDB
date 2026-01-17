"""
============================================
Import Gene Annotations from GTF File
从 GTF 文件导入基因注释数据
============================================

Usage: python import_genes.py
"""

import sys
import os
import gzip

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, GeneModel
from datetime import datetime
import logging

# ============================================
# Configuration
# ============================================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cattle_user:cattle_pass@localhost:5432/cattle_snp_db"
)

# GTF file path (relative to this script's parent directory)
GTF_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "reference",
    "Bos_taurus.ARS-UCD1.2.110.gtf.gz"
)

# ============================================
# Logging Setup
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# Database Setup
# ============================================
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Create tables
logger.info("Creating database tables...")
Base.metadata.create_all(engine)
logger.info("Tables created successfully")


def parse_gtf_file(gtf_file_path):
    """
    Parse GTF file and yield gene records

    GTF format:
    seqname   source   feature   start   end   score   strand   frame   attribute
    """
    logger.info(f"Parsing GTF file: {gtf_file_path}")

    open_func = gzip.open if gtf_file_path.endswith('.gz') else open
    genes_added = 0
    genes_skipped = 0

    with open_func(gtf_file_path, 'rt') as f:
        for line_num, line in enumerate(f, 1):
            # Skip comments
            if line.startswith('#'):
                continue

            parts = line.strip().split('\t')
            if len(parts) < 9:
                continue

            seqname = parts[0]
            source = parts[1]
            feature = parts[2]
            start = int(parts[3])
            end = int(parts[4])
            score = parts[5]
            strand = parts[6]
            frame = parts[7]
            attributes = parts[8]

            # Only process gene features
            if feature.lower() != 'gene':
                continue

            # Parse attributes
            attr_dict = {}
            for attr in attributes.split(';'):
                attr = attr.strip()
                if not attr:
                    continue
                if ' ' in attr:
                    key, value = attr.split(' ', 1)
                    key = key.strip()
                    value = value.strip().strip('"')
                    attr_dict[key] = value

            gene_id = attr_dict.get('gene_id', '')
            gene_name = attr_dict.get('gene_name', attr_dict.get('Name', ''))
            gene_type = attr_dict.get('gene_type', attr_dict.get('gene_biotype', ''))
            description = attr_dict.get('description', '')

            # Clean chromosome name (remove 'chr' prefix if present)
            chrom = seqname.replace('chr', '').replace('CHR', '')

            if not gene_id:
                logger.warning(f"Line {line_num}: Missing gene_id, skipping")
                genes_skipped += 1
                continue

            yield {
                'gene_id': gene_id,
                'gene_name': gene_name or None,
                'chrom': chrom,
                'start': start,
                'end': end,
                'strand': strand,
                'gene_type': gene_type or None,
                'description': description or None
            }

            genes_added += 1

            if genes_added % 1000 == 0:
                logger.info(f"Processed {genes_added} genes...")

    logger.info(f"Finished parsing GTF file. Total genes: {genes_added}, Skipped: {genes_skipped}")


def import_genes():
    """Import genes from GTF file to database"""
    session = Session()

    try:
        # Check if genes table already has data
        existing_count = session.query(GeneModel).count()
        if existing_count > 0:
            logger.warning(f"Database already contains {existing_count} genes")
            response = input("Do you want to clear existing genes and re-import? (yes/no): ")
            if response.lower() != 'yes':
                logger.info("Import cancelled")
                return

            # Clear existing genes
            logger.info("Clearing existing genes...")
            session.query(GeneModel).delete()
            session.commit()
            logger.info("Existing genes cleared")

        # Parse and import genes
        logger.info("Starting gene import...")
        batch_size = 1000
        batch = []
        total_imported = 0

        for gene_data in parse_gtf_file(GTF_FILE):
            batch.append(GeneModel(**gene_data))

            if len(batch) >= batch_size:
                session.bulk_save_objects(batch)
                session.commit()
                total_imported += len(batch)
                logger.info(f"Imported {total_imported} genes so far...")
                batch = []

        # Import remaining genes in batch
        if batch:
            session.bulk_save_objects(batch)
            session.commit()
            total_imported += len(batch)

        logger.info(f"Gene import completed successfully! Total genes imported: {total_imported}")

        # Verify import
        final_count = session.query(GeneModel).count()
        logger.info(f"Verification: Database now contains {final_count} genes")

    except Exception as e:
        session.rollback()
        logger.error(f"Error during import: {str(e)}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    if not os.path.exists(GTF_FILE):
        logger.error(f"GTF file not found: {GTF_FILE}")
        logger.error(f"Please ensure the file exists at: {os.path.abspath(GTF_FILE)}")
        sys.exit(1)

    logger.info("="*60)
    logger.info("Gene Annotation Import Tool")
    logger.info("="*60)
    logger.info(f"Database: {DATABASE_URL}")
    logger.info(f"GTF File: {GTF_FILE}")
    logger.info("="*60)

    import_genes()
    logger.info("Import process completed!")
