import React, { createContext, useState, useEffect, useContext } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

type AuthContextType = {
  isLoading: boolean;
  isAuthenticated: boolean;
  isGuest: boolean;
  userId: string | null;
  startGuestSession: () => void;
  signIn: (userId: string) => void;
  signOut: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isGuest, setIsGuest] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const checkSession = async () => {
      try {
        console.log('AuthContext: Checking session...');
        const sessionUserId = await AsyncStorage.getItem('userId');
        const sessionGuest = await AsyncStorage.getItem('isGuest');

        console.log('AuthContext: sessionUserId:', sessionUserId);
        console.log('AuthContext: sessionGuest:', sessionGuest);

        if (sessionUserId) {
          setUserId(sessionUserId);
          setIsAuthenticated(true);
        } else if (sessionGuest === 'true') {
          setUserId('test_user_123');
          setIsGuest(true);
        }
      } catch (e) {
        console.error("Failed to load session", e);
      } finally {
        setIsLoading(false);
        console.log('AuthContext: Finished checking session.');
      }
    };

    checkSession();
  }, []);

  const startGuestSession = async () => {
    try {
      await AsyncStorage.setItem('isGuest', 'true');
      setUserId('test_user_123');
      setIsGuest(true);
      setIsAuthenticated(false);
    } catch (e) {
      console.error("Failed to start guest session", e);
    }
  };

  const signIn = async (newUserId: string) => {
    try {
      await AsyncStorage.setItem('userId', newUserId);
      await AsyncStorage.removeItem('isGuest');
      setUserId(newUserId);
      setIsAuthenticated(true);
      setIsGuest(false);
    } catch (e) {
      console.error("Failed to sign in", e);
    }
  };

  const signOut = async () => {
    try {
      await AsyncStorage.removeItem('userId');
      await AsyncStorage.removeItem('isGuest');
      setUserId(null);
      setIsAuthenticated(false);
      setIsGuest(false);
    } catch (e) {
      console.error("Failed to sign out", e);
    }
  };

  console.log('AuthContext state:', { isLoading, isAuthenticated, isGuest, userId });

  return (
    <AuthContext.Provider
      value={{ isLoading, isAuthenticated, isGuest, userId, startGuestSession, signIn, signOut }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 