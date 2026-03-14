import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';
import LoginScreen from './src/screens/LoginScreen';
import SignupScreen from './src/screens/SignupScreen';
import ChatScreen from './src/screens/ChatScreen';
import PlanScreen from './src/screens/PlanScreen';
import ChatBotScreen from './src/screens/ChatBotScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import InsightsScreen from './src/screens/InsightsScreen';
import SnapshotScreen from './src/screens/SnapshotScreen';
import RecordVideoScreen from './src/screens/RecordVideoScreen';
import ExerciseSelectScreen from './src/screens/ExerciseSelectScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <>
      <StatusBar style="light" />
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Login"
          screenOptions={{
            headerShown: false,
            cardStyle: { backgroundColor: '#1e1b4b' }
          }}
        >
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Signup" component={SignupScreen} />
          <Stack.Screen name="Chat" component={ChatScreen} />
          <Stack.Screen name="Plan" component={PlanScreen} />
          <Stack.Screen name="ChatBot" component={ChatBotScreen} />
          <Stack.Screen name="Dashboard" component={DashboardScreen} />
          <Stack.Screen name="Insights" component={InsightsScreen} />
          <Stack.Screen name="Snapshot" component={SnapshotScreen} />
          <Stack.Screen name="RecordVideo" component={RecordVideoScreen} />
          <Stack.Screen name="ExerciseSelect" component={ExerciseSelectScreen} />
        </Stack.Navigator>
      </NavigationContainer>
    </>
  );
}
