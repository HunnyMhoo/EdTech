import { useState, useEffect, useCallback } from 'react';
import {
  fetchDailyMission,
  updateMissionProgressApi,
  submitAnswerWithFeedback,
  markFeedbackShown,
  retryQuestion,
  Mission,
  Answer,
  LegacyAnswer,
  Question,
  MissionProgressUpdatePayload,
  FeedbackResponse,
} from '@/features/mission/api/missionApi';
import { showAlert } from '@/shared/services/notificationService';

interface FeedbackState {
  visible: boolean;
  feedback: FeedbackResponse | null;
  questionId: string | null;
}

interface QuestionState {
  currentAnswer: string;
  isAnswered: boolean;
  isComplete: boolean;
  attemptCount: number;
  canRetry: boolean;
}

export const useMission = (userId: string = 'test_user_123') => {
  const [mission, setMission] = useState<Mission | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  
  // Feedback modal state
  const [feedbackState, setFeedbackState] = useState<FeedbackState>({
    visible: false,
    feedback: null,
    questionId: null,
  });

  // Question states for current session
  const [questionStates, setQuestionStates] = useState<Record<string, QuestionState>>({});

  const loadMission = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const fetchedMission = await fetchDailyMission(userId);
      setMission(fetchedMission);
      setCurrentQuestionIndex(fetchedMission.current_question_index || 0);
      
      // Initialize question states from mission answers
      const initialStates: Record<string, QuestionState> = {};
      fetchedMission.questions.forEach((question) => {
        const existingAnswer = fetchedMission.answers.find(
          (ans) => ans.question_id === question.question_id
        );
        
        initialStates[question.question_id] = {
          currentAnswer: existingAnswer?.current_answer || '',
          isAnswered: !!existingAnswer && existingAnswer.attempt_count > 0,
          isComplete: existingAnswer?.is_complete || false,
          attemptCount: existingAnswer?.attempt_count || 0,
          canRetry: existingAnswer ? !existingAnswer.is_complete && existingAnswer.attempt_count < existingAnswer.max_retries : true,
        };
      });
      
      setQuestionStates(initialStates);
    } catch (e: any) {
      const errorMessage = e.message || 'Failed to load mission.';
      setError(errorMessage);
      showAlert('Error', errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    loadMission();
  }, [loadMission]);

  const updateQuestionState = (questionId: string, updates: Partial<QuestionState>) => {
    setQuestionStates(prev => ({
      ...prev,
      [questionId]: {
        ...prev[questionId],
        ...updates,
      },
    }));
  };

  const getCurrentAnswer = (questionId: string): string => {
    return questionStates[questionId]?.currentAnswer || '';
  };

  const setCurrentAnswer = (questionId: string, answer: string) => {
    updateQuestionState(questionId, { currentAnswer: answer });
  };

  const submitAnswer = useCallback(async (questionId: string, answer: any) => {
    if (!mission || isSubmitting) return;

    setIsSubmitting(true);
    
    try {
      const feedback = await submitAnswerWithFeedback(userId, questionId, answer);
      
      // Update question state
      updateQuestionState(questionId, {
        currentAnswer: answer,
        isAnswered: true,
        isComplete: feedback.question_complete || false,
        attemptCount: feedback.attempt_count,
        canRetry: feedback.can_retry || false,
      });

      // Show feedback modal
      setFeedbackState({
        visible: true,
        feedback,
        questionId,
      });

    } catch (e: any) {
      console.error('Failed to submit answer:', e);
      showAlert('Submit Error', 'Could not submit your answer. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }, [mission, userId, isSubmitting]);

  const closeFeedback = useCallback(async () => {
    if (!feedbackState.questionId) return;

    try {
      // Mark feedback as shown
      await markFeedbackShown(userId, feedbackState.questionId);
      
      // Hide feedback modal
      setFeedbackState({
        visible: false,
        feedback: null,
        questionId: null,
      });

      // Reload mission to get updated status
      await loadMission();

      // Auto-advance to next question if current question is complete
      if (feedbackState.feedback?.is_correct || !feedbackState.feedback?.can_retry) {
        const nextQuestionIndex = currentQuestionIndex + 1;
        if (mission && nextQuestionIndex < mission.questions.length) {
          setCurrentQuestionIndex(nextQuestionIndex);
        }
      }

    } catch (e: any) {
      console.error('Failed to mark feedback as shown:', e);
      // Still close the modal even if API call fails
      setFeedbackState({
        visible: false,
        feedback: null,
        questionId: null,
      });
    }
  }, [feedbackState.questionId, feedbackState.feedback, userId, loadMission, currentQuestionIndex, mission]);

  const retryCurrentQuestion = useCallback(async () => {
    if (!feedbackState.questionId) return;

    try {
      await retryQuestion(userId, feedbackState.questionId);
      
      // Reset question state for retry
      updateQuestionState(feedbackState.questionId, {
        currentAnswer: '',
        isAnswered: false,
      });

      // Close feedback modal
      setFeedbackState({
        visible: false,
        feedback: null,
        questionId: null,
      });

    } catch (e: any) {
      console.error('Failed to retry question:', e);
      showAlert('Retry Error', 'Could not reset question for retry. Please try again.');
    }
  }, [feedbackState.questionId, userId]);

  const goToQuestion = (index: number) => {
    if (mission && index >= 0 && index < mission.questions.length) {
      setCurrentQuestionIndex(index);
    }
  };

  // Legacy method for backward compatibility
  const saveProgress = useCallback(async (
    indexToSave: number,
    answersToSave: LegacyAnswer[]
  ) => {
    if (!mission) return;
    
    const payload: MissionProgressUpdatePayload = {
      current_question_index: indexToSave,
      answers: answersToSave,
    };

    try {
      await updateMissionProgressApi(mission.user_id, payload);
    } catch (e: any) {
      console.error('Failed to save progress:', e);
      showAlert('Save Error', 'Could not save your progress. Please try again.');
    }
  }, [mission]);

  const currentQuestion: Question | null = mission ? mission.questions[currentQuestionIndex] : null;
  const currentQuestionState = currentQuestion ? questionStates[currentQuestion.question_id] : null;

  return {
    // Mission data
    mission,
    currentQuestion,
    currentQuestionIndex,
    
    // Loading states
    isLoading,
    error,
    isSubmitting,
    
    // Question state
    currentQuestionState,
    getCurrentAnswer,
    setCurrentAnswer,
    
    // Feedback state
    feedbackState,
    
    // Actions
    loadMission,
    submitAnswer,
    closeFeedback,
    retryCurrentQuestion,
    goToQuestion,
    
    // Legacy compatibility
    userAnswers: mission?.answers || [],
    saveProgress,
  };
}; 