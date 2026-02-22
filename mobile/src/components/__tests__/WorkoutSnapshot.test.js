import React from 'react';
import { render } from '@testing-library/react-native';
import WorkoutSnapshot from '../WorkoutSnapshot';

describe('WorkoutSnapshot', () => {
  it('renders recovery day when workout is undefined', () => {
    const { getAllByText } = render(<WorkoutSnapshot />);

    expect(getAllByText('Recovery Day').length).toBeGreaterThan(0);
  });

  it('renders workout type and exercises', () => {
    const workout = {
      workoutType: 'Upper Body',
      exercises: [
        { name: 'Bench Press', sets: 3, reps: 8, weight: '70%' },
        { name: 'Pull Up', sets: 3, reps: 6, weight: 'Bodyweight' },
      ],
    };

    const { getByText } = render(<WorkoutSnapshot workout={workout} />);

    expect(getByText('Upper Body')).toBeTruthy();
    expect(getByText('Bench Press')).toBeTruthy();
    expect(getByText('3 x 8 x 70%')).toBeTruthy();
    expect(getByText('Pull Up')).toBeTruthy();
  });
});
