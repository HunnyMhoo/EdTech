require('react-native/jest/setup.js');
global.__DEV__ = true;
require('jest-fetch-mock').enableMocks();

import 'react-native-gesture-handler/jestSetup';
import mockAsyncStorage from '@react-native-async-storage/async-storage/jest/async-storage-mock';

jest.mock('@react-native-async-storage/async-storage', () => mockAsyncStorage);

jest.mock('react-native-reanimated', () => require('react-native-reanimated/mock'));

// Reset modules and mock 'react-native' to ensure a clean environment
jest.resetModules();

jest.mock('react-native', () => {
  const RN = jest.requireActual('react-native');

  // Globally mock StyleSheet
  RN.StyleSheet = {
    ...RN.StyleSheet,
    create: styles => styles,
  };

  // Mock other native modules as needed
  RN.NativeModules.UIManager = {
    RCTView: {
      directViewConfig: {
        uiViewClassName: 'RCTView',
        validAttributes: { style: true },
      },
    },
    customBubblingEventTypes: {},
    customDirectEventTypes: {},
  };

  RN.NativeModules.RNGestureHandlerModule = {
    attachGestureHandler: jest.fn(),
    createGestureHandler: jest.fn(),
    dropGestureHandler: jest.fn(),
    updateGestureHandler: jest.fn(),
    State: {},
    Directions: {},
  };

  // Mock SettingsManager
  RN.NativeModules.SettingsManager = {
    settings: {
      AppleLocale: 'en_US',
      AppleLanguages: ['en-US'],
    },
  };

  return RN;
});

// Clean up any other specific mocks that might conflict
jest.mock('react-native/Libraries/TurboModule/TurboModuleRegistry', () => ({
  getEnforcing: () => ({}),
}));
jest.mock('react-native/Libraries/StyleSheet/StyleSheet', () => ({
  create: styles => styles,
}));
jest.mock('react-native/Libraries/Components/View/ReactNativeStyleAttributes', () => ({}));
jest.mock('react-native/Libraries/NewAppScreen', () => ({}));
jest.mock('react-native/Libraries/Components/View/View', () => 'View');
jest.mock('react-native/src/private/featureflags/specs/NativeReactNativeFeatureFlags', () => ({}));
jest.mock('react-native/src/private/featureflags/ReactNativeFeatureFlagsBase', () => ({}));
jest.mock('react-native/src/private/featureflags/ReactNativeFeatureFlags', () => ({})); 