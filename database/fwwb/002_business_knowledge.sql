-- A07 第一模块：业务知识管理
SET search_path TO fwwb, public;

CREATE TABLE IF NOT EXISTS fwwb.business_objects (
    id BIGSERIAL PRIMARY KEY,
    object_code VARCHAR(100) NOT NULL UNIQUE,
    object_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    source_table VARCHAR(200),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fwwb.business_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_code VARCHAR(100) NOT NULL UNIQUE,
    metric_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    formula_expression TEXT NOT NULL,
    unit VARCHAR(30),
    time_field VARCHAR(100),
    source_tables JSONB NOT NULL DEFAULT '[]',
    dimension_fields JSONB NOT NULL DEFAULT '[]',
    synonyms JSONB NOT NULL DEFAULT '[]',
    version INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fwwb.business_rules (
    id BIGSERIAL PRIMARY KEY,
    rule_code VARCHAR(100) NOT NULL UNIQUE,
    rule_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    rule_type VARCHAR(50) NOT NULL,
    expression TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    priority INTEGER NOT NULL DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fwwb.analysis_topics (
    id BIGSERIAL PRIMARY KEY,
    topic_code VARCHAR(100) NOT NULL UNIQUE,
    topic_name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    object_codes JSONB NOT NULL DEFAULT '[]',
    metric_codes JSONB NOT NULL DEFAULT '[]',
    example_questions JSONB NOT NULL DEFAULT '[]',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'fwwb' AND indexname = 'idx_business_objects_category'
    ) THEN
        CREATE INDEX idx_business_objects_category ON fwwb.business_objects(category);
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'fwwb' AND indexname = 'idx_business_metrics_category'
    ) THEN
        CREATE INDEX idx_business_metrics_category ON fwwb.business_metrics(category);
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'fwwb' AND indexname = 'idx_business_rules_category'
    ) THEN
        CREATE INDEX idx_business_rules_category ON fwwb.business_rules(category);
    END IF;
END $$;

COMMENT ON TABLE fwwb.business_objects IS '制造业业务对象知识';
COMMENT ON TABLE fwwb.business_metrics IS '制造业业务指标及计算口径';
COMMENT ON TABLE fwwb.business_rules IS '制造业业务规则';
COMMENT ON TABLE fwwb.analysis_topics IS '制造业分析主题';

DO $$
BEGIN
IF NOT EXISTS (SELECT 1 FROM fwwb.business_objects WHERE object_code = 'product') THEN
INSERT INTO fwwb.business_objects
    (object_code, object_name, category, description, source_table)
VALUES
    ('product', '产品', '生产', '企业生产和库存管理的产品对象', 'fwwb.dim_product'),
    ('production_line', '产线', '生产', '承担生产任务的制造产线', 'fwwb.dim_production_line'),
    ('process', '工序', '生产', '产品制造过程中的加工步骤', 'fwwb.dim_process'),
    ('equipment', '设备', '设备', '参与生产加工和检测的设备', 'fwwb.dim_equipment'),
    ('production_order', '生产工单', '生产', '生产计划下达形成的执行单据', 'fwwb.fact_production_order'),
    ('quality_inspection', '质量检验', '质量', '生产过程及完工产品的质量检验记录', 'fwwb.fact_quality_inspection'),
    ('inventory', '库存', '库存', '产品当前库存和安全库存信息', 'fwwb.fact_inventory');
END IF;
END $$;

DO $$
BEGIN
IF NOT EXISTS (SELECT 1 FROM fwwb.business_metrics WHERE metric_code = 'output_qty') THEN
INSERT INTO fwwb.business_metrics
    (metric_code, metric_name, category, description, formula_expression, unit, time_field, source_tables, dimension_fields, synonyms)
