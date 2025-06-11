import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  TextInput,
  Alert,
} from 'react-native';
import { PracticeTopic } from '../api/practiceApi';

interface TopicSelectorProps {
  topics: PracticeTopic[];
  selectedTopic: string;
  questionCount: number;
  onTopicSelect: (topic: string) => void;
  onQuestionCountChange: (count: number) => void;
  onStartPractice: () => void;
  isLoading?: boolean;
}

const TopicSelector: React.FC<TopicSelectorProps> = ({
  topics,
  selectedTopic,
  questionCount,
  onTopicSelect,
  onQuestionCountChange,
  onStartPractice,
  isLoading = false,
}) => {
  const [customCount, setCustomCount] = useState(questionCount.toString());

  const handleQuestionCountChange = (text: string) => {
    setCustomCount(text);
    const count = parseInt(text);
    if (!isNaN(count) && count > 0 && count <= 20) {
      onQuestionCountChange(count);
    }
  };

  const handleStartPractice = () => {
    if (!selectedTopic) {
      Alert.alert('Select Topic', 'Please select a topic to practice.');
      return;
    }

    const selectedTopicData = topics.find(t => t.name === selectedTopic);
    if (!selectedTopicData?.available) {
      Alert.alert('Topic Unavailable', 'This topic is not available for practice.');
      return;
    }

    if (questionCount > selectedTopicData.question_count) {
      Alert.alert(
        'Not Enough Questions',
        `This topic only has ${selectedTopicData.question_count} questions available.`
      );
      return;
    }

    onStartPractice();
  };

  const availableTopics = topics.filter(topic => topic.available);
  const selectedTopicData = topics.find(t => t.name === selectedTopic);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Choose Your Practice Topic</Text>
      
      {/* Topic Selection */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Select Topic</Text>
        <ScrollView 
          style={styles.topicList}
          showsVerticalScrollIndicator={false}
        >
          {availableTopics.map((topic) => (
            <TouchableOpacity
              key={topic.name}
              style={[
                styles.topicItem,
                selectedTopic === topic.name && styles.selectedTopicItem,
              ]}
              onPress={() => onTopicSelect(topic.name)}
            >
              <View style={styles.topicInfo}>
                <Text
                  style={[
                    styles.topicName,
                    selectedTopic === topic.name && styles.selectedTopicName,
                  ]}
                >
                  {topic.name}
                </Text>
                <Text style={styles.questionCount}>
                  {topic.question_count} questions available
                </Text>
              </View>
              {selectedTopic === topic.name && (
                <Text style={styles.checkmark}>✓</Text>
              )}
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Question Count Selection */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Number of Questions</Text>
        <View style={styles.questionCountContainer}>
          {/* Quick Select Buttons */}
          <View style={styles.quickSelectRow}>
            {[5, 10, 15, 20].map((count) => (
              <TouchableOpacity
                key={count}
                style={[
                  styles.quickSelectButton,
                  questionCount === count && styles.selectedQuickSelect,
                  selectedTopicData && count > selectedTopicData.question_count && styles.disabledButton,
                ]}
                onPress={() => {
                  if (!selectedTopicData || count <= selectedTopicData.question_count) {
                    onQuestionCountChange(count);
                    setCustomCount(count.toString());
                  }
                }}
                disabled={selectedTopicData && count > selectedTopicData.question_count}
              >
                <Text
                  style={[
                    styles.quickSelectText,
                    questionCount === count && styles.selectedQuickSelectText,
                    selectedTopicData && count > selectedTopicData.question_count && styles.disabledText,
                  ]}
                >
                  {count}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Custom Input */}
          <View style={styles.customInputContainer}>
            <Text style={styles.customInputLabel}>Custom:</Text>
            <TextInput
              style={styles.customInput}
              value={customCount}
              onChangeText={handleQuestionCountChange}
              keyboardType="numeric"
              placeholder="1-20"
              placeholderTextColor="#999"
              maxLength={2}
            />
          </View>

          {selectedTopicData && (
            <Text style={styles.maxQuestionsHint}>
              Max: {selectedTopicData.question_count} for this topic
            </Text>
          )}
        </View>
      </View>

      {/* Start Button */}
      <TouchableOpacity
        style={[
          styles.startButton,
          (!selectedTopic || isLoading) && styles.disabledButton,
        ]}
        onPress={handleStartPractice}
        disabled={!selectedTopic || isLoading}
      >
        <Text
          style={[
            styles.startButtonText,
            (!selectedTopic || isLoading) && styles.disabledText,
          ]}
        >
          {isLoading ? 'Starting...' : 'Start Practice'}
        </Text>
      </TouchableOpacity>

      {/* Summary */}
      {selectedTopic && (
        <View style={styles.summary}>
          <Text style={styles.summaryText}>
            Ready to practice <Text style={styles.summaryHighlight}>{selectedTopic}</Text> with{' '}
            <Text style={styles.summaryHighlight}>{questionCount}</Text> questions
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#F5F5F5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 24,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  topicList: {
    maxHeight: 200,
  },
  topicItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  selectedTopicItem: {
    backgroundColor: '#E3F2FD',
    borderColor: '#007AFF',
    borderWidth: 2,
  },
  topicInfo: {
    flex: 1,
  },
  topicName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  selectedTopicName: {
    color: '#007AFF',
  },
  questionCount: {
    fontSize: 14,
    color: '#666',
  },
  checkmark: {
    fontSize: 20,
    color: '#007AFF',
    fontWeight: 'bold',
  },
  questionCountContainer: {
    backgroundColor: '#fff',
    padding: 16,
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
  quickSelectRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  quickSelectButton: {
    flex: 1,
    paddingVertical: 12,
    marginHorizontal: 4,
    backgroundColor: '#F0F0F0',
    borderRadius: 6,
    alignItems: 'center',
  },
  selectedQuickSelect: {
    backgroundColor: '#007AFF',
  },
  quickSelectText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
  selectedQuickSelectText: {
    color: '#fff',
  },
  customInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  customInputLabel: {
    fontSize: 16,
    color: '#333',
    marginRight: 12,
  },
  customInput: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: '#F9F9F9',
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#DDD',
    fontSize: 16,
    color: '#333',
  },
  maxQuestionsHint: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  startButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 16,
  },
  startButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
  },
  disabledButton: {
    backgroundColor: '#CCC',
  },
  disabledText: {
    color: '#999',
  },
  summary: {
    backgroundColor: '#E8F5E8',
    padding: 16,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  summaryText: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
  },
  summaryHighlight: {
    fontWeight: '600',
    color: '#4CAF50',
  },
});

export default TopicSelector; 