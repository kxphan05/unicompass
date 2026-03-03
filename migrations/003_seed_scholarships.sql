-- UniCompass: Seed scholarship data for all 6 universities
-- Run this in Supabase Dashboard -> SQL Editor -> New Query -> paste -> Run

-- NUS Scholarships
INSERT INTO scholarships (university, name, bond_years, citizenship, url, notes) VALUES
  ('NUS', 'NUS Global Merit Scholarship', 0, ARRAY['Singaporean', 'PR', 'International'], 'https://www.nus.edu.sg/oam/scholarships', 'Covers tuition, living allowance, overseas programme support. No bond.'),
  ('NUS', 'NUS Merit Scholarship', 0, ARRAY['Singaporean', 'PR'], 'https://www.nus.edu.sg/oam/scholarships', 'Covers tuition fees for duration of programme. No bond.'),
  ('NUS', 'NUS Sports Scholarship', 0, ARRAY['Singaporean', 'PR', 'International'], 'https://www.nus.edu.sg/oam/scholarships', 'For outstanding athletes. Covers tuition and living allowance.'),
  ('NUS', 'NUS Performing & Visual Arts Scholarship', 0, ARRAY['Singaporean', 'PR', 'International'], 'https://www.nus.edu.sg/oam/scholarships', 'For students with exceptional arts talent.'),
  ('NUS', 'NUS Science & Technology Undergraduate Scholarship', 3, ARRAY['Singaporean'], 'https://www.nus.edu.sg/oam/scholarships', 'For Science/Engineering. 3-year bond with sponsoring agency.'),
  ('NUS', 'NUS Community Leadership Scholarship', 0, ARRAY['Singaporean', 'PR'], 'https://www.nus.edu.sg/oam/scholarships', 'For demonstrated community leadership. No bond.'),
  ('NUS', 'NUS AI Talent Scholarship', 0, ARRAY['Singaporean', 'PR', 'International'], 'https://www.nus.edu.sg/oam/scholarships', 'For students with strong aptitude in AI/ML. Covers tuition, living allowance, and AI research immersion opportunities.')
ON CONFLICT DO NOTHING;

-- NTU Scholarships
INSERT INTO scholarships (university, name, bond_years, citizenship, url, notes) VALUES
  ('NTU', 'Nanyang Scholarship', 0, ARRAY['Singaporean', 'PR', 'International'], 'https://www.ntu.edu.sg/admissions/undergraduate/scholarships', 'Premier scholarship. Full tuition, living allowance, overseas immersion. No bond.'),
  ('NTU', 'NTU University Scholarship', 0, ARRAY['Singaporean', 'PR'], 'https://www.ntu.edu.sg/admissions/undergraduate/scholarships', 'Covers tuition fees. No bond.'),
  ('NTU', 'College Scholarship', 0, ARRAY['Singaporean', 'PR'], 'https://www.ntu.edu.sg/admissions/undergraduate/scholarships', 'College-level merit scholarship covering tuition.'),
  ('NTU', 'CN Yang Scholars Programme', 0, ARRAY['Singaporean', 'PR', 'International'], 'https://www.ntu.edu.sg/admissions/undergraduate/scholarships', 'For Science/Engineering students with strong research aptitude.'),
  ('NTU', 'Renaissance Engineering Programme Scholarship', 0, ARRAY['Singaporean', 'PR', 'International'], 'https://www.ntu.edu.sg/admissions/undergraduate/scholarships', 'Double-degree engineering + business. Full scholarship with global exposure.'),
  ('NTU', 'NTU Sports Scholarship', 0, ARRAY['Singaporean', 'PR', 'International'], 'https://www.ntu.edu.sg/admissions/undergraduate/scholarships', 'For national/varsity athletes. Tuition and allowance.'),
  ('NTU', 'NTU TAISP (Turing AI Scholars Programme)', 0, ARRAY['Singaporean', 'PR', 'International'], 'https://www.ntu.edu.sg/admissions/undergraduate/scholarships', 'For students passionate about AI research. Full tuition, living allowance, and research mentorship with NTU AI faculty.')
ON CONFLICT DO NOTHING;

