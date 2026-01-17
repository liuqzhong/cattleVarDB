"""
============================================
Import Transcripts and Exons from GTF File
从 GTF 文件导入转录本和外显子信息
============================================

Usage:
    python import_transcripts.py --file ../database/reference/Bos_taurus.ARS-UCD1.2.110.gtf.gz
"""

import argparse
import gzip
import logging
import os
import re
import sys
from typing import Optional, Tuple
from tqdm import tqdm

# Add parent directory to path to import from main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from main import TranscriptModel, ExonModel, Base

# Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cattle_user:cattle_pass@localhost:5432/cattle_snp_db"
)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_gtf_attributes(attributes_str: str) -> dict:
    """解析 GTF 属性字段"""
    attributes = {}
    pattern = r'(\w+)\s+"([^"]+)";'
    matches = re.findall(pattern, attributes_str)

    for key, value in matches:
        attributes[key] = value

    return attributes


def import_transcripts_and_exons(file_path: str):
    """
    导入转录本和外显子数据
    """
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create tables
        logger.info("Creating database tables if not exists...")
        Base.metadata.create_all(engine)
        logger.info("Tables ready")

        logger.info(f"Parsing GTF file: {file_path}")

        # Open GTF file (handle gzipped files)
        open_func = gzip.open if file_path.endswith('.gz') else open

        transcripts_data = []
        exons_data = []
        transcript_count = 0
        exon_count = 0

        with open_func(file_path, 'rt') as f:
            for line_num, line in tqdm(enumerate(f, 1), desc="Parsing GTF", unit=" lines"):
                if line.startswith('#'):
                    continue

                parts = line.strip().split('\t')
                if len(parts) < 9:
                    continue

                chrom = parts[0]
                feature = parts[2]
                start = int(parts[3])
                end = int(parts[4])
                strand = parts[6]
                attributes = parts[8]

                # Clean chromosome name
                chrom = chrom.replace('chr', '').replace('CHR', '')

                # Parse attributes
                attrs = parse_gtf_attributes(attributes)

                if feature == 'transcript':
                    transcript_id = attrs.get('transcript_id')
                    gene_id = attrs.get('gene_id')

                    if transcript_id and gene_id:
                        transcripts_data.append({
                            'transcript_id': transcript_id,
                            'gene_id': gene_id,
                            'chrom': chrom,
                            'start_pos': start,
                            'end_pos': end,
                            'strand': strand
                        })
                        transcript_count += 1

                elif feature == 'exon':
                    transcript_id = attrs.get('transcript_id')
                    exon_number = attrs.get('exon_number')

                    if transcript_id and exon_number:
                        try:
                            exon_num = int(exon_number)
                            exons_data.append({
                                'transcript_id': transcript_id,
                                'chrom': chrom,
                                'start_pos': start,
                                'end_pos': end,
                                'exon_number': exon_num
                            })
                            exon_count += 1
                        except ValueError:
                            pass

        logger.info(f"Found {transcript_count} transcripts and {exon_count} exons")

        # Import transcripts in batch
        batch_size = 1000
        imported_transcripts = 0

        logger.info("Importing transcripts...")
        for i in tqdm(range(0, len(transcripts_data), batch_size), desc="Importing transcripts"):
            batch = transcripts_data[i:i + batch_size]

            for transcript_data in batch:
                try:
                    # Check if transcript already exists
                    existing = session.query(TranscriptModel).filter_by(
                        transcript_id=transcript_data['transcript_id']
                    ).first()

                    if not existing:
                        transcript = TranscriptModel(**transcript_data)
                        session.add(transcript)
                        imported_transcripts += 1
                except Exception as e:
                    logger.error(f"Error inserting transcript: {e}")

            session.commit()

        logger.info(f"Imported {imported_transcripts} transcripts")

        # Import exons in batch
        batch_size = 5000
        imported_exons = 0

        logger.info("Importing exons...")
        for i in tqdm(range(0, len(exons_data), batch_size), desc="Importing exons"):
            batch = exons_data[i:i + batch_size]

            for exon_data in batch:
                try:
                    # Check if exon already exists
                    existing = session.query(ExonModel).filter_by(
                        transcript_id=exon_data['transcript_id'],
                        exon_number=exon_data['exon_number']
                    ).first()

                    if not existing:
                        exon = ExonModel(**exon_data)
                        session.add(exon)
                        imported_exons += 1
                except Exception as e:
                    logger.error(f"Error inserting exon: {e}")

            session.commit()

        logger.info(f"Imported {imported_exons} exons")

        # Verify using func.count()
        from sqlalchemy import func
        final_transcripts = session.query(func.count(TranscriptModel.id)).scalar()
        final_exons = session.query(func.count(ExonModel.id)).scalar()

        logger.info(f"Verification: {final_transcripts} transcripts, {final_exons} exons in database")

    except Exception as e:
        session.rollback()
        logger.error(f"Error during import: {str(e)}")
        raise
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description='Import transcripts and exons from GTF file')
    parser.add_argument('--file', required=True, help='Path to GTF file (can be gzipped)')

    args = parser.parse_args()

    if not os.path.exists(args.file):
        logger.error(f"File not found: {args.file}")
        sys.exit(1)

    import_transcripts_and_exons(args.file)


if __name__ == "__main__":
    main()
