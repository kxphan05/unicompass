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
  round: number;
  sources: string[];
}

export interface University {
  key: string;
  fullName: string;
  color: string;
}
