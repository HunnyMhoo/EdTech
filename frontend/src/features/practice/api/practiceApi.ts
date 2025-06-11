import { Question } from '../../mission/api/missionApi';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Types for practice API
export interface PracticeTopic {
  name: string;
  question_count: number;
  available: boolean;
}

export interface PracticeAnswer {
  question_id: string;
  user_answer: any;
  is_correct: boolean;
  answered_at: string;
}

export interface PracticeSession {
  session_id: string;
  user_id: string;
  topic: string;
  question_count: number;
  questions: Question[];
  answers: PracticeAnswer[];
  status: 'in_progress' | 'completed' | 'abandoned';
  correct_count: number;
  created_at: string;
  completed_at?: string;
}

export interface PracticeFeedback {
  already_answered: boolean;
  is_correct: boolean;
  correct_answer: string;
  explanation: string;
  user_answer: any;
  session_complete?: boolean;
  progress?: {
    answered: number;
    total: number;
  };
}

export interface PracticeSessionSummary {
  session_id: string;
  topic: string;
  status: string;
  created_at: string;
  completed_at?: string;
  score: {
    total_questions: number;
    answered_questions: number;
    correct_answers: number;
    accuracy: number;
    completion_rate: number;
  };
  questions_answered: number;
  total_questions: number;
  correct_answers: number;
}

export interface CreatePracticeSessionRequest {
  topic: string;
  question_count: number;
}

export interface ApiResponse<T> {
  status: string;
  message: string;
  data?: T;
}

// API Functions

export const fetchPracticeTopics = async (): Promise<PracticeTopic[]> => {
  const response = await fetch(`${API_BASE_URL}/practice/topics`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: ApiResponse<PracticeTopic[]> = await response.json();
  return responseData.data || [];
};

export const createPracticeSession = async (
  userId: string,
  request: CreatePracticeSessionRequest
): Promise<PracticeSession> => {
  const response = await fetch(`${API_BASE_URL}/practice/sessions?user_id=${userId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: ApiResponse<PracticeSession> = await response.json();
  return responseData.data!;
};

export const fetchPracticeSession = async (sessionId: string): Promise<PracticeSession> => {
  const response = await fetch(`${API_BASE_URL}/practice/sessions/${sessionId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: ApiResponse<PracticeSession> = await response.json();
  return responseData.data!;
};

export const submitPracticeAnswer = async (
  sessionId: string,
  questionId: string,
  answer: any
): Promise<PracticeFeedback> => {
  const response = await fetch(`${API_BASE_URL}/practice/sessions/${sessionId}/submit-answer`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question_id: questionId,
      answer: answer,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: any = await response.json();
  return responseData.feedback;
};

export const fetchPracticeSessionSummary = async (sessionId: string): Promise<PracticeSessionSummary> => {
  const response = await fetch(`${API_BASE_URL}/practice/sessions/${sessionId}/summary`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: ApiResponse<PracticeSessionSummary> = await response.json();
  return responseData.data!;
};

export const fetchUserPracticeSessions = async (
  userId: string,
  status?: string,
  limit?: number
): Promise<PracticeSession[]> => {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (limit) params.append('limit', limit.toString());

  const response = await fetch(`${API_BASE_URL}/practice/users/${userId}/sessions?${params}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: ApiResponse<PracticeSession[]> = await response.json();
  return responseData.data || [];
};

export const fetchUserPracticeStats = async (userId: string): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/practice/users/${userId}/stats`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: ApiResponse<any> = await response.json();
  return responseData.data || {};
}; 