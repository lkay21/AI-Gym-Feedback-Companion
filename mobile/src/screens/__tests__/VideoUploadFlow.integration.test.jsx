/**
 * Integration test: RecordVideoScreen → ExerciseSelectScreen
 *
 * Simulates the full video-upload entry flow using a real shared navigation
 * state object (instead of a native stack) to avoid native gesture-handler
 * dependencies that can't run in a Jest / Node environment.
 */
import React, { useState } from "react";
import { render, fireEvent, waitFor } from "@testing-library/react-native";
import RecordVideoScreen from "../RecordVideoScreen";
import ExerciseSelectScreen from "../ExerciseSelectScreen";

jest.mock("@expo/vector-icons", () => ({ Ionicons: "Ionicons" }));

function VideoUploadApp() {
  const [screen, setScreen] = useState("RecordVideo");

  const navigation = {
    navigate: (name) => setScreen(name),
    goBack: () => setScreen("RecordVideo"),
  };

  if (screen === "RecordVideo") {
    return <RecordVideoScreen navigation={navigation} />;
  }
  return <ExerciseSelectScreen navigation={navigation} />;
}

describe("Video upload flow integration", () => {
  it("navigates from RecordVideoScreen to ExerciseSelectScreen on Upload Video, then back", async () => {
    const { getByText, queryByText } = render(<VideoUploadApp />);

    // Start on RecordVideoScreen
    expect(getByText("Record a Video")).toBeTruthy();
    expect(queryByText("Select Your Exercise")).toBeNull();

    // Press Upload Video
    fireEvent.press(getByText("Upload Video"));

    await waitFor(() => {
      expect(getByText("Select Your Exercise")).toBeTruthy();
    });

    // ExerciseSelectScreen renders the exercise list
    expect(getByText("Exercise 1")).toBeTruthy();
    expect(getByText("Exercise 2")).toBeTruthy();
    expect(getByText("Exercise 3")).toBeTruthy();

    // Press Back — returns to RecordVideoScreen
    fireEvent.press(getByText("Back"));

    await waitFor(() => {
      expect(getByText("Record a Video")).toBeTruthy();
    });
  });

  it("does not navigate when Re-record Video is pressed", async () => {
    const { getByText, queryByText } = render(<VideoUploadApp />);

    fireEvent.press(getByText("Re-record Video"));

    await waitFor(() => {
      expect(getByText("Record a Video")).toBeTruthy();
      expect(queryByText("Select Your Exercise")).toBeNull();
    });
  });
});
