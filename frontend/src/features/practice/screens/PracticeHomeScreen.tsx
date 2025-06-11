import React from 'react';
import {
  View,
  Text,
  ActivityIndicator,
  Button,
  StyleSheet,
  Alert,
} from 'react-native';
import { useAuth } from '../../auth/state/AuthContext';
import { usePractice } from '../hooks/usePractice';
import TopicSelector from '../components/TopicSelector';
import PracticeSummary from '../components/PracticeSummary';

interface PracticeHomeScreenProps {
  onStartSession: (sessionId: string) => void;
}

const PracticeHomeScreen: React.FC<PracticeHomeScreenProps> = ({ onStartSession }) => {
  const { userId } = useAuth();
  const {
    topics,
    topicsLoading,
    topicsError,
    loadTopics,
    selectedTopic,
    setSelectedTopic,
    questionCount,
    setQuestionCount,
    sessionCreating,
    createSession,
    sessionSummary,
    resetPractice,
  } = usePractice(userId || '');

  const handleTopicSelect = (topic: string) => {
    setSelectedTopic(topic);
  };

  const handleQuestionCountChange = (count: number) => {
    setQuestionCount(count);
  };

  const handleStartPractice = async () => {
    if (!selectedTopic) {
      Alert.alert('Select Topic', 'Please select a topic to practice.');
      return;
    }

    try {
      const session = await createSession({
        topic: selectedTopic,
        question_count: questionCount,
      });
      
      onStartSession(session.session_id);
    } catch (error) {
      // Error is already handled in the hook
      console.error('Failed to start practice session:', error);
    }
  };

  const handleStartNewSession = async () => {
    if (!sessionSummary) return;

    try {
      const session = await createSession({
        topic: sessionSummary.topic,
        question_count: questionCount,
      });
      
      onStartSession(session.session_id);
    } catch (error) {
      console.error('Failed to start new practice session:', error);
    }
  };

  const handleBackToTopics = () => {
    resetPractice();
  };

  // Show loading state
  if (topicsLoading) {
    return (
      <View style={styles.containerCentered}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading practice topics...</Text>
      </View>
    );
  }

  // Show error state
  if (topicsError) {
    return (
      <View style={styles.containerCentered}>
        <Text style={styles.errorText}>Error: {topicsError}</Text>
        <Button title="Try Again" onPress={loadTopics} />
      </View>
    );
  }

  // Show "no topics" state
  if (!topics || topics.length === 0) {
    return (
      <View style={styles.containerCentered}>
        <Text style={styles.text}>No practice topics available. Check back later!</Text>
        <Button title="Refresh" onPress={loadTopics} />
      </View>
    );
  }

  // Show session summary if available
  if (sessionSummary) {
    return (
      <PracticeSummary
        summary={sessionSummary}
        onStartNewSession={handleStartNewSession}
        onBackToTopics={handleBackToTopics}
        isLoading={sessionCreating}
      />
    );
  }

  // Show topic selector
  return (
    <TopicSelector
      topics={topics}
      selectedTopic={selectedTopic}
      questionCount={questionCount}
      onTopicSelect={handleTopicSelect}
      onQuestionCountChange={handleQuestionCountChange}
      onStartPractice={handleStartPractice}
      isLoading={sessionCreating}
    />
  );
};

const styles = StyleSheet.create({
  containerCentered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#F5F5F5',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    fontSize: 16,
    color: '#F44336',
    textAlign: 'center',
    marginBottom: 16,
  },
  text: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
    marginBottom: 16,
  },
});

export default PracticeHomeScreen; 