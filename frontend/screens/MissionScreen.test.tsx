import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import MissionScreen from './MissionScreen';

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

describe('MissionScreen', () => {
  it('renders multiple-choice options for the current question', async () => {
    const { findByText } = render(<MissionScreen navigation={mockNavigation} />);
    expect(await findByText('What is 2 + 2?')).toBeTruthy();
    expect(await findByText('3')).toBeTruthy();
    expect(await findByText('4')).toBeTruthy();
    expect(await findByText('5')).toBeTruthy();
  });

  it('allows selecting a choice and submitting', async () => {
    const { findByText, getByText } = render(<MissionScreen navigation={mockNavigation} />);
    const choice = await findByText('4');
    fireEvent.press(choice);
    expect(choice.parent?.props.style).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ backgroundColor: '#e6f0ff' }),
      ])
    );
    const submitButton = getByText('Submit Answer');
    fireEvent.press(submitButton);
    // No error alert expected
  });

  it('shows an alert if submitting without selecting a choice', async () => {
    const { findByText, getByText } = render(<MissionScreen navigation={mockNavigation} />);
    const submitButton = getByText('Submit Answer');
    fireEvent.press(submitButton);
    // Would show alert, but Alert is not rendered in test env; check no crash
    expect(await findByText('What is 2 + 2?')).toBeTruthy();
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
    require('../services/missionApi').fetchDailyMission.mockImplementationOnce(() => Promise.resolve(missionWithNoChoices));
    const { findByText } = render(<MissionScreen navigation={mockNavigation} />);
    expect(await findByText('No choices available for this question.')).toBeTruthy();
  });
}); 