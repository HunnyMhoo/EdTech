import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  SafeAreaView,
} from 'react-native';
import { useAuth } from '../../auth/state/AuthContext';
import { useReviewMistakes, GroupingType } from '../hooks/useReviewMistakes';
import { MistakeCard } from '../components/MistakeCard';
import { MistakeDetailModal } from '../components/MistakeDetailModal';
import { ReviewMistakeItem } from '../api/reviewMistakesApi';

export const ReviewMistakesScreen: React.FC = () => {
  const { userId } = useAuth();
  
  const {
    mistakes,
    groupedMistakes,
    groupCounts,
    skillAreas,
    stats,
    loading,
    error,
    grouping,
    pagination,
    currentPage,
    itemsPerPage,
    selectedSkillArea,
    setGrouping,
    setPage,
    setSelectedSkillArea,
    refresh,
    hasNoMistakes,
    noMistakesMessage,
    totalMistakes,
  } = useReviewMistakes(userId || '');

  const [selectedMistake, setSelectedMistake] = useState<ReviewMistakeItem | null>(null);
  const [modalVisible, setModalVisible] = useState(false);

  const handleMistakePress = (mistake: ReviewMistakeItem) => {
    setSelectedMistake(mistake);
    setModalVisible(true);
  };

  const handleCloseModal = () => {
    setModalVisible(false);
    setSelectedMistake(null);
  };

  const renderGroupingTabs = () => (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tabContainer}>
      <TouchableOpacity
        style={[styles.tab, grouping === 'none' && styles.activeTab]}
        onPress={() => setGrouping('none')}
      >
        <Text style={[styles.tabText, grouping === 'none' && styles.activeTabText]}>
          All Mistakes
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity
        style={[styles.tab, grouping === 'date' && styles.activeTab]}
        onPress={() => setGrouping('date')}
      >
        <Text style={[styles.tabText, grouping === 'date' && styles.activeTabText]}>
          By Date
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity
        style={[styles.tab, grouping === 'topic' && styles.activeTab]}
        onPress={() => setGrouping('topic')}
      >
        <Text style={[styles.tabText, grouping === 'topic' && styles.activeTabText]}>
          By Topic
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );

  const renderSkillAreaFilter = () => {
    if (skillAreas.length === 0) return null;

    return (
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterContainer}>
        <TouchableOpacity
          style={[styles.filterChip, !selectedSkillArea && styles.activeFilterChip]}
          onPress={() => setSelectedSkillArea(null)}
        >
          <Text style={[styles.filterChipText, !selectedSkillArea && styles.activeFilterChipText]}>
            All Topics
          </Text>
        </TouchableOpacity>
        
        {skillAreas.map((skillArea) => (
          <TouchableOpacity
            key={skillArea}
            style={[styles.filterChip, selectedSkillArea === skillArea && styles.activeFilterChip]}
            onPress={() => setSelectedSkillArea(skillArea)}
          >
            <Text style={[
              styles.filterChipText,
              selectedSkillArea === skillArea && styles.activeFilterChipText
            ]}>
              {skillArea}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    );
  };

  const renderSummaryStats = () => {
    if (!stats || hasNoMistakes) return null;

    return (
      <View style={styles.statsContainer}>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{stats.total_mistakes}</Text>
          <Text style={styles.statLabel}>Total Mistakes</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{stats.skill_areas_count}</Text>
          <Text style={styles.statLabel}>Topics</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>
            {Object.keys(stats.difficulty_breakdown).length}
          </Text>
          <Text style={styles.statLabel}>Difficulty Levels</Text>
        </View>
      </View>
    );
  };

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyIcon}>🎉</Text>
      <Text style={styles.emptyTitle}>Great job!</Text>
      <Text style={styles.emptyMessage}>{noMistakesMessage}</Text>
    </View>
  );

  const renderPagination = () => {
    if (!pagination || pagination.total_pages <= 1) return null;

    const renderPageButton = (page: number, isActive: boolean) => (
      <TouchableOpacity
        key={page}
        style={[styles.pageButton, isActive && styles.activePageButton]}
        onPress={() => setPage(page)}
      >
        <Text style={[styles.pageButtonText, isActive && styles.activePageButtonText]}>
          {page}
        </Text>
      </TouchableOpacity>
    );

    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(pagination.total_pages, currentPage + 2);
    const pages = [];

    for (let i = startPage; i <= endPage; i++) {
      pages.push(renderPageButton(i, i === currentPage));
    }

    return (
      <View style={styles.paginationContainer}>
        <TouchableOpacity
          style={[styles.navButton, !pagination.has_previous && styles.disabledButton]}
          onPress={() => pagination.has_previous && setPage(currentPage - 1)}
          disabled={!pagination.has_previous}
        >
          <Text style={[styles.navButtonText, !pagination.has_previous && styles.disabledButtonText]}>
            Previous
          </Text>
        </TouchableOpacity>

        <View style={styles.pageNumbers}>
          {pages}
        </View>

        <TouchableOpacity
          style={[styles.navButton, !pagination.has_next && styles.disabledButton]}
          onPress={() => pagination.has_next && setPage(currentPage + 1)}
          disabled={!pagination.has_next}
        >
          <Text style={[styles.navButtonText, !pagination.has_next && styles.disabledButtonText]}>
            Next
          </Text>
        </TouchableOpacity>
      </View>
    );
  };

  const renderGroupedMistakes = () => {
    const groups = Object.keys(groupedMistakes);
    
    return (
      <ScrollView
        style={styles.content}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={refresh} />}
      >
        {groups.map((groupKey) => (
          <View key={groupKey} style={styles.groupContainer}>
            <View style={styles.groupHeader}>
              <Text style={styles.groupTitle}>{groupKey}</Text>
              <Text style={styles.groupCount}>
                {groupCounts[groupKey]} mistake{groupCounts[groupKey] !== 1 ? 's' : ''}
              </Text>
            </View>
            
            {groupedMistakes[groupKey].map((mistake) => (
              <MistakeCard
                key={mistake.question_id}
                mistake={mistake}
                onPress={() => handleMistakePress(mistake)}
                showDate={grouping !== 'date'}
                compact={true}
              />
            ))}
          </View>
        ))}
        
        {renderPagination()}
      </ScrollView>
    );
  };

  const renderUngroupedMistakes = () => (
    <FlatList
      data={mistakes}
      renderItem={({ item }) => (
        <MistakeCard
          mistake={item}
          onPress={() => handleMistakePress(item)}
          showDate={true}
        />
      )}
      keyExtractor={(item) => item.question_id}
      style={styles.content}
      contentContainerStyle={styles.flatListContent}
      refreshControl={<RefreshControl refreshing={loading} onRefresh={refresh} />}
      ListFooterComponent={renderPagination}
    />
  );

  if (error) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Error: {error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={refresh}>
            <Text style={styles.retryButtonText}>Try Again</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Review My Past Mistakes</Text>
        {totalMistakes > 0 && (
          <Text style={styles.headerSubtitle}>
            {totalMistakes} mistake{totalMistakes !== 1 ? 's' : ''} to review
          </Text>
        )}
      </View>

      {hasNoMistakes ? (
        renderEmptyState()
      ) : (
        <>
          {renderSummaryStats()}
          {renderGroupingTabs()}
          {renderSkillAreaFilter()}
          
          {loading && !hasNoMistakes ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#3B82F6" />
              <Text style={styles.loadingText}>Loading mistakes...</Text>
            </View>
          ) : grouping === 'none' ? (
            renderUngroupedMistakes()
          ) : (
            renderGroupedMistakes()
          )}
        </>
      )}

      <MistakeDetailModal
        visible={modalVisible}
        mistake={selectedMistake}
        onClose={handleCloseModal}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '500',
  },
  statsContainer: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    marginHorizontal: 20,
    marginTop: 16,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 20,
    fontWeight: '700',
    color: '#3B82F6',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: '500',
  },
  statDivider: {
    width: 1,
    backgroundColor: '#E5E7EB',
    marginHorizontal: 16,
  },
  tabContainer: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  tab: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginRight: 12,
    borderRadius: 20,
    backgroundColor: '#F3F4F6',
  },
  activeTab: {
    backgroundColor: '#3B82F6',
  },
  tabText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
  },
  activeTabText: {
    color: '#FFFFFF',
  },
  filterContainer: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  filterChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 8,
    borderRadius: 16,
    backgroundColor: '#F9FAFB',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  activeFilterChip: {
    backgroundColor: '#EBF4FF',
    borderColor: '#3B82F6',
  },
  filterChipText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#6B7280',
  },
  activeFilterChipText: {
    color: '#3B82F6',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 16,
  },
  flatListContent: {
    paddingBottom: 20,
  },
  groupContainer: {
    marginBottom: 24,
  },
  groupHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    paddingHorizontal: 4,
  },
  groupTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  groupCount: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '500',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 8,
    textAlign: 'center',
  },
  emptyMessage: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 24,
  },
  paginationContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 20,
    paddingHorizontal: 4,
  },
  navButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: '#3B82F6',
  },
  disabledButton: {
    backgroundColor: '#E5E7EB',
  },
  navButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  disabledButtonText: {
    color: '#9CA3AF',
  },
  pageNumbers: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  pageButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 4,
    backgroundColor: '#F3F4F6',
  },
  activePageButton: {
    backgroundColor: '#3B82F6',
  },
  pageButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
  },
  activePageButtonText: {
    color: '#FFFFFF',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#6B7280',
    fontWeight: '500',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  errorText: {
    fontSize: 16,
    color: '#EF4444',
    textAlign: 'center',
    marginBottom: 20,
  },
  retryButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: '#3B82F6',
  },
  retryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
}); 