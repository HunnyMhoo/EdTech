import React from 'react';
import { Text, StyleSheet } from 'react-native';

type QuestionDisplayProps = {
  questionIndex: number;
  questionText: string;
};

const QuestionDisplay: React.FC<QuestionDisplayProps> = ({ questionIndex, questionText }) => {
  return (
    <Text style={styles.questionText}>
      {`Question ${questionIndex + 1}: ${questionText}`}
    </Text>
  );
};

const styles = StyleSheet.create({
  questionText: {
    fontSize: 18,
    fontWeight: '500',
    marginBottom: 15,
  },
});

export default QuestionDisplay; 