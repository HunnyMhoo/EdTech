import React, { useState, useEffect } from 'react';
import { View, Text, ActivityIndicator, Button, StyleSheet, TextInput } from 'react-native';
import { fetchDailyMission, Mission, Question } from '../services/missionApi';

// Placeholder for TailwindCSS or other styling solution
// For example, if using tailwind-rn:
// import tw from 'tailwind-rn';

const HomeScreen: React.FC = () => {
  const [mission, setMission] = useState<Mission | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [currentQuestionDisplayIndex, setCurrentQuestionDisplayIndex] = useState<number>(0);
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({}); // { question_id: answer_text }

  const loadMission = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchDailyMission();
      setMission(data);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
      // In a real app, you might want to log this error to a service
      console.error('Failed to load mission:', err);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    loadMission();
  }, []);

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
      {currentQuestion && (
        <View key={currentQuestion.question_id} style={styles.questionContainer}>
          <Text style={styles.questionText}>{currentQuestionDisplayIndex + 1}. {currentQuestion.question_text}</Text>
          <TextInput
            style={styles.input}
            onChangeText={(text) => handleAnswerChange(currentQuestion.question_id, text)}
            value={userAnswers[currentQuestion.question_id] || ''}
            placeholder="Type your answer here"
          />
          {/* You can also display other question details here if needed */}
          {/* e.g., <Text style={styles.skillAreaText}>Skill: {currentQuestion.skill_area}</Text> */}
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
      
      {/* Placeholder for mission submission button - to be added later */}
      {/* We can also add a button here to log current answers for debugging */}
      {/* <Button title="Log Answers" onPress={() => console.log(userAnswers)} /> */}
    </View>
  );
};

// Basic StyleSheet for demonstration. Replace with Tailwind or other styling.
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
    // Example of what could be a Tailwind class: text-2xl font-bold mb-5 text-center
  },
  text: {
    fontSize: 16,
    textAlign: 'center',
    // Example: text-lg text-center
  },
  errorText: {
    fontSize: 16,
    color: 'red',
    textAlign: 'center',
    marginBottom: 10,
    // Example: text-lg text-red-600 text-center mb-2
  },
  questionContainer: {
    backgroundColor: '#ffffff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    // Example: bg-white p-4 rounded-lg mb-3 shadow
  },
  questionText: {
    fontSize: 18,
    marginBottom: 10, // Added margin for spacing before input
    // Example: text-xl
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
  }
});

export default HomeScreen; 