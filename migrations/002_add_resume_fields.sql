-- Add resume fields to profiles table
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS resume_text TEXT DEFAULT '';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS resume_path TEXT DEFAULT '';

-- Create storage bucket for resumes (run via Supabase dashboard if this fails)
INSERT INTO storage.buckets (id, name, public)
VALUES ('resumes', 'resumes', false)
ON CONFLICT (id) DO NOTHING;
