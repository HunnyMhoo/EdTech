import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
} from 'react-native';
import { PracticeSessionSummary } from '../api/practiceApi';

interface PracticeSummaryProps {
  summary: PracticeSessionSummary;
  onStartNewSession: () => void;
  onBackToTopics: () => void;
  isLoading?: boolean;
}

const PracticeSummary: React.FC<PracticeSummaryProps> = ({
  summary,
  onStartNewSession,
  onBackToTopics,
  isLoading = false,
}) => {
  const { score } = summary;
  const accuracy = Math.round(score.accuracy);
  const completionRate = Math.round(score.completion_rate);

  const getPerformanceColor = (percentage: number) => {
    if (percentage >= 80) return '#4CAF50';
    if (percentage >= 60) return '#FF9800';
    return '#F44336';
  };

  const getPerformanceLabel = (percentage: number) => {
    if (percentage >= 90) return 'Excellent!';
    if (percentage >= 80) return 'Great work!';
    if (percentage >= 70) return 'Good job!';
    if (percentage >= 60) return 'Not bad!';
    return 'Keep practicing!';
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' at ' + date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Practice Complete!</Text>
        <Text style={styles.subtitle}>
          {summary.topic} • {formatDateTime(summary.completed_at || summary.created_at)}
        </Text>
      </View>

      {/* Score Overview */}
      <View style={styles.scoreCard}>
        <View style={styles.mainScore}>
          <Text style={styles.scoreValue}>
            {score.correct_answers}/{score.total_questions}
          </Text>
          <Text style={styles.scoreLabel}>Correct Answers</Text>
        </View>

        <View style={styles.percentageContainer}>
          <Text 
            style={[
              styles.percentage, 
              { color: getPerformanceColor(accuracy) }
            ]}
          >
            {accuracy}%
          </Text>
          <Text 
            style={[
              styles.performanceLabel,
              { color: getPerformanceColor(accuracy) }
            ]}
          >
            {getPerformanceLabel(accuracy)}
          </Text>
        </View>
      </View>

      {/* Detailed Stats */}
      <View style={styles.statsContainer}>
        <Text style={styles.sectionTitle}>Session Details</Text>
        
        <View style={styles.statsList}>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Questions Answered</Text>
            <Text style={styles.statValue}>
              {score.answered_questions} / {score.total_questions}
            </Text>
          </View>

          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Completion Rate</Text>
            <Text style={[styles.statValue, { color: getPerformanceColor(completionRate) }]}>
              {completionRate}%
            </Text>
          </View>

          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Accuracy</Text>
            <Text style={[styles.statValue, { color: getPerformanceColor(accuracy) }]}>
              {accuracy}%
            </Text>
          </View>

          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Topic</Text>
            <Text style={styles.statValue}>{summary.topic}</Text>
          </View>

          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Status</Text>
            <Text style={[
              styles.statValue,
              { color: summary.status === 'completed' ? '#4CAF50' : '#FF9800' }
            ]}>
              {summary.status.charAt(0).toUpperCase() + summary.status.slice(1)}
            </Text>
          </View>
        </View>
      </View>

      {/* Progress Bar */}
      <View style={styles.progressSection}>
        <View style={styles.progressHeader}>
          <Text style={styles.progressLabel}>Overall Progress</Text>
          <Text style={styles.progressText}>
            {score.correct_answers} correct out of {score.total_questions}
          </Text>
        </View>
        <View style={styles.progressBar}>
          <View 
            style={[
              styles.progressFill,
              { 
                width: `${accuracy}%`,
                backgroundColor: getPerformanceColor(accuracy)
              }
            ]}
          />
        </View>
      </View>

      {/* Motivational Message */}
      <View style={styles.messageCard}>
        {accuracy >= 80 ? (
          <View>
            <Text style={styles.messageTitle}>🎉 Excellent Work!</Text>
            <Text style={styles.messageText}>
              You're mastering {summary.topic}! Keep up the great practice to maintain your skills.
            </Text>
          </View>
        ) : accuracy >= 60 ? (
          <View>
            <Text style={styles.messageTitle}>📈 Good Progress!</Text>
            <Text style={styles.messageText}>
              You're on the right track with {summary.topic}. A bit more practice will help you excel!
            </Text>
          </View>
        ) : (
          <View>
            <Text style={styles.messageTitle}>💪 Keep Going!</Text>
            <Text style={styles.messageText}>
              {summary.topic} can be challenging, but every practice session helps you improve. Don't give up!
            </Text>
          </View>
        )}
      </View>

      {/* Action Buttons */}
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[styles.button, styles.primaryButton]}
          onPress={onStartNewSession}
          disabled={isLoading}
        >
          <Text style={styles.primaryButtonText}>
            {isLoading ? 'Starting...' : `Practice ${summary.topic} Again`}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.secondaryButton]}
          onPress={onBackToTopics}
        >
          <Text style={styles.secondaryButtonText}>
            Choose Different Topic
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  scoreCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 24,
    marginBottom: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  mainScore: {
    alignItems: 'center',
    marginBottom: 16,
  },
  scoreValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#333',
  },
  scoreLabel: {
    fontSize: 18,
    color: '#666',
    marginTop: 4,
  },
  percentageContainer: {
    alignItems: 'center',
  },
  percentage: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  performanceLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 4,
  },
  statsContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    marginBottom: 16,
  },
  statsList: {
    gap: 12,
  },
  statItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  statLabel: {
    fontSize: 16,
    color: '#666',
  },
  statValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  progressSection: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  progressLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  progressText: {
    fontSize: 14,
    color: '#666',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
  messageCard: {
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    padding: 20,
    marginBottom: 24,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  messageTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  messageText: {
    fontSize: 16,
    color: '#666',
    lineHeight: 22,
  },
  buttonContainer: {
    gap: 12,
    paddingBottom: 20,
  },
  button: {
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  primaryButton: {
    backgroundColor: '#007AFF',
  },
  primaryButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
  },
  secondaryButton: {
    backgroundColor: '#F0F0F0',
    borderWidth: 1,
    borderColor: '#DDD',
  },
  secondaryButtonText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
});

export default PracticeSummary; 