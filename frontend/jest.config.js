module.exports = {
  preset: 'react-native',
  rootDir: '.',
  setupFiles: ['<rootDir>/jest-setup-files.js'],
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  testPathIgnorePatterns: [
    '/node_modules/',
    '/e2e/'
  ],
  transformIgnorePatterns: [
    '/node_modules/(?!((jest-)?react-native|@react-native(-community)?)/)',
  ],
  moduleNameMapper: {
    '^@components/(.*)$': '<rootDir>/components/$1',
    '^@screens/(.*)$': '<rootDir>/screens/$1',
    '^@services/(.*)$': '<rootDir>/services/$1',
    '^@hooks/(.*)$': '<rootDir>/hooks/$1',
    '^@config/(.*)$': '<rootDir>/config/$1',
    '^@assets/(.*)$': '<rootDir>/assets/$1',
    '^@navigation/(.*)$': '<rootDir>/navigation/$1',
    '^@utils/(.*)$': '<rootDir>/utils/$1',
    '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js',
    '^react-native/Libraries/StyleSheet/StyleSheet$': '<rootDir>/__mocks__/StyleSheet.mock.js',
  }
}; 