/**
 * Integration test: UploadExerciseScreen (RecordVideoScreen) → ExerciseSelectScreen
 *
 * Uses a shared React state object to simulate navigation without a native
 * NavigationContainer, which avoids gesture-handler dependencies in Jest.
 */
import React, { useState } from "react";
import { render, fireEvent, waitFor, act } from "@testing-library/react-native";
import RecordVideoScreen from "../RecordVideoScreen";
import ExerciseSelectScreen from "../ExerciseSelectScreen";

jest.mock("@expo/vector-icons", () => ({ Ionicons: "Ionicons" }));

jest.mock("../../services/api", () => ({
  cvAPI: { analyzeVideo: jest.fn() },
}));

jest.mock("@react-native-async-storage/async-storage", () => ({
  getItem: jest.fn().mockResolvedValue(null),
  setItem: jest.fn().mockResolvedValue(undefined),
}));

function VideoUploadApp() {
  const [screen, setScreen] = useState("RecordVideo");
  const [routeParams, setRouteParams] = useState({});

  const navigation = {
    navigate: (name, params) => {
      setRouteParams(params ?? {});
      setScreen(name);
    },
    goBack: () => setScreen("RecordVideo"),
  };

  if (screen === "RecordVideo") {
    return (
      <RecordVideoScreen
        navigation={navigation}
        route={{ params: routeParams }}
      />
    );
  }
  return <ExerciseSelectScreen navigation={navigation} />;
}

describe("Video upload flow integration", () => {
  it("starts on UploadExerciseScreen and not on ExerciseSelectScreen", () => {
    const { getByText, queryByText } = render(<VideoUploadApp />);
    expect(getByText("Analyze Your Form")).toBeTruthy();
    expect(queryByText("Select Your Exercise")).toBeNull();
  });

  it("navigates to ExerciseSelectScreen when Select an Exercise is pressed", async () => {
    const { getByText, queryByText } = render(<VideoUploadApp />);

    await act(async () => {
      fireEvent.press(getByText("Select an Exercise"));
    });

    await waitFor(() => {
      expect(getByText("Select Your Exercise")).toBeTruthy();
    });
    expect(queryByText("Analyze Your Form")).toBeNull();
  });

  it("ExerciseSelectScreen lists exercises", async () => {
    const { getByText } = render(<VideoUploadApp />);

    await act(async () => {
      fireEvent.press(getByText("Select an Exercise"));
    });

    await waitFor(() => {
      expect(getByText("Bicep Curl (Biceps)")).toBeTruthy();
      expect(getByText("Lateral Raise (Shoulders)")).toBeTruthy();
    });
  });

  it("pressing Back on ExerciseSelectScreen returns to UploadExerciseScreen", async () => {
    const { getByText } = render(<VideoUploadApp />);

    await act(async () => {
      fireEvent.press(getByText("Select an Exercise"));
    });
    await waitFor(() => expect(getByText("Select Your Exercise")).toBeTruthy());

    await act(async () => {
      fireEvent.press(getByText("Back"));
    });

    await waitFor(() => {
      expect(getByText("Analyze Your Form")).toBeTruthy();
    });
  });
});
