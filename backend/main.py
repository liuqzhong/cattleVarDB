"""
============================================
Cattle SNP Effect Value Database - Backend API
牛变异效应值数据库 - 后端API
============================================

Technology: FastAPI + SQLAlchemy + PostgreSQL
Author: Generated based on requirements
"""

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, BigInteger, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import os
import re

# ============================================
# Configuration
# ============================================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cattle_user:cattle_pass@localhost:5432/cattle_snp_db"
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
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================
# Database Models
# ============================================
class SNPModel(Base):
    """SNP基础信息表"""
    __tablename__ = "snps"  # PostgreSQL 会自动转为小写

    id = Column(Integer, primary_key=True, index=True)
    chrom = Column(String(10), nullable=False, index=True)
    pos = Column(BigInteger, nullable=False, index=True)
    rs_id = Column(String(100), nullable=True, index=True)
    ref_allele = Column(String(10), nullable=False)
    alt_allele = Column(String(10), nullable=False)
    max_abs_sad = Column(Float, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TargetModel(Base):
    """靶点（组织/细胞类型）表"""
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SNPEffectModel(Base):
    """SNP效应值表"""
    __tablename__ = "snp_effects"

    id = Column(BigInteger, primary_key=True, index=True)
    snp_id = Column(Integer, nullable=False, index=True)
    target_id = Column(Integer, nullable=False, index=True)
    effect_value = Column(Float, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class GeneModel(Base):
    """基因注释表"""
    __tablename__ = "genes"

    id = Column(Integer, primary_key=True, index=True)
    gene_id = Column(String(50), nullable=False, unique=True, index=True)
    gene_name = Column(String(255), nullable=True)
    chrom = Column(String(50), nullable=False, index=True)  # Increased from 10 to 50
    start_pos = Column(BigInteger, nullable=False)
    end_pos = Column(BigInteger, nullable=False)
    strand = Column(String(1), nullable=True)
    gene_biotype = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TranscriptModel(Base):
    """转录本表"""
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(String(50), nullable=False, unique=True, index=True)
    gene_id = Column(String(50), nullable=False, index=True)
    chrom = Column(String(50), nullable=False, index=True)
    start_pos = Column(BigInteger, nullable=False)
    end_pos = Column(BigInteger, nullable=False)
    strand = Column(String(1), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExonModel(Base):
    """外显子表"""
    __tablename__ = "exons"

    id = Column(BigInteger, primary_key=True, index=True)
    transcript_id = Column(String(50), nullable=False, index=True)
    chrom = Column(String(50), nullable=False, index=True)
    start_pos = Column(BigInteger, nullable=False)
    end_pos = Column(BigInteger, nullable=False)
    exon_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================
# Pydantic Schemas
# ============================================
class SNPBase(BaseModel):
    """SNP基础Schema"""
    chrom: str = Field(..., description="染色体 (如 chr1)")
    pos: int = Field(..., description="位置", gt=0)
    rs_id: Optional[str] = Field(None, description="dbSNP ID (如 rs1115118696)")
    ref_allele: str = Field(..., description="参考碱基")
    alt_allele: str = Field(..., description="变异碱基")
    max_abs_sad: float = Field(..., description="最大绝对SAD值")


class SNPResponse(SNPBase):
    """SNP响应Schema"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    top_effects: Optional[List[dict]] = Field(default=[], description="Top N effect values for preview")

    class Config:
        from_attributes = True


class SNPPaginatedResponse(BaseModel):
    """分页响应Schema"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_pages: int = Field(..., description="总页数")
    data: List[SNPResponse] = Field(..., description="SNP数据列表")


class SNPDetailResponse(SNPResponse):
    """SNP详情响应Schema（包含效应值）"""
    effect_values: List[dict] = Field(default=[], description="效应值列表")
    nearest_gene: Optional[dict] = Field(default=None, description="最近的基因信息")


class GeneInfoResponse(BaseModel):
    """基因信息响应"""
    gene_id: str
    gene_name: Optional[str] = None
    chrom: str
    start_pos: int
    end_pos: int
    strand: Optional[str] = None
    distance: int = Field(..., description="SNP 到基因的距离")
    gene_biotype: Optional[str] = None


class EffectValueResponse(BaseModel):
    """单个效应值响应"""
    target_name: str
    effect_value: float


class ErrorResponse(BaseModel):
    """错误响应Schema"""
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    detail: Optional[str] = Field(None, description="详细错误信息")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    database: str
    timestamp: datetime


# ============================================
# FastAPI App Initialization
# ============================================
app = FastAPI(
    title="Cattle SNP Effect Value Database API",
    description="牛变异效应值数据库 - RESTful API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Database Dependency
# ============================================
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# Utility Functions
# ============================================
def parse_chrom_pos(query: str) -> Optional[tuple]:
    """
    解析染色体:位置格式的查询字符串
    如: "chr1:15449431" -> ("1", 15449431)
    或者: "1:15449431" -> ("1", 15449431)
    """
    # Try pattern with "chr" prefix
    pattern = r'^[cC][hH][rR]([0-9XYxy]+):([0-9]+)$'
    match = re.match(pattern, query.strip())
    if match:
        chrom = match.group(1)  # Just the number, no "chr" prefix
        pos = int(match.group(2))
        return chrom, pos

    # Try pattern without "chr" prefix (just "number:position")
    pattern2 = r'^([0-9XYxy]+):([0-9]+)$'
    match2 = re.match(pattern2, query.strip())
    if match2:
        chrom = match2.group(1)
        pos = int(match2.group(2))
        return chrom, pos

    return None


def calculate_total_pages(total: int, page_size: int) -> int:
    """计算总页数"""
    return (total + page_size - 1) // page_size if page_size > 0 else 0


def find_nearest_gene(db: Session, chrom: str, pos: int) -> Optional[dict]:
    """
    查找最近的基因

    Args:
        db: 数据库会话
        chrom: 染色体
        pos: SNP 位置

    Returns:
        最近基因的信息字典，如果没有找到则返回 None
    """
    try:
        # 查找同一染色体上的所有基因
        # 优先查找包含该位置的基因（SNP 在基因内）
        genes_within = db.query(GeneModel).filter(
            GeneModel.chrom == chrom,
            GeneModel.start_pos <= pos,
            GeneModel.end_pos >= pos
        ).first()

        if genes_within:
            # SNP 在基因内
            return {
                "gene_id": genes_within.gene_id,
                "gene_name": genes_within.gene_name,
                "chrom": genes_within.chrom,
                "start_pos": genes_within.start_pos,
                "end_pos": genes_within.end_pos,
                "strand": genes_within.strand,
                "distance": 0,
                "gene_biotype": genes_within.gene_biotype,
                "location": "within"
            }

        # 如果没有找到包含 SNP 的基因，查找最近的基因
        # 查找基因起始位置在 SNP 之前的最近基因
        gene_before = db.query(GeneModel).filter(
            GeneModel.chrom == chrom,
            GeneModel.end_pos < pos
        ).order_by(
            GeneModel.end_pos.desc()
        ).first()

        # 查找基因起始位置在 SNP 之后的最近基因
        gene_after = db.query(GeneModel).filter(
            GeneModel.chrom == chrom,
            GeneModel.start_pos > pos
        ).order_by(
            GeneModel.start_pos.asc()
        ).first()

        # 计算距离并选择最近的
        nearest = None
        min_distance = float('inf')

        if gene_before:
            distance_before = pos - gene_before.end_pos
            if distance_before < min_distance:
                min_distance = distance_before
                nearest = gene_before

        if gene_after:
            distance_after = gene_after.start_pos - pos
            if distance_after < min_distance:
                min_distance = distance_after
                nearest = gene_after

        if nearest:
            return {
                "gene_id": nearest.gene_id,
                "gene_name": nearest.gene_name,
                "chrom": nearest.chrom,
                "start_pos": nearest.start_pos,
                "end_pos": nearest.end_pos,
                "strand": nearest.strand,
                "distance": int(min_distance),
                "gene_biotype": nearest.gene_biotype,
                "location": "nearby"
            }

        return None

    except Exception as e:
        logger.error(f"Error finding nearest gene: {str(e)}")
        return None


def detect_snp_region(db: Session, chrom: str, pos: int, gene_id: str) -> Optional[str]:
    """
    检测 SNP 在基因中的具体区域

    Returns:
        区域类型：exon, intron, utr_5_prime, utr_3_prime, upstream, downstream
    """
    try:
        # 获取该基因的所有转录本
        transcripts = db.query(TranscriptModel).filter(
            TranscriptModel.gene_id == gene_id,
            TranscriptModel.chrom == chrom
        ).all()

        if not transcripts:
            return "intergenic"

        # 检查每个转录本
        for transcript in transcripts:
            # 检查 SNP 是否在转录本范围内
            if pos < transcript.start_pos or pos > transcript.end_pos:
                continue

            # 检查是否在外显子中
            exon = db.query(ExonModel).filter(
                ExonModel.transcript_id == transcript.transcript_id,
                ExonModel.chrom == chrom,
                ExonModel.start_pos <= pos,
                ExonModel.end_pos >= pos
            ).first()

            if exon:
                return f"exon {exon.exon_number}"

            # 如果不在外显子中，那就在内含子中
            return "intron"

        # 如果遍历完所有转录本都没有匹配，说明在基因间
        return "intergenic"

    except Exception as e:
        logger.error(f"Error detecting SNP region: {str(e)}")
        return None


# ============================================
# API Endpoints
# ============================================

@app.get("/", response_model=dict)
async def root():
    """API根路径"""
    return {
        "message": "Cattle SNP Effect Value Database API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """健康检查接口"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return HealthResponse(
            status="healthy",
            database="connected",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )


@app.get("/snps", response_model=SNPPaginatedResponse)
async def get_snps(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    sort_by: str = Query("id", description="排序字段"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="排序方向"),
    top_n: int = Query(10, ge=0, le=20, description="Top N effect values to include"),
    db: Session = Depends(get_db)
):
    """
    获取SNP列表（分页）

    - **page**: 页码，从1开始
    - **page_size**: 每页大小，最大100
    - **sort_by**: 排序字段（id, chrom, pos, max_abs_sad等）
    - **sort_order**: 排序方向（asc或desc）
    - **top_n**: 返回前N个最常见的target的效应值（默认10，最大20）
    """
    try:
        # Build query
        query = db.query(SNPModel)

        # Get total count
        total = query.count()

        # Apply sorting
        sort_column = getattr(SNPModel, sort_by, SNPModel.id)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        offset = (page - 1) * page_size
        snps = query.offset(offset).limit(page_size).all()

        # Get most common targets (targets with most effect records)
        if top_n > 0:
            # Query to count effects per target and get top N
            from sqlalchemy import func
            target_counts = db.query(
                SNPEffectModel.target_id,
                func.count(SNPEffectModel.id).label('count')
            ).group_by(
                SNPEffectModel.target_id
            ).order_by(
                func.count(SNPEffectModel.id).desc()
            ).limit(top_n).all()

            common_target_ids = [t[0] for t in target_counts]
            common_targets = db.query(TargetModel).filter(TargetModel.id.in_(common_target_ids)).all()
            common_target_map = {t.id: t.name for t in common_targets}
        else:
            common_target_ids = []
            common_target_map = {}

        # Get effect values for the common targets for each SNP
        snp_data = []
        for snp in snps:
            snp_dict = {
                "id": snp.id,
                "chrom": snp.chrom,
                "pos": snp.pos,
                "rs_id": snp.rs_id,
                "ref_allele": snp.ref_allele,
                "alt_allele": snp.alt_allele,
                "max_abs_sad": snp.max_abs_sad,
                "created_at": snp.created_at,
                "updated_at": snp.updated_at,
                "top_effects": []
            }

            if top_n > 0 and common_target_ids:
                # Get effect values for common targets only
                effects = db.query(SNPEffectModel).filter(
                    SNPEffectModel.snp_id == snp.id,
                    SNPEffectModel.target_id.in_(common_target_ids)
                ).all()

                # Create effect dict with target names
                snp_dict["top_effects"] = [
                    {
                        "target_name": common_target_map[effect.target_id],
                        "effect_value": effect.effect_value
                    }
                    for effect in effects
                ]

            snp_data.append(snp_dict)

        # Calculate total pages
        total_pages = calculate_total_pages(total, page_size)

        return SNPPaginatedResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            data=snp_data
        )

    except Exception as e:
        logger.error(f"Error fetching SNPs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch SNPs: {str(e)}"
        )


@app.get("/snps/search", response_model=SNPPaginatedResponse)
async def search_snps(
    query: str = Query(..., min_length=1, description="搜索查询 (chr:position 或 rsID)"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    top_n: int = Query(10, ge=0, le=20, description="Top N effect values to include"),
    db: Session = Depends(get_db)
):
    """
    搜索SNP

    支持两种搜索格式:
    - **chr:position**: 如 "chr1:15449431" (精确匹配)
    - **rsID**: 如 "rs1115118696" (模糊匹配)
    """
    try:
        search_query = db.query(SNPModel)

        # Try to parse as chrom:position format
        chrom_pos = parse_chrom_pos(query)
        if chrom_pos:
            chrom, pos = chrom_pos
            search_query = search_query.filter(
                SNPModel.chrom == chrom,
                SNPModel.pos == pos
            )
            logger.info(f"Searching by chrom:pos - {chrom}:{pos}")
        else:
            # Search by rs_id (fuzzy match)
            search_query = search_query.filter(
                SNPModel.rs_id.ilike(f"%{query}%")
            )
            logger.info(f"Searching by rs_id - {query}")

        # Get total count
        total = search_query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        results = search_query.offset(offset).limit(page_size).all()

        # Get most common targets (targets with most effect records)
        if top_n > 0:
            # Query to count effects per target and get top N
            from sqlalchemy import func
            target_counts = db.query(
                SNPEffectModel.target_id,
                func.count(SNPEffectModel.id).label('count')
            ).group_by(
                SNPEffectModel.target_id
            ).order_by(
                func.count(SNPEffectModel.id).desc()
            ).limit(top_n).all()

            common_target_ids = [t[0] for t in target_counts]
            common_targets = db.query(TargetModel).filter(TargetModel.id.in_(common_target_ids)).all()
            common_target_map = {t.id: t.name for t in common_targets}
        else:
            common_target_ids = []
            common_target_map = {}

        # Get effect values for the common targets for each SNP
        snp_data = []
        for snp in results:
            snp_dict = {
                "id": snp.id,
                "chrom": snp.chrom,
                "pos": snp.pos,
                "rs_id": snp.rs_id,
                "ref_allele": snp.ref_allele,
                "alt_allele": snp.alt_allele,
                "max_abs_sad": snp.max_abs_sad,
                "created_at": snp.created_at,
                "updated_at": snp.updated_at,
                "top_effects": []
            }

            if top_n > 0 and common_target_ids:
                # Get effect values for common targets only
                effects = db.query(SNPEffectModel).filter(
                    SNPEffectModel.snp_id == snp.id,
                    SNPEffectModel.target_id.in_(common_target_ids)
                ).all()

                # Create effect dict with target names
                snp_dict["top_effects"] = [
                    {
                        "target_name": common_target_map[effect.target_id],
                        "effect_value": effect.effect_value
                    }
                    for effect in effects
                ]

            snp_data.append(snp_dict)

        total_pages = calculate_total_pages(total, page_size)

        return SNPPaginatedResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            data=snp_data
        )

    except Exception as e:
        logger.error(f"Error searching SNPs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@app.get("/snps/{snp_id}", response_model=SNPDetailResponse)
async def get_snp_detail(
    snp_id: int,
    db: Session = Depends(get_db)
):
    """
    获取SNP详情（包含效应值）

    - **snp_id**: SNP数据库ID
    """
    try:
        # Get SNP basic info
        snp = db.query(SNPModel).filter(SNPModel.id == snp_id).first()
        if not snp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SNP with id {snp_id} not found"
            )

        # Get effect values with target names
        effects = db.query(
            SNPEffectModel.effect_value,
            TargetModel.name
        ).join(
            TargetModel, SNPEffectModel.target_id == TargetModel.id
        ).filter(
            SNPEffectModel.snp_id == snp_id
        ).all()

        effect_values = [
            {"target_name": effect.name, "effect_value": effect.effect_value}
            for effect in effects
        ]

        # Find nearest gene
        nearest_gene = find_nearest_gene(db, snp.chrom, snp.pos)

        # Detect SNP region (exon, intron, etc.)
        if nearest_gene and nearest_gene.get('location') == 'within':
            region = detect_snp_region(db, snp.chrom, snp.pos, nearest_gene['gene_id'])
            if region:
                nearest_gene['region'] = region

        return SNPDetailResponse(
            **snp.__dict__,
            effect_values=effect_values,
            nearest_gene=nearest_gene
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching SNP detail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch SNP detail: {str(e)}"
        )


@app.get("/targets", response_model=List[dict])
async def get_targets(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=500, description="返回记录数"),
    db: Session = Depends(get_db)
):
    """
    获取靶点（组织/细胞类型）列表

    - **skip**: 跳过的记录数
    - **limit**: 返回的记录数
    """
    try:
        targets = db.query(TargetModel).offset(skip).limit(limit).all()
        return [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category,
                "description": t.description
            }
            for t in targets
        ]
    except Exception as e:
        logger.error(f"Error fetching targets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch targets: {str(e)}"
        )


@app.get("/stats", response_model=dict)
async def get_statistics(db: Session = Depends(get_db)):
    """
    获取数据库统计信息
    """
    try:
        snp_count = db.query(SNPModel).count()
        target_count = db.query(TargetModel).count()
        effect_count = db.query(SNPEffectModel).count()

        return {
            "total_snps": snp_count,
            "total_targets": target_count,
            "total_effect_records": effect_count,
            "data_timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )


@app.get("/snps/{snp_id}/region", response_model=dict)
async def get_snp_region_data(
    snp_id: int,
    window_size: int = Query(50000, ge=1000, le=1000000, description="窗口大小（bp）"),
    db: Session = Depends(get_db)
):
    """
    获取 SNP 周围区域的数据，用于 IGV 可视化

    返回指定窗口范围内的：
    - 所有基因
    - 所有 SNP
    """
    try:
        # 获取 SNP 信息
        snp = db.query(SNPModel).filter(SNPModel.id == snp_id).first()
        if not snp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SNP with id {snp_id} not found"
            )

        chrom = snp.chrom
        center_pos = snp.pos
        start_pos = max(1, center_pos - window_size // 2)
        end_pos = center_pos + window_size // 2

        # 获取窗口范围内的所有基因
        genes = db.query(GeneModel).filter(
            GeneModel.chrom == chrom,
            GeneModel.start_pos <= end_pos,
            GeneModel.end_pos >= start_pos
        ).all()

        # 转换基因数据为 BED 格式（IGV 可用）
        gene_features = []
        for gene in genes:
            gene_features.append({
                "chrom": chrom,
                "start": gene.start_pos - 1,  # BED 格式是 0-based
                "end": gene.end_pos,
                "name": gene.gene_name or gene.gene_id,
                "gene_id": gene.gene_id,
                "strand": gene.strand or "+",
                "gene_biotype": gene.gene_biotype
            })

        # 获取窗口范围内的所有 SNP
        snps = db.query(SNPModel).filter(
            SNPModel.chrom == chrom,
            SNPModel.pos >= start_pos,
            SNPModel.pos <= end_pos
        ).all()

        snp_features = []
        for s in snps:
            snp_features.append({
                "chrom": chrom,
                "start": s.pos - 1,
                "end": s.pos,
                "name": s.rs_id,
                "snp_id": s.rs_id,
                "ref": s.ref_allele,
                "alt": s.alt_allele,
                "pos": s.pos
            })

        return {
            "chrom": chrom,
            "start": start_pos,
            "end": end_pos,
            "center_snp": {
                "id": snp.id,
                "snp_id": snp.rs_id,
                "pos": snp.pos,
                "ref": snp.ref_allele,
                "alt": snp.alt_allele
            },
            "genes": gene_features,
            "snps": snp_features,
            "total_genes": len(gene_features),
            "total_snps": len(snp_features)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching region data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch region data: {str(e)}"
        )


# ============================================
# Exception Handlers
# ============================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred",
            "detail": str(exc)
        }
    )


# ============================================
# Startup Event
# ============================================
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("Starting Cattle SNP Effect Value Database API...")
    logger.info(f"Database URL: {DATABASE_URL}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Shutting down Cattle SNP Effect Value Database API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
