module.exports = {
  preset: "jest-expo",
  setupFiles: [
    "./jestSetup.js"
  ],7
  transformIgnorePatterns: [
    "node_modules/(?!((jest-)?react-native|@react-native(-community)?|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|react-native-svg))",
  ],
};