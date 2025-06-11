import React, { useState, useEffect } from 'react';
import { View, Text, ActivityIndicator, Button, StyleSheet, TextInput } from 'react-native';
import { fetchDailyMission, Mission } from '../api/missionApi';
import { useAuth } from '../../auth/state/AuthContext';

const MissionScreen: React.FC = () => {
  const { userId, signOut } = useAuth();
  const [mission, setMission] = useState<Mission | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [currentQuestionDisplayIndex, setCurrentQuestionDisplayIndex] = useState<number>(0);
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({}); // { question_id: answer_text }

  const loadMission = async () => {
    if (!userId) return;

    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchDailyMission(userId);
      setMission(data);
      if (data.current_question_index > 0) {
        setCurrentQuestionDisplayIndex(data.current_question_index);
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
      console.error('Failed to load mission:', err);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    loadMission();
  }, [userId]);

  const handleNextQuestion = () => {
    if (mission && currentQuestionDisplayIndex < mission.questions.length - 1) {
      setCurrentQuestionDisplayIndex(currentQuestionDisplayIndex + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionDisplayIndex > 0) {
      setCurrentQuestionDisplayIndex(currentQuestionDisplayIndex - 1);
    }
  };

  const handleAnswerChange = (questionId: string, text: string) => {
    setUserAnswers(prevAnswers => ({
      ...prevAnswers,
      [questionId]: text,
    }));
  };

  if (isLoading) {
    return (
      <View style={styles.containerCentered}>
        <ActivityIndicator size="large" color="#0000ff" />
        <Text style={styles.text}>Loading daily mission...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.containerCentered}>
        <Text style={styles.errorText}>Error: {error}</Text>
        <Button title="Try Again" onPress={loadMission} />
      </View>
    );
  }

  if (!mission || !mission.questions || mission.questions.length === 0) {
    return (
      <View style={styles.containerCentered}>
        <Text style={styles.text}>No mission available for today. Check back later!</Text>
      </View>
    );
  }

  const currentQuestion = mission?.questions[currentQuestionDisplayIndex];

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Your Daily Mission</Text>
      <Text style={styles.userIdText}>User ID: {userId}</Text>
      {currentQuestion && (
        <View key={currentQuestion.question_id} style={styles.questionContainer}>
          <Text style={styles.questionText}>{currentQuestionDisplayIndex + 1}. {currentQuestion.question_text}</Text>
          <TextInput
            style={styles.input}
            onChangeText={(text) => handleAnswerChange(currentQuestion.question_id, text)}
            value={userAnswers[currentQuestion.question_id] || ''}
            placeholder="Type your answer here"
          />
        </View>
      )}

      <View style={styles.navigationContainer}>
        <Button title="Previous" onPress={handlePreviousQuestion} disabled={currentQuestionDisplayIndex === 0} />
        <Text style={styles.progressText}>
          Question {currentQuestionDisplayIndex + 1} of {mission?.questions.length || 0}
        </Text>
        <Button
          title="Next"
          onPress={handleNextQuestion}
          disabled={!mission || currentQuestionDisplayIndex === mission.questions.length - 1}
        />
      </View>
      <View style={styles.signOutButton}>
        <Button title="Sign Out" onPress={signOut} color="#ff3b30" />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f0f0f0',
  },
  containerCentered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f0f0f0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  userIdText: {
    textAlign: 'center',
    marginBottom: 10,
    color: 'grey',
  },
  text: {
    fontSize: 16,
    textAlign: 'center',
  },
  errorText: {
    fontSize: 16,
    color: 'red',
    textAlign: 'center',
    marginBottom: 10,
  },
  questionContainer: {
    backgroundColor: '#ffffff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
  },
  questionText: {
    fontSize: 18,
    marginBottom: 10,
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    paddingHorizontal: 10,
    marginBottom: 10,
    backgroundColor: 'white',
  },
  navigationContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 20,
  },
  progressText: {
    fontSize: 14,
  },
  signOutButton: {
    marginTop: 20,
  }
});

export default MissionScreen; 