import React from "react";
import { render, fireEvent } from "@testing-library/react-native";
import SnapshotScreen from "../SnapshotScreen";

jest.mock("react-native-calendars", () => {
  const React = require("react");
  const { Text } = require("react-native");
  return {
    Calendar: ({ onDayPress }) => (
      <Text
        testID="calendar"
        onPress={() => onDayPress({ dateString: "2025-12-15" })}
      >
        Calendar
      </Text>
    ),
  };
});

jest.mock("../../components/MenuDropdown", () => {
  const React = require("react");
  const { Text } = require("react-native");
  return function MockMenuDropdown() {
    return <Text>Menu</Text>;
  };
});

jest.mock("@expo/vector-icons", () => ({ Ionicons: "Ionicons" }));

describe("SnapshotScreen unit tests", () => {
  const mockNavigation = { navigate: jest.fn() };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders screen title and section headers", () => {
    const { getByText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    expect(getByText("Workout Snapshot")).toBeTruthy();
    expect(getByText("Today's Snapshot")).toBeTruthy();
    expect(getByText("Targeted Muscle Groups")).toBeTruthy();
  });

  it("renders all five day pills", () => {
    const { getByText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    expect(getByText("Sat")).toBeTruthy();
    expect(getByText("Sun")).toBeTruthy();
    expect(getByText("Mon")).toBeTruthy();
    expect(getByText("Tue")).toBeTruthy();
    expect(getByText("Wed")).toBeTruthy();
  });

  it("renders all three exercises in the session card", () => {
    const { getByText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    expect(getByText("Exercise 1")).toBeTruthy();
    expect(getByText("Exercise 2")).toBeTruthy();
    expect(getByText("Exercise 3")).toBeTruthy();
  });

  it("renders session card warmup info", () => {
    const { getByText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    // Use regex to avoid smart-quote vs straight-quote mismatch in source
    expect(getByText(/Starting Today.s Session/)).toBeTruthy();
    expect(getByText("10.00 mins")).toBeTruthy();
    expect(getByText("Running")).toBeTruthy();
    expect(getByText("Exercises")).toBeTruthy();
  });

  it("does not navigate when prompt is empty", () => {
    const { getByPlaceholderText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    const input = getByPlaceholderText("Enter Your Prompt Here...");
    fireEvent(input, "submitEditing");
    expect(mockNavigation.navigate).not.toHaveBeenCalled();
  });

  it("does not navigate when prompt is whitespace only", () => {
    const { getByPlaceholderText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    const input = getByPlaceholderText("Enter Your Prompt Here...");
    fireEvent.changeText(input, "   ");
    fireEvent(input, "submitEditing");
    expect(mockNavigation.navigate).not.toHaveBeenCalled();
  });

  it("navigates to ChatBot with prompt text and clears input on send", () => {
    const { getByPlaceholderText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    const input = getByPlaceholderText("Enter Your Prompt Here...");
    fireEvent.changeText(input, "How do I squat correctly?");
    fireEvent(input, "submitEditing");

    expect(mockNavigation.navigate).toHaveBeenCalledWith("ChatBot", {
      q: "How do I squat correctly?",
    });
    expect(input.props.value).toBe("");
  });

  it("updates selected day pill when pressed", () => {
    const { getByText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    fireEvent.press(getByText("Sat"));
    // Sat pill should now be active — no crash and pill renders correctly
    expect(getByText("Sat")).toBeTruthy();
  });
});
