import { useState, useEffect, useCallback } from 'react';
import {
  getReviewMistakes,
  getGroupedReviewMistakes,
  getAvailableSkillAreas,
  getReviewStats,
  ReviewMistakeItem,
  ReviewMistakesResponse,
  GroupedReviewMistakesResponse,
  ReviewStatsResponse,
  ReviewMistakesParams,
  GroupedReviewMistakesParams,
  PaginationInfo
} from '../api/reviewMistakesApi';

export type GroupingType = 'none' | 'date' | 'topic';

export interface UseReviewMistakesState {
  // Data
  mistakes: ReviewMistakeItem[];
  groupedMistakes: Record<string, ReviewMistakeItem[]>;
  groupCounts: Record<string, number>;
  skillAreas: string[];
  stats: ReviewStatsResponse | null;
  
  // State
  loading: boolean;
  error: string | null;
  grouping: GroupingType;
  pagination: PaginationInfo | null;
  
  // Filters
  currentPage: number;
  itemsPerPage: number;
  selectedSkillArea: string | null;
  
  // Actions
  loadMistakes: () => Promise<void>;
  loadGroupedMistakes: (groupBy: 'date' | 'topic') => Promise<void>;
  loadSkillAreas: () => Promise<void>;
  loadStats: () => Promise<void>;
  setGrouping: (grouping: GroupingType) => void;
  setPage: (page: number) => void;
  setItemsPerPage: (items: number) => void;
  setSelectedSkillArea: (skillArea: string | null) => void;
  refresh: () => Promise<void>;
  
  // Computed
  totalMistakes: number;
  hasNoMistakes: boolean;
  noMistakesMessage: string;
}

export const useReviewMistakes = (userId: string): UseReviewMistakesState => {
  // State
  const [mistakes, setMistakes] = useState<ReviewMistakeItem[]>([]);
  const [groupedMistakes, setGroupedMistakes] = useState<Record<string, ReviewMistakeItem[]>>({});
  const [groupCounts, setGroupCounts] = useState<Record<string, number>>({});
  const [skillAreas, setSkillAreas] = useState<string[]>([]);
  const [stats, setStats] = useState<ReviewStatsResponse | null>(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [grouping, setGrouping] = useState<GroupingType>('none');
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  
  // Filters
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(20);
  const [selectedSkillArea, setSelectedSkillArea] = useState<string | null>(null);

  // Load mistakes without grouping
  const loadMistakes = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params: ReviewMistakesParams = {
        page: currentPage,
        items_per_page: itemsPerPage,
        skill_area: selectedSkillArea || undefined,
      };
      
      const response = await getReviewMistakes(userId, params);
      
      setMistakes(response.mistakes);
      setPagination(response.pagination);
      
      // Clear grouped data when loading ungrouped
      setGroupedMistakes({});
      setGroupCounts({});
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      console.error('Error loading mistakes:', err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, itemsPerPage, selectedSkillArea]);

  // Load grouped mistakes
  const loadGroupedMistakes = useCallback(async (groupBy: 'date' | 'topic') => {
    try {
      setLoading(true);
      setError(null);
      
      const params: GroupedReviewMistakesParams = {
        group_by: groupBy,
        page: currentPage,
        items_per_page: itemsPerPage,
        skill_area: selectedSkillArea || undefined,
      };
      
      const response = await getGroupedReviewMistakes(userId, params);
      
      setGroupedMistakes(response.grouped_mistakes);
      setGroupCounts(response.group_counts);
      setPagination(response.pagination);
      
      // Clear ungrouped data when loading grouped
      setMistakes([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      console.error('Error loading grouped mistakes:', err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, itemsPerPage, selectedSkillArea]);

  // Load available skill areas
  const loadSkillAreas = useCallback(async () => {
    try {
      const skillAreasData = await getAvailableSkillAreas(userId);
      setSkillAreas(skillAreasData);
    } catch (err) {
      console.error('Error loading skill areas:', err);
    }
  }, [userId]);

  // Load stats
  const loadStats = useCallback(async () => {
    try {
      const statsData = await getReviewStats(userId);
      setStats(statsData);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  }, [userId]);

  // Refresh current view
  const refresh = useCallback(async () => {
    switch (grouping) {
      case 'date':
        await loadGroupedMistakes('date');
        break;
      case 'topic':
        await loadGroupedMistakes('topic');
        break;
      default:
        await loadMistakes();
        break;
    }
  }, [grouping, loadMistakes, loadGroupedMistakes]);

  // Handle grouping changes
  const handleSetGrouping = useCallback((newGrouping: GroupingType) => {
    setGrouping(newGrouping);
    setCurrentPage(1); // Reset to first page when changing grouping
  }, []);

  // Handle page changes
  const setPage = useCallback((page: number) => {
    setCurrentPage(page);
  }, []);

  // Handle items per page changes
  const handleSetItemsPerPage = useCallback((items: number) => {
    setItemsPerPage(items);
    setCurrentPage(1); // Reset to first page when changing page size
  }, []);

  // Handle skill area filter changes
  const handleSetSelectedSkillArea = useCallback((skillArea: string | null) => {
    setSelectedSkillArea(skillArea);
    setCurrentPage(1); // Reset to first page when changing filter
  }, []);

  // Load data when dependencies change
  useEffect(() => {
    switch (grouping) {
      case 'date':
        loadGroupedMistakes('date');
        break;
      case 'topic':
        loadGroupedMistakes('topic');
        break;
      default:
        loadMistakes();
        break;
    }
  }, [grouping, currentPage, itemsPerPage, selectedSkillArea, loadMistakes, loadGroupedMistakes]);

  // Load initial data on mount
  useEffect(() => {
    loadSkillAreas();
    loadStats();
  }, [loadSkillAreas, loadStats]);

  // Computed values
  const totalMistakes = stats?.total_mistakes || 0;
  const hasNoMistakes = totalMistakes === 0;
  const noMistakesMessage = "Great job! You have no mistakes to review right now.";

  return {
    // Data
    mistakes,
    groupedMistakes,
    groupCounts,
    skillAreas,
    stats,
    
    // State
    loading,
    error,
    grouping,
    pagination,
    
    // Filters
    currentPage,
    itemsPerPage,
    selectedSkillArea,
    
    // Actions
    loadMistakes,
    loadGroupedMistakes,
    loadSkillAreas,
    loadStats,
    setGrouping: handleSetGrouping,
    setPage,
    setItemsPerPage: handleSetItemsPerPage,
    setSelectedSkillArea: handleSetSelectedSkillArea,
    refresh,
    
    // Computed
    totalMistakes,
    hasNoMistakes,
    noMistakesMessage,
  };
}; 