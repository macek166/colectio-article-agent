-- Migration: Add source_url column to topics table
-- Enables linking specific source URLs to topics directly from Strategist phase
ALTER TABLE topics ADD COLUMN IF NOT EXISTS source_url TEXT;
