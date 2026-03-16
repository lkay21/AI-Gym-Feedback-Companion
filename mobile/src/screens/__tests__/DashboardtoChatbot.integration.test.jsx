import React from "react";
import { Text } from "react-native";
import { render, fireEvent } from "@testing-library/react-native";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import DashboardScreen from "../DashboardScreen";

const Stack = createNativeStackNavigator();

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