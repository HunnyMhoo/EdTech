import { jest } from '@jest/globals';

jest.mock('react-native/Libraries/StyleSheet/StyleSheet', () => ({
    create: styles => styles,
})); 