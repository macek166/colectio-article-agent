-- Migration: Create content table with JSONB columns
-- Description: Stores generated article content with research sources and metadata

CREATE TABLE IF NOT EXISTS content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID REFERENCES topics(id) ON DELETE CASCADE,
    topic_title VARCHAR(200) NOT NULL,
    category VARCHAR(20) NOT NULL CHECK (category IN ('pokemon', 'hockey', 'soccer')),
    draft TEXT,
    final_content TEXT NOT NULL,
    research_sources JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('draft', 'completed', 'published', 'archived'))
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_content_topic_id ON content(topic_id);
CREATE INDEX IF NOT EXISTS idx_content_category ON content(category);
CREATE INDEX IF NOT EXISTS idx_content_status ON content(status);

-- Create GIN indexes for JSONB columns for efficient querying
CREATE INDEX IF NOT EXISTS idx_content_research_sources ON content USING GIN (research_sources);
CREATE INDEX IF NOT EXISTS idx_content_metadata ON content USING GIN (metadata);

-- Add comment for documentation
COMMENT ON TABLE content IS 'Stores generated article content with research sources and metadata';
COMMENT ON COLUMN content.research_sources IS 'JSONB array of research source URLs';
COMMENT ON COLUMN content.metadata IS 'JSONB object containing SEO keywords, timestamps, and other metadata';
