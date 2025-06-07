import { renderHook, act } from '@testing-library/react-native';
import { useMission } from './useMission';

jest.mock('../services/missionApi', () => ({
  fetchDailyMission: jest.fn(),
  updateMissionProgressApi: jest.fn(),
}));

describe('useMission', () => {
  it('should be defined', () => {
    expect(useMission).toBeDefined();
  });

  // Add more tests here
}); 