-- SMU Scholarships
INSERT INTO scholarships (university, name, bond_years, citizenship, url, notes) VALUES
  ('SMU', 'Lee Kong Chian Scholars Programme', 0, ARRAY['Singaporean', 'PR', 'International'], 'https://admissions.smu.edu.sg/scholarships-financial-aid', 'Premier scholarship. Full tuition, overseas programme, mentorship. No bond.'),
  ('SMU', 'SMU Global Impact Scholarship', 0, ARRAY['Singaporean', 'PR', 'International'], 'https://admissions.smu.edu.sg/scholarships-financial-aid', 'Full tuition, overseas exchange, community impact project. No bond.'),
  ('SMU', 'SMU Merit Scholarship', 0, ARRAY['Singaporean', 'PR'], 'https://admissions.smu.edu.sg/scholarships-financial-aid', 'Covers full or partial tuition based on merit.'),
  ('SMU', 'Yip Pin Xiu Scholarship', 0, ARRAY['Singaporean'], 'https://admissions.smu.edu.sg/scholarships-financial-aid', 'For students who have overcome adversity. Full tuition.'),
  ('SMU', 'SMU Entrepreneurship Scholarship', 0, ARRAY['Singaporean', 'PR'], 'https://admissions.smu.edu.sg/scholarships-financial-aid', 'For aspiring entrepreneurs with demonstrated initiative.')
ON CONFLICT DO NOTHING;

-- SUSS Scholarships
INSERT INTO scholarships (university, name, bond_years, citizenship, url, notes) VALUES
  ('SUSS', 'SUSS Scholarship', 0, ARRAY['Singaporean'], 'https://www.suss.edu.sg/part-time-undergraduate/scholarships-and-financial-aid', 'Merit-based. Covers tuition fees for full-time undergrad programmes.'),
  ('SUSS', 'SUSS Community Leadership Scholarship', 0, ARRAY['Singaporean'], 'https://www.suss.edu.sg/part-time-undergraduate/scholarships-and-financial-aid', 'For students with strong community service record.'),
  ('SUSS', 'SUSS Work-Study Scholarship', 0, ARRAY['Singaporean'], 'https://www.suss.edu.sg/part-time-undergraduate/scholarships-and-financial-aid', 'Combined scholarship for students in work-study programmes.')
ON CONFLICT DO NOTHING;

-- SUTD Scholarships
INSERT INTO scholarships (university, name, bond_years, citizenship, url, notes) VALUES
  ('SUTD', 'SUTD Global Distinguished Scholarship', 0, ARRAY['Singaporean', 'PR', 'International'], 'https://www.sutd.edu.sg/admissions/undergraduate/scholarships', 'Full tuition, living allowance, overseas programme. No bond.'),
  ('SUTD', 'SUTD Merit Scholarship', 0, ARRAY['Singaporean', 'PR'], 'https://www.sutd.edu.sg/admissions/undergraduate/scholarships', 'Covers tuition fees. For students with excellent academic records.'),
  ('SUTD', 'SUTD Community Leadership Scholarship', 0, ARRAY['Singaporean', 'PR'], 'https://www.sutd.edu.sg/admissions/undergraduate/scholarships', 'For student leaders with community impact.'),
  ('SUTD', 'SUTD-MIT Design Scholarship', 0, ARRAY['Singaporean', 'PR', 'International'], 'https://www.sutd.edu.sg/admissions/undergraduate/scholarships', 'For design-oriented students. Includes MIT exchange opportunity.')
ON CONFLICT DO NOTHING;

-- SIT Scholarships
INSERT INTO scholarships (university, name, bond_years, citizenship, url, notes) VALUES
  ('SIT', 'SIT Scholarship', 3, ARRAY['Singaporean'], 'https://www.singaporetech.edu.sg/admissions/scholarships-awards', 'Covers tuition and provides living allowance. 3-year bond.'),
  ('SIT', 'SIT-University Partner Scholarship', 0, ARRAY['Singaporean', 'PR'], 'https://www.singaporetech.edu.sg/admissions/scholarships-awards', 'Joint scholarship with overseas university partners.'),
  ('SIT', 'SkillsFuture Study Award', 0, ARRAY['Singaporean'], 'https://www.singaporetech.edu.sg/admissions/scholarships-awards', 'Government-supported award for applied degree programmes.'),
  ('SIT', 'SIT Industry Scholarship', 3, ARRAY['Singaporean'], 'https://www.singaporetech.edu.sg/admissions/scholarships-awards', 'Sponsored by industry partners. Includes guaranteed employment.')
ON CONFLICT DO NOTHING;
