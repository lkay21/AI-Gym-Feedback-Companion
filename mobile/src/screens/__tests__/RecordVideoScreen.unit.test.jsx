import React from "react";
import { render, fireEvent, waitFor, act } from "@testing-library/react-native";
import { Alert } from "react-native";
import RecordVideoScreen from "../RecordVideoScreen";

jest.mock("@expo/vector-icons", () => ({ Ionicons: "Ionicons" }));

jest.mock("../../services/api", () => ({
  cvAPI: {
    analyzeVideo: jest.fn(),
  },
}));

// Per-test AsyncStorage override (global mock from jest.setup.js handles the default).
jest.mock("@react-native-async-storage/async-storage", () => ({
  getItem: jest.fn().mockResolvedValue(null),
  setItem: jest.fn().mockResolvedValue(undefined),
}));

describe("RecordVideoScreen (UploadExerciseScreen) unit tests", () => {
  const mockNavigation = { navigate: jest.fn(), goBack: jest.fn() };
  const mockRoute = {};

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the screen title", () => {
    const { getByText } = render(
      <RecordVideoScreen navigation={mockNavigation} route={mockRoute} />
    );
    expect(getByText("Analyze Your Form")).toBeTruthy();
  });

  it("renders the Choose Exercise section label", () => {
    const { getByText } = render(
      <RecordVideoScreen navigation={mockNavigation} route={mockRoute} />
    );
    expect(getByText("Choose Exercise")).toBeTruthy();
  });

  it("renders Select an Exercise button when no exercise chosen", () => {
    const { getByText } = render(
      <RecordVideoScreen navigation={mockNavigation} route={mockRoute} />
    );
    expect(getByText("Select an Exercise")).toBeTruthy();
  });

  it("renders the Select Video section label", () => {
    const { getByText } = render(
      <RecordVideoScreen navigation={mockNavigation} route={mockRoute} />
    );
    expect(getByText("Select Video")).toBeTruthy();
  });

  it("renders the video drop zone", () => {
    const { getByText } = render(
      <RecordVideoScreen navigation={mockNavigation} route={mockRoute} />
    );
    expect(getByText("Tap to choose a video")).toBeTruthy();
  });

  it("renders the Upload & Get Feedback button", () => {
    const { getByText } = render(
      <RecordVideoScreen navigation={mockNavigation} route={mockRoute} />
    );
    expect(getByText("Upload & Get Feedback")).toBeTruthy();
  });

  it("navigates to ExerciseSelect when Select an Exercise is pressed", async () => {
    const { getByText } = render(
      <RecordVideoScreen navigation={mockNavigation} route={mockRoute} />
    );
    await act(async () => {
      fireEvent.press(getByText("Select an Exercise"));
    });
    expect(mockNavigation.navigate).toHaveBeenCalledWith("ExerciseSelect");
  });

  it("renders the pro tip guidance text", () => {
    const { getByText } = render(
      <RecordVideoScreen navigation={mockNavigation} route={mockRoute} />
    );
    expect(getByText("Pro tip")).toBeTruthy();
    expect(
      getByText(/Keep your full body in frame/i)
    ).toBeTruthy();
  });
});
