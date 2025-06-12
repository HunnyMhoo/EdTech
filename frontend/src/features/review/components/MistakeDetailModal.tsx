import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { ReviewMistakeItem } from '../api/reviewMistakesApi';

interface MistakeDetailModalProps {
  visible: boolean;
  mistake: ReviewMistakeItem | null;
  onClose: () => void;
}

export const MistakeDetailModal: React.FC<MistakeDetailModalProps> = ({
  visible,
  mistake,
  onClose,
}) => {
  if (!mistake) return null;

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('th-TH', {
        day: '2-digit',
        month: 'long',
        year: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const formatDateTime = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('th-TH', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  const getDifficultyColor = (level: number) => {
    switch (level) {
      case 1: return '#22C55E';
      case 2: return '#F59E0B';
      case 3: return '#EF4444';
      default: return '#6B7280';
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

  const renderChoice = (choice: { id: string; text: string }) => {
    const isUserAnswer = choice.id === mistake.user_answer_id;
    const isCorrectAnswer = choice.id === mistake.correct_answer_id;
    
    let choiceStyle: any = styles.choice;
    let choiceTextStyle: any = styles.choiceText;
    let indicator = null;

    if (isCorrectAnswer) {
      choiceStyle = [styles.choice, styles.correctChoice];
      choiceTextStyle = [styles.choiceText, styles.correctChoiceText];
      indicator = <View style={styles.correctIndicator} />;
    } else if (isUserAnswer) {
      choiceStyle = [styles.choice, styles.incorrectChoice];
      choiceTextStyle = [styles.choiceText, styles.incorrectChoiceText];
      indicator = <View style={styles.incorrectIndicator} />;
    }

    return (
      <View key={choice.id} style={choiceStyle}>
        <View style={styles.choiceContent}>
          {indicator}
          <Text style={choiceTextStyle}>{choice.text}</Text>
        </View>
        {isUserAnswer && !isCorrectAnswer && (
          <Text style={styles.userAnswerLabel}>Your answer</Text>
        )}
        {isCorrectAnswer && (
          <Text style={styles.correctAnswerLabel}>Correct answer</Text>
        )}
      </View>
    );
  };

  const renderExplanation = (explanation: string) => {
    // Simple formatting support for bold, italic, and basic lists
    const parts = explanation.split(/(\*\*.*?\*\*|\*.*?\*)/g);
    
    return (
      <Text style={styles.explanationText}>
        {parts.map((part, index) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return (
              <Text key={index} style={styles.boldText}>
                {part.slice(2, -2)}
              </Text>
            );
          } else if (part.startsWith('*') && part.endsWith('*')) {
            return (
              <Text key={index} style={styles.italicText}>
                {part.slice(1, -1)}
              </Text>
            );
          }
          return part;
        })}
      </Text>
    );
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <SafeAreaView style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Text style={styles.closeButtonText}>✕</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Review Mistake</Text>
          <View style={styles.headerSpacer} />
        </View>

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* Mission Info */}
          <View style={styles.missionInfo}>
            <View style={styles.missionInfoRow}>
              <Text style={styles.missionInfoLabel}>Mission Date:</Text>
              <Text style={styles.missionInfoValue}>
                {formatDate(mistake.mission_date)}
              </Text>
            </View>
            <View style={styles.missionInfoRow}>
              <Text style={styles.missionInfoLabel}>Completed:</Text>
              <Text style={styles.missionInfoValue}>
                {formatDateTime(mistake.mission_completion_date)}
              </Text>
            </View>
            <View style={styles.missionInfoRow}>
              <Text style={styles.missionInfoLabel}>Attempts:</Text>
              <Text style={styles.missionInfoValue}>
                {mistake.attempt_count}
              </Text>
            </View>
          </View>

          {/* Question Section */}
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
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
            </View>
            
            <Text style={styles.questionText}>{mistake.question_text}</Text>
          </View>

          {/* Choices Section */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Answer Choices</Text>
            <View style={styles.choicesContainer}>
              {mistake.choices.map(renderChoice)}
            </View>
          </View>

          {/* Explanation Section */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Explanation</Text>
            <View style={styles.explanationContainer}>
              {renderExplanation(mistake.explanation)}
            </View>
          </View>
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#F3F4F6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  closeButtonText: {
    fontSize: 16,
    color: '#6B7280',
    fontWeight: '600',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  headerSpacer: {
    width: 32,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  missionInfo: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  missionInfoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  missionInfoLabel: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '500',
  },
  missionInfoValue: {
    fontSize: 14,
    color: '#111827',
    fontWeight: '600',
  },
  section: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  sectionHeader: {
    marginBottom: 16,
  },
  skillAreaContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  skillArea: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginRight: 12,
  },
  difficultyBadge: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
  },
  difficultyText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  questionText: {
    fontSize: 18,
    fontWeight: '500',
    color: '#111827',
    lineHeight: 26,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 16,
  },
  choicesContainer: {
    gap: 12,
  },
  choice: {
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    backgroundColor: '#F9F9F9',
    padding: 16,
  },
  correctChoice: {
    borderColor: '#22C55E',
    backgroundColor: '#F0FDF4',
  },
  incorrectChoice: {
    borderColor: '#EF4444',
    backgroundColor: '#FEF2F2',
  },
  choiceContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  choiceText: {
    fontSize: 16,
    color: '#374151',
    flex: 1,
  },
  correctChoiceText: {
    color: '#15803D',
    fontWeight: '500',
  },
  incorrectChoiceText: {
    color: '#DC2626',
    fontWeight: '500',
  },
  correctIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#22C55E',
    marginRight: 12,
  },
  incorrectIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#EF4444',
    marginRight: 12,
  },
  userAnswerLabel: {
    fontSize: 12,
    color: '#DC2626',
    fontWeight: '600',
    marginTop: 8,
    textAlign: 'right',
  },
  correctAnswerLabel: {
    fontSize: 12,
    color: '#15803D',
    fontWeight: '600',
    marginTop: 8,
    textAlign: 'right',
  },
  explanationContainer: {
    backgroundColor: '#F8FAFC',
    borderRadius: 8,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#3B82F6',
  },
  explanationText: {
    fontSize: 16,
    color: '#374151',
    lineHeight: 24,
  },
  boldText: {
    fontWeight: '700',
  },
  italicText: {
    fontStyle: 'italic',
  },
}); 