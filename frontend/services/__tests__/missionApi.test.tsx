import { fetchDailyMission, Mission } from '../missionApi';

// fetch is globally available and mocked by jest-fetch-mock
declare var fetch: jest.Mock;

const mockSuccessfulResponse = (data: any) => {
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ status: 'success', data }),
  } as Response);
};

const mockFailedResponse = (status: number, statusText: string = 'Error') => {
  fetch.mockResolvedValueOnce({
    ok: false,
    status,
    statusText,
    text: async () => statusText,
    json: async () => ({ status: 'error', message: statusText }),
  } as Response);
};

const mockNetworkError = () => {
  fetch.mockRejectedValueOnce(new TypeError('Network failed'));
};

describe('fetchDailyMission', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('returns mock mission data when API is mocked in implementation', async () => {
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

    const mission = await fetchDailyMission();
    expect(mission).toBeDefined();
    expect(mission.user_id).toBeDefined();
    expect(Array.isArray(mission.questions)).toBe(true);
    expect(fetch).toHaveBeenCalled();
  });

  test('throws an error if the network response is not ok', async () => {
    mockFailedResponse(500, 'Internal Server Error');

    await expect(fetchDailyMission()).rejects.toThrow(
      'Could not retrieve daily mission: Failed to fetch mission: 500 - Internal Server Error'
    );
    expect(fetch).toHaveBeenCalled();
  });

  test('throws an error if there is a network failure', async () => {
    mockNetworkError();

    await expect(fetchDailyMission()).rejects.toThrow(
      'Could not retrieve daily mission: Network failed'
    );
    expect(fetch).toHaveBeenCalled();
  });
}); 