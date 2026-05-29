-- Solana Marketing Suite Database Schema
-- PostgreSQL 15+

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_address VARCHAR(44) UNIQUE NOT NULL,
    discord_id VARCHAR(32),
    twitter_handle VARCHAR(32),
    telegram_id VARCHAR(32),
    email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_wallet ON users(wallet_address);
CREATE INDEX idx_users_discord ON users(discord_id);
CREATE INDEX idx_users_twitter ON users(twitter_handle);
CREATE INDEX idx_users_telegram ON users(telegram_id);

-- Airdrops table
CREATE TABLE IF NOT EXISTS airdrops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_name VARCHAR(255) NOT NULL,
    description TEXT,
    total_amount DECIMAL(20, 9) NOT NULL,
    distributed_amount DECIMAL(20, 9) DEFAULT 0,
    recipient_count INTEGER DEFAULT 0,
    claimed_count INTEGER DEFAULT 0,
    status VARCHAR(32) DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    config JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_airdrops_status ON airdrops(status);
CREATE INDEX idx_airdrops_created ON airdrops(created_at DESC);

-- Airdrop recipients
CREATE TABLE IF NOT EXISTS airdrop_recipients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airdrop_id UUID REFERENCES airdrops(id) ON DELETE CASCADE,
    wallet_address VARCHAR(44) NOT NULL,
    amount DECIMAL(20, 9) NOT NULL,
    tier VARCHAR(32),
    status VARCHAR(32) DEFAULT 'pending',
    claimed_at TIMESTAMP WITH TIME ZONE,
    transaction_signature VARCHAR(88),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(airdrop_id, wallet_address)
);

CREATE INDEX idx_recipients_airdrop ON airdrop_recipients(airdrop_id);
CREATE INDEX idx_recipients_wallet ON airdrop_recipients(wallet_address);
CREATE INDEX idx_recipients_status ON airdrop_recipients(status);

-- Quests table
CREATE TABLE IF NOT EXISTS quests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(32) DEFAULT 'standard',
    status VARCHAR(32) DEFAULT 'active',
    total_reward DECIMAL(20, 9) NOT NULL,
    participant_count INTEGER DEFAULT 0,
    completion_count INTEGER DEFAULT 0,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    prerequisites UUID[],
    config JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quests_status ON quests(status);
CREATE INDEX idx_quests_type ON quests(type);

-- Quest tasks
CREATE TABLE IF NOT EXISTS quest_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quest_id UUID REFERENCES quests(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(32) NOT NULL,
    reward DECIMAL(20, 9) NOT NULL,
    order_index INTEGER NOT NULL,
    prerequisite_task_id UUID REFERENCES quest_tasks(id),
    verification_method VARCHAR(32) DEFAULT 'auto',
    verification_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_quest ON quest_tasks(quest_id);

-- Quest progress
CREATE TABLE IF NOT EXISTS quest_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quest_id UUID REFERENCES quests(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(32) DEFAULT 'in_progress',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    earned_reward DECIMAL(20, 9) DEFAULT 0,
    completed_tasks UUID[],
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(quest_id, user_id)
);

CREATE INDEX idx_progress_quest ON quest_progress(quest_id);
CREATE INDEX idx_progress_user ON quest_progress(user_id);
CREATE INDEX idx_progress_status ON quest_progress(status);

-- NFT Collections
CREATE TABLE IF NOT EXISTS nft_collections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    symbol VARCHAR(32) NOT NULL,
    description TEXT,
    mint_address VARCHAR(44),
    total_supply INTEGER NOT NULL,
    minted_count INTEGER DEFAULT 0,
    price DECIMAL(20, 9),
    royalty_percentage DECIMAL(5, 2) DEFAULT 5.00,
    status VARCHAR(32) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_collections_mint ON nft_collections(mint_address);
CREATE INDEX idx_collections_status ON nft_collections(status);

-- NFT Tiers
CREATE TABLE IF NOT EXISTS nft_tiers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    collection_id UUID REFERENCES nft_collections(id) ON DELETE CASCADE,
    name VARCHAR(32) NOT NULL,
    supply INTEGER NOT NULL,
    minted INTEGER DEFAULT 0,
    price DECIMAL(20, 9),
    required_tokens DECIMAL(20, 9),
    benefits JSONB DEFAULT '[]'::jsonb,
    image_url VARCHAR(255),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tiers_collection ON nft_tiers(collection_id);

-- NFT Holdings
CREATE TABLE IF NOT EXISTS nft_holdings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    collection_id UUID REFERENCES nft_collections(id) ON DELETE CASCADE,
    tier_id UUID REFERENCES nft_tiers(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    nft_mint_address VARCHAR(44) UNIQUE,
    purchase_price DECIMAL(20, 9),
    purchased_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_holdings_user ON nft_holdings(user_id);
CREATE INDEX idx_holdings_mint ON nft_holdings(nft_mint_address);

-- Influencers
CREATE TABLE IF NOT EXISTS influencers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    handle VARCHAR(255) NOT NULL,
    platform VARCHAR(32) NOT NULL,
    followers INTEGER,
    engagement_rate DECIMAL(5, 2),
    categories VARCHAR(32)[],
    rating DECIMAL(3, 2) DEFAULT 0.00,
    past_campaigns INTEGER DEFAULT 0,
    price_tweet DECIMAL(20, 2),
    price_thread DECIMAL(20, 2),
    price_review DECIMAL(20, 2),
    contact_email VARCHAR(255),
    metadata JSONB DEFAULT '{}'::jsonb,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(handle, platform)
);

CREATE INDEX idx_influencers_platform ON influencers(platform);
CREATE INDEX idx_influencers_rating ON influencers(rating DESC);

-- Influencer Campaigns
CREATE TABLE IF NOT EXISTS influencer_campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    budget DECIMAL(20, 2) NOT NULL,
    spent DECIMAL(20, 2) DEFAULT 0,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(32) DEFAULT 'planning',
    metrics JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_campaigns_status ON influencer_campaigns(status);

-- Campaign Influencer Assignments
CREATE TABLE IF NOT EXISTS campaign_influencers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID REFERENCES influencer_campaigns(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    deal_type VARCHAR(32) NOT NULL,
    price DECIMAL(20, 2) NOT NULL,
    deliverables JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(32) DEFAULT 'pending',
    impressions INTEGER DEFAULT 0,
    engagement INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    roi DECIMAL(10, 2),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id, influencer_id)
);