VALUES
    ('output_qty', '产量', '生产', '指定统计范围内的实际生产数量', 'SUM(actual_qty)', '件', 'production_date', '["fwwb.fact_process_output"]', '["line_id","process_name","production_date"]', '["生产量","实际产量"]'),
    ('process_yield_rate', '工序良率', '质量', '工序合格数量占实际生产数量的比例', 'SUM(qualified_qty) * 100.0 / NULLIF(SUM(actual_qty), 0)', '%', 'production_date', '["fwwb.fact_process_output"]', '["line_id","process_name","production_date"]', '["良率","合格率","良品率"]'),
    ('defect_rate', '不良率', '质量', '不良数量占检验数量的比例', 'SUM(defect_qty) * 100.0 / NULLIF(SUM(inspected_qty), 0)', '%', 'inspection_date', '["fwwb.fact_quality_inspection"]', '["product_name","process_name","inspection_date"]', '["缺陷率","次品率"]'),
    ('downtime_minutes', '设备停机时长', '设备', '统计周期内设备停机分钟数', 'SUM(downtime_minutes)', '分钟', 'started_at', '["fwwb.fact_equipment_downtime"]', '["equipment_name","started_at"]', '["停机时间","设备停机"]'),
    ('inventory_gap', '安全库存缺口', '库存', '安全库存高于当前库存的缺口数量', 'GREATEST(safety_qty - current_qty, 0)', '件', 'record_date', '["fwwb.fact_inventory"]', '["product_name","record_date"]', '["库存缺口","缺货量"]');
END IF;
END $$;

DO $$
BEGIN
IF NOT EXISTS (SELECT 1 FROM fwwb.business_rules WHERE rule_code = 'low_yield_warning') THEN
INSERT INTO fwwb.business_rules
    (rule_code, rule_name, category, rule_type, expression, description, priority)
VALUES
    ('low_yield_warning', '低良率预警', '质量', 'threshold', 'process_yield_rate < 95', '工序良率低于95%时触发预警', 10),
    ('high_defect_warning', '高不良率预警', '质量', 'threshold', 'defect_rate > 5', '产品或工序不良率超过5%时触发预警', 10),
    ('long_downtime_warning', '长时间停机预警', '设备', 'threshold', 'downtime_minutes > 120', '单台设备累计停机超过120分钟时触发预警', 20),
    ('inventory_replenishment', '库存补货规则', '库存', 'threshold', 'current_qty < safety_qty', '当前库存低于安全库存时建议补货', 10);
END IF;
END $$;

DO $$
BEGIN
IF NOT EXISTS (SELECT 1 FROM fwwb.analysis_topics WHERE topic_code = 'production_analysis') THEN
INSERT INTO fwwb.analysis_topics
    (topic_code, topic_name, description, object_codes, metric_codes, example_questions)
VALUES
    ('production_analysis', '生产分析', '分析产量、工单完成情况和产线趋势', '["production_line","process","production_order"]', '["output_qty"]', '["统计每条产线最近7天的产量趋势","分析本月各工序产量"]'),
    ('quality_analysis', '质量分析', '分析工序良率、产品不良率和缺陷类型', '["product","process","quality_inspection"]', '["process_yield_rate","defect_rate"]', '["分析各工序本月良率","找出最近一个月不良数量最高的产品"]'),
    ('equipment_analysis', '设备分析', '分析设备停机、故障和运行效率', '["equipment"]', '["downtime_minutes"]', '["统计各设备本周停机时间","分析设备停机时间和不良率是否相关"]'),
    ('inventory_analysis', '库存分析', '分析当前库存和安全库存缺口', '["product","inventory"]', '["inventory_gap"]', '["找出低于安全库存的产品"]');
END IF;
END $$;

GRANT SELECT, INSERT, UPDATE, DELETE ON
    fwwb.business_objects,
    fwwb.business_metrics,
    fwwb.business_rules,
    fwwb.analysis_topics
TO zbw_fwwb, zst_fwwb, hzm_fwwb, hhy_fwwb, sky_fwwb;

GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA fwwb
TO zbw_fwwb, zst_fwwb, hzm_fwwb, hhy_fwwb, sky_fwwb;
