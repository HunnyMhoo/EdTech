import { useState, useEffect, useCallback } from 'react';
import {
  fetchPracticeTopics,
  createPracticeSession,
  fetchPracticeSession,
  submitPracticeAnswer,
  fetchPracticeSessionSummary,
  PracticeTopic,
  PracticeSession,
  PracticeFeedback,
  PracticeSessionSummary,
  CreatePracticeSessionRequest,
} from '../api/practiceApi';
import { Question } from '../../mission/api/missionApi';
// Simplified alert for practice mode - replace with proper notification service later
const showAlert = (title: string, message: string) => {
  console.error(title + ': ' + message);
};

interface PracticeFeedbackState {
  visible: boolean;
  feedback: PracticeFeedback | null;
  questionId: string | null;
}

interface PracticeAnswerState {
  [questionId: string]: string;
}

export const usePractice = (userId: string) => {
  // Practice topics state
  const [topics, setTopics] = useState<PracticeTopic[]>([]);
  const [topicsLoading, setTopicsLoading] = useState<boolean>(false);
  const [topicsError, setTopicsError] = useState<string | null>(null);

  // Session creation state
  const [selectedTopic, setSelectedTopic] = useState<string>('');
  const [questionCount, setQuestionCount] = useState<number>(5);
  const [sessionCreating, setSessionCreating] = useState<boolean>(false);

  // Active session state
  const [currentSession, setCurrentSession] = useState<PracticeSession | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [sessionLoading, setSessionLoading] = useState<boolean>(false);
  const [sessionError, setSessionError] = useState<string | null>(null);

  // Answer submission state
  const [answers, setAnswers] = useState<PracticeAnswerState>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  
  // Feedback modal state
  const [feedbackState, setFeedbackState] = useState<PracticeFeedbackState>({
    visible: false,
    feedback: null,
    questionId: null,
  });

  // Session summary state
  const [sessionSummary, setSessionSummary] = useState<PracticeSessionSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = useState<boolean>(false);

  // Load practice topics
  const loadTopics = useCallback(async () => {
    try {
      setTopicsLoading(true);
      setTopicsError(null);
      const practiceTopics = await fetchPracticeTopics();
      setTopics(practiceTopics);
    } catch (e: any) {
      const errorMessage = e.message || 'Failed to load practice topics.';
      setTopicsError(errorMessage);
      showAlert('Error', errorMessage);
    } finally {
      setTopicsLoading(false);
    }
  }, []);

  // Create new practice session
  const createSession = useCallback(async (request: CreatePracticeSessionRequest) => {
    try {
      setSessionCreating(true);
      setSessionError(null);
      
      const session = await createPracticeSession(userId, request);
      setCurrentSession(session);
      setCurrentQuestionIndex(0);
      setAnswers({});
      setSessionSummary(null);
      
      return session;
    } catch (e: any) {
      const errorMessage = e.message || 'Failed to create practice session.';
      setSessionError(errorMessage);
      showAlert('Error', errorMessage);
      throw e;
    } finally {
      setSessionCreating(false);
    }
  }, [userId]);

  // Load existing practice session
  const loadSession = useCallback(async (sessionId: string) => {
    try {
      setSessionLoading(true);
      setSessionError(null);
      
      const session = await fetchPracticeSession(sessionId);
      setCurrentSession(session);
      
      // Restore answers state
      const answersState: PracticeAnswerState = {};
      session.answers.forEach(answer => {
        answersState[answer.question_id] = answer.user_answer;
      });
      setAnswers(answersState);
      
      // Set current question index based on progress
      const nextUnansweredIndex = session.questions.findIndex(
        question => !session.answers.some(answer => answer.question_id === question.question_id)
      );
      setCurrentQuestionIndex(nextUnansweredIndex >= 0 ? nextUnansweredIndex : session.questions.length - 1);
      
      return session;
    } catch (e: any) {
      const errorMessage = e.message || 'Failed to load practice session.';
      setSessionError(errorMessage);
      showAlert('Error', errorMessage);
      throw e;
    } finally {
      setSessionLoading(false);
    }
  }, []);

  // Submit answer for current question
  const submitAnswer = useCallback(async (questionId: string, answer: any) => {
    if (!currentSession || isSubmitting) return;

    setIsSubmitting(true);
    
    try {
      const feedback = await submitPracticeAnswer(currentSession.session_id, questionId, answer);
      
      // Update local answers state
      setAnswers(prev => ({
        ...prev,
        [questionId]: answer,
      }));

      // Show feedback modal
      setFeedbackState({
        visible: true,
        feedback,
        questionId,
      });

      // If session is complete, we'll load summary when feedback is closed
      
    } catch (e: any) {
      console.error('Failed to submit answer:', e);
      showAlert('Submit Error', 'Could not submit your answer. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }, [currentSession, isSubmitting]);

  // Close feedback modal
  const closeFeedback = useCallback(async () => {
    if (!feedbackState.feedback || !currentSession) return;

    try {
      // Hide feedback modal
      setFeedbackState({
        visible: false,
        feedback: null,
        questionId: null,
      });

      // If session is complete, load summary
      if (feedbackState.feedback.session_complete) {
        setSummaryLoading(true);
        try {
          const summary = await fetchPracticeSessionSummary(currentSession.session_id);
          setSessionSummary(summary);
        } catch (e: any) {
          console.error('Failed to load session summary:', e);
          showAlert('Error', 'Could not load session summary.');
        } finally {
          setSummaryLoading(false);
        }
      } else {
        // Auto-advance to next question
        const nextQuestionIndex = currentQuestionIndex + 1;
        if (nextQuestionIndex < currentSession.questions.length) {
          setCurrentQuestionIndex(nextQuestionIndex);
        }
      }

    } catch (e: any) {
      console.error('Failed to close feedback:', e);
      // Still close the modal even if there's an error
      setFeedbackState({
        visible: false,
        feedback: null,
        questionId: null,
      });
    }
  }, [feedbackState.feedback, currentSession, currentQuestionIndex]);

  // Navigate to specific question
  const goToQuestion = useCallback((index: number) => {
    if (currentSession && index >= 0 && index < currentSession.questions.length) {
      setCurrentQuestionIndex(index);
    }
  }, [currentSession]);

  // Get current question
  const getCurrentQuestion = useCallback((): Question | null => {
    if (!currentSession || currentQuestionIndex >= currentSession.questions.length) {
      return null;
    }
    return currentSession.questions[currentQuestionIndex];
  }, [currentSession, currentQuestionIndex]);

  // Get answer for specific question
  const getAnswer = useCallback((questionId: string): string => {
    return answers[questionId] || '';
  }, [answers]);

  // Set answer for specific question
  const setAnswer = useCallback((questionId: string, answer: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer,
    }));
  }, []);

  // Check if question has been answered
  const isQuestionAnswered = useCallback((questionId: string): boolean => {
    return currentSession?.answers.some(answer => answer.question_id === questionId) || false;
  }, [currentSession]);

  // Get session progress
  const getSessionProgress = useCallback(() => {
    if (!currentSession) return { answered: 0, total: 0 };
    
    return {
      answered: currentSession.answers.length,
      total: currentSession.questions.length,
    };
  }, [currentSession]);

  // Reset practice state
  const resetPractice = useCallback(() => {
    setCurrentSession(null);
    setCurrentQuestionIndex(0);
    setAnswers({});
    setSessionSummary(null);
    setSessionError(null);
    setFeedbackState({
      visible: false,
      feedback: null,
      questionId: null,
    });
  }, []);

  // Load topics on mount
  useEffect(() => {
    loadTopics();
  }, [loadTopics]);

  return {
    // Topics
    topics,
    topicsLoading,
    topicsError,
    loadTopics,

    // Session creation
    selectedTopic,
    setSelectedTopic,
    questionCount,
    setQuestionCount,
    sessionCreating,
    createSession,

    // Active session
    currentSession,
    currentQuestionIndex,
    sessionLoading,
    sessionError,
    loadSession,

    // Questions and answers
    getCurrentQuestion,
    getAnswer,
    setAnswer,
    isQuestionAnswered,
    goToQuestion,

    // Answer submission
    isSubmitting,
    submitAnswer,
    feedbackState,
    closeFeedback,

    // Session summary
    sessionSummary,
    summaryLoading,
    getSessionProgress,

    // Utilities
    resetPractice,
  };
}; 