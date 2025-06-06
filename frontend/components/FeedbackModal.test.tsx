import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import FeedbackModal from './FeedbackModal';

describe('FeedbackModal', () => {
  it('renders correctly when visible', () => {
    const { getByText } = render(
      <FeedbackModal
        isVisible={true}
        isCorrect={true}
        correctAnswer="A"
        explanation="This is the explanation"
        onDismiss={() => {}}
      />
    );
    expect(getByText('Correct!')).toBeTruthy();
    expect(getByText('The correct answer is: A')).toBeTruthy();
    expect(getByText('This is the explanation')).toBeTruthy();
  });

  it('shows incorrect message when isCorrect is false', () => {
    const { getByText } = render(
      <FeedbackModal
        isVisible={true}
        isCorrect={false}
        correctAnswer="A"
        explanation="This is the explanation"
        onDismiss={() => {}}
      />
    );
    expect(getByText('Incorrect')).toBeTruthy();
  });

  it('calls onDismiss when the continue button is pressed', () => {
    const onDismissMock = jest.fn();
    const { getByText } = render(
      <FeedbackModal
        isVisible={true}
        isCorrect={true}
        correctAnswer="A"
        explanation="This is the explanation"
        onDismiss={onDismissMock}
      />
    );
    fireEvent.press(getByText('Continue'));
    expect(onDismissMock).toHaveBeenCalled();
  });

  it('does not render when isVisible is false', () => {
    const { queryByText } = render(
      <FeedbackModal
        isVisible={false}
        isCorrect={true}
        correctAnswer="A"
        explanation="This is the explanation"
        onDismiss={() => {}}
      />
    );
    expect(queryByText('Correct!')).toBeNull();
  });
}); 