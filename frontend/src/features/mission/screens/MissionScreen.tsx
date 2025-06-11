import React from 'react';
import { View, Text, ActivityIndicator, Button, StyleSheet, ScrollView, Alert } from 'react-native';
import { useAuth } from '../../auth/state/AuthContext';
import { useMission } from '../hooks/useMission';
import MultipleChoiceQuestion from '../components/MultipleChoiceQuestion';
import FeedbackModal from '../components/FeedbackModal';

const MissionScreen: React.FC = () => {
  const { userId, signOut } = useAuth();
  const {
    mission,
    currentQuestion,
    currentQuestionIndex,
    isLoading,
    error,
    isSubmitting,
    currentQuestionState,
    getCurrentAnswer,
    setCurrentAnswer,
    feedbackState,
    loadMission,
    submitAnswer,
    closeFeedback,
    retryCurrentQuestion,
    goToQuestion,
  } = useMission(userId || '');

  const handleAnswerChange = (answer: string) => {
    if (currentQuestion) {
      setCurrentAnswer(currentQuestion.question_id, answer);
    }
  };

  const handleSubmitAnswer = () => {
    if (!currentQuestion || !currentQuestionState) return;
    
    const answer = getCurrentAnswer(currentQuestion.question_id);
    if (!answer.trim()) {
      Alert.alert('Missing Answer', 'Please provide an answer before submitting.');
      return;
    }

    submitAnswer(currentQuestion.question_id, answer);
  };

  const canSubmit = () => {
    if (!currentQuestion || !currentQuestionState) return false;
    const answer = getCurrentAnswer(currentQuestion.question_id);
    return answer.trim().length > 0 && !isSubmitting && !currentQuestionState.isComplete;
  };

  const canNavigate = (direction: 'prev' | 'next') => {
    if (!mission) return false;
    
    if (direction === 'prev') {
      return currentQuestionIndex > 0;
    } else {
      return currentQuestionIndex < mission.questions.length - 1;
    }
  };

  if (isLoading) {
    return (
      <View style={styles.containerCentered}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading daily mission...</Text>
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
        <Button title="Refresh" onPress={loadMission} />
      </View>
    );
  }

  if (!currentQuestion) {
    return (
      <View style={styles.containerCentered}>
        <Text style={styles.text}>Question not found</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView 
        contentContainerStyle={styles.scrollContainer}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Daily Mission</Text>
          <Text style={styles.userIdText}>User: {userId}</Text>
          <Text style={styles.statusText}>Status: {mission.status}</Text>
        </View>

        {/* Progress Indicator */}
        <View style={styles.progressContainer}>
          <Text style={styles.progressText}>
            Question {currentQuestionIndex + 1} of {mission.questions.length}
          </Text>
          <View style={styles.progressBar}>
            <View 
              style={[
                styles.progressFill,
                { width: `${((currentQuestionIndex + 1) / mission.questions.length) * 100}%` }
              ]}
            />
          </View>
        </View>

        {/* Question */}
        <MultipleChoiceQuestion
          question={currentQuestion}
          questionIndex={currentQuestionIndex}
          onAnswerChange={handleAnswerChange}
          currentAnswer={getCurrentAnswer(currentQuestion.question_id)}
          disabled={isSubmitting || currentQuestionState?.isComplete}
          showFeedback={false}
        />

        {/* Question Status */}
        {currentQuestionState && (
          <View style={styles.questionStatus}>
            {currentQuestionState.isComplete && (
              <Text style={styles.completedText}>
                ✓ Question completed ({currentQuestionState.attemptCount} attempts)
              </Text>
            )}
            {currentQuestionState.isAnswered && !currentQuestionState.isComplete && (
              <Text style={styles.attemptText}>
                Attempts: {currentQuestionState.attemptCount} / 3
              </Text>
            )}
          </View>
        )}

        {/* Submit Button */}
        <View style={styles.submitContainer}>
          <Button
            title={isSubmitting ? 'Submitting...' : 'Submit Answer'}
            onPress={handleSubmitAnswer}
            disabled={!canSubmit()}
            color="#007AFF"
          />
        </View>

        {/* Navigation */}
        <View style={styles.navigationContainer}>
          <Button
            title="Previous"
            onPress={() => goToQuestion(currentQuestionIndex - 1)}
            disabled={!canNavigate('prev')}
            color="#666"
          />
          <Button
            title="Next"
            onPress={() => goToQuestion(currentQuestionIndex + 1)}
            disabled={!canNavigate('next')}
            color="#666"
          />
        </View>

        {/* Mission Progress Summary */}
        <View style={styles.summaryContainer}>
          <Text style={styles.summaryTitle}>Progress Summary</Text>
          <View style={styles.summaryStats}>
            <Text style={styles.summaryText}>
              Answered: {mission.answers.filter(a => a.is_complete).length} / {mission.questions.length}
            </Text>
            <Text style={styles.summaryText}>
              Correct: {mission.answers.filter(a => a.is_correct).length}
            </Text>
          </View>
        </View>
      </ScrollView>

      {/* Sign Out Button */}
      <View style={styles.signOutContainer}>
        <Button title="Sign Out" onPress={signOut} color="#FF3B30" />
      </View>

      {/* Feedback Modal */}
      <FeedbackModal
        visible={feedbackState.visible}
        feedback={feedbackState.feedback}
        onClose={closeFeedback}
        onRetry={retryCurrentQuestion}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  scrollContainer: {
    padding: 16,
    paddingBottom: 100,
  },
  containerCentered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#F5F5F5',
  },
  header: {
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  userIdText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  statusText: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
  },
  progressContainer: {
    marginBottom: 24,
  },
  progressText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
    marginBottom: 8,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 4,
  },
  questionStatus: {
    alignItems: 'center',
    marginTop: 16,
  },
  completedText: {
    fontSize: 14,
    color: '#4CAF50',
    fontWeight: '600',
  },
  attemptText: {
    fontSize: 14,
    color: '#FF9800',
    fontWeight: '500',
  },
  submitContainer: {
    marginTop: 24,
    marginBottom: 16,
  },
  navigationContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
    paddingHorizontal: 20,
  },
  summaryContainer: {
    marginTop: 32,
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  summaryTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  summaryStats: {
    gap: 8,
  },
  summaryText: {
    fontSize: 14,
    color: '#666',
  },
  signOutContainer: {
    position: 'absolute',
    bottom: 16,
    left: 16,
    right: 16,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  text: {
    fontSize: 16,
    textAlign: 'center',
    color: '#333',
    marginBottom: 16,
  },
  errorText: {
    fontSize: 16,
    color: '#FF3B30',
    textAlign: 'center',
    marginBottom: 16,
  },
});

export default MissionScreen; 