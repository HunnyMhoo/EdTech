import { API_BASE_URL } from '@/config';

// Enhanced answer interface with attempt tracking
export interface AnswerAttempt {
  answer: any;
  is_correct: boolean;
  timestamp: string;
}

export interface Answer {
  question_id: string;
  current_answer: any;
  is_correct: boolean;
  attempt_count: number;
  attempts_history: AnswerAttempt[];
  feedback_shown: boolean;
  is_complete: boolean;
  max_retries: number;
}

// Legacy answer interface for backward compatibility
export interface LegacyAnswer {
  question_id: string;
  answer: any;
  feedback_shown?: boolean;
}

// Define the Question type based on the backend model
export interface Question {
  question_id: string;
  question_text: string;
  skill_area: string;
  difficulty_level: number;
  choices?: Array<{ id: string; text: string }>;
  feedback_th: string;
  correct_answer_id: string;
}

// Updated Mission interface to match DailyMissionDocument from backend
export interface Mission {
  user_id: string;
  date: string;
  questions: Question[];
  status: 'not_started' | 'in_progress' | 'complete' | 'archived';
  current_question_index: number;
  answers: Answer[];
  created_at: string;
  updated_at: string;
}

// Feedback response interface
export interface FeedbackResponse {
  already_complete: boolean;
  is_correct: boolean;
  correct_answer: string;
  explanation: string;
  attempt_count: number;
  max_retries?: number;
  can_retry?: boolean;
  question_complete?: boolean;
}

// API response wrapper
export interface ApiResponse<T = any> {
  status: string;
  message: string;
  data?: T;
  feedback?: FeedbackResponse;
}

// Payload for updating mission progress
export interface MissionProgressUpdatePayload {
  current_question_index: number;
  answers: LegacyAnswer[]; // Keep legacy format for backward compatibility
  status?: 'not_started' | 'in_progress' | 'complete' | 'archived';
}

// Payload for submitting answers
export interface AnswerSubmissionPayload {
  question_id: string;
  answer: any;
}

export const fetchDailyMission = async (userId: string): Promise<Mission> => {
  const response = await fetch(`${API_BASE_URL}/missions/daily/${userId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: ApiResponse<Mission> = await response.json();
  return responseData.data!;
};

export const updateMissionProgressApi = async (
  userId: string,
  payload: MissionProgressUpdatePayload
): Promise<Mission> => {
  const response = await fetch(`${API_BASE_URL}/missions/daily/${userId}/progress`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: ApiResponse<Mission> = await response.json();
  return responseData.data!;
};

export const submitAnswerWithFeedback = async (
  userId: string,
  questionId: string,
  answer: any
): Promise<FeedbackResponse> => {
  const payload: AnswerSubmissionPayload = {
    question_id: questionId,
    answer: answer,
  };

  const response = await fetch(`${API_BASE_URL}/missions/daily/${userId}/submit-answer`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: ApiResponse = await response.json();
  return responseData.feedback!;
};

export const markFeedbackShown = async (
  userId: string,
  questionId: string
): Promise<{ mission_status: string }> => {
  const response = await fetch(`${API_BASE_URL}/missions/daily/${userId}/mark-feedback-shown`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question_id: questionId }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: any = await response.json();
  return { mission_status: responseData.mission_status || 'in_progress' };
};

export const retryQuestion = async (
  userId: string,
  questionId: string
): Promise<{ remaining_attempts: number }> => {
  const response = await fetch(`${API_BASE_URL}/missions/daily/${userId}/retry-question`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question_id: questionId }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: any = await response.json();
  return { remaining_attempts: responseData.remaining_attempts || 0 };
};

// --- Mocked Data (can be removed or kept for testing if backend is down) ---
// Example: To use mock data if API_BASE_URL is not reachable or for specific tests.
const MOCK_MODE = false; // Set to true to use mock data unconditionally

const getMockMission = async (): Promise<Mission> => {
    console.log('Using mocked mission data (getMockMission)');
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      user_id: 'mock_user_123',
      date: new Date().toISOString().split('T')[0],
      questions: ['q1_mock', 'q2_mock', 'q3_mock', 'q4_mock', 'q5_mock'].map((id, index) => ({
        question_id: id,
        question_text: `This is mock question ${index + 1}?`,
        skill_area: 'Mock',
        difficulty_level: 1,
        choices: [
            { id: `${id}_choice1`, text: 'Choice A' },
            { id: `${id}_choice2`, text: 'Choice B' },
        ],
        feedback_th: `นี่คือคำอธิบายจำลองสำหรับ ${id}`,
        correct_answer_id: `${id}_choice1`,
      })),
      status: 'not_started',
      current_question_index: 0,
      answers: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
};

// You could modify fetchDailyMission and updateMissionProgressApi to use MOCK_MODE
// For example:
// if (MOCK_MODE) return getMockMission();
// inside fetchDailyMission before the try block. 