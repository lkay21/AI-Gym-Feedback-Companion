import { mapPlanToCalendarEvents } from '../planMapping';

describe('mapPlanToCalendarEvents', () => {
  it('maps plan days to calendar events with workout and rest types', () => {
    const plan = {
      weeks: [
        {
          weekNumber: 1,
          days: [
            {
              date: '2026-02-15',
              workoutType: 'Upper Body',
              exercises: [{ name: 'Bench Press', sets: 3, reps: 8, weight: '70%' }],
            },
            {
              date: '2026-02-16',
              workoutType: 'Rest',
              exercises: [],
            },
          ],
        },
      ],
    };

    const events = mapPlanToCalendarEvents(plan);

    expect(events).toHaveLength(2);
    expect(events[0]).toMatchObject({
      title: 'Upper Body',
      date: '2026-02-15',
      type: 'workout',
    });
    expect(events[1]).toMatchObject({
      title: 'Rest',
      date: '2026-02-16',
      type: 'rest',
    });
  });

  it('returns empty array for invalid plan', () => {
    expect(mapPlanToCalendarEvents(null)).toEqual([]);
    expect(mapPlanToCalendarEvents({})).toEqual([]);
  });
});
