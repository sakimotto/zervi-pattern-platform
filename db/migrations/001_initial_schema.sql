-- Initial schema for Zervi Pattern Platform

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    make TEXT,
    model TEXT,
    year_start INT,
    year_end INT,
    market TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS patterns (
    id SERIAL PRIMARY KEY,
    vehicle_id INT REFERENCES vehicles(id),
    name TEXT NOT NULL,
    row_position TEXT,
    seat_position TEXT,
    file_path TEXT,
    dxf_hash TEXT UNIQUE,
    status TEXT DEFAULT 'draft',
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS panels (
    id SERIAL PRIMARY KEY,
    pattern_id INT REFERENCES patterns(id) ON DELETE CASCADE,
    panel_number TEXT,
    part_number TEXT,
    material_code TEXT,
    geometry JSONB NOT NULL,
    area_mm2 NUMERIC,
    cut_length_mm NUMERIC,
    bounding_box JSONB,
    centroid JSONB,
    embedding VECTOR(1536),
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS labels (
    id SERIAL PRIMARY KEY,
    pattern_id INT REFERENCES patterns(id) ON DELETE CASCADE,
    panel_id INT REFERENCES panels(id) ON DELETE SET NULL,
    text TEXT,
    layer TEXT,
    label_type TEXT,
    position JSONB,
    height NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS holes (
    id SERIAL PRIMARY KEY,
    panel_id INT REFERENCES panels(id) ON DELETE CASCADE,
    center_x NUMERIC,
    center_y NUMERIC,
    radius_mm NUMERIC,
    diameter_mm NUMERIC,
    classification TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS blocks (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    geometry JSONB NOT NULL,
    embedding VECTOR(1536),
    usage_count INT DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bom_lines (
    id SERIAL PRIMARY KEY,
    pattern_id INT REFERENCES patterns(id) ON DELETE CASCADE,
    panel_id INT REFERENCES panels(id) ON DELETE SET NULL,
    material_code TEXT,
    description TEXT,
    quantity NUMERIC,
    unit TEXT,
    cost_local NUMERIC,
    odoo_product_id INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS operations (
    id SERIAL PRIMARY KEY,
    pattern_id INT REFERENCES patterns(id) ON DELETE CASCADE,
    panel_id INT REFERENCES panels(id) ON DELETE SET NULL,
    sequence INT,
    operation_type TEXT,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS work_instructions (
    id SERIAL PRIMARY KEY,
    operation_id INT REFERENCES operations(id) ON DELETE CASCADE,
    step_number INT,
    title TEXT,
    description TEXT,
    media_urls TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS knowledge (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    embedding VECTOR(1536),
    source TEXT,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id SERIAL PRIMARY KEY,
    agent_name TEXT NOT NULL,
    task TEXT NOT NULL,
    input JSONB,
    output JSONB,
    confidence NUMERIC,
    human_approved BOOLEAN DEFAULT NULL,
    approved_by TEXT,
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_panels_embedding ON panels USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_blocks_embedding ON blocks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON knowledge USING ivfflat (embedding vector_cosine_ops);
