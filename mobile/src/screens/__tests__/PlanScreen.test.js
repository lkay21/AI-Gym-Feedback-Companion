import React from 'react';
import { render, waitFor, fireEvent } from '@testing-library/react-native';
import PlanScreen from '../PlanScreen';
import { chatAPI } from '../../services/api';

jest.mock('react-native-calendars', () => {
  const React = require('react');
  const { Text } = require('react-native');

  return {
    Calendar: ({ onDayPress }) => (
      <Text testID="calendar" onPress={() => onDayPress({ dateString: '2026-02-15' })}>
        Calendar
      </Text>
    ),
  };
});

jest.mock('../../services/api', () => ({
  chatAPI: {
    generatePlan: jest.fn(),
  },
}));

const mockPlan = {
  planName: 'Test Plan',
  startDate: '2026-02-15',
  weeks: [
    {
      weekNumber: 1,
      days: [
        {
          date: '2026-02-15',
          workoutType: 'Upper Body',
          exercises: [{ name: 'Bench Press', sets: 3, reps: 8, weight: '70%' }],
        },
      ],
    },
  ],
};

describe('PlanScreen', () => {
  it('renders loading then plan content', async () => {
    chatAPI.generatePlan.mockResolvedValueOnce({
      success: true,
      data: { structuredPlan: mockPlan },
    });

    const { getByText, queryByText } = render(<PlanScreen />);

    expect(getByText('Loading plan...')).toBeTruthy();

    await waitFor(() => {
      expect(queryByText('Loading plan...')).toBeNull();
      expect(getByText('Your Fitness Plan')).toBeTruthy();
    });
  });

  it('opens snapshot modal when a day is pressed', async () => {
    chatAPI.generatePlan.mockResolvedValueOnce({
      success: true,
      data: { structuredPlan: mockPlan },
    });

    const { getByText } = render(<PlanScreen />);

    await waitFor(() => {
      expect(getByText('Your Fitness Plan')).toBeTruthy();
    });

    fireEvent.press(getByText('Calendar'));

    await waitFor(() => {
      expect(getByText('Upper Body')).toBeTruthy();
      expect(getByText('2026-02-15')).toBeTruthy();
    });
  });

  it('shows error state when API fails', async () => {
    chatAPI.generatePlan.mockResolvedValueOnce({
      success: false,
      error: 'Failed to fetch plan',
    });

    const { getByText } = render(<PlanScreen />);

    await waitFor(() => {
      expect(getByText('Failed to fetch plan')).toBeTruthy();
    });
  });
});
