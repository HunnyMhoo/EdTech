import React from 'react';
import { Modal, View, Text, StyleSheet, TouchableOpacity } from 'react-native';

interface FeedbackModalProps {
  isVisible: boolean;
  isCorrect: boolean;
  correctAnswer: string;
  explanation: string;
  onDismiss: () => void;
}

const FeedbackModal: React.FC<FeedbackModalProps> = ({
  isVisible,
  isCorrect,
  correctAnswer,
  explanation,
  onDismiss,
}) => {
  return (
    <Modal
      animationType="slide"
      transparent={true}
      visible={isVisible}
      onRequestClose={onDismiss}
    >
      <View style={styles.centeredView}>
        <View style={styles.modalView}>
          <Text style={[styles.title, { color: isCorrect ? 'green' : 'red' }]}>
            {isCorrect ? 'Correct!' : 'Incorrect'}
          </Text>
          <Text style={styles.text}>The correct answer is: {correctAnswer}</Text>
          <Text style={styles.text}>{explanation}</Text>
          <TouchableOpacity
            style={[styles.button, styles.buttonClose]}
            onPress={onDismiss}
          >
            <Text style={styles.textStyle}>Continue</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  centeredView: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalView: {
    margin: 20,
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 35,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  title: {
    marginBottom: 15,
    textAlign: 'center',
    fontSize: 24,
    fontWeight: 'bold',
  },
  text: {
    marginBottom: 15,
    textAlign: 'center',
  },
  button: {
    borderRadius: 20,
    padding: 10,
    elevation: 2,
    minWidth: 100,
  },
  buttonClose: {
    backgroundColor: '#2196F3',
  },
  textStyle: {
    color: 'white',
    fontWeight: 'bold',
    textAlign: 'center',
  },
});

export default FeedbackModal; 