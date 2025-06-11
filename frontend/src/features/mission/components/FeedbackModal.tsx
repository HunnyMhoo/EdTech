import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
} from 'react-native';
import { BaseModal } from '@/shared/components/Modal';
import { FeedbackResponse } from '../api/missionApi';

interface FeedbackModalProps {
  visible: boolean;
  feedback: FeedbackResponse | null;
  onClose: () => void;
  onRetry?: () => void;
  autoCloseDelay?: number; // Auto-close delay in seconds (0 = no auto-close)
}

export const FeedbackModal: React.FC<FeedbackModalProps> = ({
  visible,
  feedback,
  onClose,
  onRetry,
  autoCloseDelay = 0,
}) => {
  const [fadeAnim] = useState(new Animated.Value(0));
  const [autoCloseTimeout, setAutoCloseTimeout] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (visible && feedback) {
      // Fade in animation
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }).start();

      // Set up auto-close if specified
      if (autoCloseDelay > 0) {
        const timeout = setTimeout(() => {
          handleClose();
        }, autoCloseDelay * 1000);
        setAutoCloseTimeout(timeout);
      }
    } else {
      // Clear timeout if modal is hidden
      if (autoCloseTimeout) {
        clearTimeout(autoCloseTimeout);
        setAutoCloseTimeout(null);
      }
    }

    return () => {
      if (autoCloseTimeout) {
        clearTimeout(autoCloseTimeout);
      }
    };
  }, [visible, feedback, autoCloseDelay]);

  const handleClose = () => {
    if (autoCloseTimeout) {
      clearTimeout(autoCloseTimeout);
      setAutoCloseTimeout(null);
    }
    
    // Fade out animation
    Animated.timing(fadeAnim, {
      toValue: 0,
      duration: 200,
      useNativeDriver: true,
    }).start(() => {
      onClose();
    });
  };

  const handleRetry = () => {
    handleClose();
    if (onRetry) {
      // Small delay to allow modal to close
      setTimeout(() => onRetry(), 250);
    }
  };

  if (!feedback) {
    return null;
  }

  const isCorrect = feedback.is_correct;
  const canRetry = feedback.can_retry && !feedback.already_complete;
  const showRetryButton = canRetry && onRetry;

  return (
    <BaseModal
      visible={visible}
      onClose={handleClose}
      showCloseButton={!autoCloseDelay}
      animationType="fade"
    >
      <Animated.View style={[styles.container, { opacity: fadeAnim }]}>
        {/* Result Icon and Status */}
        <View style={[styles.statusContainer, isCorrect ? styles.correctBg : styles.incorrectBg]}>
          <Text style={styles.statusIcon}>
            {isCorrect ? '✓' : '✗'}
          </Text>
          <Text style={styles.statusText}>
            {isCorrect ? 'Correct!' : 'Incorrect'}
          </Text>
        </View>

        {/* Answer Information */}
        <View style={styles.answerSection}>
          <View style={styles.answerRow}>
            <Text style={styles.answerLabel}>Correct Answer:</Text>
            <Text style={styles.answerValue}>{feedback.correct_answer}</Text>
          </View>
          
          <View style={styles.attemptInfo}>
            <Text style={styles.attemptText}>
              Attempt {feedback.attempt_count} of {feedback.max_retries || 3}
            </Text>
          </View>
        </View>

        {/* Explanation */}
        {feedback.explanation && (
          <View style={styles.explanationSection}>
            <Text style={styles.explanationTitle}>Explanation:</Text>
            <Text style={styles.explanationText}>{feedback.explanation}</Text>
          </View>
        )}

        {/* Action Buttons */}
        <View style={styles.buttonContainer}>
          {showRetryButton && (
            <TouchableOpacity
              style={[styles.button, styles.retryButton]}
              onPress={handleRetry}
            >
              <Text style={styles.retryButtonText}>
                Try Again ({(feedback.max_retries || 3) - feedback.attempt_count} left)
              </Text>
            </TouchableOpacity>
          )}
          
          <TouchableOpacity
            style={[styles.button, styles.closeButton]}
            onPress={handleClose}
          >
            <Text style={styles.closeButtonText}>
              {isCorrect || !canRetry ? 'Continue' : 'Skip'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Auto-close indicator */}
        {autoCloseDelay > 0 && (
          <View style={styles.autoCloseIndicator}>
            <Text style={styles.autoCloseText}>
              Auto-closing in {autoCloseDelay} seconds...
            </Text>
          </View>
        )}
      </Animated.View>
    </BaseModal>
  );
};

const styles = StyleSheet.create({
  container: {
    minWidth: 280,
  },
  statusContainer: {
    alignItems: 'center',
    paddingVertical: 20,
    marginBottom: 16,
    borderRadius: 8,
  },
  correctBg: {
    backgroundColor: '#E8F5E8',
    borderColor: '#4CAF50',
    borderWidth: 1,
  },
  incorrectBg: {
    backgroundColor: '#FFF3F3',
    borderColor: '#F44336',
    borderWidth: 1,
  },
  statusIcon: {
    fontSize: 48,
    color: '#333',
    marginBottom: 8,
  },
  statusText: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
  },
  answerSection: {
    marginBottom: 16,
  },
  answerRow: {
    flexDirection: 'row',
    marginBottom: 8,
    alignItems: 'center',
  },
  answerLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#666',
    minWidth: 100,
  },
  answerValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  attemptInfo: {
    alignItems: 'center',
    marginTop: 8,
  },
  attemptText: {
    fontSize: 12,
    color: '#888',
    fontStyle: 'italic',
  },
  explanationSection: {
    marginBottom: 20,
    padding: 16,
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  explanationTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  explanationText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#555',
  },
  buttonContainer: {
    gap: 12,
  },
  button: {
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
  },
  retryButton: {
    backgroundColor: '#007AFF',
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  closeButton: {
    backgroundColor: '#F0F0F0',
    borderWidth: 1,
    borderColor: '#DDD',
  },
  closeButtonText: {
    color: '#333',
    fontSize: 16,
    fontWeight: '500',
  },
  autoCloseIndicator: {
    marginTop: 16,
    alignItems: 'center',
  },
  autoCloseText: {
    fontSize: 12,
    color: '#888',
    fontStyle: 'italic',
  },
});

export default FeedbackModal; 