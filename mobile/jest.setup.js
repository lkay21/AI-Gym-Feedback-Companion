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

// react-native-safe-area-context uses native bridges; stub it for all test files.
// Must export SafeAreaInsetsContext so @react-navigation/stack's StackView can
// reference Context.Consumer without crashing.
jest.mock('react-native-safe-area-context', () => {
	const React = require('react');
	const { View } = require('react-native');
	const INSETS = { top: 0, bottom: 0, left: 0, right: 0 };
	const FRAME = { x: 0, y: 0, width: 390, height: 844 };
	const SafeAreaInsetsContext = React.createContext(INSETS);
	const SafeAreaFrameContext = React.createContext(FRAME);
	return {
		SafeAreaView: ({ children, edges, ...props }) =>
			React.createElement(View, props, children),
		SafeAreaProvider: ({ children }) =>
			React.createElement(
				SafeAreaInsetsContext.Provider,
				{ value: INSETS },
				React.createElement(SafeAreaFrameContext.Provider, { value: FRAME }, children)
			),
		SafeAreaConsumer: ({ children }) => children(INSETS),
		SafeAreaInsetsContext,
		SafeAreaFrameContext,
		useSafeAreaInsets: () => INSETS,
		useSafeAreaFrame: () => FRAME,
		initialWindowMetrics: { frame: FRAME, insets: INSETS },
	};
});

// expo-av is a native video module; stub Video so import doesn't crash.
jest.mock('expo-av', () => {
	const React = require('react');
	const { View } = require('react-native');
	return {
		Video: ({ testID, ...props }) =>
			React.createElement(View, { testID: testID ?? 'video-player' }),
		ResizeMode: { CONTAIN: 'contain', COVER: 'cover', STRETCH: 'stretch' },
		Audio: { setAudioModeAsync: jest.fn() },
	};
});

// expo-document-picker opens a native file picker; stub it.
jest.mock('expo-document-picker', () => ({
	getDocumentAsync: jest.fn().mockResolvedValue({ canceled: true, assets: [] }),
}));
