module.exports = {
  preset: 'react-native',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  testPathIgnorePatterns: [
    '/node_modules/',
    '/e2e/'
  ],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/frontend/src/$1'
  },
  transformIgnorePatterns: [
    "node_modules/(?!(react-native|@react-native|@react-native-community|@testing-library|react-navigation|@react-navigation|react-native-gesture-handler|react-native-reanimated)/)"
  ],
}; 