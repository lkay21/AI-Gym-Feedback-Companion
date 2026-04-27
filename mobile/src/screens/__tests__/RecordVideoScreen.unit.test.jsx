import React from "react";
import { render, fireEvent } from "@testing-library/react-native";
import RecordVideoScreen from "../RecordVideoScreen";

jest.mock("@expo/vector-icons", () => ({ Ionicons: "Ionicons" }));

describe("RecordVideoScreen unit tests", () => {
  const mockNavigation = { navigate: jest.fn() };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the screen title and section label", () => {
    const { getByText } = render(
      <RecordVideoScreen navigation={mockNavigation} />
    );
    expect(getByText("Record a Video")).toBeTruthy();
    expect(getByText("CV Processing Screen")).toBeTruthy();
  });

  it("renders recording instructions", () => {
    const { getByText } = render(
      <RecordVideoScreen navigation={mockNavigation} />
    );
    expect(getByText(/Click Start to begin recording/i)).toBeTruthy();
  });

  it("renders both action buttons", () => {
    const { getByText } = render(
      <RecordVideoScreen navigation={mockNavigation} />
    );
    expect(getByText("Re-record Video")).toBeTruthy();
    expect(getByText("Upload Video")).toBeTruthy();
  });

  it("renders guidance tip", () => {
    const { getByText } = render(
      <RecordVideoScreen navigation={mockNavigation} />
    );
    expect(getByText("Step Further Back!")).toBeTruthy();
    expect(
      getByText("Keep your full body within frame of the camera!")
    ).toBeTruthy();
  });

  it("navigates to ExerciseSelect when Upload Video is pressed", () => {
    const { getByText } = render(
      <RecordVideoScreen navigation={mockNavigation} />
    );
    fireEvent.press(getByText("Upload Video"));
    expect(mockNavigation.navigate).toHaveBeenCalledWith("ExerciseSelect");
  });

  it("does not navigate when Re-record Video is pressed", () => {
    const { getByText } = render(
      <RecordVideoScreen navigation={mockNavigation} />
    );
    fireEvent.press(getByText("Re-record Video"));
    expect(mockNavigation.navigate).not.toHaveBeenCalled();
  });
});
