-- UniCompass: Initial schema migration
-- Run this in your Supabase Dashboard -> SQL Editor -> New Query -> paste -> Run

-- 1. Universities config (referenced by other tables)
CREATE TABLE IF NOT EXISTS universities (
  key         TEXT PRIMARY KEY,
  full_name   TEXT NOT NULL,
  website     TEXT,
  color       TEXT,
  active      BOOLEAN DEFAULT true
);

-- 2. Student profiles
CREATE TABLE IF NOT EXISTS profiles (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alevel      JSONB,
  ccas        TEXT[],
  course      TEXT,
  citizenship TEXT,
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- 3. Debate sessions
CREATE TABLE IF NOT EXISTS debates (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id  UUID REFERENCES profiles(id),
  agents      TEXT[],
  status      TEXT DEFAULT 'pending',
  summary     TEXT,
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- 4. Individual messages in a debate
CREATE TABLE IF NOT EXISTS messages (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  debate_id   UUID REFERENCES debates(id),
  agent       TEXT,
  content     TEXT,
  round       TEXT,
  sources     TEXT[],
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- 5. Scholarships
CREATE TABLE IF NOT EXISTS scholarships (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  university  TEXT REFERENCES universities(key),
  name        TEXT,
  bond_years  INT,
  citizenship TEXT[],
  url         TEXT,
  notes       TEXT
);

-- 6. Seed university data
INSERT INTO universities (key, full_name, website, color) VALUES
  ('NUS',  'National University of Singapore',            'nus.edu.sg',            '#003D7C'),
  ('NTU',  'Nanyang Technological University',            'ntu.edu.sg',            '#C4122F'),
  ('SMU',  'Singapore Management University',             'smu.edu.sg',            '#0033A0'),
  ('SUSS', 'Singapore University of Social Sciences',     'suss.edu.sg',           '#5B2D8E'),
  ('SUTD', 'Singapore University of Technology & Design', 'sutd.edu.sg',           '#E4002B'),
  ('SIT',  'Singapore Institute of Technology',           'singaporetech.edu.sg',  '#0073CE')
ON CONFLICT (key) DO NOTHING;

-- 7. Enable RLS but allow service key full access
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE debates ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE universities ENABLE ROW LEVEL SECURITY;
ALTER TABLE scholarships ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all" ON profiles FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON debates FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON messages FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON universities FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON scholarships FOR ALL USING (true) WITH CHECK (true);
