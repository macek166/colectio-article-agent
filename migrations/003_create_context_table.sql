-- Migration: Create context table
-- Description: Stores agent conversation context and outputs for each topic

CREATE TABLE IF NOT EXISTS context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID REFERENCES topics(id) ON DELETE CASCADE,
    agent_name VARCHAR(50) NOT NULL,
    output JSONB NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_context_topic_id ON context(topic_id);
CREATE INDEX IF NOT EXISTS idx_context_agent_name ON context(agent_name);
CREATE INDEX IF NOT EXISTS idx_context_timestamp ON context(timestamp);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_context_output ON context USING GIN (output);
CREATE INDEX IF NOT EXISTS idx_context_metadata ON context USING GIN (metadata);

-- Add comment for documentation
COMMENT ON TABLE context IS 'Stores agent conversation context and outputs for debugging and analysis';
COMMENT ON COLUMN context.agent_name IS 'Name of the agent that produced this output (Strategist, Researcher, Writer, Editor, Archivist)';
COMMENT ON COLUMN context.output IS 'JSONB object containing the agent output data';
