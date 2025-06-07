require('react-native/jest/setup.js');
global.__DEV__ = true;
require('jest-fetch-mock').enableMocks();

import 'react-native-gesture-handler/jestSetup';
import mockAsyncStorage from '@react-native-async-storage/async-storage/jest/async-storage-mock';

jest.mock('@react-native-async-storage/async-storage', () => mockAsyncStorage);

jest.mock('react-native-reanimated', () => require('react-native-reanimated/mock'));

jest.mock('react-native/Libraries/BatchedBridge/NativeModules', () => {
    const RNCCameraRoll = {
        saveToCameraRoll: jest.fn(),
        getPhotos: jest.fn(() => Promise.resolve({ edges: [] })),
    };

    const RNCNetInfo = {
        getCurrentState: jest.fn(() => Promise.resolve()),
        addListener: jest.fn(),
        removeListeners: jest.fn(),
    };

    const RNDeviceInfo = {
        getDeviceName: jest.fn(),
    };

    return {
        RNCCameraRoll,
        RNCNetInfo,
        RNDeviceInfo,
        // Add other native modules you use here
    };
});

// The following mocks are often handled by the react-native preset or are too aggressive.
// They are being removed to let the default Jest environment for React Native work correctly.
// A more targeted approach can be used if specific modules still cause issues. 