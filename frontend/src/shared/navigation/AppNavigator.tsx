import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuth } from '../../features/auth/state/AuthContext';
import WelcomeScreen from '../../features/auth/screens/WelcomeScreen';
import LoginScreen from '../../features/auth/screens/LoginScreen';
import MissionScreen from '../../features/mission/screens/MissionScreen';
import { ActivityIndicator, View } from 'react-native';

const Stack = createNativeStackNavigator();

const AppNavigator: React.FC = () => {
  const { isLoading, isAuthenticated, isGuest } = useAuth();

  console.log('AppNavigator state:', { isLoading, isAuthenticated, isGuest });

  if (isLoading) {
    // You can return a splash screen here
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated || isGuest ? (
          <Stack.Screen name="Mission" component={MissionScreen} />
        ) : (
          <>
            <Stack.Screen name="Welcome" component={WelcomeScreen} />
            <Stack.Screen name="Login" component={LoginScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator; 