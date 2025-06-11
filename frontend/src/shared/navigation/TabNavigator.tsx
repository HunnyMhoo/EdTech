import React, { useState } from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, Text } from 'react-native';
import MissionScreen from '../../features/mission/screens/MissionScreen';
import PracticeHomeScreen from '../../features/practice/screens/PracticeHomeScreen';
import PracticeSessionScreen from '../../features/practice/screens/PracticeSessionScreen';

const Tab = createBottomTabNavigator();

type PracticeState = {
  mode: 'home' | 'session' | 'complete';
  sessionId?: string;
};

const TabNavigator: React.FC = () => {
  const [practiceState, setPracticeState] = useState<PracticeState>({ mode: 'home' });

  const handleStartPracticeSession = (sessionId: string) => {
    setPracticeState({ mode: 'session', sessionId });
  };

  const handlePracticeSessionComplete = () => {
    setPracticeState({ mode: 'home' });
  };

  const handleBackToPracticeHome = () => {
    setPracticeState({ mode: 'home' });
  };

  const PracticeStackScreen = () => {
    switch (practiceState.mode) {
      case 'session':
        return (
          <PracticeSessionScreen
            sessionId={practiceState.sessionId!}
            onSessionComplete={handlePracticeSessionComplete}
            onBackToHome={handleBackToPracticeHome}
          />
        );
      case 'home':
      default:
        return (
          <PracticeHomeScreen
            onStartSession={handleStartPracticeSession}
          />
        );
    }
  };

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#666',
        tabBarStyle: {
          backgroundColor: '#fff',
          borderTopWidth: 1,
          borderTopColor: '#E0E0E0',
          paddingTop: 5,
          paddingBottom: 5,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
      }}
    >
      <Tab.Screen
        name="DailyMission"
        component={MissionScreen}
        options={{
          tabBarLabel: 'Daily Mission',
          tabBarIcon: ({ focused, color }) => (
            <View style={{ alignItems: 'center' }}>
              <Text style={{ fontSize: 20, color }}>📚</Text>
            </View>
          ),
        }}
      />
      <Tab.Screen
        name="Practice"
        component={PracticeStackScreen}
        options={{
          tabBarLabel: 'Free Practice',
          tabBarIcon: ({ focused, color }) => (
            <View style={{ alignItems: 'center' }}>
              <Text style={{ fontSize: 20, color }}>🎯</Text>
            </View>
          ),
        }}
      />
    </Tab.Navigator>
  );
};

export default TabNavigator; 