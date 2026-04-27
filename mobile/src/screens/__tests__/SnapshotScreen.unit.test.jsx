import React from "react";
import { render, fireEvent, waitFor, act } from "@testing-library/react-native";
import SnapshotScreen from "../SnapshotScreen";

jest.mock("react-native-calendars", () => {
  const React = require("react");
  const { Text } = require("react-native");
  return {
    Calendar: ({ onDayPress }) => (
      <Text
        testID="calendar"
        onPress={() => onDayPress({ dateString: "2026-04-28" })}
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

jest.mock("../../services/api", () => ({
  chatAPI: { generatePlan: jest.fn() },
}));

jest.mock("../../utils/planMapping", () => ({
  mapPlanToCalendarEvents: jest.fn(),
}));

import { chatAPI } from "../../services/api";
import { mapPlanToCalendarEvents } from "../../utils/planMapping";

const MOCK_EVENTS = [
  {
    date: "2026-04-28",
    type: "workout",
    title: "Upper Body",
    metadata: {
      workoutType: "Upper Body",
      estimatedDurationMinutes: 45,
      exercises: [{ name: "Bench Press", sets: 3, reps: 10 }],
    },
  },
];

const MOCK_PLAN_RESPONSE = {
  success: true,
  data: {
    structuredPlan: { planName: "My Test Plan", weeks: [] },
  },
};

describe("SnapshotScreen unit tests", () => {
  const mockNavigation = { navigate: jest.fn() };

  beforeEach(() => {
    jest.clearAllMocks();
    chatAPI.generatePlan.mockResolvedValue(MOCK_PLAN_RESPONSE);
    mapPlanToCalendarEvents.mockReturnValue(MOCK_EVENTS);
  });

  it("renders screen title and header on initial mount", () => {
    const { getByText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    expect(getByText("Workout Snapshot")).toBeTruthy();
    expect(getByText("Today's Snapshot")).toBeTruthy();
  });

  it("shows loading indicator while plan is fetching", () => {
    const { getByText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    expect(getByText("Loading your plan…")).toBeTruthy();
  });

  it("shows plan name after successful API load", async () => {
    const { getByText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    await waitFor(() => {
      expect(getByText("My Test Plan")).toBeTruthy();
    });
  });

  it("shows error text and Retry button when API fails", async () => {
    chatAPI.generatePlan.mockResolvedValue({
      success: false,
      error: "Server unavailable",
    });
    const { getByText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    await waitFor(() => {
      expect(getByText("Server unavailable")).toBeTruthy();
      expect(getByText("Retry")).toBeTruthy();
    });
  });

  it("retries loading when Retry is pressed", async () => {
    chatAPI.generatePlan
      .mockResolvedValueOnce({ success: false, error: "Server unavailable" })
      .mockResolvedValueOnce(MOCK_PLAN_RESPONSE);

    const { getByText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    await waitFor(() => expect(getByText("Retry")).toBeTruthy());

    await act(async () => {
      fireEvent.press(getByText("Retry"));
    });

    await waitFor(() => {
      expect(getByText("My Test Plan")).toBeTruthy();
    });
    expect(chatAPI.generatePlan).toHaveBeenCalledTimes(2);
  });

  it("does not navigate when prompt is empty", async () => {
    const { getByPlaceholderText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    // Flush the initial chatAPI.generatePlan call so there are no pending updates.
    await act(async () => {});
    const input = getByPlaceholderText("Enter Your Prompt Here...");
    fireEvent(input, "submitEditing");
    expect(mockNavigation.navigate).not.toHaveBeenCalled();
  });

  it("does not navigate when prompt is whitespace only", async () => {
    const { getByPlaceholderText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    await act(async () => {});
    const input = getByPlaceholderText("Enter Your Prompt Here...");
    fireEvent.changeText(input, "   ");
    fireEvent(input, "submitEditing");
    expect(mockNavigation.navigate).not.toHaveBeenCalled();
  });

  it("navigates to ChatBot with prompt text and clears input on send", async () => {
    const { getByPlaceholderText } = render(
      <SnapshotScreen navigation={mockNavigation} />
    );
    await act(async () => {});
    const input = getByPlaceholderText("Enter Your Prompt Here...");
    fireEvent.changeText(input, "How do I squat correctly?");
    fireEvent(input, "submitEditing");
    expect(mockNavigation.navigate).toHaveBeenCalledWith("ChatBot", {
      q: "How do I squat correctly?",
    });
    expect(input.props.value).toBe("");
  });
});
