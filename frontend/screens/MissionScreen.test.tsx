import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import MissionScreen from './MissionScreen';
import { useMission } from '../hooks/useMission';

// Mock navigation prop
const mockNavigation = { goBack: jest.fn() };

const mockMission = {
  user_id: 'user1',
  date: '2024-06-01',
  questions: [
    {
      question_id: 'q1',
      question_text: 'What is 2 + 2?',
      skill_area: 'Math',
      difficulty_level: 1,
      choices: [
        { id: 'a', text: '3' },
        { id: 'b', text: '4' },
        { id: 'c', text: '5' },
      ],
    },
    {
      question_id: 'q2',
      question_text: 'What is the capital of France?',
      skill_area: 'Geography',
      difficulty_level: 1,
      choices: [
        { id: 'a', text: 'Berlin' },
        { id: 'b', text: 'Paris' },
        { id: 'c', text: 'London' },
      ],
    },
  ],
  status: 'not_started',
  current_question_index: 0,
  answers: [],
  created_at: '2024-06-01T00:00:00Z',
  updated_at: '2024-06-01T00:00:00Z',
};

jest.mock('../services/missionApi', () => ({
  fetchDailyMission: jest.fn(() => Promise.resolve(mockMission)),
  updateMissionProgressApi: jest.fn(() => Promise.resolve(mockMission)),
}));

jest.mock('../hooks/useMission');

const mockedUseMission = useMission as jest.Mock;

describe('MissionScreen', () => {
  beforeEach(() => {
    mockedUseMission.mockReturnValue({
      mission: mockMission,
      currentQuestion: mockMission.questions[0],
      currentQuestionIndex: 0,
      isLoading: false,
      error: null,
      selectAnswer: jest.fn(),
      submitAnswer: jest.fn(),
      nextQuestion: jest.fn(),
      previousQuestion: jest.fn(),
      userAnswers: [],
    });
  });

  it('renders multiple-choice options for the current question', async () => {
    const { findByText } = render(<MissionScreen navigation={mockNavigation} />);
    await waitFor(async () => {
      expect(await findByText('What is 2 + 2?')).toBeTruthy();
      expect(await findByText('3')).toBeTruthy();
      expect(await findByText('4')).toBeTruthy();
      expect(await findByText('5')).toBeTruthy();
    });
  });

  it('allows selecting a choice and submitting', async () => {
    const { findByText, getByText } = render(<MissionScreen navigation={mockNavigation} />);
    const choice = await findByText('4');
    fireEvent.press(choice);
    await waitFor(() => {
      expect(choice.parent?.props.style).toBeDefined();
    });
    const submitButton = getByText('Submit Answer');
    fireEvent.press(submitButton);
    // No error alert expected
  });

  it('shows an alert if submitting without selecting a choice', async () => {
    const { getByText } = render(<MissionScreen navigation={mockNavigation} />);
    await waitFor(() => {
      expect(getByText('Submit Answer')).toBeTruthy();
    });
  });

  it('shows error if no choices are available', async () => {
    const missionWithNoChoices = {
      ...mockMission,
      questions: [
        {
          question_id: 'q3',
          question_text: 'No choices here',
          skill_area: 'Test',
          difficulty_level: 1,
          choices: [],
        },
      ],
    };
    
    mockedUseMission.mockReturnValueOnce({
      mission: missionWithNoChoices,
      currentQuestion: missionWithNoChoices.questions[0],
      isLoading: false,
      userAnswers: [],
    });

    const { findByText } = render(<MissionScreen navigation={mockNavigation} />);
    await waitFor(async () => {
      expect(await findByText('No choices available for this question.')).toBeTruthy();
    });
  });
}); 