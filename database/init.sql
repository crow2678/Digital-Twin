-- Digital Twin Database Initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Voice transcriptions table
CREATE TABLE IF NOT EXISTS voice_transcriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    text TEXT NOT NULL,
    confidence FLOAT,
    language VARCHAR(10),
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    meeting_id UUID,
    chunk_id VARCHAR(255)
);

-- Collaboration insights table
CREATE TABLE IF NOT EXISTS collaboration_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    transcription_id UUID REFERENCES voice_transcriptions(id),
    action_items JSONB,
    decisions JSONB,
    questions JSONB,
    priority_score FLOAT,
    sentiment VARCHAR(50),
    stakeholders JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Meeting sessions table
CREATE TABLE IF NOT EXISTS meeting_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(255),
    participants JSONB,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    total_transcriptions INTEGER DEFAULT 0,
    effectiveness_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suggested actions table
CREATE TABLE IF NOT EXISTS suggested_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    insight_id UUID REFERENCES collaboration_insights(id),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    confidence FLOAT,
    status VARCHAR(50) DEFAULT 'pending',
    context JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_voice_transcriptions_user_id ON voice_transcriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_voice_transcriptions_created_at ON voice_transcriptions(created_at);
CREATE INDEX IF NOT EXISTS idx_voice_transcriptions_meeting_id ON voice_transcriptions(meeting_id);
CREATE INDEX IF NOT EXISTS idx_collaboration_insights_user_id ON collaboration_insights(user_id);
CREATE INDEX IF NOT EXISTS idx_suggested_actions_status ON suggested_actions(status);
CREATE INDEX IF NOT EXISTS idx_meeting_sessions_user_id ON meeting_sessions(user_id);

-- Insert default user for development
INSERT INTO users (email, name) VALUES ('dev@digitaltwin.com', 'Development User') 
ON CONFLICT (email) DO NOTHING;