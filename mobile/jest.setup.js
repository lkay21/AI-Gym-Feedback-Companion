// Must run before screens that import AsyncStorage (see async-storage Jest docs).
jest.mock("@react-native-async-storage/async-storage", () =>
  require("@react-native-async-storage/async-storage/jest/async-storage-mock")
);
