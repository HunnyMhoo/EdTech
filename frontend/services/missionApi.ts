// Base URL for the API. Adjust if your backend runs elsewhere.
const API_BASE_URL = 'http://localhost:8000'; // Assuming backend runs on port 8000

// Interface for individual answers as stored in the backend
export interface Answer {
  question_id: string;
  answer: any; // Can be string, number, object, depending on question type
}

export interface Question {
  question_id: string; // Assuming this is the identifier for a question from the backend
  text: string;
  // Add other question-related fields if necessary (e.g., options for MCQs)
}

// Updated Mission interface to match DailyMissionDocument from backend
export interface Mission {
  user_id: string;
  date: string; // ISO date string (e.g., "2023-10-27")
  question_ids: string[]; // List of question_id strings
  status: 'not_started' | 'in_progress' | 'complete';
  current_question_index: number;
  answers: Answer[];
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
  // Questions might be fetched separately or embedded. For now, assuming question_ids are primary.
  // If questions are embedded, the type would be Question[] instead of string[] for question_ids
  // and the backend would need to populate them.
  // For this iteration, let's assume we get question_ids and might need a separate fetch for details, or they are simple enough.
}

// Generic API response wrapper to match backend's MissionResponse
interface ApiResponse<T> {
  status: string;
  data?: T;
  message?: string;
}

export const fetchDailyMission = async (): Promise<Mission> => {
  const endpoint = `${API_BASE_URL}/api/missions/today`;

  try {
    console.log(`Fetching daily mission from: ${endpoint}`);
    const response = await fetch(endpoint, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // Include Authorization header if/when auth is implemented
        // 'Authorization': `Bearer ${your_auth_token}`,
      },
    });

    if (!response.ok) {
      const errorBody = await response.text();
      console.error('API error:', response.status, errorBody);
      throw new Error(`Failed to fetch mission: ${response.status} - ${errorBody}`);
    }

    const result: ApiResponse<Mission> = await response.json();

    if (result.status === 'success' && result.data) {
      console.log('Successfully fetched daily mission:', result.data);
      return result.data;
    } else {
      console.error('API returned non-success status or no data:', result);
      throw new Error(result.message || 'Failed to retrieve mission data.');
    }
  } catch (error) {
    console.error('Error in fetchDailyMission:', error);
    if (error instanceof Error) {
      throw new Error(`Could not retrieve daily mission: ${error.message}`);
    }
    throw new Error('An unknown error occurred while fetching the daily mission.');
  }
};

// Payload for updating mission progress
export interface MissionProgressUpdatePayload {
  current_question_index: number;
  answers: Answer[];
  status?: 'not_started' | 'in_progress' | 'complete';
}

export const updateMissionProgressApi = async (
  payload: MissionProgressUpdatePayload
): Promise<Mission> => {
  const endpoint = `${API_BASE_URL}/api/missions/today/progress`;

  try {
    console.log(`Updating mission progress to: ${endpoint}`, payload);
    const response = await fetch(endpoint, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        // 'Authorization': `Bearer ${your_auth_token}`,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      console.error('API error while updating progress:', response.status, errorBody);
      throw new Error(`Failed to update mission progress: ${response.status} - ${errorBody}`);
    }

    const result: ApiResponse<Mission> = await response.json();

    if (result.status === 'success' && result.data) {
      console.log('Successfully updated mission progress:', result.data);
      return result.data;
    } else {
      console.error('API returned non-success status or no data on progress update:', result);
      throw new Error(result.message || 'Failed to update mission progress.');
    }
  } catch (error) {
    console.error('Error in updateMissionProgressApi:', error);
    if (error instanceof Error) {
      throw new Error(`Could not update mission progress: ${error.message}`);
    }
    throw new Error('An unknown error occurred while updating mission progress.');
  }
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
      question_ids: ['q1_mock', 'q2_mock', 'q3_mock', 'q4_mock', 'q5_mock'],
      // For mock purposes, we might need to provide full Question objects if MissionScreen expects them directly.
      // However, the Mission interface defined above uses question_ids: string[], implying details might be looked up elsewhere or are simple.
      // Let's assume question_ids are sufficient and MissionScreen will map them to text if needed from a local source for mock.
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