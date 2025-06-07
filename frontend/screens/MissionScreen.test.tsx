import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import MissionScreen from './MissionScreen';
import { useMission } from '@hooks/useMission';
import Toast from 'react-native-toast-message';

// Mock the toast library
jest.mock('react-native-toast-message', () => ({
  show: jest.fn(),
  hide: jest.fn(),
}));

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
      correct_answer_id: 'b',
      feedback_th: 'Correct, 2+2 is 4',
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
      correct_answer_id: 'b',
      feedback_th: 'Correct, Paris is the capital of France',
    },
  ],
  status: 'not_started',
  current_question_index: 0,
  answers: [],
  created_at: '2024-06-01T00:00:00Z',
  updated_at: '2024-06-01T00:00:00Z',
};

jest.mock('../hooks/useMission');

const mockedUseMission = useMission as jest.Mock;
const mockSubmitAnswer = jest.fn();

describe('MissionScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockedUseMission.mockReturnValue({
      mission: mockMission,
      currentQuestion: mockMission.questions[0],
      currentQuestionIndex: 0,
      isLoading: false,
      error: null,
      userAnswers: [],
      loadMission: jest.fn(),
      submitAnswer: mockSubmitAnswer,
      goToQuestion: jest.fn(),
    });
  });

  it('renders multiple-choice options for the current question', async () => {
    const { findByText } = render(<MissionScreen navigation={mockNavigation} />);
    expect(await findByText('What is 2 + 2?')).toBeTruthy();
    expect(await findByText('3')).toBeTruthy();
    expect(await findByText('4')).toBeTruthy();
    expect(await findByText('5')).toBeTruthy();
  });

  it('shows success toast for correct answer and calls submitAnswer on hide', async () => {
    const { getByText } = render(<MissionScreen navigation={mockNavigation} />);
    
    fireEvent.press(getByText('4'));
    fireEvent.press(getByText('Submit Answer'));

    expect(Toast.show).toHaveBeenCalledWith({
      type: 'success',
      text1: 'Correct!',
      text2: 'Correct, 2+2 is 4',
      visibilityTime: 4000,
      autoHide: true,
      onHide: expect.any(Function),
    });
    
    // Manually call the onHide function to simulate the toast hiding
    const onHideCallback = (Toast.show as jest.Mock).mock.calls[0][0].onHide;
    onHideCallback();
    
    expect(mockSubmitAnswer).toHaveBeenCalledWith('q1', 'b');
  });

  it('shows error toast for incorrect answer and calls submitAnswer on hide', async () => {
    const { getByText } = render(<MissionScreen navigation={mockNavigation} />);
    
    fireEvent.press(getByText('3'));
    fireEvent.press(getByText('Submit Answer'));

    expect(Toast.show).toHaveBeenCalledWith({
      type: 'error',
      text1: 'Incorrect',
      text2: 'The correct answer is: 4. Correct, 2+2 is 4',
      visibilityTime: 4000,
      autoHide: true,
      onHide: expect.any(Function),
    });

    const onHideCallback = (Toast.show as jest.Mock).mock.calls[0][0].onHide;
    onHideCallback();

    expect(mockSubmitAnswer).toHaveBeenCalledWith('q1', 'a');
  });

  it('disables submit button until an answer is selected', () => {
    const { getByText } = render(<MissionScreen navigation={mockNavigation} />);
    const submitButton = getByText('Submit Answer');
    expect(submitButton.props.accessibilityState.disabled).toBe(true);

    fireEvent.press(getByText('4'));
    expect(submitButton.props.accessibilityState.disabled).toBe(false);
  });
}); 