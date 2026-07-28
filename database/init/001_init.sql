CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS datamind;
CREATE SCHEMA IF NOT EXISTS manufacturing;

CREATE TABLE IF NOT EXISTS datamind.business_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_code VARCHAR(100) UNIQUE NOT NULL,
    metric_name VARCHAR(200) NOT NULL,
    description TEXT,
    formula_expression TEXT NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT '生产',
    source_tables JSONB NOT NULL DEFAULT '[]',
    dimension_fields JSONB NOT NULL DEFAULT '[]',
    synonyms JSONB NOT NULL DEFAULT '[]',
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS datamind.knowledge_embeddings (
    id BIGSERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL,
    source_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1024),
    metadata JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS datamind.analysis_tasks (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL,
    question TEXT NOT NULL,
    intent VARCHAR(100),
    generated_sql TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    result_summary TEXT,
    result_data JSONB NOT NULL DEFAULT '{}',
    audit_trace JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS datamind.metadata_tables (
    id BIGSERIAL PRIMARY KEY,
    schema_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(200) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    row_estimate BIGINT NOT NULL DEFAULT 0,
    UNIQUE (schema_name, table_name)
);

CREATE TABLE IF NOT EXISTS datamind.metadata_columns (
    id BIGSERIAL PRIMARY KEY,
    table_id BIGINT NOT NULL REFERENCES datamind.metadata_tables(id) ON DELETE CASCADE,
    column_name VARCHAR(200) NOT NULL,
    data_type VARCHAR(100) NOT NULL,
    description TEXT,
    sample_values JSONB NOT NULL DEFAULT '[]',
    is_sensitive BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (table_id, column_name)
);

CREATE TABLE IF NOT EXISTS manufacturing.dim_production_line (
    id BIGSERIAL PRIMARY KEY,
    line_code VARCHAR(50) UNIQUE NOT NULL,
    line_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS manufacturing.fact_process_output (
    id BIGSERIAL PRIMARY KEY,
    production_date DATE NOT NULL,
    line_id BIGINT NOT NULL REFERENCES manufacturing.dim_production_line(id),
    process_name VARCHAR(100) NOT NULL,
    actual_qty INTEGER NOT NULL CHECK (actual_qty >= 0),
    qualified_qty INTEGER NOT NULL CHECK (qualified_qty >= 0)
);

CREATE TABLE IF NOT EXISTS manufacturing.fact_quality_inspection (
    id BIGSERIAL PRIMARY KEY,
    inspection_date DATE NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    process_name VARCHAR(100) NOT NULL,
    inspected_qty INTEGER NOT NULL CHECK (inspected_qty >= 0),
    defect_qty INTEGER NOT NULL CHECK (defect_qty >= 0),
    defect_type VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS manufacturing.fact_equipment_downtime (
    id BIGSERIAL PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    downtime_minutes INTEGER NOT NULL CHECK (downtime_minutes >= 0),
    reason VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS manufacturing.fact_inventory (
    id BIGSERIAL PRIMARY KEY,
    record_date DATE NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    current_qty INTEGER NOT NULL CHECK (current_qty >= 0),
    safety_qty INTEGER NOT NULL CHECK (safety_qty >= 0)
);

COMMENT ON TABLE manufacturing.fact_process_output IS '工序产量事实表';
COMMENT ON COLUMN manufacturing.fact_process_output.actual_qty IS '实际生产数量';
COMMENT ON COLUMN manufacturing.fact_process_output.qualified_qty IS '检验合格数量';

INSERT INTO datamind.business_metrics
    (metric_code, metric_name, description, formula_expression, source_tables, dimension_fields, synonyms)
VALUES
    ('process_yield_rate', '工序良率', '工序合格数量占实际生产数量的比例',
     'SUM(qualified_qty) / NULLIF(SUM(actual_qty), 0) * 100',
     '["manufacturing.fact_process_output"]', '["process_name", "line_id", "production_date"]',
     '["良率", "合格率", "良品率"]')
ON CONFLICT (metric_code) DO NOTHING;

INSERT INTO manufacturing.dim_production_line (line_code, line_name)
VALUES ('LINE-01', '一号产线'), ('LINE-02', '二号产线')
ON CONFLICT (line_code) DO NOTHING;

INSERT INTO manufacturing.fact_process_output
    (production_date, line_id, process_name, actual_qty, qualified_qty)
SELECT CURRENT_DATE - offset_day,
       line.id,
       '装配',
       CASE WHEN line.line_code = 'LINE-01' THEN 900 + (7 - offset_day) * 25 ELSE 800 + (7 - offset_day) * 18 END,
       CASE WHEN line.line_code = 'LINE-01' THEN 880 + (7 - offset_day) * 24 ELSE 780 + (7 - offset_day) * 17 END
FROM generate_series(0, 6) AS days(offset_day)
CROSS JOIN manufacturing.dim_production_line AS line
WHERE NOT EXISTS (SELECT 1 FROM manufacturing.fact_process_output);

INSERT INTO manufacturing.fact_quality_inspection
    (inspection_date, product_name, process_name, inspected_qty, defect_qty, defect_type)
SELECT CURRENT_DATE - offset_day, '产品A', '装配', 500, 8 + offset_day, '装配偏差'
FROM generate_series(0, 6) AS days(offset_day)
WHERE NOT EXISTS (SELECT 1 FROM manufacturing.fact_quality_inspection);

INSERT INTO manufacturing.fact_equipment_downtime
    (equipment_name, started_at, ended_at, downtime_minutes, reason)
SELECT '装配机-' || number,
       NOW() - (number || ' days')::INTERVAL,
       NOW() - (number || ' days')::INTERVAL + INTERVAL '30 minutes',
       30,
       '计划维护'
FROM generate_series(1, 3) AS numbers(number)
WHERE NOT EXISTS (SELECT 1 FROM manufacturing.fact_equipment_downtime);

INSERT INTO manufacturing.fact_inventory
    (record_date, product_name, current_qty, safety_qty)
SELECT CURRENT_DATE, product_name, current_qty, 300
FROM (VALUES ('产品A', 520), ('产品B', 260), ('产品C', 410)) AS sample(product_name, current_qty)
WHERE NOT EXISTS (SELECT 1 FROM manufacturing.fact_inventory);
