export interface StudentProfile {
  alevel: Record<string, string>;
  ccas: string[];
  course: string;
  citizenship: string;
  additional_comments: string;
}

export interface StudentProfileResponse extends StudentProfile {
  id: string;
  resume_text: string;
  resume_path: string;
}

export interface DebateCreate {
  profile_id: string;
  agents: string[];
}

export interface DebateSession {
  id: string;
  profile_id: string;
  agents: string[];
  status: string;
  summary: string | null;
  created_at: string;
}

export interface DebateEvent {
  agent: string;
  content: string;
  round: number | string;
  sources: string[];
}

export interface University {
  key: string;
  fullName: string;
  color: string;
}

export type ProsConsData = Record<string, { pros: string[]; cons: string[] }>;

export interface Scholarship {
  id: string;
  university: string;
  name: string;
  bond_years: number | null;
  citizenship: string[];
  url: string;
  notes: string;
  eligibility?: string;
  benefits?: string;
}
