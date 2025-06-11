import React from 'react';
import AppNavigator from './shared/navigation/AppNavigator';
import { AuthProvider } from './features/auth/state/AuthContext';

const App = () => {
  return (
    <AuthProvider>
      <AppNavigator />
    </AuthProvider>
  );
};

export default App; 