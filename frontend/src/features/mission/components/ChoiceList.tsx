import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Question } from '../api/missionApi';

type Choice = NonNullable<Question['choices']>[number];

type ChoiceListProps = {
  choices: Choice[];
  selectedChoiceId: string;
  onSelectChoice: (id: string) => void;
  isAnswered: boolean;
  correctAnswerId?: string;
};

const ChoiceList: React.FC<ChoiceListProps> = ({
  choices,
  selectedChoiceId,
  onSelectChoice,
  isAnswered,
  correctAnswerId,
}) => {
  return (
    <View style={{ width: '100%' }}>
      {choices.map((choice: Choice) => (
        <TouchableOpacity
          key={choice.id}
          style={[
            styles.choiceButton,
            selectedChoiceId === choice.id && styles.choiceButtonSelected,
            isAnswered && choice.id === correctAnswerId && styles.correctChoice,
            isAnswered && selectedChoiceId === choice.id && selectedChoiceId !== correctAnswerId && styles.incorrectChoice,
          ]}
          onPress={() => !isAnswered && onSelectChoice(choice.id)}
          accessibilityRole="radio"
          accessibilityState={{ selected: selectedChoiceId === choice.id, disabled: isAnswered }}
          accessible={true}
          disabled={isAnswered}
        >
          <Text style={styles.choiceText}>{choice.text}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  choiceButton: {
    padding: 15,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 5,
    marginBottom: 10,
    width: '100%',
  },
  choiceButtonSelected: {
    backgroundColor: '#e0e0e0',
    borderColor: 'blue',
  },
  choiceText: {
    fontSize: 16,
  },
  correctChoice: {
    backgroundColor: 'lightgreen',
    borderColor: 'green',
  },
  incorrectChoice: {
    backgroundColor: 'lightcoral',
    borderColor: 'red',
  },
});

export default ChoiceList; 