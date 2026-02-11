-- Migration: Create topics table with UNIQUE constraint on title
-- Description: Stores all generated topics with category and status tracking

CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL UNIQUE,
    category VARCHAR(20) NOT NULL CHECK (category IN ('pokemon', 'hockey', 'soccer')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed'))
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_topics_title ON topics(title);
CREATE INDEX IF NOT EXISTS idx_topics_category ON topics(category);
CREATE INDEX IF NOT EXISTS idx_topics_status ON topics(status);

-- Add comment for documentation
COMMENT ON TABLE topics IS 'Stores all generated topics for trading card articles';
COMMENT ON COLUMN topics.title IS 'Unique topic title used for deduplication';
COMMENT ON COLUMN topics.category IS 'Trading card category: pokemon, hockey, or soccer';
COMMENT ON COLUMN topics.status IS 'Processing status: pending, in_progress, completed, or failed';
