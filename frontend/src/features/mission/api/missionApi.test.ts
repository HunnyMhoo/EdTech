import { fetchDailyMission, Mission } from './missionApi';
import { API_BASE_URL } from '@/config';

// jest-fetch-mock is auto-enabled in jest.setup.js

const mockSuccessfulResponse = (data: Mission) => {
  fetch.mockResponseOnce(JSON.stringify({ status: 'success', data }));
};

const mockFailedResponse = (status: number, statusText: string = 'Error') => {
  fetch.mockResponseOnce(JSON.stringify({ status: 'error', message: statusText }), {
    status,
    statusText,
  });
};

const mockNetworkError = () => {
  fetch.mockRejectOnce(new TypeError('Network failed'));
};

describe('fetchDailyMission', () => {
  beforeEach(() => {
    fetch.resetMocks();
  });

  test('returns mission data when API call is successful', async () => {
    const mockMissionData: Mission = {
      user_id: 'user1',
      date: new Date().toISOString(),
      questions: [],
      status: 'not_started',
      current_question_index: 0,
      answers: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    mockSuccessfulResponse(mockMissionData);

    const mission = await fetchDailyMission('test_user_123');
    expect(mission).toEqual(mockMissionData);
    expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/missions/daily/test_user_123`, expect.any(Object));
  });

  test('throws an error if the network response is not ok', async () => {
    mockFailedResponse(500, 'Internal Server Error');

    await expect(fetchDailyMission('test_user_123')).rejects.toThrow(
      'Could not retrieve daily mission: Failed to fetch mission: 500 - {"status":"error","message":"Internal Server Error"}'
    );
    expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/missions/daily/test_user_123`, expect.any(Object));
  });

  test('throws an error if there is a network failure', async () => {
    mockNetworkError();

    await expect(fetchDailyMission('test_user_123')).rejects.toThrow(
      'Could not retrieve daily mission: Network failed'
    );
    expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/missions/daily/test_user_123`, expect.any(Object));
  });
}); 