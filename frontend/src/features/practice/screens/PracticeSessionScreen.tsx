import React, { useEffect } from 'react';
import {
  View,
  Text,
  ActivityIndicator,
  Button,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import { useAuth } from '../../auth/state/AuthContext';
import { usePractice } from '../hooks/usePractice';
import MultipleChoiceQuestion from '../../mission/components/MultipleChoiceQuestion';
import { FeedbackModal } from '../../mission/components/FeedbackModal';

interface PracticeSessionScreenProps {
  sessionId: string;
  onSessionComplete: () => void;
  onBackToHome: () => void;
}

const PracticeSessionScreen: React.FC<PracticeSessionScreenProps> = ({
  sessionId,
  onSessionComplete,
  onBackToHome,
}) => {
  const { userId } = useAuth();
  const {
    currentSession,
    currentQuestionIndex,
    sessionLoading,
    sessionError,
    loadSession,
    getCurrentQuestion,
    getAnswer,
    setAnswer,
    isQuestionAnswered,
    goToQuestion,
    isSubmitting,
    submitAnswer,
    feedbackState,
    closeFeedback,
    getSessionProgress,
    sessionSummary,
  } = usePractice(userId || '');

  // Load session on mount
  useEffect(() => {
    if (sessionId) {
      loadSession(sessionId);
    }
  }, [sessionId, loadSession]);

  // Navigate to session complete when summary is available
  useEffect(() => {
    if (sessionSummary) {
      onSessionComplete();
    }
  }, [sessionSummary, onSessionComplete]);

  const currentQuestion = getCurrentQuestion();
  const progress = getSessionProgress();

  const handleAnswerChange = (answer: string) => {
    if (currentQuestion) {
      setAnswer(currentQuestion.question_id, answer);
    }
  };

  const handleSubmitAnswer = () => {
    if (!currentQuestion) return;
    
    const answer = getAnswer(currentQuestion.question_id);
    if (!answer.trim()) {
      Alert.alert('Missing Answer', 'Please provide an answer before submitting.');
      return;
    }

    submitAnswer(currentQuestion.question_id, answer);
  };

  const canSubmit = () => {
    if (!currentQuestion) return false;
    const answer = getAnswer(currentQuestion.question_id);
    const alreadyAnswered = isQuestionAnswered(currentQuestion.question_id);
    return answer.trim().length > 0 && !isSubmitting && !alreadyAnswered;
  };

  const canNavigate = (direction: 'prev' | 'next') => {
    if (!currentSession) return false;
    
    if (direction === 'prev') {
      return currentQuestionIndex > 0;
    } else {
      return currentQuestionIndex < currentSession.questions.length - 1;
    }
  };

  // Transform practice feedback to mission feedback format for reuse
  const transformedFeedback = feedbackState.feedback ? {
    already_complete: feedbackState.feedback.already_answered,
    is_correct: feedbackState.feedback.is_correct,
    correct_answer: feedbackState.feedback.correct_answer,
    explanation: feedbackState.feedback.explanation,
    attempt_count: 1, // Practice doesn't have retry logic
    max_retries: 1,
    can_retry: false, // No retries in practice mode
    question_complete: true,
  } : null;

  if (sessionLoading) {
    return (
      <View style={styles.containerCentered}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading practice session...</Text>
      </View>
    );
  }

  if (sessionError) {
    return (
      <View style={styles.containerCentered}>
        <Text style={styles.errorText}>Error: {sessionError}</Text>
        <Button title="Try Again" onPress={() => loadSession(sessionId)} />
        <Button title="Back to Topics" onPress={onBackToHome} />
      </View>
    );
  }

  if (!currentSession || !currentSession.questions || currentSession.questions.length === 0) {
    return (
      <View style={styles.containerCentered}>
        <Text style={styles.text}>No questions available for this session.</Text>
        <Button title="Back to Topics" onPress={onBackToHome} />
      </View>
    );
  }

  if (!currentQuestion) {
    return (
      <View style={styles.containerCentered}>
        <Text style={styles.text}>Question not found</Text>
        <Button title="Back to Topics" onPress={onBackToHome} />
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
          <Text style={styles.title}>Free Practice</Text>
          <Text style={styles.topicText}>Topic: {currentSession.topic}</Text>
          <Text style={styles.statusText}>Status: {currentSession.status}</Text>
        </View>

        {/* Progress Indicator */}
        <View style={styles.progressContainer}>
          <Text style={styles.progressText}>
            Question {currentQuestionIndex + 1} of {currentSession.questions.length}
          </Text>
          <View style={styles.progressBar}>
            <View 
              style={[
                styles.progressFill,
                { width: `${((currentQuestionIndex + 1) / currentSession.questions.length) * 100}%` }
              ]}
            />
          </View>
          <Text style={styles.progressStats}>
            Answered: {progress.answered} / {progress.total}
          </Text>
        </View>

        {/* Question */}
        <MultipleChoiceQuestion
          question={currentQuestion}
          questionIndex={currentQuestionIndex}
          onAnswerChange={handleAnswerChange}
          currentAnswer={getAnswer(currentQuestion.question_id)}
          disabled={isSubmitting || isQuestionAnswered(currentQuestion.question_id)}
          showFeedback={false}
        />

        {/* Question Status */}
        {isQuestionAnswered(currentQuestion.question_id) && (
          <View style={styles.questionStatus}>
            <Text style={styles.completedText}>
              ✓ Question answered
            </Text>
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

        {/* Session Summary */}
        <View style={styles.summaryContainer}>
          <Text style={styles.summaryTitle}>Practice Progress</Text>
          <View style={styles.summaryStats}>
            <Text style={styles.summaryText}>
              Questions: {progress.answered} / {progress.total} answered
            </Text>
            <Text style={styles.summaryText}>
              Topic: {currentSession.topic}
            </Text>
          </View>
        </View>
      </ScrollView>

      {/* Back Button */}
      <View style={styles.backContainer}>
        <Button title="Back to Topics" onPress={onBackToHome} color="#FF3B30" />
      </View>

      {/* Feedback Modal - Reuse existing component */}
      <FeedbackModal
        visible={feedbackState.visible}
        feedback={transformedFeedback}
        onClose={closeFeedback}
        // No retry functionality in practice mode
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
  topicText: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '600',
    marginBottom: 4,
  },
  statusText: {
    fontSize: 14,
    color: '#666',
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
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 4,
  },
  progressStats: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
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
  backContainer: {
    position: 'absolute',
    bottom: 20,
    left: 16,
    right: 16,
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

export default PracticeSessionScreen; 