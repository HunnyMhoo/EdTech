import React from 'react';
import { create } from 'react-test-renderer';
import { TouchableOpacity } from 'react-native';
import { MistakeCard } from '../../../src/features/review/components/MistakeCard';
import { ReviewMistakeItem } from '../../../src/features/review/api/reviewMistakesApi';

describe('MistakeCard', () => {
  const mockMistake: ReviewMistakeItem = {
    question_id: 'Q1',
    question_text: 'What is 2+2?',
    skill_area: 'Mathematics',
    difficulty_level: 1,
    choices: [
      { id: 'A', text: '3' },
      { id: 'B', text: '4' },
      { id: 'C', text: '5' }
    ],
    user_answer_id: 'A',
    user_answer_text: '3',
    correct_answer_id: 'B',
    correct_answer_text: '4',
    explanation: 'The correct answer is 4.',
    mission_date: '2024-01-15',
    mission_completion_date: '2024-01-15T08:30:00Z',
    attempt_count: 2
  };

  const mockOnPress = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders correctly without crashing', () => {
    const component = create(
      <MistakeCard mistake={mockMistake} onPress={mockOnPress} />
    );
    expect(component).toBeTruthy();
  });

  it('calls onPress when TouchableOpacity is pressed', () => {
    const component = create(
      <MistakeCard mistake={mockMistake} onPress={mockOnPress} />
    );
    
    const touchable = component.root.findByType(TouchableOpacity);
    touchable.props.onPress();
    
    expect(mockOnPress).toHaveBeenCalledTimes(1);
  });

  it('renders with showDate false', () => {
    const component = create(
      <MistakeCard 
        mistake={mockMistake} 
        onPress={mockOnPress} 
        showDate={false} 
      />
    );
    expect(component).toBeTruthy();
  });

  it('renders with compact mode', () => {
    const component = create(
      <MistakeCard 
        mistake={mockMistake} 
        onPress={mockOnPress} 
        compact={true} 
      />
    );
    expect(component).toBeTruthy();
  });

  it('handles different difficulty levels', () => {
    const testCases = [1, 2, 3, 4];
    
    testCases.forEach((level) => {
      const mistakeWithLevel = { ...mockMistake, difficulty_level: level };
      const component = create(
        <MistakeCard mistake={mistakeWithLevel} onPress={mockOnPress} />
      );
      expect(component).toBeTruthy();
    });
  });

  it('handles single attempt count', () => {
    const singleAttemptMistake = { ...mockMistake, attempt_count: 1 };
    const component = create(
      <MistakeCard mistake={singleAttemptMistake} onPress={mockOnPress} />
    );
    expect(component).toBeTruthy();
  });

  it('matches snapshot', () => {
    const component = create(
      <MistakeCard mistake={mockMistake} onPress={mockOnPress} />
    );
    expect(component.toJSON()).toMatchSnapshot();
  });
}); 