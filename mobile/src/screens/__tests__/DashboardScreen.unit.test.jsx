import React from "react";
import { render, fireEvent } from "@testing-library/react-native";
import DashboardScreen from "../DashboardScreen";

jest.mock("../../components/MenuDropdown", () => {
  const React = require("react");
  const { Text } = require("react-native");

  return function MockMenuDropdown() {
    return <Text>Mock MenuDropdown</Text>;
  };
});

describe("DashboardScreen unit tests", () => {
  const mockNavigation = {
    navigate: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders today's plan card correctly", () => {
    const { getByText } = render(
      <DashboardScreen navigation={mockNavigation} />
    );

    expect(getByText("Fitness Dashboard")).toBeTruthy();
    expect(getByText("Today's Plan")).toBeTruthy();
  });

  it("clears the chat input and navigates after valid send", () => {
    const { getByTestId } = render(
      <DashboardScreen navigation={mockNavigation} />
    );

    const input = getByTestId("chat-input");
    const sendButton = getByTestId("send-button");

    fireEvent.changeText(input, "How do I improve my squat form?");
    expect(input.props.value).toBe("How do I improve my squat form?");

    fireEvent.press(sendButton);

    expect(mockNavigation.navigate).toHaveBeenCalledWith("ChatBot", {
      q: "How do I improve my squat form?",
    });

    expect(getByTestId("chat-input").props.value).toBe("");
  });

  it("does not navigate when the input is empty or whitespace only", () => {
    const { getByTestId } = render(
      <DashboardScreen navigation={mockNavigation} />
    );

    const input = getByTestId("chat-input");
    const sendButton = getByTestId("send-button");

    fireEvent.changeText(input, "   ");
    fireEvent.press(sendButton);

    expect(mockNavigation.navigate).not.toHaveBeenCalled();
    expect(getByTestId("chat-input").props.value).toBe("   ");
  });
});