CREATE INDEX idx_assignments_campaign ON campaign_influencers(campaign_id);
CREATE INDEX idx_assignments_influencer ON campaign_influencers(influencer_id);

-- Analytics Events
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(64) NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id VARCHAR(64),
    properties JSONB DEFAULT '{}'::jsonb,
    source VARCHAR(32),
    campaign_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_type ON analytics_events(event_type);
CREATE INDEX idx_events_user ON analytics_events(user_id);
CREATE INDEX idx_events_created ON analytics_events(created_at DESC);
CREATE INDEX idx_events_session ON analytics_events(session_id);

-- Daily Metrics (aggregated)
CREATE TABLE IF NOT EXISTS daily_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL UNIQUE,
    total_users INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    total_transactions INTEGER DEFAULT 0,
    total_volume DECIMAL(30, 9) DEFAULT 0,
    avg_transaction_size DECIMAL(20, 9),
    twitter_followers INTEGER,
    discord_members INTEGER,
    telegram_members INTEGER,
    token_price DECIMAL(20, 9),
    market_cap DECIMAL(30, 9),
    metrics JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_date ON daily_metrics(date DESC);

-- Leaderboard
CREATE TABLE IF NOT EXISTS leaderboard (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(32) NOT NULL,
    points DECIMAL(20, 2) DEFAULT 0,
    rank INTEGER,
    period VARCHAR(32) DEFAULT 'all_time',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, category, period)
);

CREATE INDEX idx_leaderboard_category ON leaderboard(category, period);
CREATE INDEX idx_leaderboard_points ON leaderboard(points DESC);

-- Audit Log
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action VARCHAR(64) NOT NULL,
    entity_type VARCHAR(64),
    entity_id UUID,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_created ON audit_log(created_at DESC);

-- Functions

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_airdrops_updated_at BEFORE UPDATE ON airdrops
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quests_updated_at BEFORE UPDATE ON quests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_collections_updated_at BEFORE UPDATE ON nft_collections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_influencers_updated_at BEFORE UPDATE ON influencers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON influencer_campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views

-- Active users view
CREATE OR REPLACE VIEW active_users AS
SELECT 
    u.*,
    COUNT(DISTINCT qp.id) as quests_completed,
    SUM(qp.earned_reward) as total_earned,
    COUNT(DISTINCT nh.id) as nfts_owned
FROM users u
LEFT JOIN quest_progress qp ON u.id = qp.user_id AND qp.status = 'completed'
LEFT JOIN nft_holdings nh ON u.id = nh.user_id
WHERE u.last_active_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY u.id;

-- Campaign performance view
CREATE OR REPLACE VIEW campaign_performance AS
SELECT 
    ic.*,
    i.handle,
    i.platform,
    i.followers,
    i.engagement_rate,
    CASE 
        WHEN ci.spend > 0 THEN (ci.conversions::DECIMAL / ci.spend) * 100
        ELSE 0 
    END as conversion_rate,
    ci.roi
FROM influencer_campaigns ic
JOIN campaign_influencers ci ON ic.id = ci.campaign_id
JOIN influencers i ON ci.influencer_id = i.id
WHERE ic.status = 'active';

-- Initialize default data
INSERT INTO daily_metrics (date, metrics)
VALUES (CURRENT_DATE, '{}'::jsonb)
ON CONFLICT (date) DO NOTHING;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO solana_marketing;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO solana_marketing;