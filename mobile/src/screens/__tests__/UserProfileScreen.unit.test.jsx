import React from "react";
import { render, fireEvent, waitFor, act } from "@testing-library/react-native";
import { Alert } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import UserProfileScreen from "../UserProfileScreen";

// Inline factory so the mock isn't affected by jest.mock hoisting
jest.mock("@react-native-async-storage/async-storage", () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  multiRemove: jest.fn(),
}));

jest.mock("@expo/vector-icons", () => ({ Ionicons: "Ionicons" }));

jest.mock("../../components/MenuDropdown", () => {
  const React = require("react");
  const { Text } = require("react-native");
  return function MockMenuDropdown() {
    return <Text>Menu</Text>;
  };
});

describe("UserProfileScreen unit tests", () => {
  const mockNavigation = {
    navigate: jest.fn(),
    reset: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    AsyncStorage.getItem.mockResolvedValue(null);
    AsyncStorage.setItem.mockResolvedValue(undefined);
    AsyncStorage.multiRemove.mockResolvedValue(undefined);
  });

  it("renders all profile field labels", async () => {
    const { getByText } = render(
      <UserProfileScreen navigation={mockNavigation} />
    );
    await waitFor(() => {
      expect(getByText("Email")).toBeTruthy();
      expect(getByText("Weight")).toBeTruthy();
      expect(getByText("Height")).toBeTruthy();
      expect(getByText("Fitness Goals")).toBeTruthy();
    });
  });

  it("renders save and logout buttons", async () => {
    const { getByText } = render(
      <UserProfileScreen navigation={mockNavigation} />
    );
    await waitFor(() => {
      expect(getByText("Save Profile")).toBeTruthy();
      expect(getByText("Log Out")).toBeTruthy();
    });
  });

  it("loads and displays stored profile email on mount", async () => {
    AsyncStorage.getItem.mockResolvedValue(
      JSON.stringify({ email: "test@example.com", weight: "180 lbs" })
    );

    const { getByDisplayValue } = render(
      <UserProfileScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByDisplayValue("test@example.com")).toBeTruthy();
    });
  });

  it("shows avatar letter derived from stored email", async () => {
    AsyncStorage.getItem.mockResolvedValue(
      JSON.stringify({ email: "alice@example.com" })
    );

    const { getByText } = render(
      <UserProfileScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText("A")).toBeTruthy();
    });
  });

  it("saves profile to AsyncStorage and shows Saved! on success", async () => {
    const { getByText } = render(
      <UserProfileScreen navigation={mockNavigation} />
    );

    // Wait for the initial async loadProfile to finish (loading → false)
    // so the Save button is no longer disabled.
    await act(async () => {});

    await act(async () => {
      fireEvent.press(getByText("Save Profile"));
    });

    await waitFor(() => {
      expect(AsyncStorage.setItem).toHaveBeenCalledWith(
        "userProfile",
        expect.any(String)
      );
      expect(getByText("Saved!")).toBeTruthy();
    });
  });

  it("shows error alert when AsyncStorage.setItem fails", async () => {
    AsyncStorage.setItem.mockRejectedValue(new Error("Storage full"));
    const alertSpy = jest.spyOn(Alert, "alert");

    const { getByText } = render(
      <UserProfileScreen navigation={mockNavigation} />
    );

    // Wait for initial load to finish before pressing Save
    await act(async () => {});

    await act(async () => {
      fireEvent.press(getByText("Save Profile"));
    });

    await waitFor(() => {
      expect(alertSpy).toHaveBeenCalledWith(
        "Error",
        "Could not save your profile."
      );
    });
  });

  it("clears AsyncStorage and resets navigation to Login on logout", async () => {
    const { getByText } = render(
      <UserProfileScreen navigation={mockNavigation} />
    );

    await waitFor(() => expect(getByText("Log Out")).toBeTruthy());

    await act(async () => {
      fireEvent.press(getByText("Log Out"));
    });

    await waitFor(() => {
      expect(AsyncStorage.multiRemove).toHaveBeenCalledWith([
        "authToken",
        "lastCVResult",
        "user",
        "username",
        "userId",
      ]);
      expect(mockNavigation.reset).toHaveBeenCalledWith({
        index: 0,
        routes: [{ name: "Login" }],
      });
    });
  });

  it("falls back to defaults when AsyncStorage.getItem throws on mount", async () => {
    AsyncStorage.getItem.mockRejectedValue(new Error("Storage unavailable"));

    const { getByText } = render(
      <UserProfileScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText("Save Profile")).toBeTruthy();
    });
  });
});
