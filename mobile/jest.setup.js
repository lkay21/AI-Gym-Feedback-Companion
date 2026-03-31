import '@testing-library/jest-native/extend-expect';
import 'react-native-gesture-handler/jestSetup';

// DashboardScreen and api.js import AsyncStorage; Jest has no native module without this mock.
jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock')
);

jest.mock('react-native-reanimated', () => require('react-native-reanimated/mock'));

jest.mock('expo-linear-gradient', () => {
	const React = require('react');
	const { View } = require('react-native');
	return {
		LinearGradient: ({ children, ...props }) => <View {...props}>{children}</View>,
	};
});
