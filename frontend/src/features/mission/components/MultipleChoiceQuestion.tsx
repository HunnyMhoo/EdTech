import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  TextInput,
  StyleSheet,
} from 'react-native';
import { Question } from '../api/missionApi';

interface MultipleChoiceQuestionProps {
  question: Question;
  questionIndex: number;
  onAnswerChange: (answer: string) => void;
  currentAnswer?: string;
  disabled?: boolean;
  showFeedback?: boolean;
  isCorrect?: boolean;
}

export const MultipleChoiceQuestion: React.FC<MultipleChoiceQuestionProps> = ({
  question,
  questionIndex,
  onAnswerChange,
  currentAnswer = '',
  disabled = false,
  showFeedback = false,
  isCorrect = false,
}) => {
  const [selectedChoice, setSelectedChoice] = useState<string>(currentAnswer);
  const [textAnswer, setTextAnswer] = useState<string>(currentAnswer);

  // Update local state when currentAnswer prop changes (e.g., on retry)
  useEffect(() => {
    if (question.choices && question.choices.length > 0) {
      setSelectedChoice(currentAnswer);
    } else {
      setTextAnswer(currentAnswer);
    }
  }, [currentAnswer, question.choices]);

  const isMultipleChoice = question.choices && question.choices.length > 0;

  const handleChoiceSelect = (choiceId: string) => {
    if (disabled) return;
    
    setSelectedChoice(choiceId);
    onAnswerChange(choiceId);
  };

  const handleTextChange = (text: string) => {
    if (disabled) return;
    
    setTextAnswer(text);
    onAnswerChange(text);
  };

  const getChoiceStyle = (choiceId: string) => {
    const isSelected = selectedChoice === choiceId;
    let baseStyle = styles.choice;

    if (showFeedback) {
      if (choiceId === question.correct_answer_id) {
        return [styles.choice, styles.correctChoice];
      } else if (isSelected && !isCorrect) {
        return [styles.choice, styles.incorrectChoice];
      }
    } else if (isSelected) {
      return [styles.choice, styles.selectedChoice];
    }

    if (disabled) {
      return [styles.choice, styles.disabledChoice];
    }

    return styles.choice;
  };

  const getChoiceTextStyle = (choiceId: string) => {
    const isSelected = selectedChoice === choiceId;

    if (showFeedback) {
      if (choiceId === question.correct_answer_id) {
        return [styles.choiceText, styles.correctChoiceText];
      } else if (isSelected && !isCorrect) {
        return [styles.choiceText, styles.incorrectChoiceText];
      }
    } else if (isSelected) {
      return [styles.choiceText, styles.selectedChoiceText];
    }

    return styles.choiceText;
  };

  return (
    <View style={styles.container}>
      <View style={styles.questionHeader}>
        <Text style={styles.questionNumber}>Question {questionIndex + 1}</Text>
        <Text style={styles.questionText}>{question.question_text}</Text>
      </View>

      <View style={styles.answerSection}>
        {isMultipleChoice ? (
          <View style={styles.choicesContainer}>
            {question.choices!.map((choice) => (
              <TouchableOpacity
                key={choice.id}
                style={getChoiceStyle(choice.id)}
                onPress={() => handleChoiceSelect(choice.id)}
                disabled={disabled}
                activeOpacity={disabled ? 1 : 0.7}
              >
                <View style={styles.choiceContent}>
                  <View style={styles.radioButton}>
                    {selectedChoice === choice.id && (
                      <View style={styles.radioButtonInner} />
                    )}
                  </View>
                  <Text style={getChoiceTextStyle(choice.id)}>
                    {choice.text}
                  </Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        ) : (
          <View style={styles.textInputContainer}>
            <TextInput
              style={[
                styles.textInput,
                showFeedback && (isCorrect ? styles.correctInput : styles.incorrectInput),
                disabled && styles.disabledInput,
              ]}
              value={textAnswer}
              onChangeText={handleTextChange}
              placeholder="Type your answer here..."
              editable={!disabled}
              multiline
              numberOfLines={3}
              textAlignVertical="top"
            />
          </View>
        )}
      </View>

      {showFeedback && (
        <View style={styles.feedbackIndicator}>
          <Text style={[
            styles.feedbackText,
            isCorrect ? styles.correctFeedbackText : styles.incorrectFeedbackText
          ]}>
            {isCorrect ? '✓ Correct!' : '✗ Incorrect'}
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 20,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  questionHeader: {
    marginBottom: 20,
  },
  questionNumber: {
    fontSize: 14,
    fontWeight: '600',
    color: '#007AFF',
    marginBottom: 8,
  },
  questionText: {
    fontSize: 18,
    lineHeight: 24,
    color: '#333',
    fontWeight: '500',
  },
  answerSection: {
    marginBottom: 16,
  },
  choicesContainer: {
    gap: 12,
  },
  choice: {
    borderWidth: 2,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    padding: 16,
    backgroundColor: '#FAFAFA',
  },
  selectedChoice: {
    borderColor: '#007AFF',
    backgroundColor: '#F0F8FF',
  },
  correctChoice: {
    borderColor: '#4CAF50',
    backgroundColor: '#E8F5E8',
  },
  incorrectChoice: {
    borderColor: '#F44336',
    backgroundColor: '#FFEBEE',
  },
  disabledChoice: {
    opacity: 0.6,
  },
  choiceContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  radioButton: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#CCC',
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  radioButtonInner: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#007AFF',
  },
  choiceText: {
    fontSize: 16,
    color: '#333',
    flex: 1,
  },
  selectedChoiceText: {
    color: '#007AFF',
    fontWeight: '500',
  },
  correctChoiceText: {
    color: '#4CAF50',
    fontWeight: '600',
  },
  incorrectChoiceText: {
    color: '#F44336',
    fontWeight: '500',
  },
  textInputContainer: {
    marginTop: 8,
  },
  textInput: {
    borderWidth: 2,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    padding: 16,
    fontSize: 16,
    backgroundColor: '#FAFAFA',
    minHeight: 80,
  },
  correctInput: {
    borderColor: '#4CAF50',
    backgroundColor: '#E8F5E8',
  },
  incorrectInput: {
    borderColor: '#F44336',
    backgroundColor: '#FFEBEE',
  },
  disabledInput: {
    opacity: 0.6,
    backgroundColor: '#F5F5F5',
  },
  feedbackIndicator: {
    alignItems: 'center',
    marginTop: 8,
  },
  feedbackText: {
    fontSize: 16,
    fontWeight: '600',
  },
  correctFeedbackText: {
    color: '#4CAF50',
  },
  incorrectFeedbackText: {
    color: '#F44336',
  },
});

export default MultipleChoiceQuestion; 