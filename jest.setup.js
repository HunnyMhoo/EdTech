require('react-native/jest/setup.js');
global.__DEV__ = true;
require('jest-fetch-mock').enableMocks();

import 'react-native-gesture-handler/jestSetup';
import mockAsyncStorage from '@react-native-async-storage/async-storage/jest/async-storage-mock';

jest.mock('@react-native-async-storage/async-storage', () => mockAsyncStorage);

jest.mock('react-native-reanimated', () => require('react-native-reanimated/mock'));

jest.mock('react-native', () => {
    const RN = jest.requireActual('react-native');
  
    // Mock UIManager as it is often a source of issues
    RN.NativeModules.UIManager = {
      RCTView: {
        directViewConfig: {
          uiViewClassName: 'RCTView',
          validAttributes: {
            style: true,
          },
        },
      },
      customBubblingEventTypes: {},
      customDirectEventTypes: {},
    };

    // Mock Gesture Handler
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

// Mock React Native native modules that cause __fbBatchedBridgeConfig errors
jest.mock('react-native/Libraries/TurboModule/TurboModuleRegistry', () => ({
  getEnforcing: () => ({}),
}));
jest.mock('react-native/Libraries/StyleSheet/StyleSheet', () => ({
  create: styles => styles,
}));
jest.mock('react-native/Libraries/Components/View/ReactNativeStyleAttributes', () => ({}));
jest.mock('react-native/Libraries/NewAppScreen', () => ({}));
jest.mock('react-native/Libraries/Components/View/View', () => 'View');
// Mock React Native feature flag internals
jest.mock('react-native/src/private/featureflags/specs/NativeReactNativeFeatureFlags', () => ({}));
jest.mock('react-native/src/private/featureflags/ReactNativeFeatureFlagsBase', () => ({}));
jest.mock('react-native/src/private/featureflags/ReactNativeFeatureFlags', () => ({})); 