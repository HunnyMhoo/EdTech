import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { ReviewMistakeItem } from '../api/reviewMistakesApi';

interface MistakeCardProps {
  mistake: ReviewMistakeItem;
  onPress: () => void;
  showDate?: boolean;
  compact?: boolean;
}

export const MistakeCard: React.FC<MistakeCardProps> = ({ 
  mistake, 
  onPress, 
  showDate = true,
  compact = false 
}) => {
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('th-TH', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const getDifficultyColor = (level: number) => {
    switch (level) {
      case 1: return '#22C55E'; // Green for easy
      case 2: return '#F59E0B'; // Orange for medium
      case 3: return '#EF4444'; // Red for hard
      default: return '#6B7280'; // Gray for unknown
    }
  };

  const getDifficultyText = (level: number) => {
    switch (level) {
      case 1: return 'Easy';
      case 2: return 'Medium';
      case 3: return 'Hard';
      default: return `Level ${level}`;
    }
  };

  return (
    <TouchableOpacity 
      style={[styles.card, compact && styles.compactCard]} 
      onPress={onPress}
      activeOpacity={0.7}
    >
      {/* Header with skill area and difficulty */}
      <View style={styles.header}>
        <View style={styles.skillAreaContainer}>
          <Text style={styles.skillArea}>{mistake.skill_area}</Text>
          <View style={[
            styles.difficultyBadge, 
            { backgroundColor: getDifficultyColor(mistake.difficulty_level) }
          ]}>
            <Text style={styles.difficultyText}>
              {getDifficultyText(mistake.difficulty_level)}
            </Text>
          </View>
        </View>
        
        {showDate && (
          <Text style={styles.date}>
            {formatDate(mistake.mission_date)}
          </Text>
        )}
      </View>

      {/* Question text */}
      <Text 
        style={[styles.questionText, compact && styles.compactQuestionText]}
        numberOfLines={compact ? 2 : 3}
      >
        {mistake.question_text}
      </Text>

      {/* Answer comparison */}
      <View style={styles.answerSection}>
        <View style={styles.answerRow}>
          <View style={styles.answerLabel}>
            <View style={styles.incorrectIndicator} />
            <Text style={styles.answerLabelText}>Your answer:</Text>
          </View>
          <Text style={[styles.answerText, styles.incorrectAnswer]} numberOfLines={1}>
            {mistake.user_answer_text}
          </Text>
        </View>
        
        <View style={styles.answerRow}>
          <View style={styles.answerLabel}>
            <View style={styles.correctIndicator} />
            <Text style={styles.answerLabelText}>Correct answer:</Text>
          </View>
          <Text style={[styles.answerText, styles.correctAnswer]} numberOfLines={1}>
            {mistake.correct_answer_text}
          </Text>
        </View>
      </View>

      {/* Footer with attempt count */}
      <View style={styles.footer}>
        <Text style={styles.attemptCount}>
          {mistake.attempt_count} attempt{mistake.attempt_count !== 1 ? 's' : ''}
        </Text>
        <View style={styles.viewDetailsContainer}>
          <Text style={styles.viewDetailsText}>Tap to view details</Text>
          <Text style={styles.chevron}>›</Text>
        </View>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
    borderWidth: 1,
    borderColor: '#F3F4F6',
  },
  compactCard: {
    padding: 12,
    marginBottom: 8,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  skillAreaContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  skillArea: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginRight: 8,
  },
  difficultyBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  difficultyText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#FFFFFF',
  },
  date: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: '500',
  },
  questionText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#111827',
    lineHeight: 22,
    marginBottom: 16,
  },
  compactQuestionText: {
    fontSize: 14,
    marginBottom: 12,
  },
  answerSection: {
    marginBottom: 16,
  },
  answerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  answerLabel: {
    flexDirection: 'row',
    alignItems: 'center',
    width: 120,
  },
  incorrectIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#EF4444',
    marginRight: 8,
  },
  correctIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#22C55E',
    marginRight: 8,
  },
  answerLabelText: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: '500',
  },
  answerText: {
    fontSize: 14,
    fontWeight: '500',
    flex: 1,
  },
  incorrectAnswer: {
    color: '#EF4444',
  },
  correctAnswer: {
    color: '#22C55E',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  attemptCount: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: '500',
  },
  viewDetailsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  viewDetailsText: {
    fontSize: 12,
    color: '#3B82F6',
    fontWeight: '500',
    marginRight: 4,
  },
  chevron: {
    fontSize: 16,
    color: '#3B82F6',
    fontWeight: '600',
  },
}); 