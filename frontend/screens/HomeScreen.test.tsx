import React from 'react';
import { render, waitFor } from '@testing-library/react-native';
import HomeScreen from './HomeScreen';
import { useMission } from '../hooks/useMission';

jest.mock('../hooks/useMission');

const mockMission = {
  user_id: 'user1',
  date: '2024-01-01',
  status: 'not_started',
  questions: [
    {
      question_id: 'q1',
      question_text: 'What is 2+2?',
      skill_area: 'math',
      difficulty_level: 1,
      choices: [],
      correct_answer_id: 'a',
      feedback_th: 'feedback',
    },
  ],
  current_question_index: 0,
  answers: [],
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const mockedUseMission = useMission as jest.Mock;

describe('HomeScreen', () => {
  beforeEach(() => {
    mockedUseMission.mockReturnValue({
      mission: mockMission,
      isLoading: false,
      error: null,
    });
  });

  it('renders correctly and shows mission', async () => {
    const { getByText } = render(<HomeScreen />);

    await waitFor(() => {
      expect(getByText('What is 2+2?')).toBeTruthy();
    });
  });
}); 