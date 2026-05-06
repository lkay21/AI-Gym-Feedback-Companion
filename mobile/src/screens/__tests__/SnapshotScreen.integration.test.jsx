import React from "react";
import { Text } from "react-native";
import { fireEvent, render, waitFor } from "@testing-library/react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import SnapshotScreen from "../SnapshotScreen";
import { chatAPI } from "../../services/api";

jest.mock("@expo/vector-icons", () => {
  const React = require("react");
  const { Text } = require("react-native");
  return {
    Ionicons: ({ name }) => <Text>{name}</Text>,
  };
});

jest.mock("../../components/MenuDropdown", () => {
  const React = require("react");
  const { Text } = require("react-native");
  return function MockMenuDropdown() {
    return <Text>Mock MenuDropdown</Text>;
  };
});

jest.mock("react-native-calendars", () => {
  const React = require("react");
  const { Text } = require("react-native");
  return {
    Calendar: ({ onDayPress }) => (
      <Text testID="snapshot-calendar" onPress={() => onDayPress({ dateString: "2026-02-16" })}>
        Mock Calendar
      </Text>
    ),
  };
});

jest.mock("../../services/api", () => ({
  chatAPI: {
    generatePlan: jest.fn(),
  },
}));

describe("SnapshotScreen generated plan integration", () => {
  const navigation = { navigate: jest.fn() };

  const structuredPlan = {
    planName: "2 Week Strength Plan",
    startDate: "2026-02-15",
    weeks: [
      {
        weekNumber: 1,
        days: [
          {
            date: "2026-02-15",
            workoutType: "Upper Body",
            estimatedDurationMinutes: 45,
            exercises: [{ name: "Bench Press", sets: 3, reps: 8, weight: "70 lbs" }],
          },
          {
            date: "2026-02-16",
            workoutType: "Lower Body",
            estimatedDurationMinutes: 40,
            exercises: [{ name: "Squat", sets: 4, reps: 6, weight: "95 lbs" }],
          },
        ],
      },
    ],
  };

  beforeEach(() => {
    jest.clearAllMocks();
    AsyncStorage.getItem.mockResolvedValue("user-123");
    AsyncStorage.setItem.mockResolvedValue();
  });

  it("renders snapshot content from generated fitness plan", async () => {
    chatAPI.generatePlan.mockResolvedValueOnce({
      success: true,
      data: { structuredPlan },
    });

    const { getByText, queryByText } = render(<SnapshotScreen navigation={navigation} />);

    expect(getByText("Loading your plan…")).toBeTruthy();

    await waitFor(() => {
      expect(queryByText("Loading your plan…")).toBeNull();
      expect(getByText("Workout Snapshot")).toBeTruthy();
      expect(getByText("2 Week Strength Plan")).toBeTruthy();
      expect(getByText("Upper Body")).toBeTruthy();
      expect(getByText("Bench Press")).toBeTruthy();
    });
  });

  it("updates displayed workout details when another date is selected", async () => {
    chatAPI.generatePlan.mockResolvedValueOnce({
      success: true,
      data: { structuredPlan },
    });

    const { getByText } = render(<SnapshotScreen navigation={navigation} />);

    await waitFor(() => {
      expect(getByText("Bench Press")).toBeTruthy();
    });

    fireEvent.press(getByText("Mock Calendar"));

    await waitFor(() => {
      expect(getByText("Lower Body")).toBeTruthy();
      expect(getByText("Squat")).toBeTruthy();
    });
  });

  it("shows onboarding error when plan generation requires profile completion", async () => {
    chatAPI.generatePlan.mockResolvedValueOnce({
      success: false,
      data: { requiresOnboarding: true },
    });

    const { getByText } = render(<SnapshotScreen navigation={navigation} />);

    await waitFor(() => {
      expect(
        getByText("Complete your health profile and generate a plan in Chat first.")
      ).toBeTruthy();
      expect(getByText("Retry")).toBeTruthy();
    });
  });
});
