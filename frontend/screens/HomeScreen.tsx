import React, { useState, useEffect } from 'react';
import { View, Text, ActivityIndicator, Button, StyleSheet } from 'react-native';
import { fetchDailyMission, Mission, Question } from '../services/missionApi';

// Placeholder for TailwindCSS or other styling solution
// For example, if using tailwind-rn:
// import tw from 'tailwind-rn';

const HomeScreen: React.FC = () => {
  const [mission, setMission] = useState<Mission | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

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

  if (!mission || mission.questions.length === 0) {
    return (
      <View style={styles.containerCentered}>
        <Text style={styles.text}>No mission available for today. Check back later!</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Your Daily Mission</Text>
      {mission.questions.map((question: Question, index: number) => (
        <View key={question.id} style={styles.questionContainer}>
          <Text style={styles.questionText}>{index + 1}. {question.text}</Text>
          {/* Placeholder for answer input/options */}
        </View>
      ))}
      {/* Placeholder for mission submission button */}
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
    // Example: text-xl
  },
});

export default HomeScreen; 