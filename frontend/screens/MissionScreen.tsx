import React, { useState, useEffect } from 'react';
import { View, Text, Button, StyleSheet, ScrollView, Alert } from 'react-native';
import Toast from 'react-native-toast-message';
import { useMission } from '@hooks/useMission';
import QuestionDisplay from '@components/QuestionDisplay';
import ChoiceList from '@components/ChoiceList';
import MissionNav from '@components/MissionNav';
import type { Answer, Question } from '@services/missionApi';

// Extract the choice type from the Question interface for local use
type Choice = NonNullable<Question['choices']>[number];

// Assuming navigation props are passed if this screen is part of a navigation stack
// For simplicity, not strictly typed here, but in a real app, you'd use @react-navigation/native types
type MissionScreenProps = {
  navigation?: any;
};

const MissionScreen: React.FC<MissionScreenProps> = ({ navigation }) => {
  const {
    mission,
    currentQuestion,
    currentQuestionIndex,
    isLoading,
    error,
    userAnswers,
    loadMission,
    submitAnswer,
    goToQuestion,
  } = useMission();

  const [selectedChoiceId, setSelectedChoiceId] = useState<string>('');

  useEffect(() => {
    // When question changes, check for a previous answer and set the selected choice
    if (currentQuestion) {
      const existingAnswer = userAnswers.find((ans: Answer) => ans.question_id === currentQuestion.question_id);
      setSelectedChoiceId(existingAnswer?.answer || '');
    }
  }, [currentQuestion, userAnswers]);

  const handleAnswerSubmit = () => {
    if (!currentQuestion || !selectedChoiceId) {
      Alert.alert('No Selection', 'Please select an option.');
      return;
    }

    const isCorrect = selectedChoiceId === currentQuestion.correct_answer_id;
    const correctAnswerChoice = currentQuestion.choices?.find(c => c.id === currentQuestion.correct_answer_id);

    Toast.show({
      type: isCorrect ? 'success' : 'error',
      text1: isCorrect ? 'Correct!' : 'Incorrect',
      text2: isCorrect 
        ? currentQuestion.feedback_th
        : `The correct answer is: ${correctAnswerChoice?.text || 'N/A'}. ${currentQuestion.feedback_th}`,
      visibilityTime: 4000,
      autoHide: true,
      onHide: () => {
        if (currentQuestion && selectedChoiceId) {
          submitAnswer(currentQuestion.question_id, selectedChoiceId);
        }
      }
    });
  };

  if (isLoading) {
    return <View style={styles.container}><Text>Loading mission...</Text></View>;
  }

  if (error) {
    return <View style={styles.container}><Text>Error: {error}</Text><Button title="Retry" onPress={loadMission} /></View>;
  }

  if (!mission || !currentQuestion) {
    return <View style={styles.container}><Text>No mission data available.</Text></View>;
  }

  const isAnswered = userAnswers.some((ans: Answer) => ans.question_id === currentQuestion.question_id);

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Daily Mission</Text>
      <Text style={styles.date}>Date: {new Date(mission.date).toLocaleDateString()}</Text>
      <Text style={styles.status}>Status: {mission.status}</Text>

      <View style={styles.questionContainer}>
        <QuestionDisplay
          questionIndex={currentQuestionIndex}
          questionText={currentQuestion.question_text}
        />
        {currentQuestion.choices && currentQuestion.choices.length > 0 ? (
          <ChoiceList
            choices={currentQuestion.choices}
            selectedChoiceId={selectedChoiceId}
            onSelectChoice={setSelectedChoiceId}
            isAnswered={isAnswered}
            correctAnswerId={currentQuestion.correct_answer_id}
          />
        ) : (
          <Text style={{ color: 'red' }}>No choices available for this question.</Text>
        )}
        <Button title="Submit Answer" onPress={handleAnswerSubmit} disabled={isAnswered || !selectedChoiceId} />
      </View>

      <MissionNav
        onPrevious={() => goToQuestion(currentQuestionIndex - 1)}
        onNext={() => goToQuestion(currentQuestionIndex + 1)}
        isPreviousDisabled={currentQuestionIndex === 0}
        isNextDisabled={currentQuestionIndex === mission.questions.length - 1}
      />

      <Text style={styles.progressText}>
        Question {currentQuestionIndex + 1} of {mission.questions.length}
      </Text>
      <Text style={styles.debugText}>User ID: {mission.user_id}</Text>
      <Text style={styles.debugText}>Answers Logged: {JSON.stringify(userAnswers)}</Text>

      {navigation && <Button title="Back to Home (Example)" onPress={() => navigation.goBack()} />}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  date: {
    fontSize: 16,
    marginBottom: 5,
  },
  status: {
    fontSize: 16,
    marginBottom: 20,
    textTransform: 'capitalize',
  },
  questionContainer: {
    width: '100%',
    marginBottom: 20,
    padding: 15,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
  },
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
  navigationButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    marginBottom: 20,
  },
  progressText: {
    marginTop: 10,
    fontSize: 14,
    color: '#666',
  },
  debugText: {
    marginTop: 5,
    fontSize: 10,
    color: '#999',
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

export default MissionScreen; 