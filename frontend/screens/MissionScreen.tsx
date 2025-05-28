import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, Button, TextInput, StyleSheet, Alert, ScrollView } from 'react-native';
import { fetchDailyMission, updateMissionProgressApi, Mission, Answer, MissionProgressUpdatePayload } from '../services/missionApi';

// Assuming navigation props are passed if this screen is part of a navigation stack
// For simplicity, not strictly typed here, but in a real app, you'd use @react-navigation/native types
type MissionScreenProps = {
  navigation?: any; 
  route?: any; 
};

// A placeholder for actual question content. In a real app, this might come from a store or be part of the Mission object.
const getQuestionText = (questionId: string, index: number): string => {
  return `Question ${index + 1}: ${questionId}`; // Example: "Question 1: q1_mock"
};

const MissionScreen: React.FC<MissionScreenProps> = ({ navigation }) => {
  const [mission, setMission] = useState<Mission | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [userAnswers, setUserAnswers] = useState<Answer[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadMission = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const fetchedMission = await fetchDailyMission();
      setMission(fetchedMission);
      setCurrentQuestionIndex(fetchedMission.current_question_index || 0);
      setUserAnswers(fetchedMission.answers || []);
      // Set currentAnswer if resuming on a question that already has an answer
      const resumedAnswer = fetchedMission.answers.find(
        ans => ans.question_id === fetchedMission.question_ids[fetchedMission.current_question_index]
      );
      setCurrentAnswer(resumedAnswer?.answer as string || '');
    } catch (e: any) {
      setError(e.message || 'Failed to load mission.');
      Alert.alert('Error', e.message || 'Failed to load mission.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMission();
  }, [loadMission]);

  const handleSaveProgress = useCallback(async (updatedIndex?: number, updatedAnswers?: Answer[]) => {
    if (!mission) return;

    const indexToSave = updatedIndex !== undefined ? updatedIndex : currentQuestionIndex;
    const answersToSave = updatedAnswers !== undefined ? updatedAnswers : userAnswers;
    
    // Determine mission status
    let newStatus = mission.status;
    if (answersToSave.length > 0 && answersToSave.length < mission.question_ids.length) {
        newStatus = 'in_progress';
    } else if (answersToSave.length === mission.question_ids.length) {
        // This simple check assumes all questions answered means complete.
        // More complex logic might be needed (e.g. all answers must be non-empty)
        newStatus = 'complete';
    }


    const payload: MissionProgressUpdatePayload = {
      current_question_index: indexToSave,
      answers: answersToSave,
      status: newStatus,
    };

    try {
      const updatedMission = await updateMissionProgressApi(payload);
      setMission(updatedMission); // Update local mission state with response from backend
      console.log('Progress saved successfully');
    } catch (e: any) {
      console.error('Failed to save progress:', e);
      Alert.alert('Save Error', 'Could not save your progress. Please try again.');
    }
  }, [mission, currentQuestionIndex, userAnswers]);

  const handleAnswerSubmit = () => {
    if (!mission || currentAnswer.trim() === '') {
      Alert.alert('No Answer', 'Please provide an answer.');
      return;
    }

    const questionId = mission.question_ids[currentQuestionIndex];
    const newAnswers = userAnswers.filter(ans => ans.question_id !== questionId);
    newAnswers.push({ question_id: questionId, answer: currentAnswer });
    setUserAnswers(newAnswers);
    
    // Save progress after submitting an answer
    handleSaveProgress(currentQuestionIndex, newAnswers);

    // Optionally move to next question or show completion
    if (currentQuestionIndex < mission.question_ids.length - 1) {
      // setCurrentQuestionIndex(currentQuestionIndex + 1); // Moving to next is handled by handleNext
      // setCurrentAnswer(''); // Clear for next question
    } else {
      Alert.alert('Mission Progress', 'You have answered the last question!');
      // Potentially navigate away or show a summary
    }
  };

  const handleNextQuestion = () => {
    if (mission && currentQuestionIndex < mission.question_ids.length - 1) {
      const nextIndex = currentQuestionIndex + 1;
      setCurrentQuestionIndex(nextIndex);
      const nextQuestionId = mission.question_ids[nextIndex];
      const existingAnswer = userAnswers.find(ans => ans.question_id === nextQuestionId);
      setCurrentAnswer(existingAnswer?.answer as string || '');
      handleSaveProgress(nextIndex, userAnswers); // Save progress on explicit navigation
    }
  };

  const handlePreviousQuestion = () => {
    if (mission && currentQuestionIndex > 0) {
      const prevIndex = currentQuestionIndex - 1;
      setCurrentQuestionIndex(prevIndex);
      const prevQuestionId = mission.question_ids[prevIndex];
      const existingAnswer = userAnswers.find(ans => ans.question_id === prevQuestionId);
      setCurrentAnswer(existingAnswer?.answer as string || '');
      handleSaveProgress(prevIndex, userAnswers); // Save progress on explicit navigation
    }
  };

  if (isLoading) {
    return <View style={styles.container}><Text>Loading mission...</Text></View>;
  }

  if (error) {
    return <View style={styles.container}><Text>Error: {error}</Text><Button title="Retry" onPress={loadMission} /></View>;
  }

  if (!mission) {
    return <View style={styles.container}><Text>No mission data available.</Text></View>;
  }

  const currentQuestionId = mission.question_ids[currentQuestionIndex];
  const questionText = getQuestionText(currentQuestionId, currentQuestionIndex);

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Daily Mission</Text>
      <Text style={styles.date}>Date: {new Date(mission.date).toLocaleDateString()}</Text>
      <Text style={styles.status}>Status: {mission.status}</Text>
      
      <View style={styles.questionContainer}>
        <Text style={styles.questionText}>{questionText}</Text>
        <TextInput
          style={styles.input}
          placeholder="Your answer"
          value={currentAnswer}
          onChangeText={setCurrentAnswer}
          multiline
        />
        <Button title="Submit Answer" onPress={handleAnswerSubmit} />
      </View>

      <View style={styles.navigationButtons}>
        <Button title="Previous" onPress={handlePreviousQuestion} disabled={currentQuestionIndex === 0} />
        <Button title="Next" onPress={handleNextQuestion} disabled={currentQuestionIndex === mission.question_ids.length - 1} />
      </View>
      
      <Text style={styles.progressText}>
        Question {currentQuestionIndex + 1} of {mission.question_ids.length}
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
  questionText: {
    fontSize: 18,
    marginBottom: 10,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 10,
    borderRadius: 5,
    marginBottom: 10,
    minHeight: 60,
    textAlignVertical: 'top',
  },
  navigationButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '80%',
    marginBottom: 20,
  },
  progressText: {
    fontSize: 14,
    color: 'gray',
    marginBottom: 10,
  },
  debugText: {
    fontSize: 12,
    color: '#aaa',
    marginTop: 5,
  }
});

export default MissionScreen; 