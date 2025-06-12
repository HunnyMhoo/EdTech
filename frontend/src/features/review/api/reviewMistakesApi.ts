import { API_BASE_URL } from '@/config';

// API response wrapper (matching existing pattern)
export interface ApiResponse<T = any> {
  status: string;
  message?: string;
  data?: T;
}

// Types for Review Mistakes API
export interface ReviewMistakeItem {
  question_id: string;
  question_text: string;
  skill_area: string;
  difficulty_level: number;
  choices: Array<{
    id: string;
    text: string;
  }>;
  user_answer_id: string;
  user_answer_text: string;
  correct_answer_id: string;
  correct_answer_text: string;
  explanation: string;
  mission_date: string;  // ISO date string
  mission_completion_date: string;  // ISO datetime string
  attempt_count: number;
}

export interface PaginationInfo {
  current_page: number;
  total_pages: number;
  total_items: number;
  items_per_page: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface ReviewMistakesResponse {
  mistakes: ReviewMistakeItem[];
  pagination: PaginationInfo;
  total_mistakes: number;
}

export interface GroupedReviewMistakesResponse {
  grouped_mistakes: Record<string, ReviewMistakeItem[]>;
  pagination: PaginationInfo;
  total_mistakes: number;
  group_counts: Record<string, number>;
}

export interface ReviewStatsResponse {
  total_mistakes: number;
  skill_areas_count: number;
  skill_areas: string[];
  difficulty_breakdown: Record<number, number>;
}

// API parameters
export interface ReviewMistakesParams {
  page?: number;
  items_per_page?: number;
  skill_area?: string;
}

export interface GroupedReviewMistakesParams {
  group_by: 'date' | 'topic';
  page?: number;
  items_per_page?: number;
  skill_area?: string;
}

// API functions following the pattern of missionApi.ts
export const getReviewMistakes = async (
  userId: string,
  params: ReviewMistakesParams = {}
): Promise<ReviewMistakesResponse> => {
  const queryParams = new URLSearchParams();
  
  if (params.page) queryParams.append('page', params.page.toString());
  if (params.items_per_page) queryParams.append('items_per_page', params.items_per_page.toString());
  if (params.skill_area) queryParams.append('skill_area', params.skill_area);

  const url = queryParams.toString() 
    ? `${API_BASE_URL}/review-mistakes/${userId}?${queryParams}` 
    : `${API_BASE_URL}/review-mistakes/${userId}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: ApiResponse<ReviewMistakesResponse> = await response.json();
  return responseData.data!;
};

export const getGroupedReviewMistakes = async (
  userId: string,
  params: GroupedReviewMistakesParams
): Promise<GroupedReviewMistakesResponse> => {
  const queryParams = new URLSearchParams();
  
  queryParams.append('group_by', params.group_by);
  if (params.page) queryParams.append('page', params.page.toString());
  if (params.items_per_page) queryParams.append('items_per_page', params.items_per_page.toString());
  if (params.skill_area) queryParams.append('skill_area', params.skill_area);

  const url = `${API_BASE_URL}/review-mistakes/${userId}/grouped?${queryParams}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: ApiResponse<GroupedReviewMistakesResponse> = await response.json();
  return responseData.data!;
};

export const getAvailableSkillAreas = async (userId: string): Promise<string[]> => {
  const url = `${API_BASE_URL}/review-mistakes/${userId}/skill-areas`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: ApiResponse<string[]> = await response.json();
  return responseData.data!;
};

export const getReviewStats = async (userId: string): Promise<ReviewStatsResponse> => {
  const url = `${API_BASE_URL}/review-mistakes/${userId}/stats`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData: ApiResponse<ReviewStatsResponse> = await response.json();
  return responseData.data!;
}; 