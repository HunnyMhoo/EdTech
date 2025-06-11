import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
import { useAuth } from '../state/AuthContext';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

type RootStackParamList = {
  Welcome: undefined;
  Login: undefined;
};

type WelcomeScreenProps = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Welcome'>;
};

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ navigation }) => {
  const { startGuestSession } = useAuth();

  console.log('WelcomeScreen: Rendering');

  const handleGuestLogin = () => {
    startGuestSession();
    // The AppNavigator will handle the screen change
  };

  const handleGoToLogin = () => {
    navigation.navigate('Login');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome to the App!</Text>
      <Text style={styles.subtitle}>Try it out as a guest or sign in.</Text>
      <View style={styles.buttonContainer}>
        <Button title="Quick Start" onPress={handleGuestLogin} />
      </View>
      <View style={styles.buttonContainer}>
        <Button title="Sign In" onPress={handleGoToLogin} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: 'gray',
    marginBottom: 30,
    textAlign: 'center',
  },
  buttonContainer: {
    width: '80%',
    marginVertical: 10,
  },
});

export default WelcomeScreen; 