jest.mock("react-native-gesture-handler", () => {
  const React = require("react");
  const { View } = require("react-native");

  return {
    __esModule: true,
    default: {
      install: jest.fn(),
    },
    GestureHandlerRootView: ({ children }) => <View>{children}</View>,
    State: {},
    PanGestureHandler: View,
    TapGestureHandler: View,
    LongPressGestureHandler: View,
    FlingGestureHandler: View,
    ForceTouchGestureHandler: View,
    NativeViewGestureHandler: View,
    RotationGestureHandler: View,
    PinchGestureHandler: View,
    Directions: {},
  };
});

import React from "react";
import { Text } from "react-native";
import { render, fireEvent } from "@testing-library/react-native";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";
import DashboardScreen from "../DashboardScreen";

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

const Stack = createStackNavigator();

function MockChatBotScreen({ route }) {
  return <Text>ChatBot Screen: {route.params?.q}</Text>;
}

describe("Dashboard to ChatBot integration test", () => {
  it("navigates to ChatBot screen after valid input submission", async () => {
    const { getByTestId, findByText } = render(
      <NavigationContainer>
        <Stack.Navigator>
          <Stack.Screen name="Dashboard" component={DashboardScreen} />
          <Stack.Screen name="ChatBot" component={MockChatBotScreen} />
        </Stack.Navigator>
      </NavigationContainer>
    );

    fireEvent.changeText(
      getByTestId("chat-input"),
      "Help me improve lateral raises"
    );

    fireEvent.press(getByTestId("send-button"));

    expect(
      await findByText("ChatBot Screen: Help me improve lateral raises")
    ).toBeTruthy();
  });
});