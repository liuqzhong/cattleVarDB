-- ============================================
-- Cattle SNP Effect Value Database Schema
-- 牛变异效应值数据库 - 数据库结构设计
-- ============================================

-- Database Selection: PostgreSQL
-- Reason:
-- 1. Better support for JSON/JSONB data types (for flexible metadata)
-- 2. Excellent full-text search capabilities
-- 3. Advanced indexing options (GIN, GiST)
-- 4. Materialized views for query optimization
-- 5. Better concurrency handling for scientific data queries

-- Drop existing tables (for clean reinstall)
DROP TABLE IF EXISTS snp_effects CASCADE;
DROP TABLE IF EXISTS snp_effect_summary CASCADE;
DROP TABLE IF EXISTS targets CASCADE;
DROP TABLE IF EXISTS snps CASCADE;

-- ============================================
-- Table 1: targets
-- Stores 578 tissue/cell type information
-- 存储组织/细胞类型信息
-- ============================================
CREATE TABLE targets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100),  -- e.g., 'tissue', 'cell_type', 'embryo_stage'
    description TEXT,
    metadata JSONB,  -- Flexible storage for additional attributes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Table 2: snps
-- Stores SNP basic information (first 6 columns from TSV)
-- 存储SNP基础信息
-- ============================================
CREATE TABLE snps (
    id SERIAL PRIMARY KEY,
    chrom VARCHAR(10) NOT NULL,  -- Chromosome (chr1-chr29, chrX)
    pos BIGINT NOT NULL,         -- Position on chromosome
    rs_id VARCHAR(100),          -- dbSNP identifier (rsID)
    ref_allele VARCHAR(10) NOT NULL,  -- Reference allele
    alt_allele VARCHAR(10) NOT NULL,  -- Alternative allele
    max_abs_sad FLOAT NOT NULL,  -- Maximum absolute SAD value
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_snp UNIQUE (chrom, pos, ref_allele, alt_allele)
);

-- ============================================
-- Extensions
-- ============================================
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For fuzzy text search

-- ============================================
-- Table 3: snp_effects
-- Stores effect values for each SNP-target combination
-- 存储每个SNP对每个靶点的效应值
-- ============================================
CREATE TABLE snp_effects (
    id BIGSERIAL PRIMARY KEY,
    snp_id INTEGER NOT NULL REFERENCES snps(id) ON DELETE CASCADE,
    target_id INTEGER NOT NULL REFERENCES targets(id) ON DELETE CASCADE,
    effect_value FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_snp_target UNIQUE (snp_id, target_id)
);

-- ============================================
-- Materialized View: snp_effect_summary
-- Pre-computed summary for quick queries
-- 预计算汇总视图，用于快速查询
-- ============================================
CREATE MATERIALIZED VIEW snp_effect_summary AS
SELECT
    s.id AS snp_id,
    s.chrom,
    s.pos,
    s.rs_id,
    s.ref_allele,
    s.alt_allele,
    s.max_abs_sad,
    COUNT(e.id) AS total_targets,
    AVG(e.effect_value) AS mean_effect,
    STDDEV(e.effect_value) AS std_effect,
    MIN(e.effect_value) AS min_effect,
    MAX(e.effect_value) AS max_effect
FROM snps s
LEFT JOIN snp_effects e ON s.id = e.snp_id
GROUP BY s.id;

-- ============================================
-- Indexes for Performance Optimization
-- 索引优化
-- ============================================

-- snps table indexes
CREATE INDEX idx_snps_chrom_pos ON snps(chrom, pos);
CREATE INDEX idx_snps_rs_id ON snps(rs_id) WHERE rs_id IS NOT NULL;
CREATE INDEX idx_snps_max_abs_sad ON snps(max_abs_sad DESC);
CREATE INDEX idx_snps_chrom_pos_ref_alt ON snps(chrom, pos, ref_allele, alt_allele);

-- snp_effects table indexes
CREATE INDEX idx_snp_effects_snp_id ON snp_effects(snp_id);
CREATE INDEX idx_snp_effects_target_id ON snp_effects(target_id);
CREATE INDEX idx_snp_effects_value ON snp_effects(effect_value);

-- For full-text search on rs_id
CREATE INDEX idx_snps_rs_id_trgm ON snps USING gin(rs_id gin_trgm_ops);

-- ============================================
-- Functions for common operations
-- ============================================

-- Function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_summary_view()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW snp_effect_summary;
END;
$$ LANGUAGE plpgsql;

-- Function to search SNPs by chromosome:position or rs_id
CREATE OR REPLACE FUNCTION search_snps(search_query VARCHAR)
RETURNS TABLE (
    id INTEGER,
    chrom VARCHAR,
    pos BIGINT,
    rs_id VARCHAR,
    ref_allele VARCHAR,
    alt_allele VARCHAR,
    max_abs_sad FLOAT
) AS $$
BEGIN
    -- Try to parse as chr:position format
    IF search_query ~ '^[cC][hH][rR][0-9XY]+:[0-9]+$' THEN
        RETURN QUERY
        SELECT s.id, s.chrom, s.pos, s.rs_id, s.ref_allele, s.alt_allele, s.max_abs_sad
        FROM snps s
        WHERE s.chrom || ':' || s.pos = search_query;
    -- Try to search by rs_id
    ELSE
        RETURN QUERY
        SELECT s.id, s.chrom, s.pos, s.rs_id, s.ref_allele, s.alt_allele, s.max_abs_sad
        FROM snps s
        WHERE s.rs_id ILIKE '%' || search_query || '%';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Triggers for updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_snps_updated_at BEFORE UPDATE ON snps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_targets_updated_at BEFORE UPDATE ON targets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Statistics and metadata
-- ============================================
-- Create a table to track data import status
CREATE TABLE IF NOT EXISTS DATA_IMPORT_LOG (
    id SERIAL PRIMARY KEY,
    import_type VARCHAR(50) NOT NULL,
    source_file VARCHAR(500),
    records_processed INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Comments for documentation
COMMENT ON TABLE snps IS 'Stores SNP basic information from cattle variants';
COMMENT ON TABLE targets IS 'Stores tissue/cell type information (578 targets)';
COMMENT ON TABLE snp_effects IS 'Stores effect values for SNP-target combinations';
COMMENT ON TABLE snp_effect_summary IS 'Pre-computed summary statistics for quick queries';
COMMENT ON COLUMN snps.max_abs_sad IS 'Maximum absolute SAD (Signal Aberration Deviation) value across all targets';
COMMENT ON COLUMN snp_effects.effect_value IS 'Normalized effect value (norRPKM) for specific SNP-target combination';
