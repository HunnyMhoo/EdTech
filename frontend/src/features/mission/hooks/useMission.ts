import { useState, useEffect, useCallback } from 'react';
import {
  fetchDailyMission,
  updateMissionProgressApi,
  Mission,
  Answer,
  Question,
  MissionProgressUpdatePayload,
} from '@/features/mission/api/missionApi';
import { showAlert } from '@/shared/services/notificationService';

export const useMission = (userId: string = 'test_user_123') => {
  const [mission, setMission] = useState<Mission | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [userAnswers, setUserAnswers] = useState<Answer[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadMission = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const fetchedMission = await fetchDailyMission(userId);
      setMission(fetchedMission);
      setCurrentQuestionIndex(fetchedMission.current_question_index || 0);
      setUserAnswers(fetchedMission.answers || []);
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

  const saveProgress = useCallback(async (
    indexToSave: number,
    answersToSave: Answer[]
  ) => {
    if (!mission) return;
    
    const payload: MissionProgressUpdatePayload = {
      current_question_index: indexToSave,
      answers: answersToSave,
    };

    try {
      const updatedMission = await updateMissionProgressApi(mission.user_id, payload);
      setMission(updatedMission); // Update local state with response
    } catch (e: any) {
      console.error('Failed to save progress:', e);
      showAlert('Save Error', 'Could not save your progress. Please try again.');
    }
  }, [mission]);

  const submitAnswer = useCallback((questionId: string, answer: any) => {
    if (!mission) return;

    const newAnswers = userAnswers.filter(ans => ans.question_id !== questionId);
    newAnswers.push({ question_id: questionId, answer, feedback_shown: true });
    setUserAnswers(newAnswers);

    const isMissionComplete = newAnswers.length === mission.questions.length;
    
    if (currentQuestionIndex < mission.questions.length - 1) {
      const nextIndex = currentQuestionIndex + 1;
      setCurrentQuestionIndex(nextIndex);
      saveProgress(nextIndex, newAnswers);
    } else {
      saveProgress(currentQuestionIndex, newAnswers);
      showAlert('Mission Complete!', 'You have answered all questions.');
    }
  }, [mission, currentQuestionIndex, userAnswers, saveProgress]);
  
  const goToQuestion = (index: number) => {
    if (mission && index >= 0 && index < mission.questions.length) {
      setCurrentQuestionIndex(index);
    }
  };

  const currentQuestion: Question | null = mission ? mission.questions[currentQuestionIndex] : null;

  return {
    mission,
    currentQuestion,
    currentQuestionIndex,
    isLoading,
    error,
    userAnswers,
    loadMission,
    submitAnswer,
    goToQuestion,
  };
}; 