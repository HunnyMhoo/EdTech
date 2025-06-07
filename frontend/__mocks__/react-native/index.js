const RN = jest.requireActual('react-native');

RN.StyleSheet = {
  create: (styles) => styles,
};

module.exports = RN; 